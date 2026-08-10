#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 10-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm          : utils_datetime.py
#  Version           : 2.0
#  Beschreibung      : Keine Beschreibung verfügbar.
#  Zeilen            : 561
#  Abhängigkeiten    : datetime, fractions, re, typing, tzlocal, zoneinfo
#  Klassen           : DateTimeUtils
# ------------------------------------------------------------------------------
#  Public Methoden:
#    DateTimeUtils                                        → Statische Klasse zur Kapselung aller Datums-, Zeit- und Zeitzonen-Hilfsfunktionen.
#      add_timedelta(datetime, int | timedelta)           → Addiert auf ein DateTime eine Anzahl Sekunden oder ein timedelta auf.
#      format_datetime(datetime, str, timedelta, 
#                      str | tzinfo)                      → Formatiert ein datetime-Objekt in einen String, nach optionaler Anwendung einer
#      convert_to_offset_str(datetime)                    → Konvertiert den Zeitzonen-Offset in das Format '+HH:MM' (entspricht timezone_to_str).
#      create_aware_base_datetime(int, int, int, 
#                                 int, int, int, int, str | tzinfo) → Erstellt ein zeitzonen-bewusstes datetime-Objekt mit anpassbaren Basisdaten.
#      delta_time(str | datetime, timedelta, str)         → Konvertiert einen Timestamp-String oder ein datetime-Objekt in ein UTC-datetime,
#      convert_to_timezone(datetime, str | tzinfo)        → Konvertiert ein datetime-Objekt in die angegebene Zeitzone.
#      datetime_diff(datetime, datetime)                  → Berechnet die Zeitdifferenz zwischen zwei datetime-Objekten.
#      parse_datetime_string(str, bool)                   → Parst einen Datums-String anhand bekannter Formate (ISO 8601, EXIF, IPTC).
#      get_timezone_hour_offset(datetime)                 → Ermittelt den Stunden-Offset der Zeitzone eines datetime-Objekts.
#      parse_offset(str)                                  → Analysiert einen Zeitzonen-Offset-String und konvertiert ihn in ein datetime.timedelta-Objekt.
#      datetime_to_fractions(datetime)                    → Konvertiert Stunden, Minuten und Sekunden eines datetime-Objekts in rationale Strings.
#      prepare_exif_datetime_fields(str, str)             → Verarbeitet die Rohwerte des Datums und Offsets, um ein vollständiges
#      prepare_iptc_datetime_fields(str, str)             → Konvertiert EXIF-Datum und Offset in die Zielformate für IPTC und gibt
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter.bergheim@gmail.com>
# ------------------------------------------------------------------------------

import re
from datetime import datetime, timezone, tzinfo, timedelta
from fractions import Fraction
from typing import Final
from zoneinfo import ZoneInfo
import tzlocal

