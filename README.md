# rpg_utils

# RPG Tools Framework Suite

Eine leistungsfähige, modulare Python-Framework-Suite zur Extraktion und Verarbeitung von **GoPro-Telemetriedaten (GPMF)**, Erzeugung von **GPX-Tracks**, **Geokodierung**, **Karten-Rendering**, **Video-Overlays** sowie wiederverwendbaren **PySide6-UI-Utilities**.

---

## 🏗️ Architektur & Modul-Übersicht

Das Framework **rpg-tools** stellt die zentrale Bibliothek dar, auf der Anwendungs-Suites wie **[gopro-tools](https://github.com/RalfPeter/gopro-tools)** (GUIs und CLI-Skripte) aufbauen:

  ┌───────────────────────────────────────────────────────────────────────────────────┐
  │                                    gopro-tools                                    │
  │        (Anwendungen: gui_gopro2file, gui_gopro2overlay, CLI Pipelines)            │
  └─────────────────────────────────────────┬─────────────────────────────────────────┘
                                            │  nutzt als Bibliothek
                                            ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                                     rpg-tools                                       │
  │                              (Core Framework Suite)                                 │
  ├───────────┬───────────┬───────────┬────────────────┬───────────────────┬────────────┤
  │ rpg_gpmf  │  rpg_geo  │  rpg_gpx  │    rpg_gui     │     rpg_utils     │rpg_overlay │
  │Telemetrie │Geocoding  │GPX Tracks │ PySide6 Base   │ Shared Utilities  │ Video      │
  │GPMF KLV   │GeoNames   │Schema / IO│ Templates/Utils│ Logger/Config/Math│ Overlays   │
  └───────────┴───────────┴───────────┴────────────────┴───────────────────┴────────────┘

---

---

## rpg_utils

Zentrale Infrastruktur-Module und Hilfsfunktionen für Python-Projekte.

### Allgemeines
Das Framework **`rpg_utils`** dient als zentrale, projektsübergreifende Werkzeugsammlung (Core Utility Framework) für Python 3.10+ Anwendungen. Es bündelt grundlegende Funktionen für:
* **Pfad- und Dateisystem-Operationen:** Sichere Datei-Umbenennungen, Ermittlung von AppData/Skript-/Resource-Pfade sowie plattformunabhängige Berechtigungsprüfungen.
* **Typensichere Parameter- & Konfigurationsverwaltung:** Unterstützung von Dataclasses mit automatischer YAML-Persistierung und CLI-Argument-Parsing.
* **Enterprise Logging & Progress Tracking:** Einheitliches Callback-Routing für CLI- und GUI-Anwendungen (z. B. PyQt/PySide) inkl. Absturzberichten (Crash Logger).
* **Datums-, Zeit- & Zeitzonenverarbeitung:** ISO 8601, Zulu/UTC-, EXIF- und IPTC-Konvertierungen sowie Zeitzonenberechnungen.
* **HTTP-Utilities:** Gesicherte und ungesicherte GET/POST-Requests mit automatischem Retry-/SSL-Handling.
* **Mathematische & Geografische Hilfsfunktionen:** Geofence/Koordinaten-Umrechnungen (DD <-> DMS <-> Exif Rationals) und numerische Typkonvertierungen.
* **String-Verarbeitung:** Platzhalter-Ersetzung, UTF-8/Bytes-Dekodierung und sichere Konvertierungen.

---

### Abhängigkeiten

#### Externe Abhängigkeiten (über `pip` zu installieren)
* `requests`
* `pyyaml` (`yaml`)
* `tzlocal`

#### Interne / Standardbibliothek-Abhängigkeiten
* Python 3.10+ Standardbibliothek (`argparse`, `ctypes`, `dataclasses`, `datetime`, `enum`, `fractions`, `http`, `inspect`, `logging`, `pathlib`, `platform`, `re`, `sys`, `tempfile`, `textwrap`, `traceback`, `typing`, `zoneinfo`)

---

### Öffentliche Klassen und Methoden

#### 1. `BaseConfig` (`utils_config.py`)
Zentrale Verwaltung für grundlegende Applikations-Pfade (UI, Konfigurations-YAML, Icons) und Datums-Formatstrings.

##### Öffentliche Methoden & Attribute:
* **`get_app_name() -> str`**
  * Gibt den ermittelten Namen der ausführenden Applikation zurück.
  * :return: `(str)` Applikationsname.
* **Klassenattribute / Pfade:**
  * `UI_DIR: Final[Path]`: Pfad zum UI-Ordner.
  * `CONFIG_YAML: Final[Path]`: Pfad zur anwendungsspezifischen YAML-Datei.
  * `ICO_FILE: Final[Path]`: Pfad zur `.ico`-Datei.
  * `DATETIME_ISO_PY`, `DATETIME_ISO_QT`, `DISPLAY_DATETIME_FMT`: Formatstrings.

---

#### 2. `DataclassFieldsMeta` (`utils_config.py`)
Metaklasse für Dataclasses, die dynamisch einen inneren `Fields`-Container injiziert, um Attributnamen typsicher in CLI-Parsern oder Konfigurationen zu verwenden.

---

#### 3. `BaseParameters` (`utils_config.py`)
Universelle Basisklasse für die typsichere Verwaltung, CLI-Parsing und YAML-Persistierung von Anwendungsparametern.

##### Öffentliche Methoden:
* **`update_from_namespace(args: Namespace) -> None`**
  * Aktualisiert Attribute dynamisch aus einem `argparse.Namespace`.
  * :param args: `(Namespace)` Der Namespace aus dem ArgumentParser.
* **`save_to_yaml() -> None`**
  * Speichert die aktuellen Parameterwerte im YAML-Format in die Konfigurationsdatei.
* **`load_from_yaml() -> None`**
  * Lädt Parameterwerte aus der YAML-Konfigurationsdatei und aktualisiert die Instanz.
* **`parse_args() -> BaseParameters`**
  * Parst Standard-Kommandozeilenargumente (`--verbose`, `--log`) und gibt die aktualisierte Instanz zurück.
  * :return: `(BaseParameters)` Die aktualisierte Parameterinstanz.

---

#### 4. `AppLogger` (`utils_core.py`)
Zentrale Logger-Klasse mit flexiblem Callback-Routing an CLI, GUI und Dateilogger.

##### Öffentliche Methoden:
* **`create(logfile_path: Path | None = None, use_console: bool = True) -> AppLogger`**
  * Factory-Methode zur Erstellung, Konfiguration und Registrierung einer Logger-Instanz.
  * :param logfile_path: `(Path | None)` Optionaler Pfad zur Logdatei.
  * :param use_console: `(bool)` Ob Konsolenausgabe aktiviert sein soll.
  * :return: `(AppLogger)` Die fertig konfigurierte Instanz.
* **`__call__(tag: CallbackTag, *args: Any) -> None`**
  * Empfängt Log-Einträge/Status-Events und leitet diese an registrierte Handlers/Callbacks weiter.
  * :param tag: `(CallbackTag)` Tag zur Zuordnung (LOG, STATUS, PROGRESS, WARN, ERR).

---

#### 5. `ProgressEvent` (`utils_core.py`)
Immutable Dataclass zur Abbildung von Fortschrittsereignissen in Verarbeitungen.

##### Öffentliche Methoden:
* **`start(total: int) -> ProgressEvent`**
  * Erstellt ein Start-Event mit Gesamtzahl.
  * :param total: `(int)` Gesamtzahl der Schritte.
  * :return: `(ProgressEvent)` Das Initialisierungsevent.
* **`update(current: int, total: int) -> ProgressEvent`**
  * Erstellt ein Update-Event.
  * :param current: `(int)` Aktueller Schritt.
  * :param total: `(int)` Gesamtzahl der Schritte.
  * :return: `(ProgressEvent)` Das Update-Event.
* **`finished() -> ProgressEvent`**
  * Erstellt ein Abschluss-Event.
  * :return: `(ProgressEvent)` Das Fertigstellungs-Event.

---

#### 6. `DummyStream` (`utils_core.py`)
Null-Object-Pattern Implementierung für `stdout`/`stderr` in GUI-Kontexten.

---

#### 7. Global Functions (`utils_core.py`)
* **`fatal(msg: str | None = None, exitcode: int = 99) -> None`**
  * Gibt eine optionale Fehlermeldung aus und beendet das Programm.
  * :param msg: `(str | None)` Fehlermeldung.
  * :param exitcode: `(int)` Beendigungs-Code.
* **`initialize_windows_app_id(company: str, program: str, version: str = '1.0') -> None`**
  * Registriert die Applikations-ID unter Windows für korrektes Taskleisten-Grouping.
  * :param company: `(str)` Firmenname/Entwickler.
  * :param program: `(str)` Programmname.
  * :param version: `(str)` Version.
* **`setup_crash_logger() -> None`**
  * Registriert einen globalen `sys.excepthook` zur automatischen Aufzeichnung unbehandelter Laufzeitfehler in einer Crash-Datei.
* **`log_to_callback(tag: CallbackTag, *args: Any) -> None`**
  * Globale Schnittstelle zur Abgabe von Log- und Statusnachrichten an das `rpg_utils`-System.
  * :param tag: `(CallbackTag)` Ereignis-Tag.

---

#### 8. `DateTimeUtils` (`utils_datetime.py`)
Statische Klasse zur Kapselung von Datums-, Zeit- und Zeitzonen-Operationen.

##### Öffentliche Methoden:
* **`add_timedelta(dt: datetime | None = None, delta: int | timedelta | None = None) -> datetime | None`**
  * Addiert Sekunden oder ein `timedelta` auf ein `datetime`-Objekt.
  * :param dt: `(datetime | None)` Basisdatum.
  * :param delta: `(int | timedelta | None)` Delta in Sekunden oder als `timedelta`.
  * :return: `(datetime | None)` Neues Datum oder `None`.
* **`format_datetime(dt: datetime | None, format_str: str | None = None, delta: timedelta | None = None, tz: str | tzinfo | None = None) -> str`**
  * Formatiert ein `datetime`-Objekt flexibel unter Anwendung von Zeitzonen und Deltas.
  * :param dt: `(datetime | None)` Zu formatierendes Datum.
  * :param format_str: `(str | None)` Format-String.
  * :param delta: `(timedelta | None)` Optionale Zeitdifferenz.
  * :param tz: `(str | tzinfo | None)` Zielzeitzone.
  * :return: `(str)` Formatierter Datumsstring.
* **`convert_to_offset_str(dt: datetime) -> str | None`**
  * Konvertiert den Zeitzonen-Offset in ein `+HH:MM` String-Format.
  * :param dt: `(datetime)` Zeitzonenbewusstes `datetime`-Objekt.
  * :return: `(str | None)` Offset-String (z. B. `+02:00`).
* **`create_aware_base_datetime(year: int = 2000, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0, tz: str | tzinfo = TZ_UTC) -> datetime`**
  * Erstellt ein zeitzonenbewusstes `datetime`-Objekt mit Vorgabewerten.
* **`delta_time(par_timedata: str | datetime, par_delta: timedelta = timedelta(0), par_tformat: str = "%y%m%d%H%M%S.%f") -> datetime | None`**
  * Konvertiert Timestamp-Strings oder Datetime-Objekte in UTC nach Anwendens eines Deltas.
* **`convert_to_timezone(dt: datetime | None, tz: str | tzinfo | None) -> datetime | None`**
  * Konvertiert ein `datetime`-Objekt in eine Ziel-Zeitzone.
* **`datetime_diff(start_zeit: datetime, ende_zeit: datetime) -> float`**
  * Berechnet die Zeitdifferenz zweier Zeiten in Sekunden (Float).
  * :param start_zeit: `(datetime)` Startzeit.
  * :param ende_zeit: `(datetime)` Endzeit.
  * :return: `(float)` Differenz in Sekunden.
* **`parse_datetime_string(string: str | None, is_aware: bool = False) -> datetime | None`**
  * Parst Strings im ISO 8601, EXIF- oder IPTC-Format.
* **`get_timezone_hour_offset(dt: datetime) -> int`**
  * Gibt den Stunden-Offset einer Zeitzone als Integer zurück.
* **`parse_offset(offset_str: str) -> timedelta`**
  * Konvertiert Zeitzonen-Offset-Strings (z. B. `+02:00`, `-0800`) in ein `timedelta`.
* **`datetime_to_fractions(dt: datetime | None) -> str | None`**
  * Konvertiert Zeitwerte in rationale Bruch-Strings für EXIF-Metadaten.
* **`prepare_exif_datetime_fields(dto: str, offset: str | None) -> tuple[str, str | None, str | None, str | None]`**
  * Bereitet Rohdaten für korrekte EXIF-Datums- und Offset-Felder auf.
* **`prepare_iptc_datetime_fields(dto_raw: str | None, offset_raw: str | None = None) -> tuple[str, str]`**
  * Formatiert Datumsangaben für IPTC-Metadaten (`IPTCDateCreated`, `IPTCTimeCreated`).

---

#### 9. `PathUtils` (`utils_filepath.py`)
Statische Klasse für Dateisystem-Analysen, Pfadlokalisierung und Dateiumbenennungen.

##### Öffentliche Methoden:
* **`validate_input_directories(inputpaths: list[str] | None, verbose: bool = False) -> bool`**
  * Prüft, ob alle Pfade existierende Ordner sind.
  * :param inputpaths: `(list[str] | None)` Liste von Pfadstrings.
  * :param verbose: `(bool)` Logging aktivieren.
  * :return: `(bool)` `True`, falls alle existieren.
* **`get_subdirectories(directories: list[str] | None, recursive: bool = True) -> list[Path]`**
  * Ermittelt sortierte Unterverzeichnisse.
  * :param directories: `(list[str] | None)` Ausgangsverzeichnisse.
  * :param recursive: `(bool)` Rekursive Suche durchführen.
  * :return: `(list[Path])` Liste gefundener Verzeichnisse.
* **`safe_rename(src: Path | str, dst: Path | str, verbose: bool = False) -> bool`**
  * Benennt Dateien abfangend für Berechtigungs- und Dateifehler um.
  * :param src: `(Path | str)` Quellpfad.
  * :param dst: `(Path | str)` Zielpfad.
  * :return: `(bool)` `True` bei Erfolg.
* **`get_basename_without_prefix(file: Path | str) -> str`**
  * Extrahiert den Basisnamen einer Datei und entfernt Datums-Präfixe (`YYYYMMDD_HHMMSS`).
* **`create_new_filepath(file: Path | str, dt: datetime | None) -> Path | None`**
  * Erzeugt ein neues `Path`-Objekt mit Datums-Präfix im Format `YYYYMMDD_HHMMSS-basename.ext`.
* **`rename_file_with_datetime(file: Path | str, dt: datetime | None = None) -> tuple[bool, Path]`**
  * Führt Umbenennung basierend auf `datetime` durch.
  * :return: `(tuple[bool, Path])` Erfolg und resultierender Pfad.
* **`is_writable(directory: Path) -> bool`**
  * Prüft Schreibrechte in einem Verzeichnis über eine temporäre Datei.
* **`get_config_dir(app_name: str = '', verbose: bool = False) -> Path`**
  * Ermittelt das plattformspezifische AppData-/Config-Verzeichnis (Windows/macOS/Linux).
* **`get_script_dir(verbose: bool = False) -> Path`**
  * Ermittelt das Verzeichnis des gestarteten Skripts bzw. der EXE-Datei.
* **`get_script_name(suffix: str = "", verbose: bool = False) -> str`**
  * Gibt den Namen des auszuführenden Skripts oder Executables zurück.
* **`get_temp_dir(verbose: bool = False) -> Path`**
  * Gibt das systemweite Temp-Verzeichnis als `Path` zurück.
* **`get_work_dir(verbose: bool = False) -> Path`**
  * Ermittelt das Arbeitsverzeichnis (inkl. PyInstaller `_MEIPASS`-Support).
* **`get_data_dir(app_name: str = '', verbose: bool = False) -> Path`**
  * Gibt den Pfad zum Datenordner (`data`) zurück.
* **`get_resource_dir() -> Path`**
  * Gibt den Pfad zum Ressourcen-Ordner (`resources`) zurück.
* **`get_ui_dir() -> Path`**
  * Gibt den Pfad zum UI-Ordner (`ui`) zurück.

---

#### 10. `HttpUtils` (`utils_http.py`)
Statische Utility-Klasse für abfagende HTTP-GET/POST-Requests.

##### Öffentliche Methoden:
* **`get_content_from_url(url: str, error_message: str, timeout: int = 5, *, json: bool = False, return_headers: bool = False, **kwargs: Any) -> Any | None`**
  * Führt eine GET-Anfrage durch inklusive automatischem SSL-Fallback und Timeout-Handling.
  * :param url: `(str)` Ziel-URL.
  * :param error_message: `(str)` Log-Fehlertext.
  * :param timeout: `(int)` Timeout in Sekunden.
  * :param json: `(bool)` Wenn `True`, wird geparstes JSON zurückgegeben.
  * :param return_headers: `(bool)` Wenn `True`, wird ein Tupel inklusive Response-Headers geliefert.
  * :return: `(Any | None)` Status-Code, Content (und optional Headers) oder `None` bei Fehler.
* **`post_content_to_url(url: str, error_message: str, timeout: int = 5, *, json: bool = False, return_headers: bool = False, **kwargs: Any) -> Any | None`**
  * Führt eine POST-Anfrage durch.
  * :param url: `(str)` Ziel-URL.
  * :param error_message: `(str)` Log-Fehlertext.
  * :param timeout: `(int)` Timeout in Sekunden.
  * :param json: `(bool)` Wenn `True`, wird geparstes JSON zurückgegeben.
  * :param return_headers: `(bool)` Wenn `True`, wird ein Tupel inklusive Response-Headers geliefert.
  * :return: `(Any | None)` Status-Code, Content (und optional Headers) oder `None` bei Fehler.

---

#### 11. `MathUtils` (`utils_math.py`)
Statische Klasse für mathematische und geografische Umrechnungen.

##### Öffentliche Methoden:
* **`ceil4(n: int) -> int`**
  * Rundet `n` auf das nächste Vielfache von 4 auf.
  * :param n: `(int)` Eingabezahl.
  * :return: `(int)` Vielfaches von 4.
* **`to_rational_str(number: float | None) -> str`**
  * Konvertiert Gleitkommazahlen in Bruchstrings (`Zähler/Nenner`).
* **`rational_to_float(value: tuple[int, int] | str | Fraction | Any | None) -> float | None`**
  * Wandelt Brüche (Tupel, String, `Fraction`) sicher in `float` um.
* **`convert_coord_to_dms(coord: float) -> tuple[int, int, float]`**
  * Konvertiert Dezimalgrad in DMS `(Grad, Minuten, Sekunden)`.
* **`convert_dms_to_dd(deg: float | None, mm: float | None, sec: float | None) -> float | None`**
  * Konvertiert DMS-Werte `(Grad, Minuten, Sekunden)` in Dezimalgrad.
* **`format_coord_as_rational_dms(coord: float | None) -> str | None`**
  * Formatiert Koordinaten als EXIF-kompatiblen rationalen DMS-String (z. B. `'52/1 13/1 42.5/1'`).
* **`get_geo_refs(lat: float | None, lon: float | None) -> tuple[str | None, str | None]`**
  * Ermittelt Himmelsrichtungen (`'N'`, `'S'`, `'E'`, `'W'`) für Koordinaten.
* **`get_geo_ref_multipliers(lat_ref: str | None, lon_ref: str | None) -> tuple[int | None, int | None]`**
  * Liefert Faktoren (`1` oder `-1`) basierend auf Himmelsrichtungen.
* **`convert_coords_to_deg_refs(lat: float, lon: float) -> tuple[tuple[int, int, float, str], tuple[int, int, float, str]] | None`**
  * Generiert vollständiges DMS- und Ref-Tupel für Breitengrad und Längengrad.
* **`is_valid_float(value: Any) -> bool`**
  * Prüft, ob ein Wert sicher in einen `float` konvertierbar ist.
* **`safe_float(value: Any) -> float`**
  * Konvertiert Werte sicher zu `float`.
* **`safe_int(value: Any, default: int = 0) -> int`**
  * Konvertiert Werte sicher zu `int` mit konfigurierbarem Defaultwert.

---

#### 12. `StringUtils` (`utils_string.py`)
Statische Utility-Klasse für erweiterte String-Transformationen.

##### Öffentliche Methoden:
* **`decode_bytes(value: bytes | str | None) -> str | None`**
  * Dekodiert Bytes mittels UTF-8 oder liefert Strings unverändert zurück.
  * :param value: `(bytes | str | None)` Eingabe.
  * :return: `(str | None)` Dekodierter String.
* **`replace_placeholders(pattern: str, dt: datetime | None, basename: str | None = None, user: str | None = None, fallback_name: str = "UNNAMED") -> str`**
  * Ersetzt Muster-Platzhalter (`%Y`, `%m`, `%d`, `%c` für Basisname, `%u` für Benutzer) abfangend gegen ungültige Werte.
  * :param pattern: `(str)` Muster.
  * :param dt: `(datetime | None)` Datum.
  * :param basename: `(str | None)` Basisname.
  * :param user: `(str | None)` Benutzer.
  * :param fallback_name: `(str)` Ausweich-Dateiname.
  * :return: `(str)` Aufgelöster String.
* **`safe_str(val: Any, default: str = "") -> str`**
  * Wandelt beliebige Objekte sicher in einen String um.

##### Hilfsfunktionen:
* **`sstr(val: Any, default: str = "") -> str`**
  * Kurze Alias-Funktion für `StringUtils.safe_str`.
