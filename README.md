# rpg_utils

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

Zentrale Infrastruktur-Module und Hilfsfunktionen für Python-Projekte.

### Enthaltene Komponenten
* **Logging:** `AppLogger` für strukturierte Konsolen- und Datei-Protokollierung (`utils_logger.py`).
* **Konfiguration:** `utils_config.py` zur einfachen Verwaltung von YAML- und INI-Konfigurationsdateien.
* **Dateipfade:** `utils_filepath.py` für plattformunabhängige Pfadoperationen und Datei-Handhabung.
* **Datum & Zeit:** `utils_datetime.py` für Zeitzonen-Konvertierung und Robuste Datetime-Parsings.
* **Netzwerk & Mathematik:** HTTP-Client-Wrapper, Fehlerbehandlung und mathematische Berechnungen.

### Installation

pip install git+[https://github.com/RalfPeter/rpg_utils.git](https://github.com/RalfPeter/rpg_utils.git)

### Verwendung

from rpg_utils import main_logger
from rpg_utils import load_config

main_logger.log("Info", "Starte Modulverarbeitung...")