# -------------------------------------------------------------------------------------------
# Konstanten für Zeitzone (hier definiert, da mehrfach verwendet.
# -------------------------------------------------------------------------------------------
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
ISO_FORMAT_FILENAME_PART: str = '%Y%m%d_%H%M%S'       # '<Datum>_<Zeit>'
ISO_FORMAT_TZ = "%Y-%m-%d %H:%M:%S %Z"
# Wir definieren hier die UTC-Konstante, um sie zentral zu halten.
TZ_UTC: Final[tzinfo] = timezone.utc
TZ_Z: str = 'Z'
TZ_LOCALZONE: Final[tzinfo] = tzlocal.get_localzone()
# --- Konstanten für Formatierung ---
# ISO-8601-Datumsformat (Standard: YYYY-MM-DD) (nur hier verwendet)
ISO_COMPONENT_DATE: Final[str] = "%Y-%m-%d"
# Basiskomponente für Stunde, Minute, Sekunde (nur hier verwendet)
ISO_COMPONENT_TIME: Final[str] = "%H:%M:%S"
# ISO-8601-Datumsformat (Standard: YYYY-MM-DD HH:MM:SS) (nur hier verwendet)
ISO_DATETIME: Final[str] = f"{ISO_COMPONENT_DATE}T{ISO_COMPONENT_TIME}"
# Vollständiges ISO 8601-Format mit Mikrosekunden und 'Z' (Zulu/UTC): (YYYY-MM-DDTHH:MM:SS.sssZ) (nur hier verwendet)
ISO_DATETIME_ZULU: Final[str] = f"{ISO_DATETIME}.%fZ"
# Format für HH:MM Offset (z.B. +02:00) (nur hier verwendet)
OFFSET_HHMM: Final[str] = "{:02}:{:02}"
# ISO 8601 Basis-Offset-Format ohne Doppelpunkt (+HHMM) (nur hier verwendet)
OFFSET_HHMM_NO_COLON: Final[str] = "%z"
# Der standardmäßige UTC-Offset, um das 'Z' in ISO 8601 zu ersetzen  (nur hier verwendet)
OFFSET_HHMM_UTC: Final[str] = "+00:00"
# Entferne eventuell vorhandene Nicht-Ziffern aus dem offset_str
EXIF_OFFSET_PATTERN = re.compile(r"([+\-]?\d{1,2}):?(\d{2})")
# --- aus gpmf_exif
EXIF_DATE: Final[str] = "%Y:%m:%d"
EXIF_DATETIME: Final[str] = f"{EXIF_DATE} {ISO_COMPONENT_TIME}"
IPTC_DATE: Final[str] = f"{ISO_COMPONENT_DATE}"
IPTC_TIME: Final[str] = f"{ISO_COMPONENT_TIME}"
IPTC_DATETIME: Final[str] = f"{ISO_COMPONENT_DATE} {ISO_COMPONENT_TIME}"  # (nur hier verwendet)


