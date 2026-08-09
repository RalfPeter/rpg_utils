#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 06-08-2026
# Ralf Peter <ralfpeter61@email.de>
# https://github.com/RalfPeter/tracktraffic.git
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Program : utils_core.py (main - GoPro Videos and Telemetry Export)
#  Version : 1.0
# ------------------------------------------------------------------------------
#  Klassen:
#     CallbackTag
#     ProgressType
#     ProgressEvent
#     AppCallback
#     DummyStream
#     AppLogger
#  Public Methods:
#     ProgressEvent.start(total)          → Keine Beschreibung.
#     ProgressEvent.update(current, total) → Keine Beschreibung.
#     ProgressEvent.finished()            → Keine Beschreibung.
#     DummyStream.write(_message)         → Ignoriert Schreiboperationen.
#     DummyStream.flush()                 → Erfüllt das Stream-Interface.
#     AppLogger.create(logfile_path, use_console) → Factory-Methode: Erstellt, konfiguriert und registriert den Logger in einem Schritt.
#     AppLogger.logfile()                 → :return: (Path | None) Der aktuelle Pfad zur Logdatei (nur lesen).
#     AppLogger.gui_callback()            → Gibt den aktuellen GUI-Callback zurück.
#     AppLogger.gui_callback(value)       → Setzt den GUI-Callback (sollte ein Signal-Emit sein).
#     AppLogger.progress_callback()       → Gibt den aktuellen Progress-Callback zurück.
#     AppLogger.progress_callback(value)  → Setzt den Progress-Callback (sollte ein Signal-Emit sein).
#     fatal(msg, exitcode)                → Gibt eine optionale Fehlermeldung aus und beendet das Skript.
#     initialize_windows_app_id(company, program, version) → Registriert die Anwendung explizit beim Windows-System, damit das
#     setup_crash_logger()                → Registriert einen globalen excepthook für unerwartete Abstürze.
#     write_crash_file(message)           → Zentrale Hilfsfunktion zum Schreiben in die CRASH_LOG.txt.
#     log_to_callback(tag)                → Zentrale Schnittstelle für alle Frameworks.
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter61@email.de>
# ------------------------------------------------------------------------------

from __future__ import annotations
import traceback
import sys
import ctypes
from dataclasses import dataclass
from enum import Enum, auto
import textwrap
from inspect import currentframe
from logging import ERROR, INFO, WARN, FileHandler, Formatter, Logger, StreamHandler, getLogger
from pathlib import Path
from typing import Any, Callable, TypeAlias, Protocol, runtime_checkable


# ===========================================================================
# Konstanten
# ===========================================================================
DEFAULT_LOGGER_NAME: str = "main_logger"
HANDLER_CONSOLE: str = "main_console"
HANDLER_FILE: str = "main_file"
CRASH_FILE: str = "src/main_crashlog.txt"

MSG_LEN: int = 120
VALUE_LEN: int = 90
PREFIX_LEN: int = 25
PREFIX_FMT: str = f"{{:<{PREFIX_LEN}}}: "
VALUE_FMT: str = "{}\t"
VALUE_NEW_FMT: str = f"{'->':<{PREFIX_LEN}}: "
TRENNER = '-' * (VALUE_LEN+3)  # Trenner im Log


# ================================================================================
# ================================================================================
class CallbackTag(Enum):
    """
    Definiert die zulässigen Kategorien für Callback-Kommunikation.
    """
    LOG = auto()       # Dauerhaftes Logging (Datei + GUI/Konsole)
    STATUS = auto()    # Nur temporäre Info für die UI
    PROGRESS = auto()  # Exklusiv für Progressbar-Daten (Start/Update/Finish)
    WARN = auto()
    ERR = auto()


# ================================================================================
# ================================================================================
class ProgressType(Enum):
    START = auto()
    UPDATE = auto()
    FINISHED = auto()


# ================================================================================
# ================================================================================
@dataclass(frozen=True)
class ProgressEvent:
    type: ProgressType
    current: int = 0
    total: int = 0
    message: str = ""

    # --------------------------------------------------------------------------------
    @classmethod
    def start(cls, total: int) -> ProgressEvent:
        return cls(type=ProgressType.START, total=total)

    # --------------------------------------------------------------------------------
    @classmethod
    def update(cls, current: int, total: int) -> ProgressEvent:
        return cls(type=ProgressType.UPDATE, current=current, total=total)

    # --------------------------------------------------------------------------------
    @classmethod
    def finished(cls) -> ProgressEvent:
        return cls(type=ProgressType.FINISHED)


