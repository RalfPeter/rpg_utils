#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 10-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm          : utils_http.py
#  Version           : 2.0
#  Beschreibung      : Keine Beschreibung verfügbar.
#  Zeilen            : 144
#  Abhängigkeiten    : http, requests, typing
#  Klassen           : HttpUtils
# ------------------------------------------------------------------------------
#  Public Methoden:
#    HttpUtils                                            → Statische Klasse zur Kapselung von HTTP-Anfragen (GET und POST) mit
#      get_content_from_url(str, str, int)                → Lädt Inhalte von einer URL herunter (GET-Anfrage).
#      post_content_to_url(str, str, int)                 → Sendet einen POST-Request an die URL.
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter.bergheim@gmail.com>
# ------------------------------------------------------------------------------

from requests import get, post
from requests.exceptions import SSLError, ReadTimeout, RequestException
from typing import Any, Callable, TypeVar
from http import HTTPStatus

from rpg_utils.utils_core import log_to_callback, CallbackTag as Tag

# --- Konstanten ---
_T = TypeVar('_T')


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------
# HTTP Utilities (GET- und POST-Anfragen)
# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


# ================================================================================
# ================================================================================
class HttpUtils:
    """Statische Klasse zur Kapselung von HTTP-Anfragen (GET und POST) mit"""

    status_ok = HTTPStatus.OK
    status_not_found = HTTPStatus.NOT_FOUND
    status_not_modified = HTTPStatus.NOT_MODIFIED

    # --------------------------------------------------------------------------------
    @staticmethod
    def _handle_request(
            method: Callable[..., _T],
            url: str,
            error_message: str,
            timeout: int,
            json: bool,
            return_headers: bool = False,
            **kwargs: Any
    ) -> Any | None:
        """
        Interne Hilfsfunktion zur Abwicklung von requests.get/post.

        :param method: Die requests-Methode (get oder post).
        :param url: Ziel-URL.
        :param error_message: Fehlertext für Logausgabe.
        :param timeout: Timeout in Sekunden.
        :param json: Wenn True, wird r.json() zurückgegeben.
        :param return_headers: Wenn True, werden auch die Response-Headers zurückgegeben.
        :param kwargs: Weitere Parameter für die requests-Methode.
        :return: Bei Erfolg: (status_code, content) oder (status_code, content, headers) wenn return_headers=True.
                 Bei Fehler: None.
        """

        # Setze Default-User-Agent (zentral für alle APIs)
        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        if 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (compatible; GoPro2File/1.0)'

        try:
            r = method(url, timeout=timeout, **kwargs)

        except SSLError as err:
            log_to_callback(Tag.WARN, f"Zertifikat ungültig: {url}: {err!s} – versuche ohne Zertifikat (unsicher).")
            try:
                r = method(url, timeout=timeout, verify=False, **kwargs)
            except (ReadTimeout, RequestException) as err:
                log_to_callback(Tag.ERR, f"{error_message} (unsicher): {url}: {err!s}")
                return None

        except ReadTimeout as err:
            log_to_callback(Tag.ERR, f"{error_message}: {url}: {err!s}")
            return None
        except RequestException as err:
            log_to_callback(Tag.ERR, f"{error_message}: {err!s}")
            return None

        success_codes = (200, 201, 202) if method is post else (200, 201, 304)

        if r.status_code in success_codes:
            if json:
                try:
                    content = r.json()
                except ValueError as err:
                    log_to_callback(Tag.ERR, f"Ungültiges JSON bei {url}: {err!s}")
                    return None
            else:
                content = r.content

            # Rückgabe je nach Parameter
            if return_headers:
                return r.status_code, content, dict(r.headers)
            return r.status_code, content

        log_to_callback(Tag.ERR, f"{error_message}: HTTP {r.status_code} bei {url}")
        return None

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_content_from_url(
            url: str,
            error_message: str,
            timeout: int = 5,
            *,
            json: bool = False,
            return_headers: bool = False,
            **kwargs: Any
    ) -> Any | None:
        """
        Lädt Inhalte von einer URL herunter (GET-Anfrage).

        :param url: Ziel-URL.
        :param error_message: Fehlertext für Logausgabe.
        :param timeout: Timeout in Sekunden.
        :param json: Wenn True, wird JSON-Format erwartet.
        :param return_headers: Wenn True, gibt ein Tupel (status_code, content, headers) zurück.
        :param kwargs: Weitere Parameter für die requests-Methode.
        :return: (status_code, content) oder (status_code, content, headers) oder None bei Fehler
        """
        return HttpUtils._handle_request(get, url, error_message, timeout, json, return_headers, **kwargs)

    # --------------------------------------------------------------------------------
    @staticmethod
    def post_content_to_url(
            url: str,
            error_message: str,
            timeout: int = 5,
            *,
            json: bool = False,
            return_headers: bool = False,
            **kwargs: Any
    ) -> Any | None:
        """
        Sendet einen POST-Request an die URL.

        :param url: Ziel-URL.
        :param error_message: Fehlertext für Logausgabe.
        :param timeout: Timeout in Sekunden.
        :param json: Wenn True, wird JSON-Format erwartet.
        :param return_headers: Wenn True, gibt ein Tupel (status_code, content, headers) zurück.
        :param kwargs: Weitere Parameter für die requests-Methode.
        :return: (status_code, content) oder (status_code, content, headers) oder None bei Fehler
        """
        return HttpUtils._handle_request(post, url, error_message, timeout, json, return_headers, **kwargs)
