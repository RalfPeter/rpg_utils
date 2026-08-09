# gpmf-tools

Eine leistungsfähige, modulare Python-Framework-Suite zur Extraktion und Verarbeitung von **GoPro-Telemetriedaten (GPMF)**, Erzeugung von **GPX-Tracks**, **Geokodierung**, **Karten-Rendering** sowie wiederverwendbaren **PySide6-UI-Utilities**.

---

## 🏗️ Architektur & Modul-Übersicht

Das Framework **`gpmf-tools`** stellt die zentrale Bibliothek dar, auf der Anwendungs-Suites wie **[gopro-tools](https://github.com/RalfPeter/gopro-tools)** (GUIs und CLI-Skripte) aufbauen:

```text
  ┌────────────────────────────────────────────────────────────────────────┐
  │                           gopro-tools                                  │
  │  (Anwendungen: gui_gopro2file, gui_gopro2overlay, CLI Pipelines)       │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │  nutzt als Bibliothek
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                            gpmf-tools                                  │
  │                     (Core Framework Suite)                             │
  ├───────────┬───────────┬───────────┬────────────────┬───────────────────┤
  │   gpmf    │    geo    │    gpx    │      gui       │       utils       │
  │ Telemetrie│Geocoding  │GPX Tracks │ PySide6 Base   │ Shared Utilities  │
  │ Overlays  │ GeoNames  │ Schema/IO │ Templates/Utils│ Logger/Config/Math│
  └───────────┴───────────┴───────────┴────────────────┴───────────────────┘

```

### Die Sub-Frameworks im Detail

* **`gpmf`**: Kern-Modul zur Extraktion und Verarbeitung von GoPro-GPMF-Binärdaten (KLV-Parsing), Erzeugung von Telemetrie-Overlays via FFmpeg, Video-Metadaten-Analyse und GPX/Karten-Exporten.
* **`geo`**: Verwaltung von Geodaten, Integration lokaler Offline- und Online-GeoNames-Datenbanken, Geokodierung und Map-Tile-Downloads via `geotiler`.
* **`gpx`**: Typensichere Datenstrukturen (`GeoPointTime`), Schema-Validierung, I/O-Operationen und Hilfsfunktionen für GPX-Dateien.
* **`gui`**: Wiederverwendbare Qt6/PySide6 UI-Komponenten, Standard-Dialoge, UI-Templates (`gui_template.py`) und Hilfsfunktionen für Desktop-Anwendungen (`gui_utils.py`).
* **`utils`**: Zentrale Infrastruktur-Module für Logging (`AppLogger`), Konfigurationsmanagement (`utils_config.py`), Pfadverarbeitung (`utils_filepath.py`), Zeitzonen-/Datetime-Handhabung (`utils_datetime.py`), HTTP-Client und mathematische Berechnungen.

---

## 📂 Paketstruktur

```text
packages/
├── pyproject.toml          # Build-Konfiguration & Abhängigkeiten
├── README.md               # Dokumentation
├── gpmf/                   # GPMF-Extraktion, KLV-Parser, Overlays & Metadaten
├── geo/                    # GeoNames-Integration, Downloader & Geo-Manager
├── gpx/                    # GPX-Schema, I/O & Transformatoren
├── gui/                    # PySide6 UI-Utilities & Basis-Templates
└── utils/                  # Logger, Config, Datetime, HTTP, Filepath & Math

```

---

## 🛠️ Installation

### Entwicklungsmodus (Editable Install)

Wenn du das Paket lokal bearbeitest oder als Abhängigkeit in anderen Projekten nutzt:

```cmd
cd /d ../packages
pip install -e .

```

### Installation direkt aus GitHub

Sobald das Repository veröffentlicht ist, kann das Paket direkt in beliebigen Umgebungen installiert werden:

```cmd
pip install git+[https://github.com/RalfPeter/gpmf-tools.git](https://github.com/RalfPeter/gpmf-tools.git)

```

---

## 🚀 Code-Beispiele

### 1. Telemetrie aus GoPro-Datei lesen & GPX schreiben

```python
from pathlib import Path
from gpmf.gpmf_meta_gopro import GpmfFile, ExtractionMethod
from gpmf.gpmf_writer import GoProFileWrite
from utils.utils_logger import main_logger

# GPMF-Datei laden und Telemetrie extrahieren
gpmf = GpmfFile(file=Path("GOPR0001.gpmf"), verbose=True)
gpmf.get_raw_telemetry(method=ExtractionMethod.FILE, clean=False)

# GPS-Items in GPX-Datei schreiben
writer = GoProFileWrite(filepath=gpmf.file)
gpx_path = writer.write_gpx_temp(points=gpmf.gps_items)

main_logger.log("Info", f"GPX erzeugt unter: {gpx_path}")

```

### 2. Geokodierung & GeoNames-Dienste nutzen

```python
import geo.geo_basemanager as geo_manager
from utils.utils_logger import main_logger

# Ortssuche über Koordinaten
location_info = geo_manager.get_location_name(latitude=50.9375, longitude=6.9603)
main_logger.log("Info", f"Standort: {location_info}")

```

### 3. PySide6 UI-Utilities in eigener GUI nutzen

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from gui.gui_template import BaseWindow
from gui.gui_utils import center_on_screen

class MyApp(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GoPro App")
        center_on_screen(self)

if __name__ == "__main__":
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec()

```

---

## 🖥️ Anwendungsprojekte (`gopro-tools`)

Suchtst du nach den fertigen GUI- und CLI-Anwendungen? Die Benutzeroberflächen und Skripte befinden sich im separaten Anwendungs-Repository **[gopro-tools](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/RalfPeter/gopro-tools)**:

* **`gui_gopro2file`**: Batch-Export, Metadaten-Anreicherung & automatisiertes Umbenennen von GoPro-Videos.
* **`gui_gopro2overlay`**: Rendering von Telemetrie-Overlays (Tacho, Karte, Höhe, G-Kraft) in Videos via FFmpeg.
* **`prg_*.py`**: Verschiedene Kommandozeilen-Pipelines für die Stapelverarbeitung.

---

## 📋 Anforderungen & Abhängigkeiten

* **Python:** `>= 3.10`
* **GUI-Framework:** `PySide6`
* **Kernabhängigkeiten:** `pandas`, `Pillow`, `gopro-overlay`, `gpxpy`, `folium`, `lxml`, `requests`, `scipy`, `tzlocal`, `PyYAML`, `geotiler`, `overpy`, `pyexiv2`
* **Systemwerkzeuge:** `ffmpeg` / `ffprobe` im Systempfad (für Overlay-Generierung & Video-Analyse).

---

## 📄 Lizenz

Dieses Projekt ist unter der **GNU General Public License v3 (GPLv3)** lizenziert.

```

```