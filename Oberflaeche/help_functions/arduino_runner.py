import csv
import math
import time
import threading
import serial


class ArduinoRunner:
    """
    Spielt eine results.csv zeilenweise über die serielle Schnittstelle ab.

    Erwartete CSV-Spalten:
    - t
    - omega_1_rad_s
    - omega_2_rad_s
    - omega_3_rad_s
    """

    def __init__(self, port, baudrate=115200, slowdown_factor=1, on_log=None):
        self.port = port
        self.baudrate = baudrate
        self.slowdown_factor = slowdown_factor
        self.on_log = on_log

        self.running = False
        self.thread = None
        self.ser = None

    def start(self, results_path):
        """
        Startet das Abspielen der results.csv in einem eigenen Thread.
        """

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
        """
        Stoppt den laufenden Arduino-Run.
        """

        self.running = False

    def _run_loop(self, results_path):
        """
        Öffnet die serielle Schnittstelle und sendet die CSV-Zeilen
        zeitlich passend an den Arduino.
        """

        try:
            self._log("Öffne serielle Schnittstelle...")

            self.ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=0.1
            )

            # Viele Arduino-Boards resetten beim Öffnen der seriellen Verbindung.
            time.sleep(2)

            self._log("Serielle Verbindung geöffnet.")
            self._send_csv_rows(results_path)
            self._log("Run finished.")

        except Exception as error:
            self._log(f"Arduino-Fehler: {error}")

        finally:
            self._close_serial()
            self.running = False

    def _send_csv_rows(self, results_path):
        """
        Liest die CSV zeilenweise und sendet immer die aktuelle Zeile.
        Für die Wartezeit wird die nächste Zeile benötigt.
        """

        with open(results_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            try:
                current_row = next(reader)
            except StopIteration:
                self._log("CSV ist leer.")
                return

            for next_row in reader:
                if not self.running:
                    self._log("Run wurde gestoppt.")
                    return

                self._send_row(current_row)

                delta_t = self._calculate_delta_t(current_row, next_row)

                if delta_t > 0:
                    time.sleep(delta_t * self.slowdown_factor)

                current_row = next_row

            # Letzte Zeile senden
            if self.running:
                self._send_row(current_row)

    def _send_row(self, row):
        """
        Baut aus einer CSV-Zeile ein Kommando und sendet es.
        """

        if self._row_has_nan_values(row):
            self._log("Zeile mit NaN-Werten übersprungen.")
            return

        cmd = self._build_command(row)

        self.ser.write((cmd + "\n").encode())

        response = self.ser.readline().decode(errors="ignore").strip()

        t_csv = float(row["t"])

        self._log(
            f"t={t_csv:.4f} s | sent: {cmd} | received: {response}"
        )

    def _build_command(self, row):
        """
        Baut das Paket für alle drei Motoren.

        Aktueller Syntax:
        1,0,omega_0;1,1,omega_1;1,2,omega_2
        """

        omega_0 = float(row["omega_1"])
        omega_1 = float(row["omega_2"])
        omega_2 = float(row["omega_3"])

        return f"1,0,{omega_0};1,1,{omega_1};1,2,{omega_2}"

    def _calculate_delta_t(self, current_row, next_row):
        """
        Berechnet die Wartezeit zwischen zwei CSV-Zeilen.
        """

        current_t = float(current_row["t"])
        next_t = float(next_row["t"])

        delta_t = next_t - current_t

        if delta_t < 0:
            self._log("Warnung: negativer Zeitschritt in CSV erkannt.")
            return 0

        return delta_t

    def _row_has_nan_values(self, row):
        """
        Prüft, ob eine Zeile ungültige omega-Werte enthält.
        """

        omega_0 = float(row["omega_1"])
        omega_1 = float(row["omega_2"])
        omega_2 = float(row["omega_3"])

        return (
            math.isnan(omega_0)
            or math.isnan(omega_1)
            or math.isnan(omega_2)
        )

    def _close_serial(self):
        """
        Schließt die serielle Schnittstelle sauber.
        """

        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            self._log("Serielle Verbindung geschlossen.")

        self.ser = None

    def _log(self, message):
        """
        Gibt Debug-Informationen aus.
        """

        if self.on_log is not None:
            self.on_log(message)
        else:
            print(message)