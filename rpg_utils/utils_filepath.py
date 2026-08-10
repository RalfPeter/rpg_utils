#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 10-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm          : utils_filepath.py
#  Version           : 2.0
#  Beschreibung      : Keine Beschreibung verfügbar.
#  Zeilen            : 417
#  Abhängigkeiten    : datetime, pathlib, platform, re, sys, tempfile
#  Klassen           : PathUtils
# ------------------------------------------------------------------------------
#  Public Methoden:
#    PathUtils                                            → Statische Klasse zur Kapselung aller Hilfsfunktionen für Dateipfade und
#      validate_input_directories(list[str], bool)        → Prüft, ob alle Pfade in `inputpaths` existierende Verzeichnisse sind.
#      get_subdirectories(list[str], bool)                → Gibt eine sortierte Liste aller Unterverzeichnisse (einschließlich der
#      safe_rename(Path | str, Path | str, bool)          → Benennt eine Datei sicher um und behandelt gängige Fehler (FileNotFound,
#      get_basename_without_prefix(Path | str)            → Extrahiert den Basisnamen einer Datei, entfernt dabei einen
#      create_new_filepath(Path | str, datetime)          → Erzeugt einen neuen Dateipfad basierend auf einem datetime-Objekt und
#      rename_file_with_datetime(Path | str, 
#                                datetime)                → Benennt eine Datei anhand eines datetime-Objekts um, falls der
#      is_writable(Path)                                  → Prüft, ob in das angegebene Verzeichnis geschrieben werden kann.
#      get_config_dir(str, bool)                          → Ermittelt das plattformspezifische Verzeichnis für Konfigurationsdateien.
#      get_script_dir(bool)                               → Gibt den Pfad des Ordners zurück, in dem das Skript/die ausführbare Datei
#      get_main_script_name()                             → Gibt den reinen Dateinamen des gestarteten Hauptskripts zurück.
#      get_script_name(str, bool)                         → Gibt den reinen Dateinamen des gestarteten Hauptskripts oder der EXE zurück.
#      get_temp_dir(bool)                                 → Ermittelt das systemweite Verzeichnis für temporäre Dateien.
#      get_work_dir(bool)                                 → Gibt den Pfad des temporären Ordners zurück, falls das Skript
#      get_data_dir(str, bool)                            → Gibt den Path zum Datenordner ('data') im Skript / Config Verzeichnis zurück.
#      get_resource_dir()                                 → Gibt den Path zum Ressourcenordner ('resources') im im Skriptverzeichnis zurück.
#      get_ui_dir()                                       → Path of UI folder
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter.bergheim@gmail.com>
# ------------------------------------------------------------------------------

import sys
import re
import platform
import tempfile
from datetime import datetime
from pathlib import Path

from rpg_utils.utils_core import log_to_callback, CallbackTag as Tag

# --- Konstanten zur besseren Wartbarkeit ---
# Die Konstanten werden als Klassenattribute in PathUtils definiert.
DATETIME_PREFIX_PATTERN: re.Pattern = re.compile(r'^(\d{8}_\d{6})(.*)$')
# -------------------------------------------------------------------------------------------
# Konstanten für gängige Zeichenkodierungen.
# -------------------------------------------------------------------------------------------
# Encoding
ENCODING_UTF8 = 'utf-8'
ENCODING_UTF8_SIG = 'utf-8-sig'
ENCODING_ISO = 'iso-8859-1'