# --------------------------------------------------------------------------------
# Typen für Callback-Funktionen (Kompatibel mit Python 3.10+)
# --------------------------------------------------------------------------------
GuiCallback: TypeAlias = Callable[[str], None]
ProgressCallback: TypeAlias = Callable[[ProgressEvent], None]


# ================================================================================
# Universal-Callback für alle Framework-Ausgaben (Status, Log, Progress)
# ================================================================================
@runtime_checkable
class AppCallback(Protocol):
    
    # --------------------------------------------------------------------------------
    def __call__(self, tag: CallbackTag, *args: Any) -> None:
        ...


# ================================================================================
# ================================================================================
class DummyStream:
    """Null-Object-Pattern für sys.stdout/stderr in GUI-Umgebungen.

    Verhindert AttributeError (NoneType hat kein Attribut 'write'), wenn die Anwendung
    mit PyInstaller im fensterbasierten Modus (--noconsole / -w) kompiliert wurde.
    """

    # --------------------------------------------------------------------------------
    def write(self, _message: str) -> None:
        """Ignoriert Schreiboperationen.

        :param _message: (str) Nachricht.
        """
        pass

    # --------------------------------------------------------------------------------
    def flush(self) -> None:
        """Erfüllt das Stream-Interface."""
        pass


# ===========================================================================
# Hauptklasse für das Logging
# ===========================================================================
class AppLogger:
    """Zentrale Klasse für Logging-Mechanismen, Handler und GUI-Callbacks."""

    # --------------------------------------------------------------------------------
    def __init__(
        self,
        name: str = DEFAULT_LOGGER_NAME,
        level: int = INFO,
        gui_callback: GuiCallback | None = None,
        progress_callback: ProgressCallback | None = None,
        use_console: bool = True,
    ) -> None:
        """Initialisiert den Logger.

        :param name: (str) Name der Logger-Instanz.
        :param level: (int) Initiales Logging-Level.
        :param gui_callback: (GuiCallback | None) Callback für direkte CLI-Ausgaben.
        :param progress_callback: (StepCallback | None) Callback für CLI-Fortschritt.
        :param use_console: (bool) auf Konsole ausgeben
        """
        self._use_console: bool = use_console
        self._gui_callback: GuiCallback | None = gui_callback
        self._progress_callback: ProgressCallback | None = progress_callback
        self._logfile: Path | None = None

        # Logger initialisieren
        self._logger: Logger = getLogger(name)
        self._logger.setLevel(level)
        self._logger.propagate = False

        if self._use_console:
            self._init_console_handler(level)

    # --------------------------------------------------------------------------------
    @classmethod
    def create(cls, logfile_path: Path | None = None, use_console: bool = True) -> AppLogger:
        """
        Factory-Methode: Erstellt, konfiguriert und registriert den Logger in einem Schritt.

        :param logfile_path: (Path | None) Pfad zur Logdatei.
        :param use_console: (bool) Ob die Konsole genutzt werden soll.
        :return: (AppLogger) Die fertig konfigurierte Instanz.
        """
        # 1. Instanz erstellen
        logger = cls(use_console=use_console)

        # 2. Datei-Konfiguration (falls Pfad angegeben)
        if logfile_path:
            logger._configure_files(filepath=logfile_path, level=INFO)

        # 3. Kontext-Registrierung (ersetzt das alte 'register_callback')
        cls._register_callback(func=logger)

        return logger

    # --------------------------------------------------------------------------------
    @classmethod
    def _register_callback(cls, func: AppCallback | None) -> None:
        """
        Zentrale Registrierung für alle Callbacks

        :param func: (AppCallback) Die AppLogger Instanz die registriert werden soll
        """
        global _active_callback

        # Prüfe, ob sich der Zustand überhaupt ändert
        if _active_callback is func:
            return

        _active_callback = func

    # --------------------------------------------------------------------------------
    @property
    def logfile(self) -> str:
        """:return: (Path | None) Der aktuelle Pfad zur Logdatei (nur lesen)."""
        if self._logfile is None:
            return "unknown logfile name"
        else:
            return str(self._logfile)

    # --------------------------------------------------------------------------------
    @property
    def gui_callback(self) -> GuiCallback | None:
        """Gibt den aktuellen GUI-Callback zurück."""
        return self._gui_callback

    # --------------------------------------------------------------------------------
    @gui_callback.setter
    def gui_callback(self, value: GuiCallback | None) -> None:
        """Setzt den GUI-Callback (sollte ein Signal-Emit sein)."""
        self._gui_callback = value

    # --------------------------------------------------------------------------------
    @property
    def progress_callback(self) -> ProgressCallback | None:
        """Gibt den aktuellen Progress-Callback zurück."""
        return self._progress_callback

    # --------------------------------------------------------------------------------
    @progress_callback.setter
    def progress_callback(self, value: ProgressCallback | None) -> None:
        """Setzt den Progress-Callback (sollte ein Signal-Emit sein)."""
        self._progress_callback = value

    # --------------------------------------------------------------------------------
    def __call__(self, tag: CallbackTag, *args: Any) -> None:
        """Zentrale Routing-Logik: Loggt in Datei und verteilt an UI.

        :param tag: (CallbackTag) Typ des Callbacks (LOG, ERR, STATUS, PROGRESS).
        :param args: (Any) Variable Argumente für den Log-Eintrag oder Callback.
        """
        # 1. Formatierung der Nachricht (Die Logik, die dir wichtig war)
        # Wir bestimmen den Log-Level für die Formatierung
        level = ERROR if tag == CallbackTag.ERR else INFO
        lines = self._format_message(*args, level=level)

        # 2. Datei-Logging (Nur für LOG und ERR)
        if tag in (CallbackTag.LOG, CallbackTag.ERR):
            for line in lines:
                self._logger.log(level, line)

        # 3. Fehler mit Tag.ERR zusätzlich ins CRASH_LOG schreiben
        if tag == CallbackTag.ERR:
            write_crash_file("\n".join(lines))

        # 4. Routing an User-Output (GUI oder Konsole)
        match tag:
            case CallbackTag.PROGRESS:
                self._dispatch_progress(*args)
            case CallbackTag.STATUS | CallbackTag.LOG | CallbackTag.ERR | CallbackTag.WARN:
                for line in lines:
                    self._dispatch_output(line)

    # --------------------------------------------------------------------------------
    @staticmethod
    def _format_message(*args: Any, level: int = INFO) -> list[str]:
        """Extrahiert die komplette Formatierungs-Logik."""
        lines: list[str] = []
        len_args = len(args)

        if len_args == 0:
            lines.append("=" * MSG_LEN)
        elif len_args == 1 and isinstance(args[0], str) and len(args[0]) == 1:
            lines.append(args[0] * MSG_LEN)
        else:
            if level == ERROR:
                frame = currentframe()
                l_label = frame.f_code.co_name if frame and hasattr(frame, "f_code") else ""
                arg_count = len_args - 1 if len_args > 1 else 0
                message = (PREFIX_FMT + VALUE_FMT * arg_count + "{}").format(l_label, *args)
            else:
                if len_args >= 2:
                    message = (PREFIX_FMT + VALUE_FMT * (len_args - 2) + "{}").format(*args)
                else:
                    # message = (PREFIX_FMT + "{}").format(" " * PREFIX_LEN, *args)
                    message = str(args[0]) if len_args == 1 else ""

            wrapped = textwrap.fill(message, width=MSG_LEN, initial_indent="", subsequent_indent=VALUE_NEW_FMT)
            lines = wrapped.splitlines()
        return lines

    # --------------------------------------------------------------------------------
    # Dispatcher für Messages
    def _dispatch_output(self, message: str) -> None:
        """Entscheidet: GUI-Callback ODER Konsole."""
        if self._gui_callback:
            self._gui_callback(message)

        if self._use_console:
            print(message)

    # --------------------------------------------------------------------------------
    # Dispatcher für Fortschritts-Werte
    def _dispatch_progress(self, *args: Any) -> None:
        """
        Leitet den Fortschritt weiter. Unterstützt nun das ProgressEvent Objekt.

        :param args: (Any) Entweder ein ProgressEvent oder (int, int) für Legacy-Support.
        """
        if not self._progress_callback:
            return

        # Moderne Variante: Wir erhalten ein ProgressEvent Objekt
        if len(args) == 1 and isinstance(args[0], ProgressEvent):
            self._progress_callback(args[0])

    # --------------------------------------------------------------------------------
    def _init_console_handler(self, level: int) -> None:
        """Richtet den Konsolen-Handler ein.

        :param level: (int) Log-Level.
        """
        formatter = Formatter("%(message)s")
        safe_stream = sys.stderr if sys.stderr is not None else DummyStream()
        console = StreamHandler(safe_stream)
        console.setLevel(level)
        console.setFormatter(formatter)
        console.set_name(HANDLER_CONSOLE)
        self._logger.addHandler(console)

    # --------------------------------------------------------------------------------
    def _configure_files(self, filepath: Path | None = None, level: int = WARN) -> Path | None:
        """Richtet Datei-Handler ein.

        :param filepath: (Path | None) Zielpfad der Logdatei.
        :param level: (int) Log-Level.
        :return: (Path | None) Pfad zur Haupt-Logdatei.
        """
        if filepath is None:
            self._logfile = None
            return None

        for handler in list(self._logger.handlers):
            if isinstance(handler, FileHandler):
                self._logger.removeHandler(handler)

        base_path = self._get_executable_path()
        filename = base_path.stem
        dir_path = base_path.parent

        filename = (dir_path / f"{filename}.log").resolve()
        self._logfile = filename

        formatter = Formatter("%(asctime)s - %(message)s", datefmt="%Y%m%d-%H%M%S")
        file = FileHandler(filename=filename, mode="w", encoding="utf-8")
        file.setLevel(level)
        file.setFormatter(formatter)
        file.set_name(HANDLER_FILE)
        self._logger.addHandler(file)

        return self._logfile

    # --------------------------------------------------------------------------------
    @staticmethod
    def _get_executable_path() -> Path:
        """Ermittelt den Pfad der laufenden Anwendung.

        :return: (Path) Absoluter Pfad.
        """
        return _get_executable_path()