# ================================================================================
# Klassenstruktur zur Organisation der Funktionen
# ================================================================================
class DateTimeUtils:
    """Statische Klasse zur Kapselung aller Datums-, Zeit- und Zeitzonen-Hilfsfunktionen."""

    # --------------------------------------------------------------------------------
    @staticmethod
    def add_timedelta(dt: datetime | None = None, delta: int | timedelta | None = None) -> datetime | None:
        """
        Addiert auf ein DateTime eine Anzahl Sekunden oder ein timedelta auf.

        :param dt: (datetime | None) Das Basis-Datum.
        :param delta: (int | timedelta | None) Die zu addierende Zeit (Sekunden als int oder timedelta).
        :return: (datetime | None) Das neue Datum oder None, falls dt None ist.
        """
        if dt is None:
            return None

        if isinstance(delta, int):
            return dt + timedelta(seconds=delta)

        # Dank Type Narrowing: Wenn delta ein timedelta ist, wird es addiert.
        # Falls delta None oder ein falscher Typ ist, wird einfach dt zurückgegeben.
        return dt + delta if isinstance(delta, timedelta) else dt

    # --------------------------------------------------------------------------------
    @staticmethod
    def _ensure_aware(dt: datetime, default_tz: tzinfo = TZ_UTC) -> datetime:
        """Stellt sicher, dass ein datetime-Objekt zeitzonenbewusst (aware) ist.

        :param dt: (datetime) Das zu prüfende datetime-Objekt.
        :param default_tz: (tzinfo) Die Zeitzone, die zugewiesen wird, falls dt naiv ist.
        :return: (datetime) Ein garantiertes zeitzonenbewusstes datetime-Objekt.
        """
        # 1. Extraktion in lokale Variable (Type Narrowing)
        info = dt.tzinfo
        # 2. Prüfung der lokalen Variable
        if info is not None and info.utcoffset(dt) is not None:
            return dt
        else:
            return dt.replace(tzinfo=default_tz)

    # --------------------------------------------------------------------------------
    @staticmethod
    def format_datetime(
            dt: datetime | None,
            format_str: str | None = None,
            delta: timedelta | None = None,
            tz: str | tzinfo | None = None,
    ) -> str:
        """
        Formatiert ein datetime-Objekt in einen String, nach optionaler Anwendung einer
        Zeitdifferenz und Konvertierung in eine Zielzeitzone.

        Diese Methode ersetzt `datetime_to_str` und `format_zulu`.

        :param dt: Das zu formatierende datetime-Objekt.
        :param tz: Die Zeitzone, in die konvertiert werden soll (z.B. TZ_UTC, 'Europe/Berlin').
                   Wenn None, wird die aktuelle Zeitzone von dt beibehalten.
        :param format_str: Der Format-String (z.B. ISO_DATETIME_ZULU, EXIF_DATETIME).
        :param delta: Eine zusätzliche Zeitdifferenz.
        :return: Der formatierte Datums-/Zeit-String.
        :raises ValueError: Wenn dt None ist.
        """
        if dt is None:
            raise ValueError("Das zu formatierende datetime-Objekt darf nicht None sein.")

        # 1. Defensive Zuweisung (Initialisierung innerhalb der Funktion)
        format_str: str = format_str or ISO_DATETIME
        delta: timedelta = delta or timedelta(0)

        # 2. Umwandlung in gewünschte Zeitzone
        dt_aware = DateTimeUtils.convert_to_timezone(dt, tz=tz) if tz is not None else dt
        if dt_aware is None:
            # Sollte nicht passieren, aber als Schutz
            return ""

        # 3. Anwendung der Zeitdifferenz
        dt_final: datetime = dt_aware + delta

        # 4. Formatierung
        try:
            # Spezielle Behandlung für das 'Z' in ISO 8601-Zulu-Formaten
            # Wir behandeln ISO_DATETIME_ZULU gesondert, da strftime das '%f' und 'Z' nicht gut kombiniert
            if format_str == ISO_DATETIME_ZULU and dt_final.tzinfo == TZ_UTC:
                # Entfernt die letzten Zeichen (.%fZ) und formatiert manuell
                base_format = f"{ISO_DATETIME}.%f"

                # Formatierung des Datums/Uhrzeit-Teils
                formatted_dt = dt_final.strftime(base_format)

                # Kürzen auf Millisekunden (letzten 3 Ziffern des %f)
                return formatted_dt[:-3] + TZ_Z

            # Reguläre Formatierung (für EXIF_DATETIME, IPTC_DATE etc.)
            return dt_final.strftime(format_str)

        except ValueError as e:
            raise ValueError(f"Fehler beim Formatieren von datetime: ungültiger Format-String: {e}")

    # --------------------------------------------------------------------------------
    @staticmethod
    def _datetimestr_to_datetime(dt_string: str, format_str: str | None = None, time_delta: timedelta | None = None) -> datetime | None:
        """
        Parst einen datetime-ähnlichen String (z.B. YYYY-MM-DD HH:MM:SS) und erzeugt ein datetime.

        :param dt_string: Der Datumsstring.
        :param format_str: Der Zielstandard ('EXIF_DATETIME', 'IPTC_DATE' oder 'IPTC_TIME').
        :param time_delta: Die Zeitdifferenz als timedelta
        :return: Naives datetime-Objekt oder None.
        :raises ValueError: Wenn ein unbekannter Standard übergeben wird.
        """
        if format_str is None:
            format_str = "%y%m%d%H%M%S.%fZ"

        try:
            dt: datetime = datetime.strptime(dt_string, format_str)
        except ValueError:
            return None

        if time_delta is not None:
            return dt + time_delta
        else:
            return dt

    # --------------------------------------------------------------------------------
    @staticmethod
    def convert_to_offset_str(dt: datetime) -> str | None:
        """
        Konvertiert den Zeitzonen-Offset in das Format '+HH:MM' (entspricht timezone_to_str).

        Diese statische Methode vereint die Logik von timezone_to_str, um einen
        robusten Offset-String zu erstellen.

        :param dt: Ein datetime-Objekt, das bereits eine Zeitzone (`tzinfo`) hat.
        :return: Der Zeitzonen-Offset als String (z.B. '+02:00'), oder None.
        """
        offset: timedelta | None = dt.utcoffset()
        if offset is None:
            return None

        total_seconds: int = int(offset.total_seconds())
        sign: str = '+' if total_seconds >= 0 else '-'

        # Betrag der Sekunden für die Berechnung
        abs_seconds: int = abs(total_seconds)

        hours, remainder = divmod(abs_seconds, 3600)
        minutes = remainder // 60

        return sign + OFFSET_HHMM.format(hours, minutes)

    # --------------------------------------------------------------------------------
    @staticmethod
    def create_aware_base_datetime(
            year: int = 2000,
            month: int = 1,
            day: int = 1,
            hour: int = 0,
            minute: int = 0,
            second: int = 0,
            microsecond: int = 0,
            tz: str | tzinfo = TZ_UTC
    ) -> datetime:
        """
        Erstellt ein zeitzonen-bewusstes datetime-Objekt mit anpassbaren Basisdaten.

        Bietet flexible Kontrolle über das Datum, die Zeit und die Zeitzone,
        wobei die Standardwerte auf '2000-01-01 00:00:00 UTC' gesetzt sind.

        :param year: Das Jahr des Datums. Standard ist 2000.
        :param month: Der Monat des Datums. Standard ist 1.
        :param day: Der Tag des Datums. Standard ist 1.
        :param hour: Die Stunde. Standard ist 0.
        :param minute: Die Minute. Standard ist 0.
        :param second: Die Sekunde. Standard ist 0.
        :param microsecond: Die Mikrosekunde. Standard ist 0.
        :param tz: Die Zeitzone als tzinfo-Objekt (Standard: TZ_UTC) oder IANA-String.
        :return: Ein zeitzonen-bewusstes datetime-Objekt.
        """

        # 1. Zeitzonenobjekt bestimmen
        tz_info: tzinfo
        if isinstance(tz, str):
            # Falls ein IANA-String übergeben wurde (z.B. 'Europe/Berlin')
            tz_info = ZoneInfo(tz)
        else:
            # Falls ein tzinfo-Objekt übergeben wurde (z.B. TZ_UTC)
            tz_info = tz

        # 2. Erstellen des zeitzonen-bewussten datetime-Objekts
        return datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            tzinfo=tz_info
        )

    # --------------------------------------------------------------------------------
    @staticmethod
    def delta_time(
            par_timedata: str | datetime,
            par_delta: timedelta = timedelta(0),
            par_tformat: str = "%y%m%d%H%M%S.%f"
    ) -> datetime | None:
        """
        Konvertiert einen Timestamp-String oder ein datetime-Objekt in ein UTC-datetime,
        nachdem ein optionales Zeit-Delta angewendet wurde.

        Diese Methode konsolidiert das Parsen verschiedener Eingabetypen und stellt
        die abschließende Konvertierung nach UTC sicher.

        :param par_timedata: Timestamp-String, datetime-Objekt oder None für die aktuelle Zeit.
        :param par_delta: Delta (timedelta), das zum Zeitstempel hinzugefügt werden soll.
                          Standard ist Null.
        :param par_tformat: Format-String, falls par_timedata ein String ist.
        :return: UTC datetime-Objekt, oder None, falls das Parsen fehlschlägt.
        """

        if par_timedata is None:
            raise ValueError("Die übergebene datetime-Objekt darf nicht None sein.")

        elif isinstance(par_timedata, str):
            # Parsen des Strings über die Hilfsmethode, die auch das Delta anwendet.
            l_datetime = DateTimeUtils._datetimestr_to_datetime(par_timedata, par_tformat, par_delta)

        elif isinstance(par_timedata, datetime):
            # Delta direkt auf das vorhandene datetime-Objekt anwenden
            l_datetime = par_timedata + par_delta

        else:
            # Unerwarteter Typ
            l_datetime = None

        # Abschließender Schritt: Konvertierung in die Zielzone (UTC).
        # Die zuvor konsolidierte convert_to_timezone-Funktion ist hier ideal,
        # da sie alle Fälle abdeckt: Naiv -> Lokalisiert auf UTC,
        # Aware (Non-UTC) -> Konvertiert nach UTC, None -> None.
        return DateTimeUtils.convert_to_timezone(l_datetime, tz=TZ_UTC)

    # --------------------------------------------------------------------------------
    @staticmethod
    def convert_to_timezone(dt: datetime | None, tz: str | tzinfo | None) -> datetime | None:
        """
        Konvertiert ein datetime-Objekt in die angegebene Zeitzone.

        Wenn `tz` ein String ist, wird es als Zeitzonenname (z.B. 'Europe/Berlin') interpretiert.
        Wenn `tz` None ist, wird in die lokale Systemzeit konvertiert.
        Wenn `tz` eine tzinfo (z.B. timezone.utc) ist, wird diese verwendet.

        :param dt: Das datetime-Objekt (kann naive oder aware sein).
        :param tz: Die Zielzeitzone (Name, tzinfo-Objekt oder None für Lokalzeit).
        :return: Das in die Zielzeitzone umgerechnete datetime-Objekt.
        """
        if dt is None:
            return None

        # 1. Sicherstellen, dass das datetime-Objekt zeitzonenbewusst ist
        # if dt.tzinfo is None:
            # raise TypeError("Das datetime-Objejt Parameter 'target_tz' muss ein String, ein tzinfo-Objekt oder None sein.")
            # Standardverhalten: Naive Zeiten als Lokalzeit interpretieren
            # dt = DateTimeUtils.localize_datetime(dt)

        # 2. Ziel-Zeitzonenobjekt bestimmen
        if isinstance(tz, str):
            # Zielzone ist ein String (z.B. 'Europe/Berlin')
            tz_info = ZoneInfo(tz)
        elif isinstance(tz, tzinfo):
            # Zielzone ist bereits ein tzinfo-Objekt (z.B. timezone.utc)
            tz_info = tz
        elif tz is None and dt.tzinfo is None:
            # Zielzone ist die lokale Systemzeit (bisheriges `convert_to_local_time` ohne tz)
            tz_info = TZ_LOCALZONE
        else:
            tz_info = None
            # Fallback für unerwartete Typen
            # raise TypeError("Der Parameter 'target_tz' muss ein String, ein tzinfo-Objekt oder None sein.")

        # 3. Konvertierung durchführen
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz_info)
        elif tz_info is not None:
            dt = dt.astimezone(tz_info) if tz_info != dt.tzinfo else dt

        return dt

    # --------------------------------------------------------------------------------
    @staticmethod
    def datetime_diff(start_zeit: datetime, ende_zeit: datetime) -> float:
        """
        Berechnet die Zeitdifferenz zwischen zwei datetime-Objekten.

        Beide Zeiten werden zuerst in tz-aware Objekte umgewandelt (naive Zeiten
        erhalten die Standard-Zeitzone des Berechners), bevor die Subtraktion
        durchgeführt wird.

        :param start_zeit: Der Startzeitpunkt.
        :type start_zeit: datetime
        :param ende_zeit: Der Endzeitpunkt.
        :type ende_zeit: datetime
        :raises TypeError: Wenn eines der übergebenen Objekte kein datetime-Objekt ist.
        :returns: Die Zeitdifferenz (ende_zeit - start_zeit).
        :rtype: timedelta
        :dok: Berechnet die Differenz nach Sicherstellung der Zeitzonen-Awareness.
        """
        # 1. Sicherstellen, dass beide Zeiten tz-aware sind
        tz_aware_start = DateTimeUtils._ensure_aware(start_zeit)
        tz_aware_ende = DateTimeUtils._ensure_aware(ende_zeit)
        # 2. Subtraktion der tz-aware Objekte ergibt eine timedelta
        differenz: timedelta = tz_aware_ende - tz_aware_start
        # 3. Konvertierung der timedelta in die Gesamtzahl der Sekunden
        # timedelta.total_seconds() liefert einen float, was ideal für Präzision ist.
        return abs(differenz.total_seconds())

    # --------------------------------------------------------------------------------
    @staticmethod
    def parse_datetime_string(string: str | None, is_aware: bool = False) -> datetime | None:
        """
        Parst einen Datums-String anhand bekannter Formate (ISO 8601, EXIF, IPTC).

        :param string: Der Datums-String.
        :param is_aware: Gibt an, ob im String eine Zeitzone erwartet wird.
        :return: Das geparste datetime-Objekt.
        :raises ValueError: Wenn kein passendes Format gefunden wird.
        """
        if not string:
            return None

        # 1. Versuch: Robustes ISO 8601 (inkl. Zulu 'Z'-Handling)
        try:
            dt_iso_str = string.rstrip(TZ_Z) + OFFSET_HHMM_UTC if string.upper().endswith(TZ_Z) else string
            return datetime.fromisoformat(dt_iso_str)
        except ValueError:
            pass  # Kein valides ISO-Format -> weiter mit den spezifischen Formaten

        # 2. Versuch: Spezifische EXIF- & IPTC-Formate
        formats = [EXIF_DATETIME, IPTC_DATETIME]

        if is_aware:
            formats = [f + OFFSET_HHMM_NO_COLON for f in formats] + formats

        for date_format in formats:
            try:
                return datetime.strptime(string, date_format)
            except ValueError:
                pass

        raise ValueError(f"Unbekanntes Datumsformat: {string}. Erwartete Formate: {formats}")

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_timezone_hour_offset(dt: datetime) -> int:
        """
        Ermittelt den Stunden-Offset der Zeitzone eines datetime-Objekts.

        Der Offset wird als ganze Zahl (Integer) zurückgegeben, z.B. 2 für +02:00
        oder -5 für -05:00. Die Funktion nutzt total_seconds() zur korrekten
        Verarbeitung positiver und negativer Offsets.

        :param dt: Ein 'tz-aware' datetime-Objekt.
        :return: Der Stunden-Offset der Zeitzone (int), oder 0, falls kein Offset
                 (tz-naive datetime) vorhanden ist.
        """
        utcoffset: timedelta | None = dt.utcoffset()

        if utcoffset is None:
            # Wird bei tz-naive (Zeitzonen-uninformierten) datetime-Objekten zurückgegeben.
            # Hier wird, wie von Ihnen impliziert, 0 zurückgegeben.
            return 0

        # Berechnet total_seconds() (inkl. Vorzeichen) und konvertiert zu Stunden-Integer.
        # Beachten Sie: total_seconds() liefert ein float, daher die Notwendigkeit des int-Cast.
        return int(utcoffset.total_seconds() // 3600)

    # --------------------------------------------------------------------------------
    @staticmethod
    def parse_offset(offset_str: str) -> timedelta:
        """
        Analysiert einen Zeitzonen-Offset-String und konvertiert ihn in ein datetime.timedelta-Objekt.

        Die Methode ist robust gegenüber gängigen Formaten wie '+02:00', '+2:00', '-0800'.

        :param offset_str: (str) Der Zeitzonen-Offset-String aus EXIF-Daten.
        :raises ValueError: Wenn der Offset-String nicht in ein gültiges Format geparst werden kann.
        :returns: (timedelta) Das resultierende Zeitintervall.
        """
        # Entferne eventuell vorhandene Nicht-Ziffern aus dem offset_str
        match = EXIF_OFFSET_PATTERN.match(offset_str.strip())

        if not match:
            # Versuch, den String als reinen HHMM-String ohne Trennzeichen zu behandeln
            if len(offset_str) == 5 and (offset_str.startswith('+') or offset_str.startswith('-')):
                match = EXIF_OFFSET_PATTERN.match(f"{offset_str[:3]}:{offset_str[3:]}")
            elif len(offset_str) == 4 and offset_str.isdigit():
                match = EXIF_OFFSET_PATTERN.match(f"+{offset_str[:2]}:{offset_str[2:]}")

        if not match:
            raise ValueError(f"Ungültiges Format für Zeitzonen-Offset: '{offset_str}'")

        sign = -1 if match.group(1).startswith('-') else 1
        hours = int(match.group(1).lstrip('+-') or 0)
        minutes = int(match.group(2) or 0)

        total_minutes = (hours * 60 + minutes) * sign

        return timedelta(minutes=total_minutes)

    # --------------------------------------------------------------------------------
    @staticmethod
    def datetime_to_fractions(dt: datetime | None) -> str | None:
        """Konvertiert Stunden, Minuten und Sekunden eines datetime-Objekts in rationale Strings.
        
        :param dt: (datetime | None) Beschreibung von dt.
        :return: (str | None) Beschreibung des Rückgabewerts.
        """

        # --------------------------------------------------------------------------------
        def number_to_rational_str(number: float) -> str:
            """Konvertiert eine Gleitkommazahl in einen rationalen String (Zähler/Nenner).
            
            :param number: (float) Beschreibung von number.
            :return: (str) Beschreibung des Rückgabewerts.
            """

            fraction = Fraction(number).limit_denominator(max_denominator=10 ** 6)
            return f'{fraction.numerator}/{fraction.denominator}'

        if dt is None:
            return None

        hours_fraction = number_to_rational_str(dt.hour)
        minutes_fraction = number_to_rational_str(dt.minute)
        seconds_fraction = number_to_rational_str(dt.second)
        return f'{hours_fraction} {minutes_fraction} {seconds_fraction}'

    # --------------------------------------------------------------------------------
    @staticmethod
    def prepare_exif_datetime_fields(
            dto: str,
            offset: str | None,
    ) -> tuple[str, str | None, str | None, str | None]:
        """
        Verarbeitet die Rohwerte des Datums und Offsets, um ein vollständiges
        Dictionary von EXIF-Korrekturen zu erzeugen.

        :param dto: Der Wert aus data[ExifDateTimeOriginal] (z.B. '2025-09-13 12:34:56').
        :param offset: Der Wert aus data[ExifOffsetTimeOriginal] (z.B. '+0200') oder None.
        :return: Ein tupel mit allen korrigierten Datums-/Zeitfeldern.
        """
        # 1. Korrektur des Datumsformats (ersetze '-' durch ':' im Datumsteil)
        # Bsp: '2025-09-13 12:34:56' -> '2025:09:13 12:34:56'
        dto_corrected: str = dto[:10].replace('-', ':') + dto[10:]

        dtz: datetime  # Das zeitzonen-bewusste Ergebnis

        # 2. Parsen des Datums mit oder ohne Offset
        if offset:
            # 2a. Parsen mit Offset-Zeit: YYYY:MM:DD HH:MM:SS+-HHMM
            try:
                # dto_corrected + offset_raw (z.B. '2025:09:13 12:34:56+0200')
                dtz = datetime.strptime(dto_corrected + offset, EXIF_DATETIME + OFFSET_HHMM_NO_COLON)
            except ValueError:
                # Fallback: Naiv parsen und als UTC annehmen
                dtz = datetime.strptime(dto_corrected, EXIF_DATETIME).replace(tzinfo=timezone.utc)
        else:
            # 2b. Parsen ohne Offset-Zeit: YYYY:MM:DD HH:MM:SS
            # Naiv parsen
            dtz = datetime.strptime(dto_corrected, EXIF_DATETIME)

        # 3. Rückgabe der 4 Strings
        d_stamp = dtz.strftime(EXIF_DATE) if dtz else None
        t_stamp = DateTimeUtils.datetime_to_fractions(dtz) if dtz else None

        return dto_corrected, offset, d_stamp, t_stamp

    # --------------------------------------------------------------------------------
    @staticmethod
    def prepare_iptc_datetime_fields(
            dto_raw: str | None,
            offset_raw: str | None = None,
    ) -> tuple[str, str]:
        """
        Konvertiert EXIF-Datum und Offset in die Zielformate für IPTC und gibt
        das UTC-Datum/Zeit-Objekt zurück.

        :param dto_raw: Der String aus self.data_exif[ExifDateTimeOriginal].
        :param offset_raw: Der String aus self.data_exif[ExifOffsetTimeOriginal] oder None.
        :return: Ein Tupel mit (iptc_date, iptc_time).
        """
        # 1. Standard-Offset setzen, falls keiner übergeben wurde (oder falls None)
        if dto_raw is None or dto_raw == '':
            return '', ''
        offset_used: str = offset_raw or ''  # if offset_raw is not None else None

        # 2. Parsen des Datums mit dem Offset
        try:
            # Versuche, mit Zeitzonen-Offset zu parsen
            dtz = datetime.strptime(dto_raw + offset_used, EXIF_DATETIME + OFFSET_HHMM_NO_COLON)
        except ValueError:
            # Fallback: Naiv parsen ohne Zeitzone
            dtz = datetime.strptime(dto_raw, EXIF_DATETIME)

        # 3. Neuformatierung für IPTC-Ziel-Felder
        iptc_date: str = dtz.strftime(IPTC_DATE)             # Bsp: '20250913'
        if offset_used:
            iptc_time: str = dtz.strftime(IPTC_TIME) + offset_used  # Bsp: '103456+00:00' (UTC-Zeit)
        else:
            iptc_time: str = dtz.strftime(IPTC_TIME)

        # HINWEIS: Der IPTCTimeCreated String muss den Offset am Ende haben (z.B. '103456+00:00')
        # Wir verwenden hier den korrigierten Offset in einem standardisierten Format für IPTC.
        # Der Originalcode verwendet den Offset, der zuvor aus EXIF gelesen wurde.
        # Da IPTC TimeCreated immer UTC-Zeit ist, sollte der Offset +00:00 sein.
        return iptc_date, iptc_time
