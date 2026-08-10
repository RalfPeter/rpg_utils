#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 10-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm          : utils_config.py
#  Version           : 2.0
#  Beschreibung      : Keine Beschreibung verfügbar.
#  Zeilen            : 236
#  Abhängigkeiten    : argparse, dataclasses, pathlib, sys, typing, yaml
#  Klassen           : BaseConfig, DataclassFieldsMeta, BaseParameters
# ------------------------------------------------------------------------------
#  Public Methoden:
#    BaseConfig                                           → Zentrale Pfade zu Konfigurations-, UI- und Icon-Dateien.
#      get_app_name()                                     → Gibt den Namen der Applikation zurück.
#
#    BaseParameters                                       → Universelle Basisklasse für die typsichere Verwaltung, CLI-Parsing und
#      update_from_namespace(Namespace)                   → Aktualisiert alle passenden Attribute dieser Instanz dynamisch aus einem CLI-Namespace.
#      save_to_yaml()                                     → Speichert die aktuellen Parameter sauber im YAML-Format.
#      load_from_yaml()                                   → Lädt Parameter aus einer YAML-Datei und aktualisiert die Instanz sicher.
#      parse_args()                                       → Parst die standardmäßigen Kommandozeilenparameter für die Anwendung.
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter.bergheim@gmail.com>
# ------------------------------------------------------------------------------

from __future__ import annotations
import sys
from typing import Final
from pathlib import Path
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, fields, field, asdict
from typing import Any, ClassVar
import yaml

from rpg_utils.utils_filepath import PathUtils

# Globale Konstanten für das IO-Handling (Wartbarkeit)
FILE_ENCODING: str = "utf-8"
YAML_INDENT: int = 4
DEFAULT_APP_NAME: Final[str] = "main_program"


# ================================================================================
# ================================================================================
class BaseConfig:
    """Zentrale Pfade zu Konfigurations-, UI- und Icon-Dateien."""

    # --------------------------------------------------------------------------------
    @staticmethod
    def _determine_app_name() -> str:
        """Ermittelt den Namen des ausführenden Skripts oder den Standardnamen.
        
        :return: (str) Beschreibung des Rückgabewerts.
        """

        if (m := sys.modules.get("__main__")) and hasattr(m, "__file__") and m.__file__:
            return Path(m.__file__).stem
        return DEFAULT_APP_NAME

    # Direkt als strikter String initialisieren (kein None nötig)
    _APP_NAME: Final[str] = _determine_app_name()

    # --------------------------------------------------------------------------------
    @classmethod
    def get_app_name(cls) -> str:
        """Gibt den Namen der Applikation zurück.
        
        :return: (str) Beschreibung des Rückgabewerts.
        """

        return cls._APP_NAME

    # -------------------------------------------------------------------------------------------
    _WORK_DIR: Final[Path] = PathUtils.get_work_dir()
    _SCRIPT_DIR: Final[Path] = PathUtils.get_script_dir()

    UI_DIR: Final[Path] = PathUtils.get_ui_dir()
    CONFIG_YAML: Final[Path] = _SCRIPT_DIR / f"{_APP_NAME}.yaml"
    # ICO File ermitteln
    icofile: Path = _SCRIPT_DIR / f"{_APP_NAME}.ico"
    if not icofile.is_file():
        icofile: Path = _WORK_DIR / f"{_APP_NAME}.ico"
    ICO_FILE: Final[Path] = icofile

    # Formatierungsstrings für Datums- und Zeit-Objekte.
    DATETIME_ISO_PY: Final[str] = "%Y-%m-%dT%H:%M:%S"
    DATETIME_ISO_QT: Final[str] = "yyyy-MM-ddThh:mm:ss"
    DISPLAY_DATETIME_FMT: Final[str] = "%d.%m.%Y %H:%M"


# ================================================================================
# ================================================================================
class DataclassFieldsMeta(type):
    
    # --------------------------------------------------------------------------------
    """--------------------------------------------------------------------------------"""

    def __call__(cls, *args, **kwargs) -> Any:
        # Hier findet der "Hack" statt, exakt bevor die Instanz erzeugt wird.
        # Wir prüfen nur, ob es eine Dataclass ist (hat __dataclass_fields__)
        # und ob Fields noch nicht gesetzt wurde.
        """Hier findet der "Hack" statt, exakt bevor die Instanz erzeugt wird.
        
        :return: (Any) Beschreibung des Rückgabewerts.
        """

        if hasattr(cls, "__dataclass_fields__") and not hasattr(cls, "Fields"):
            # Wir nutzen direkt das interne Dict, das ist der sicherste Weg
            field_dict = cls.__dataclass_fields__

            # Container-Generierung (wie in Ihrem Hack)
            field_map = {name: name for name in field_dict}
            fields_container = type("FieldsContainer", (), field_map)

            # Injektion in die Klasse
            setattr(cls, "Fields", fields_container)

        return super().__call__(*args, **kwargs)