# ================================================================================
# Path Utilities
# ================================================================================
class PathUtils:
    """Statische Klasse zur Kapselung aller Hilfsfunktionen für Dateipfade und"""

    # Klassenkonstanten für häufig verwendete Ordnernamen
    FOLDER_RESOURCES: str = 'resources'
    FOLDER_DATA: str = 'data'
    FOLDER_UI = 'ui'

    # --- Validierung und Suche ---

    # --------------------------------------------------------------------------------
    @staticmethod
    def validate_input_directories(inputpaths: list[str] | None, verbose: bool = False) -> bool:
        """
        Prüft, ob alle Pfade in `inputpaths` existierende Verzeichnisse sind.

        :param inputpaths: Liste der zu prüfenden Pfade (Strings).
        :param verbose: bool: Ausgabe von Log
        :return: True, wenn alle Pfade existieren und Verzeichnisse sind, sonst False.
        """
        if inputpaths is None:
            return False

        for p in inputpaths:
            path = Path(p)
            if not path.is_dir():
                if verbose:
                    log_to_callback(Tag.ERR, 'Validate Inputpaths', f"Eingabepfad existiert nicht: {p}")
                return False

        return True

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_subdirectories(directories: list[str] | None, recursive: bool = True) -> list[Path]:
        """
        Gibt eine sortierte Liste aller Unterverzeichnisse (einschließlich der
        Eingangsverzeichnisse) als Path-Objekte zurück.

        :param directories: Die Startverzeichnisse (Strings).
        :param recursive: True, um alle Unterverzeichnisse rekursiv zu suchen.
        :return: Liste von Path-Objekten der gefundenen Verzeichnisse.
        """
        if directories is None:
            return []

        found_directories: set[Path] = set()

        for directory in directories:
            path = Path(directory).resolve()

            # Füge das Startverzeichnis hinzu
            if path.is_dir():
                found_directories.add(path)

            if recursive:
                # Nutze rglob ('**/' um rekursiv zu suchen)
                # '*/' stellt sicher, dass nur Verzeichnisse gefunden werden.
                for subdir in path.rglob('*/'):
                    if subdir.is_dir():
                        found_directories.add(subdir.resolve())

        # Rückgabe als sortierte Liste von Path-Objekten
        return sorted(list(found_directories))

    # --- Datei-Operationen ---

    # --------------------------------------------------------------------------------
    @staticmethod
    def safe_rename(src: Path | str, dst: Path | str, verbose: bool = False) -> bool:
        """
        Benennt eine Datei sicher um und behandelt gängige Fehler (FileNotFound,
        FileExists, PermissionError).

        :param src: Der Quellpfad (Path oder String).
        :param dst: Der Zielpfad (Path oder String).
        :param verbose: bool: Ausgabe von Log
        :return: True bei Erfolg, False bei Fehler.
        """
        src_path = Path(src).resolve()
        dst_path = Path(dst).resolve()

        try:
            # Path.rename() ist atomar (wo möglich) und bevorzugt
            src_path.rename(dst_path)
            return True
        except FileNotFoundError:
            if verbose:
                log_to_callback(Tag.ERR, 'Umbenennen', f'Die Quelldatei {src_path.name} wurde nicht gefunden.')
            return False
        except FileExistsError:
            if verbose:
                log_to_callback(Tag.LOG, 'Umbenennen', f'Die Zieldatei {dst_path.name} existiert bereits.')
            return False
        except PermissionError:
            if verbose:
                log_to_callback(Tag.LOG, 'Umbenennen', f'Keine Berechtigung, um die Datei {src_path.name} oder {dst_path.name} zu ändern.')
            return False
        except OSError as e:
            if verbose:
                log_to_callback(Tag.LOG, 'Umbenennen', f'Ein unerwarteter Fehler ist aufgetreten: {e}')
            return False

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_basename_without_prefix(file: Path | str) -> str:
        """
        Extrahiert den Basisnamen einer Datei, entfernt dabei einen
        Datums-/Zeitstempel-Präfix der Form 'YYYYMMDD_HHMMSS'.
        Fasst `get_basename` zusammen.

        :param file: Der Dateipfad (Path oder String).
        :return: Der bereinigte Basisname (ohne Pfad und Extension).
        """
        # Dateiname extrahieren (ohne Pfad und Extension)
        filename_stem = Path(file).stem

        # Wende den Regex an (definiert oben als Konstante)
        match = DATETIME_PREFIX_PATTERN.match(filename_stem)

        if match:
            # Extrahiere den Teil nach dem Präfix (Gruppe 2)
            basename = match.group(2)
        else:
            # Name ohne Datums-/Zeit-Präfix
            basename = filename_stem

        # Entferne führende Trennzeichen ('-', '_', '#') und gib ihn zurück
        return basename.lstrip('-_#')

    # --------------------------------------------------------------------------------
    @staticmethod
    def create_new_filepath(file: Path | str, dt: datetime | None) -> Path | None:
        """
        Erzeugt einen neuen Dateipfad basierend auf einem datetime-Objekt und
        dem bereinigten Basisnamen der Originaldatei.
        Fasst `new_filename` zusammen.

        Neues Format: 'YYYYMMDD_HHMMSS-basename.ext'

        :param file: Der ursprüngliche Dateipfad.
        :param dt: Das datetime-Objekt, das als neuer Präfix verwendet wird.
        :return: Der neue Path-Objekt oder None, wenn dt fehlt.
        """
        if dt is None:
            return None

        original_path = Path(file)

        # Pfad, Extension und bereinigten Basisnamen extrahieren
        path = original_path.parent
        extension = original_path.suffix
        basename = PathUtils.get_basename_without_prefix(original_path)

        # Erzeuge das neue Datums-/Zeit-Präfix
        new_prefix = dt.strftime('%Y%m%d_%H%M%S')

        # Erzeuge den neuen Dateinamen-Stem
        new_stem = new_prefix
        if basename:
            new_stem = f"{new_prefix}-{basename}"

        # Finalen Path zusammenbauen
        new_name = f"{new_stem}{extension}"

        return path / new_name

    # --------------------------------------------------------------------------------
    @staticmethod
    def rename_file_with_datetime(file: Path | str, dt: datetime | None = None) -> tuple[bool, Path]:
        """
        Benennt eine Datei anhand eines datetime-Objekts um, falls der
        generierte Name abweicht und die Zieldatei nicht existiert.
        Fasst `rename_file` zusammen.

        :param file: Der ursprüngliche Dateipfad.
        :param dt: Das datetime-Objekt für den neuen Dateinamen-Präfix.
        :return: Ein Tupel (Erfolg: bool, Neuer/Alter Path: Path).
        """
        if dt is None:
            # Rückgabe des Originalpfades bei fehlendem Datum
            return False, Path(file)

        original_file = Path(file).resolve()
        new_file = PathUtils.create_new_filepath(original_file, dt)

        # 1. Prüfen, ob eine Umbenennung nötig ist
        if new_file is None or new_file.name == original_file.name:
            return False, original_file

        # 2. Prüfen, ob die Zieldatei bereits existiert (optional, da safe_rename dies auch tut)
        if new_file.is_file():
            log_to_callback(Tag.LOG, 'Rename Check', f'Die Datei [{new_file.name}] existiert bereits. [{original_file.name}] wurde nicht umbenannt.')
            return False, original_file

        # 3. Umbenennung durchführen
        if PathUtils.safe_rename(original_file, new_file):
            # Im Erfolgsfall das neue Path-Objekt zurückgeben
            log_to_callback(Tag.LOG, 'UNDO-RENAME', f'"{new_file}" "{original_file.name}"')
            return True, new_file
        else:
            return False, original_file

    # --------------------------------------------------------------------------------
    # --- Pfad-Lokalisierungsfunktionen ---
    @staticmethod
    def is_writable(directory: Path) -> bool:
        """
        Prüft, ob in das angegebene Verzeichnis geschrieben werden kann.

        :param directory: (Path) Der zu prüfende Ordner.
        :return: (bool) True, wenn schreibbar, sonst False.
        """
        # Wenn der Pfad nicht existiert, prüfen wir das übergeordnete Verzeichnis
        if not directory.exists():
            directory = directory.parent

        # Wir erstellen eine temporäre Datei, um den Schreibzugriff zu verifizieren
        test_file = directory / ".permission_test"
        try:
            test_file.touch()  # Erstellt eine leere Datei
            test_file.unlink()  # Löscht sie sofort wieder
            return True
        except (PermissionError, OSError):
            return False

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_config_dir(app_name: str = '', verbose: bool = False) -> Path:
        """
        Ermittelt das plattformspezifische Verzeichnis für Konfigurationsdateien.

        :param app_name: (str) Name der Anwendung für die Pfadbildung.
        :param verbose: Gibt an, ob der Pfad geloggt werden soll.
        :return: (Path) Der absolute Pfad zum Konfigurationsverzeichnis.
        """
        # wir wollen die config und data im Ordner der Anwendung, sofern Rechte vorhanden
        path = PathUtils.get_script_dir(verbose=verbose)
        if PathUtils.is_writable(path):
            return path

        system = platform.system()
        home = Path.home()
        if not app_name:
            app_name = PathUtils.get_script_name(verbose=verbose)

        if system == "Windows":
            # Windows: AppData/Roaming
            config_dir = home / "AppData" / "Roaming" / app_name
        elif system == "Darwin":
            # macOS: ~/Library/Application Support
            config_dir = home / "Library" / "Application Support" / app_name
        else:
            # Linux/Unix: ~/.config/ (XDG Standard)
            config_dir = home / ".config" / app_name

        # Verzeichnis sicherstellen
        config_dir.mkdir(parents=True, exist_ok=True)

        if verbose:
            log_to_callback(Tag.LOG, f"Aktuelles Start-Verzeichnis: {config_dir}")
        return config_dir

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_script_dir(verbose: bool = False) -> Path:
        """
        Gibt den Pfad des Ordners zurück, in dem das Skript/die ausführbare Datei
        gestartet wurde (entspricht `get_scriptfolder`).

        :param verbose: Gibt an, ob der Pfad geloggt werden soll.
        :return: Das Path-Objekt des Skript-/Exe-Ordners.
        """
        if getattr(sys, 'frozen', False):
            # Wenn das Skript als ausführbare Datei (z.B. mit PyInstaller) ausgeführt wird
            path = Path(sys.executable).resolve().parent
        else:
            # Im normalen Python-Kontext: Pfad der gestarteten Datei
            path = Path(sys.argv[0]).resolve().parent

        if verbose:
            log_to_callback(Tag.LOG, f"Aktuelles Start-Verzeichnis: {path}")
        return path

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_main_script_name() -> str:
        """Gibt den reinen Dateinamen des gestarteten Hauptskripts zurück.
        
        :return: (str) Beschreibung des Rückgabewerts.
        """

        if sys.argv and sys.argv[0]:
            return Path(sys.argv[0]).name
        return "Unbekannt"

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_script_name(suffix: str = "", verbose: bool = False) -> str:
        """Gibt den reinen Dateinamen des gestarteten Hauptskripts oder der EXE zurück.

        Berücksichtigt, ob das Programm normal oder als PyInstaller-EXE läuft.

        :param suffix: (str) Optionale neue Dateiendung (z.B. '.log' oder '.ini').
        :param verbose: (bool) Wenn True, wird der Pfad in die Logs geschrieben.
        :return: (str) Der Dateiname (z.B. 'prg_gopro2file.py' oder 'prg_gopro2file.exe').
        """
        if getattr(sys, "frozen", False):
            # Kontext: Kompilierte PyInstaller-EXE
            path = Path(sys.executable).resolve()
        else:
            # Kontext: Normales Python-Skript (z.B. in PyCharm)
            path = Path(sys.argv[0]).resolve() if sys.argv and sys.argv[0] else Path("Unbekannt.py")

        if verbose:
            # Ersetze 'log' durch deine tatsächliche Logging-Funktion
            print(f"Aktuelles Skript geladen von: {path}")

        if suffix:
            return path.with_suffix(suffix).name

        return path.name

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_temp_dir(verbose: bool = False) -> Path:
        """Ermittelt das systemweite Verzeichnis für temporäre Dateien.
        
        :param verbose: (bool) Beschreibung von verbose.
        :return: (Path) Beschreibung des Rückgabewerts.
        """

        # tempfile.gettempdir() liefert den Pfad als String zurück
        path = Path(tempfile.gettempdir()).resolve()
        if verbose:
            log_to_callback(Tag.LOG, f"Aktuelles TMP-Verzeichnis: {path}")
        return path

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_work_dir(verbose: bool = False) -> Path:
        """
        Gibt den Pfad des temporären Ordners zurück, falls das Skript
        als ausführbare Datei entpackt wurde (z.B. bei PyInstaller _MEIPASS)
        oder das aktuelle Arbeitsverzeichnis.

        :param verbose: Gibt an, ob der Pfad geloggt werden soll.
        :return: Das Path-Objekt des temporären Ordners/Arbeitsverzeichnisses.
        """
        if getattr(sys, 'frozen', False):
            # Zugriff auf den temporären Ordner (_MEIPASS) oder Fallback auf das aktuelle Verzeichnis
            path = Path(getattr(sys, '_MEIPASS', Path.cwd())).resolve()
        else:
            # Aktuelles Arbeitsverzeichnis
            path = Path.cwd().resolve()

        if verbose:
            log_to_callback(Tag.LOG, f"Aktuelles Exe-Verzeichnis: {path}")
        return path

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_data_dir(app_name: str = '', verbose: bool = False) -> Path:
        """
        Gibt den Path zum Datenordner ('data') im Skript / Config Verzeichnis zurück.

        :param app_name: (str) Name der Anwendung für die Pfadbildung.
        :param verbose: Gibt an, ob der Pfad geloggt werden soll.
        """
        if not app_name:
            app_name = PathUtils.get_script_name(verbose=verbose)

        return PathUtils.get_config_dir(app_name=app_name, verbose=verbose) / PathUtils.FOLDER_DATA

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_resource_dir() -> Path:
        """Gibt den Path zum Ressourcenordner ('resources') im im Skriptverzeichnis zurück.
        
        :return: (Path) Beschreibung des Rückgabewerts.
        """

        return PathUtils.get_work_dir() / PathUtils.FOLDER_RESOURCES

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_ui_dir() -> Path:
        """Path of UI folder
        
        :return: (Path) Beschreibung des Rückgabewerts.
        """

        return PathUtils.get_work_dir() / PathUtils.FOLDER_UI
