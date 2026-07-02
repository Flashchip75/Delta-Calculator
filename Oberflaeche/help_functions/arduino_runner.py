import csv
import math
import time
import threading
import serial


# Öffnet die serielle Schnittstelle im Hintergrundthread.
# Tkinter darf aus diesem Thread nicht direkt aktualisiert werden.
class ArduinoRunner:
    """
    Spielt eine results.csv über die serielle Schnittstelle ab.

    Erwartete CSV-Spalten:
    - t
    - omega_1
    - omega_2
    - omega_3
    """

    def __init__(self, port, baudrate=115200, slowdown_factor=1, on_log=None, on_finished=None):
        self.port = port
        self.baudrate = baudrate
        self.slowdown_factor = slowdown_factor
        self.on_log = on_log
        self.on_finished = on_finished

        self.running = False
        self.thread = None
        self.ser = None

    def start(self, results_path):
        if self.thread is not None and self.thread.is_alive():
            self._log("Arduino-Run läuft bereits.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, args=(results_path,), daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run_loop(self, results_path):
        finished_successfully = False
        start_time = time.perf_counter()

        try:
            self._log("Lade Kommandos...")
            commands = self._load_commands(results_path, min_time_step=0.01)

            if not commands:
                self._log("Keine gültigen Kommandos gefunden.")
                return

            csv_duration = commands[-1][0] - commands[0][0]
            self._log(f"CSV Sollzeit: {csv_duration:.3f} s")
            self._log(f"Anzahl Kommandos: {len(commands)}")

            self._log("Öffne serielle Schnittstelle...")
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.001)

            # Viele Arduino-Boards resetten beim Öffnen der seriellen Verbindung.
            time.sleep(2)

            self._log("Serielle Verbindung geöffnet.")

            self._log("Starte Referenzfahrt und fahre Startwinkel an...")
            self._perform_reference_run(results_path)

            self._log("Starte Trajektorie...")
            self._send_commands(commands)

            if self.running:
                finished_successfully = True
                self._log("Run finished.")

        except Exception as error:
            self._log(f"Arduino-Fehler: {error}")

        finally:
            runtime = time.perf_counter() - start_time
            self._send_stop_command()
            self._close_serial()
            self.running = False
            self._log(f"Laufzeit: {runtime:.3f} s")

            if finished_successfully and self.on_finished is not None:
                self.on_finished()

    def _load_commands(self, results_path, min_time_step=0.01):
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
        start_real_time = time.perf_counter()
        start_csv_time = commands[0][0]

        for index, (t_csv, cmd) in enumerate(commands):
            if not self.running:
                self._log("Run wurde gestoppt.")
                return

            target_time = start_real_time + (t_csv - start_csv_time) * self.slowdown_factor
            sleep_time = target_time - time.perf_counter()

            if sleep_time > 0:
                time.sleep(sleep_time)

            self.ser.write((cmd + "\n").encode())

            if index % 100 == 0:
                self._log(f"t={t_csv:.4f} s | sent command {index}/{len(commands)}")

    def _send_stop_command(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.write(("0,0,0,1,0,2,0\n").encode())

    def _build_command(self, row):
        omega_0 = float(row["omega_1"])
        omega_1 = float(row["omega_2"])
        omega_2 = float(row["omega_3"])
        return f"0,0,{omega_0*200/2/3.14159:.3f},1,{omega_1*200/2/3.14159:.3f},2,{omega_2*200/2/3.14159:.3f}"

    def _row_has_nan_values(self, row):
        omega_0 = float(row["omega_1"])
        omega_1 = float(row["omega_2"])
        omega_2 = float(row["omega_3"])

        return math.isnan(omega_0) or math.isnan(omega_1) or math.isnan(omega_2)

    def _should_send_time(self, current_t, last_sent_t, min_time_step):
        if last_sent_t is None:
            return True

        return current_t - last_sent_t >= min_time_step

    def _close_serial(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            self._log("Serielle Verbindung geschlossen.")

        self.ser = None

    def _log(self, message):
        if self.on_log is not None:
            self.on_log(message)
        else:
            print(message)



    def _load_start_angles(self, results_path):
        with open(results_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if self._row_has_nan_angle_values(row):
                    continue

                phi_0 = float(row["phi_1"])
                phi_1 = float(row["phi_2"])
                phi_2 = float(row["phi_3"])

                return phi_0, phi_1, phi_2

        raise ValueError("Keine gültige Startposition in results.csv gefunden.")


    def _perform_reference_run(self, results_path, timeout_s=30):
        start_angles = self._load_start_angles(results_path)

        reference_command = (
            f"1,"
            f"0,{start_angles[0]},"
            f"1,{start_angles[1]},"
            f"2,{start_angles[2]}"
        )

        self._log(f"Sende Referenzfahrt: {reference_command}")
        self.ser.write((reference_command + "\n").encode())

        start_time = time.perf_counter()

        while self.running:
            if time.perf_counter() - start_time > timeout_s:
                raise TimeoutError("Timeout: Arduino hat kein 'Startbereit' gesendet.")

            line = self.ser.readline().decode(errors="ignore").strip()

            if not line:
                continue

            self._log(f"Arduino: {line}")

            if line == "Startbereit":
                self._log("Arduino ist startbereit.")
                return

        raise RuntimeError("Referenzfahrt wurde abgebrochen.")

    def _row_has_nan_angle_values(self, row):
        phi_0 = float(row["phi_1"])
        phi_1 = float(row["phi_2"])
        phi_2 = float(row["phi_3"])

        return math.isnan(phi_0) or math.isnan(phi_1) or math.isnan(phi_2)