# ================================================================================
# ================================================================================
@dataclass
class BaseParameters(metaclass=DataclassFieldsMeta):
    """Universelle Basisklasse für die typsichere Verwaltung, CLI-Parsing und"""

    # Global geteilte Laufzeit- und GUI-Parameter für alle Projekte
    verbose: bool = False
    log: bool = False
    gui_geometry: str = field(default="", init=False)
    gui_state: str = field(default="", init=False)
    gui_splitters: dict[str, str] = field(default_factory=dict)
    gui_checkboxes: dict[str, bool] = field(default_factory=dict)

    # Zentrale Ausschlussliste für Parameter
    EXCLUDED_PERSISTENCE_FIELDS: ClassVar[set[str]] = set()
    Fields: ClassVar[Any]

    # --------------------------------------------------------------------------------
    @classmethod
    def _get_excluded_fields(cls) -> set[str]:
        """Gibt das Set der Felder zurück, die von der Persistierung ausgeschlossen sind.
        
        :return: (set[str]) Beschreibung des Rückgabewerts.
        """

        return cls.EXCLUDED_PERSISTENCE_FIELDS

    # --------------------------------------------------------------------------------
    def update_from_namespace(self, args: Namespace) -> None:
        """Aktualisiert alle passenden Attribute dieser Instanz dynamisch aus einem CLI-Namespace.

        :param args: (Namespace) Der Namespace aus dem ArgumentParser.
        """
        excluded = self._get_excluded_fields()

        for field_def in fields(self):
            f_name = field_def.name

            if f_name in excluded:
                continue

            if hasattr(args, f_name):
                val = getattr(args, f_name)

                if field_def.type is bool and val is not None:
                    val = bool(val)

                setattr(self, f_name, val)

    # --------------------------------------------------------------------------------
    def save_to_yaml(self) -> None:
        """Speichert die aktuellen Parameter sauber im YAML-Format.
        
        :return: (None) Beschreibung des Rückgabewerts.
        """

        file_path = BaseConfig.CONFIG_YAML

        data_dict = asdict(self)
        excluded = self._get_excluded_fields()

        for f_name in excluded:
            data_dict.pop(f_name, None)

        try:
            with open(file_path, mode="w", encoding=FILE_ENCODING) as yaml_file:
                yaml.dump(
                    data_dict,
                    yaml_file,
                    default_flow_style=False,
                    indent=YAML_INDENT,
                    sort_keys=False
                )
        except OSError as e:
            raise OSError(f"Fehler beim Schreiben der YAML-Datei {file_path}: {e}") from e

    # --------------------------------------------------------------------------------
    def load_from_yaml(self) -> None:
        """Lädt Parameter aus einer YAML-Datei und aktualisiert die Instanz sicher.
        
        :return: (None) Beschreibung des Rückgabewerts.
        """

        file_path = BaseConfig.CONFIG_YAML
        if not file_path.exists():
            return

        try:
            with open(file_path, mode="r", encoding=FILE_ENCODING) as yaml_file:
                loaded_data = yaml.safe_load(yaml_file)

            if not isinstance(loaded_data, dict):
                return

            excluded = self._get_excluded_fields()
            valid_fields = {f.name for f in fields(self) if f.name not in excluded}

            for key, val in loaded_data.items():
                if key in valid_fields:
                    field_def = next(f for f in fields(self) if f.name == key)

                    if field_def.type is bool and val is not None:
                        val = bool(val)

                    setattr(self, key, val)

            if hasattr(self, "__post_init__"):
                self.__post_init__()

        except (OSError, yaml.YAMLError) as e:
            raise e

    # --------------------------------------------------------------------------------
    def parse_args(self) -> BaseParameters:
        """Parst die standardmäßigen Kommandozeilenparameter für die Anwendung.
        
        :return: (BaseParameters) Beschreibung des Rückgabewerts.
        """

        F = self.Fields
        class_defaults: dict[str, Any] = {f.name: f.default for f in fields(self)}
        parser = ArgumentParser(description="Anwendungs-Konfiguration")

        parser.add_argument(
            "-v", f"--{F.verbose}",
            help="Erhöht die Detailstufe der Log-Ausgabe",
            action="store_true",
            default=class_defaults.get(F.verbose, False)
        )
        parser.add_argument(
            "-l", f"--{F.log}",
            help="Aktiviert das Logging in eine Datei",
            action="store_true",
            default=class_defaults.get(F.log, False)
        )

        l_args, _ = parser.parse_known_args()
        self.update_from_namespace(l_args)

        return self
