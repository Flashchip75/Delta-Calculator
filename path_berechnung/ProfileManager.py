import json

class ProfileManager:
    def __init__(self, filepath: str):
        """Initialisiert den Manager und lädt die JSON-Datei in den Speicher."""
        self.filepath = filepath
        self.profiles = self._load_profiles()

    def _load_profiles(self) -> dict:
        """Interne Methode zum Auslesen der JSON-Datei."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Fehler: Die Datei '{self.filepath}' wurde nicht gefunden.")
            return {}
        except json.JSONDecodeError:
            print(f"Fehler: Die Datei '{self.filepath}' ist ungültig oder beschädigt.")
            return {}

    def get_profile(self, profileName: str) -> list:
        """
        Nimmt einen String (Profilnamen) entgegen und gibt die jData-Liste zurück.
        Wirft einen Fehler, wenn das Profil nicht existiert.
        """
        if profileName not in self.profiles:
            raise KeyError(f"Das Profil '{profileName}' existiert in {self.filepath} nicht.")
        
        return self.profiles[profileName]