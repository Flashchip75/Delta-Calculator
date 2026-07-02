import csv
import math
import time
import threading
import serial
from pathlib import Path


class ArduinoRunner:
    """
    Spielt eine results.csv über die serielle Schnittstelle ab.

    Erwartete CSV-Spalten:
    - t
    - omega_1
    - omega_2
    - omega_3

    Arduino-Feedback wird roh geloggt.
    Beispiel:
    80.0,-60.34533,73.50
    """

    def __init__(
        self,
        port,
        baudrate=115200,
        slowdown_factor=1,
        send_frequency_hz=100,
        read_frequency_hz=0,
        log_directory=".",
        on_log=None,
        on_finished=None
    ):
        self.port = port
        self.baudrate = baudrate
        self.slowdown_factor = slowdown_factor
        self.send_frequency_hz = send_frequency_hz
        self.read_frequency_hz = read_frequency_hz
        self.log_directory = Path(log_directory)

        self.on_log = on_log
        self.on_finished = on_finished

        self.running = False
        self.thread = None
        self.ser = None

        self.log_path = self._build_log_path()

    def start(self, results_path):
        """Startet den Arduino-Run in einem separaten Thread."""
        if self.thread is not None and self.thread.is_alive():
            self._log("Arduino-Run läuft bereits.")
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._run_loop,
            args=(results_path,),
            daemon=True
        )
        self.thread.start()

    def stop(self):
        """Stoppt den laufenden Run."""
        self.running = False

    def _run_loop(self, results_path):
        """Lädt Kommandos, öffnet Serial und startet den Sende-/Lesetest."""
        finished_successfully = False
        run_start_time = time.perf_counter()

        try:
            min_time_step = 1 / self.send_frequency_hz

            self._log("Lade Kommandos...")
            commands = self._load_commands(results_path, min_time_step)

            if not commands:
                self._log("Keine gültigen Kommandos gefunden.")
                return

            csv_duration = commands[-1][0] - commands[0][0]

            self._log(f"CSV Sollzeit: {csv_duration:.3f} s")
            self._log(f"Sendefrequenz: {self.send_frequency_hz} Hz")
            self._log(f"Readfrequenz: {self.read_frequency_hz} Hz")
            self._log(f"Anzahl Kommandos: {len(commands)}")
            self._log(f"Logdatei: {self.log_path}")

            self._log("Öffne serielle Schnittstelle...")
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.001)

            # Viele Arduino-Boards resetten beim Öffnen der seriellen Verbindung.
            time.sleep(2)

            self._log("Serielle Verbindung geöffnet.")
            send_runtime = self._send_commands(commands)

            expected_runtime = csv_duration * self.slowdown_factor
            end_delay_ms = (send_runtime - expected_runtime) * 1000

            if send_runtime is not None:
                expected_runtime = csv_duration * self.slowdown_factor
                end_delay_ms = (send_runtime - expected_runtime) * 1000

                self._log(
                    f"Trajektorie: Soll={expected_runtime:.3f} s | "
                    f"Ist={send_runtime:.3f} s | "
                    f"Endverzug={end_delay_ms:.1f} ms"
                )

            if self.running:
                finished_successfully = True
                self._log("Run finished.")

        except Exception as error:
            self._log(f"Arduino-Fehler: {error}")

        finally:
            runtime = time.perf_counter() - run_start_time
            self._send_stop_command()
            self._close_serial()

            self.running = False
            self._log(f"Laufzeit gesamt: {runtime:.3f} s")

            if finished_successfully and self.on_finished is not None:
                self.on_finished()

    def _load_commands(self, results_path, min_time_step):
        """Liest CSV ein und dünnt sie passend zur Sendefrequenz aus."""
        commands = []
        last_sent_t = None

        with open(results_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if self._row_has_nan_values(row):
                    continue

                t = float(row["t"])

                if not self._should_send_time(t, last_sent_t, min_time_step):
                    continue

                cmd = self._build_command(row)
                commands.append((t, cmd))
                last_sent_t = t

        return commands

    def _send_commands(self, commands):
        """Sendet Kommandos zeitlich passend und schreibt Testdaten in eine CSV."""
        self.log_directory.mkdir(parents=True, exist_ok=True)

        start_real_time = time.perf_counter()
        start_csv_time = commands[0][0]
        read_every_n = self._calculate_read_every_n()

        with open(self.log_path, "w", newline="", encoding="utf-8") as log_file:
            writer = csv.writer(log_file)

            writer.writerow([
                "index",
                "t_csv_s",
                "t_target_relative_s",
                "t_send_relative_s",
                "send_delay_ms",
                "read_planned",
                "response_received",
                "raw_response"
            ])

            send_start_time = time.perf_counter()

            for index, (t_csv, cmd) in enumerate(commands):
                if not self.running:
                    self._log("Run wurde gestoppt.")
                    return

                t_target_relative = (t_csv - start_csv_time) * self.slowdown_factor
                target_time = start_real_time + t_target_relative

                sleep_time = target_time - time.perf_counter()
                if sleep_time > 0:
                    time.sleep(sleep_time)

                t_send = time.perf_counter()
                t_send_relative = t_send - start_real_time
                send_delay_ms = (t_send_relative - t_target_relative) * 1000

                self.ser.write((cmd + "\n").encode())

                read_planned = read_every_n is not None and index % read_every_n == 0
                response = None

                if read_planned:
                    response = self._read_response()

                writer.writerow([
                    index,
                    t_csv,
                    t_target_relative,
                    t_send_relative,
                    send_delay_ms,
                    read_planned,
                    response is not None,
                    response if response is not None else ""
                ])



                if index % 100 == 0:
                    self._log(
                        f"sent {index}/{len(commands)} | "
                        f"t_send={t_send_relative:.3f} s | "
                        f"delay={send_delay_ms:.2f} ms"
                    )

            send_runtime = time.perf_counter() - send_start_time
            return send_runtime



    def _calculate_read_every_n(self):
        """Berechnet, jede wievielte gesendete Zeile gelesen werden soll."""
        if self.read_frequency_hz is None or self.read_frequency_hz <= 0:
            return None

        if self.read_frequency_hz >= self.send_frequency_hz:
            return 1

        return max(1, round(self.send_frequency_hz / self.read_frequency_hz))

    def _read_response(self):
        """Liest eine Antwortzeile vom Arduino, falls vorhanden."""
        if self.ser is None or not self.ser.is_open:
            return None

        try:
            line = self.ser.readline().decode(errors="ignore").strip()

            if line == "":
                return None

            return line

        except Exception:
            return None

    def _send_stop_command(self):
        """Sendet am Ende ein Stop-Kommando an alle Motoren."""
        if self.ser is not None and self.ser.is_open:
            self.ser.write(("1,0,0;1,1,0;1,2,0\n").encode())  # ANPASSEN

    def _build_command(self, row):
        """Baut aus einer CSV-Zeile das Arduino-Kommando."""
        omega_0 = float(row["omega_1"])
        omega_1 = float(row["omega_2"])
        omega_2 = float(row["omega_3"])

        return f"1,0,{omega_0};1,1,{omega_1};1,2,{omega_2}"

    def _row_has_nan_values(self, row):
        """Prüft, ob eine Zeile ungültige omega-Werte enthält."""
        omega_0 = float(row["omega_1"])
        omega_1 = float(row["omega_2"])
        omega_2 = float(row["omega_3"])

        return (
            math.isnan(omega_0)
            or math.isnan(omega_1)
            or math.isnan(omega_2)
        )

    def _should_send_time(self, current_t, last_sent_t, min_time_step):
        """Entscheidet, ob diese CSV-Zeit zur gewählten Sendefrequenz passt."""
        if last_sent_t is None:
            return True

        return current_t - last_sent_t >= min_time_step

    def _build_log_path(self):
        """Erzeugt Dateinamen mit Sendefrequenz und Readfrequenz."""
        filename = (
            f"arduino_log_"
            f"send_{self.send_frequency_hz}Hz_"
            f"read_{self.read_frequency_hz}Hz.csv"
        )

        return self.log_directory / filename

    def _close_serial(self):
        """Schließt die serielle Verbindung."""
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            self._log("Serielle Verbindung geschlossen.")

        self.ser = None

    def _log(self, message):
        """Gibt Statusmeldungen an GUI oder Konsole weiter."""
        if self.on_log is not None:
            self.on_log(message)
        else:
            print(message)