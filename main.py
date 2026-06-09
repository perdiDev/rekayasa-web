"""
============================================================
  Script Integrasi TheSportsDB API - Tugas II Rekayasa Web
  API Base URL : https://www.thesportsdb.com/api/v1/json/
  API Key Publik: 123 (tanpa registrasi)
============================================================
"""

import requests
import time
import json

BASE_URL = "https://www.thesportsdb.com/api/v1/json/123"


# ── Helper ────────────────────────────────────────────────────────────────────

def _get(endpoint: str, params: dict = None) -> dict:
    """
    Melakukan HTTP GET ke endpoint TheSportsDB.
    Mengembalikan dict berisi: status_code, data (JSON), elapsed_ms.
    """
    url = f"{BASE_URL}/{endpoint}"
    start = time.time()
    try:
        response = requests.get(url, params=params, timeout=10)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        try:
            data = response.json()
        except Exception:
            data = None
        return {
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
            "data": data,
            "url": response.url,
        }
    except requests.exceptions.Timeout:
        return {"status_code": 408, "elapsed_ms": 10000, "data": None, "url": url}
    except requests.exceptions.ConnectionError:
        return {"status_code": 503, "elapsed_ms": 0, "data": None, "url": url}


# ── Endpoint Functions ────────────────────────────────────────────────────────

def search_team(team_name: str) -> dict:
    """
    Mencari tim sepak bola berdasarkan nama.
    Endpoint: GET /searchteams.php?t={team_name}
    """
    return _get("searchteams.php", {"t": team_name})


def get_next_events(team_id: int) -> dict:
    """
    Mengambil jadwal pertandingan berikutnya dari suatu tim.
    Endpoint: GET /eventsnext.php?id={team_id}
    """
    return _get("eventsnext.php", {"id": team_id})


def get_league_table(league_id: int, season: str = None) -> dict:
    """
    Mengambil tabel klasemen liga.
    Endpoint: GET /lookuptable.php?l={league_id}&s={season}
    """
    params = {"l": league_id}
    if season:
        params["s"] = season
    return _get("lookuptable.php", params)


def get_last_events(team_id: int) -> dict:
    """
    Mengambil hasil pertandingan terakhir suatu tim.
    Endpoint: GET /eventslast.php?id={team_id}
    """
    return _get("eventslast.php", {"id": team_id})


def search_player(player_name: str) -> dict:
    """
    Mencari pemain berdasarkan nama.
    Endpoint: GET /searchplayers.php?p={player_name}
    """
    return _get("searchplayers.php", {"p": player_name})


# ── Demo / Manual Test ────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 60)
    print("  TheSportsDB API - Integration Test")
    print("=" * 60)

    tests = [
        ("T01 - Cari tim valid: Arsenal",
         lambda: search_team("Arsenal")),
        ("T02 - Cari tim tidak ada: Tim_XYZ_Tidak_Ada",
         lambda: search_team("Tim_XYZ_Tidak_Ada")),
        ("T03 - Cari tim, parameter kosong (string kosong)",
         lambda: search_team("")),
        ("T04 - Jadwal tim valid (id=133613, Man City)",
         lambda: get_next_events(133613)),
        ("T05 - Jadwal tim, ID tidak valid (id=0)",
         lambda: get_next_events(0)),
        ("T06 - Klasemen EPL (id=4328, musim 2023-2024)",
         lambda: get_league_table(4328, "2023-2024")),
        ("T07 - Klasemen, ID liga salah (id=9999999)",
         lambda: get_league_table(9999999)),
    ]

    for label, fn in tests:
        print(f"\n{label}")
        result = fn()
        print(f"  Status Code : {result['status_code']}")
        print(f"  Elapsed     : {result['elapsed_ms']} ms")
        print(f"  URL         : {result['url']}")
        if result["data"]:
            # Tampilkan ringkasan data
            keys = list(result["data"].keys())
            print(f"  Data Keys   : {keys}")
            # Cek apakah data null/kosong
            first_key = keys[0] if keys else None
            val = result["data"].get(first_key) if first_key else None
            if val is None:
                print(f"  Data Value  : null (data tidak ditemukan)")
            elif isinstance(val, list):
                print(f"  Records     : {len(val)} item(s)")
        else:
            print(f"  Data        : (tidak ada / error)")

    print("\n" + "=" * 60)
    print("  Selesai.")
    print("=" * 60)
