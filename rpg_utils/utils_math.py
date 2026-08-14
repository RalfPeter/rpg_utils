#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 13-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm           : utils_math.py
#  Version            : 2.0
#  Beschreibung       : Keine Beschreibung verfügbar.
#  Zeilen             : 257
#  Abhängigkeiten     : fractions, typing
#  Klassen            : MathUtils
# ------------------------------------------------------------------------------

from fractions import Fraction
from typing import Any

# --- Konstanten ---
MAX_DENOMINATOR: int = 10 ** 6


# ================================================================================
# Math & Geo Utilities
# ================================================================================
class MathUtils:
    """Statische Klasse zur Kapselung von mathematischen Operationen und"""

    # --- Konstanten zur besseren Lesbarkeit ---
    DEFAULT_MULTIPLIER: int = -1
    NORTH: str = "N"
    EAST: str = "E"
    SOUTH: str = "S"
    WEST: str = "W"

    # --------------------------------------------------------------------------------
    @staticmethod
    def ceil4(n: int) -> int:
        """
        Gibt die nächste ganze Zahl zurück, die größer als oder gleich `n`
        und ein Vielfaches von 4 ist.

        Ursprüngliche Funktion: ceil4

        :param n: Die Eingabezahl.
        :return: Das nächste Vielfache von 4.
        """
        return (((n - 1) >> 2) + 1) << 2

    # --------------------------------------------------------------------------------
    @staticmethod
    def to_rational_str(number: float | None) -> str:
        """
        Konvertiert eine Zahl in einen rationalen String im Format 'Zähler/Nenner'.

        Ursprüngliche Funktion: number_to_rational_str

        :param number: Die Gleitkommazahl, oder None.
        :return: Der rationale String, oder None wenn number None ist.
        """
        if number is None:
            return ''

        fraction = Fraction(number).limit_denominator(max_denominator=MAX_DENOMINATOR)
        return f'{fraction.numerator}/{fraction.denominator}'

    # --------------------------------------------------------------------------------
    @staticmethod
    def rational_to_float(value: tuple[int, int] | str | Fraction | Any | None) -> float | None:
        """
        Konvertiert einen rationalen Wert (Tuple, String oder Fraction) in eine
        Gleitkommazahl.

        Ursprüngliche Funktion: convert_to_number

        :param value: (tuple[int, int] | str | Fraction) Ein Tuple (Zähler, Nenner),
                      ein String ('Zähler/Nenner') oder ein Fraction-Objekt.
        :return: (float) Die konvertierte Gleitkommazahl.
        :raises ValueError: Bei ungültigem Eingabetyp oder Division durch Null.
        """
        if value is None:
            return None

        try:
            if isinstance(value, tuple):
                if len(value) != 2:
                    raise ValueError("Tuple muss genau zwei Werte enthalten.")
                # Wir entpacken das Tuple direkt in den Konstruktor
                return float(Fraction(value[0], value[1]))

            elif isinstance(value, float):
                return value
            elif isinstance(value, str):
                # Eindeutiger Pfad für Strings
                return float(Fraction(value))
            elif isinstance(value, Fraction):
                # Eindeutiger Pfad für bereits existierende Fraction-Objekte
                return float(value)
            else:
                raise ValueError(f"Ungültiger Eingabetyp {type(value)}.")

        except ZeroDivisionError:
            return 0.0
        except (ValueError, TypeError) as e:
            raise ValueError(f"Konvertierung fehlgeschlagen: {e}") from e

    # --------------------------------------------------------------------------------
    @staticmethod
    def convert_coord_to_dms(coord: float) -> tuple[int, int, float]:
        """
        Konvertiert eine Koordinate von Dezimalgrad nach Grad, Minuten, Sekunden (DMS).

        Ursprüngliche Funktion: convert_to_deg

        :param coord: Die Koordinate als Gleitkommazahl.
        :return: Ein Tuple (Grad, Minuten, Sekunden).
        """
        deg, coord = divmod(abs(coord) * 60, 60)
        mm, sec = divmod(coord * 60, 60)
        return int(deg), int(mm), sec

    # --------------------------------------------------------------------------------
    @staticmethod
    def convert_dms_to_dd(deg: float | None, mm: float | None, sec: float | None) -> float | None:
        """
        Konvertiert Koordinaten von Grad, Minuten, Sekunden (DMS) in Dezimalgrad (DD).

        Ursprüngliche Funktion: convert_to_dec

        :param deg: Grad.
        :param mm: Minuten.
        :param sec: Sekunden.
        :return: Die Koordinate als Dezimalgrad.
        """
        if deg is None or mm is None or sec is None:
            return None
        coord = deg + (mm / 60) + (sec / 3600)
        return coord

    # --------------------------------------------------------------------------------
    @staticmethod
    def format_coord_as_rational_dms(coord: float | None) -> str | None:
        """
        Konvertiert eine Dezimalgrad-Koordinate in den rationalen DMS-String-Format
        für EXIF (z.B. '3/1 4/1 5.2/1').

        Ursprüngliche Funktion: convert_to_fractions

        :param coord: Die Koordinate als Gleitkommazahl.
        :return: Der formatierte String (rationale Grad, Minuten, Sekunden).
        """
        if not (MathUtils.is_valid_float(coord)):
            return None

        deg, mm, sec = MathUtils.convert_coord_to_dms(MathUtils.safe_float(coord))

        deg_str = MathUtils.to_rational_str(deg)
        mm_str = MathUtils.to_rational_str(mm)
        sec_str = MathUtils.to_rational_str(sec)

        return f'{deg_str} {mm_str} {sec_str}'

    # -------------------------------------------------------------------------------------------
    @staticmethod
    def get_geo_refs(lat: float | None, lon: float | None) -> tuple[str | None, str | None]:
        """
        Gibt die geografischen Referenzen (Himmelsrichtungen) als Strings ('N', 'S', 'E', 'W') zurück.

        :param lat: (float | None) Die Breitengrad-Koordinate.
        :param lon: (float | None) Die Längengrad-Koordinate.
        :return: (tuple[str | None, str | None]) (Breitengrad-Referenz, Längengrad-Referenz).
        """
        # Initialisierung der Rückgabewerte
        lat_ref: str | None = None
        lon_ref: str | None = None

        # Einzelprüfung für Breitengrad (Latitude)
        if MathUtils.is_valid_float(lat):
            # Nach dieser Prüfung weiß Python, dass lat ein float ist (Type Narrowing)
            lat_ref = MathUtils.NORTH if MathUtils.safe_float(lat) >= 0 else MathUtils.SOUTH

        # Einzelprüfung für Längengrad (Longitude)
        if MathUtils.is_valid_float(lon):
            # Nach dieser Prüfung weiß Python, dass lon ein float ist
            lon_ref = MathUtils.EAST if MathUtils.safe_float(lon) >= 0 else MathUtils.WEST

        return lat_ref, lon_ref

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_geo_ref_multipliers(lat_ref: str | None, lon_ref: str | None) -> tuple[int | None, int | None]:
        """
        Gibt die Multiplikatoren (1 oder -1) basierend auf den geografischen
        Referenz-Strings zurück.

        Die Funktion betrachtet nur das erste Zeichen des Referenz-Strings
        (z.B. 'N' aus 'North').

        :param lat_ref: Die Breitengrad-Referenz ('N' oder 'S').
        :param lon_ref: Die Längengrad-Referenz ('E' oder 'W').
        :return: Ein Tupel (Breitengrad-Multiplikator, Längengrad-Multiplikator).
        """
        if lat_ref is None or lon_ref is None:
            return None, None

        # Holen des ersten Zeichens und Umwandlung in Großbuchstaben (oder None)
        # Verarbeitung Breitengrad
        lat_mult = 1 if lat_ref and lat_ref[0].upper() == MathUtils.NORTH else MathUtils.DEFAULT_MULTIPLIER
        # Verarbeitung Längengrad
        lon_mult = 1 if lon_ref and lon_ref[0].upper() == MathUtils.EAST else MathUtils.DEFAULT_MULTIPLIER
        return lat_mult, lon_mult

    # --------------------------------------------------------------------------------
    @staticmethod
    def convert_coords_to_deg_refs(lat: float, lon: float) -> tuple[tuple[int, int, float, str], tuple[int, int, float, str]] | None:
        """
        Konvertiert Breitengrad und Längengrad in ein strukturiertes Format.

        Ursprüngliche Funktion: convert_to_degs (nutzt convert_to_strs und convert_to_deg)

        :param lat: Die Breitengrad-Koordinate.
        :param lon: Die Längengrad-Koordinate.
        :return: Ein Tupel von Tupeln mit DMS und Referenz.
        """
        lat_ref, lon_ref = MathUtils.get_geo_refs(lat, lon)
        if lat_ref is None or lon_ref is None:
            return None

        lat_dms = MathUtils.convert_coord_to_dms(lat)
        lon_dms = MathUtils.convert_coord_to_dms(lon)

        lat_deg_ref: tuple[int, int, float, str] = lat_dms + (lat_ref,)
        lon_deg_ref: tuple[int, int, float, str] = lon_dms + (lon_ref,)

        return lat_deg_ref, lon_deg_ref

    # -------------------------------------------------------------------------------------------
    @staticmethod
    def is_valid_float(value: float | int | str | Any) -> bool:
        """Prüft, ob der Wert in ein gültiges Float umgewandelt werden kann.

        :param value: (any) Der zu prüfende Wert.
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    # -------------------------------------------------------------------------------------------
    @staticmethod
    def safe_float(value: float | int | str | Any) -> float:
        """Wandelt den Wert sicher in ein Float um.

        :param value: (any) Der umzuwandelnde Wert.
        """
        return float(value)

    # -------------------------------------------------------------------------------------------
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """
        Konvertiert einen Wert sicher in int.

        :param value: Der zu konvertierende Wert.
        :param default: Rückgabewert bei Fehler.
        :return: Konvertierter int oder default.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