# --------------------------------------------------------------------------------
def fatal(msg: str | None = None, exitcode: int = 99) -> None:
    """Gibt eine optionale Fehlermeldung aus und beendet das Skript.

    :param msg: (str | None) Die Fehlermeldung.
    :param exitcode: (int) Beendigungs-Code.
    """
    if msg is not None:
        log_to_callback(CallbackTag.ERR, msg, exitcode)
    sys.exit(exitcode)


# --------------------------------------------------------------------------------
def _get_executable_path() -> Path:
    """Ermittelt den Pfad der laufenden Anwendung.

    :return: (Path) Absoluter Pfad.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return Path(sys.argv[0]).resolve()


# --------------------------------------------------------------------------------
def initialize_windows_app_id(company: str, program: str, version: str = '1.0') -> None:
    """
    Registriert die Anwendung explizit beim Windows-System, damit das
    Taskleisten-Icon korrekt von der Python-Runtime getrennt und angezeigt wird.
    Unterdrückt Linter-Warnungen bezüglich dynamischer ctypes-Attribute.
    """
    app_id: str = f"{company.lower()}.{program.lower()}.{version.lower()}"

    if sys.platform == "win32":
        try:
            # Verwenden von getattr, um statische Code-Analyse-Fehler zu vermeiden
            shell32 = ctypes.windll.shell32
            set_app_id_func = getattr(shell32, "SetCurrentProcessExplicitAppUserModelID")

            # Funktion aufrufen
            set_app_id_func(app_id)
        except AttributeError:
            print("WARNUNG: 'SetCurrentProcessExplicitAppUserModelID' wurde auf diesem System nicht gefunden.")
        except Exception as e:
            print(f"WARNUNG: Windows AppUserModelID konnte nicht gesetzt werden: {e}")


# --------------------------------------------------------------------------------
def setup_crash_logger() -> None:
    """Registriert einen globalen excepthook für unerwartete Abstürze."""
    def crash_logger(exctype: type[BaseException], value: BaseException, tb: Any) -> None:
        error_msg = "".join(traceback.format_exception(exctype, value, tb))
        base_dir = _get_executable_path().parent
        crash_file = base_dir / CRASH_FILE

        try:
            with open(crash_file, "a", encoding="utf-8") as f:
                f.write("=== NEUER CRASH ===\n")
                f.write(error_msg)
                f.write("\n\n")
        except OSError:
            pass

        sys.__excepthook__(exctype, value, tb)

    sys.excepthook = crash_logger


# --------------------------------------------------------------------------------
def write_crash_file(message: str) -> None:
    """Zentrale Hilfsfunktion zum Schreiben in die CRASH_LOG.txt."""
    base_dir = _get_executable_path().parent
    crash_file = base_dir / CRASH_FILE

    try:
        with open(crash_file, "a", encoding="utf-8") as f:
            f.write("=== FEHLER / CRASH ===\n")
            f.write(message)
            f.write("\n\n")
    except OSError:
        pass


# --------------------------------------------------------------------------------
def log_to_callback(tag: CallbackTag, *args: Any) -> None:
    """
    Zentrale Schnittstelle für alle Frameworks.

    :param tag: (CallbackTag) Der Typ der Nachricht zur eindeutigen Zuordnung.
    :param args: (Any) Die variablen Nutzdaten (z. B. Fortschrittswerte oder Log-Strings).
    """
    global _active_callback
    if _active_callback is not None:
        _active_callback(tag, *args)
    else:
        print(f"[{tag.name}]", *(str(arg) for arg in args))


# --------------------------------------------------------------------------------
# Globale Registry
# --------------------------------------------------------------------------------
_active_callback: AppCallback | None = None
# --------------------------------------------------------------------------------
