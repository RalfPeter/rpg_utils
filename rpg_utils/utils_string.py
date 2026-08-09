#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 04-08-2026
# Ralf Peter <ralfpeter61@email.de>
# https://github.com/RalfPeter/tracktraffic.git
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Program : utils_string.py (main - GoPro Videos and Telemetry Export)
#  Version : 1.0
# ------------------------------------------------------------------------------
#  Klassen:
#     StringUtils
#  Public Methods:
#     StringUtils.decode_bytes(value)     → Konvertiert ein Byte-Objekt in einen String mittels UTF-8 oder gibt
#     StringUtils.replace_placeholders(pattern, dt, basename, user, fallback_name) → Ersetzt Platzhalter im gegebenen Muster robust gegen doppelte '%'
#     StringUtils.safe_str(val, default)  → Wandelt einen Wert in String um oder gibt Default zurück.
#     sstr(val, default)                  → Wandelt einen Wert in String um oder gibt Default zurück.
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter61@email.de>
# ------------------------------------------------------------------------------

from datetime import datetime
from typing import Any


# ================================================================================
# String Utilities
# ================================================================================
class StringUtils:
    """
    Statische Klasse zur Kapselung von String-Operationen wie
    Dekodierung und Platzhalterersetzung.
    """

    # --------------------------------------------------------------------------------
    @staticmethod
    # -------------------------------------------------------------------------
    def decode_bytes(value: bytes | str | None) -> str | None:
        """
        Konvertiert ein Byte-Objekt in einen String mittels UTF-8 oder gibt
        den String unverändert zurück.

        Die Funktion stellt sicher, dass immer ein String zurückgegeben wird,
        was die nachfolgende Verarbeitung vereinfacht.

        :param value: (bytes | str | None) Das Byte- oder String-Objekt, das dekodiert werden soll.
        :return: (str) Der vollständig dekodierte oder unveränderte String oder None.
        """
        # Rückgabe eines leeren Strings, falls die Eingabe None ist.
        if value is None:
            return None

        if isinstance(value, str):
            # Gibt den String bei String-Eingabe vollständig zurück
            return value

        if isinstance(value, bytes):
            try:
                # Dekodierung
                return value.decode('utf-8')
            except UnicodeDecodeError:
                # Robuste Fehlerbehandlung
                return str(value)

        # Für den Fall, dass ein unerwarteter Typ übergeben wurde
        return None

    # --------------------------------------------------------------------------------
    @staticmethod
    def replace_placeholders(
            pattern: str,
            dt: datetime | None,
            basename: str | None = None,
            user: str | None = None,
            fallback_name: str = "UNNAMED"
    ) -> str:
        """
        Ersetzt Platzhalter im gegebenen Muster robust gegen doppelte '%'
        und stellt sicher, dass niemals ein leerer Dateiname zurückgegeben wird.

        :param pattern: Das String-Muster mit Platzhaltern (z.B. '%Y%m%d-%c-%z').
        :param dt: Das datetime-Objekt.
        :param basename: Der Basisname (für '%c').
        :param user: Der Benutzername (für '%u').
        :param fallback_name: Standard-Dateiname, falls das Ergebnis sonst leer wäre.
        :return: Der ersetzte, nicht-leere String.
        """
        # 1. Grundlegende Absicherung
        if not pattern or not pattern.strip():
            # Falls gar kein Pattern da ist, versuche den Basisnamen oder Fallback zu nehmen
            return basename.strip() if basename and basename.strip() else fallback_name

        result = pattern

        # 2. Bereinigung: Doppelte '%%' aus Kommandozeile/Escapes zu einfachen '%' reduzieren
        result = result.replace('%%', '%')

        # 3. Sauberes Handling für fehlende optionale Werte (inkl. Trennstriche)
        if not user or not str(user).strip():
            result = result.replace('-%u', '').replace('_%u', '').replace('%u', '')
        else:
            result = result.replace('%u', str(user).strip())

        if not basename or not str(basename).strip():
            result = result.replace('-%c', '').replace('_%c', '').replace('%c', '')
        else:
            result = result.replace('%c', str(basename).strip())

        # 4. Datums- und Zeitzonen-Platzhalter via strftime auflösen
        if dt is not None:
            try:
                result = dt.strftime(result)
            except ValueError:
                pass

        # 5. Finale Validierung: Dateiname darf nicht leer oder ein reiner Whitespace-String sein
        result = result.strip()

        if not result:
            # Priorität beim Fallback: basename -> optionaler fallback_name
            if basename and str(basename).strip():
                return str(basename).strip()
            return fallback_name

        return result

    # --------------------------------------------------------------------------------
    @staticmethod
    def safe_str(val: Any, default: str = "") -> str:
        """Wandelt einen Wert in String um oder gibt Default zurück."""
        return str(val) if val is not None else default


# --------------------------------------------------------------------------------
def sstr(val: Any, default: str = "") -> str:
    """Wandelt einen Wert in String um oder gibt Default zurück."""
    return str(val) if val is not None else default
