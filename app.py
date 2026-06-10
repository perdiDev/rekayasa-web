"""
============================================================
  TheSportsDB CLI — Tugas II Rekayasa Web
  Penggunaan:
    python main.py --tim Arsenal
    python main.py --jadwal 133604
    python main.py --jadwal 133604 --lalu
    python main.py --klasemen
    python main.py --klasemen --liga "La Liga" --musim 2022-2023
    python main.py --pemain "Erling Haaland"
    python main.py --bantuan
============================================================
"""

import argparse
import sys
import time
import requests

BASE_URL = "https://www.thesportsdb.com/api/v1/json/123"

LIGA_TERSEDIA = {
    "premier league"  : ("4328", "English Premier League"),
    "epl"             : ("4328", "English Premier League"),
    "la liga"         : ("4332", "La Liga"),
    "bundesliga"      : ("4331", "Bundesliga"),
    "serie a"         : ("4335", "Serie A"),
    "ligue 1"         : ("4334", "Ligue 1"),
    "liga indonesia"  : ("4643", "Liga Indonesia"),
    "liga 1"          : ("4643", "Liga Indonesia"),
    "eredivisie"      : ("4337", "Eredivisie"),
    "primeira liga"   : ("4344", "Primeira Liga"),
}

# ── Warna terminal (ANSI) ─────────────────────────────────────────────────────
class W:
    HIJAU   = "\033[92m"
    KUNING  = "\033[93m"
    MERAH   = "\033[91m"
    BIRU    = "\033[94m"
    TEBAL   = "\033[1m"
    REDUP   = "\033[2m"
    RESET   = "\033[0m"

def hijau(t):  return f"{W.HIJAU}{t}{W.RESET}"
def kuning(t): return f"{W.KUNING}{t}{W.RESET}"
def merah(t):  return f"{W.MERAH}{t}{W.RESET}"
def biru(t):   return f"{W.BIRU}{t}{W.RESET}"
def tebal(t):  return f"{W.TEBAL}{t}{W.RESET}"
def redup(t):  return f"{W.REDUP}{t}{W.RESET}"

def garis(karakter="─", lebar=60):
    print(redup(karakter * lebar))

def header(judul):
    garis("═")
    print(tebal(f"  {judul}"))
    garis("═")

# ── HTTP helper ───────────────────────────────────────────────────────────────
def get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    print(redup(f"  ↗  GET /{endpoint}"), end="", flush=True)
    mulai = time.time()
    try:
        resp = requests.get(url, params=params, timeout=10)
        ms = round((time.time() - mulai) * 1000)
        print(redup(f"  [{ms}ms]  HTTP {resp.status_code}"))
        resp.raise_for_status()

        # Tangani response kosong (API kadang mengembalikan body kosong)
        if not resp.text or not resp.text.strip():
            return {}

        try:
            return resp.json()
        except ValueError:
            # Response bukan JSON yang valid
            print(kuning(f"  ⚠ Response bukan JSON (panjang: {len(resp.text)} karakter)"))
            return {}

    except requests.exceptions.Timeout:
        print(merah("  [TIMEOUT]"))
        print(merah("  ✗ Koneksi timeout. Coba lagi."))
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(merah("  [ERROR]"))
        print(merah("  ✗ Tidak bisa terhubung ke internet. Periksa koneksi."))
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(merah(f"  ✗ HTTP Error: {e}"))
        sys.exit(1)

# ── Fitur 1: Cari Tim ─────────────────────────────────────────────────────────
def cari_tim(nama):
    header(f"Cari Tim: {nama}")
    data = get("searchteams.php", {"t": nama})

    if not data.get("teams"):
        print(kuning(f"\n  Tidak ada tim ditemukan untuk '{nama}'."))
        print(redup("  Tips: coba nama lain, mis. Arsenal, Barcelona, Juventus"))
        return

    tim_list = data["teams"]
    print(f"\n  Ditemukan {tebal(str(len(tim_list)))} tim:\n")

    for i, t in enumerate(tim_list, 1):
        print(f"  {tebal(str(i))}. {hijau(tebal(t.get('strTeam','—')))}")
        baris = [
            ("ID Tim",    t.get("idTeam", "—")),
            ("Liga",      t.get("strLeague", "—")),
            ("Negara",    t.get("strCountry", "—")),
            ("Stadion",   t.get("strStadium", "—")),
            ("Berdiri",   t.get("intFormedYear", "—")),
            ("Singkatan", t.get("strTeamShort", "—")),
        ]
        for label, val in baris:
            print(f"     {redup(label+':'): <22} {val}")

        deskripsi = t.get("strDescriptionEN") or t.get("strDescriptionID")
        if deskripsi:
            potong = deskripsi[:160].rsplit(" ", 1)[0]
            print(f"     {redup('Deskripsi:'): <22} {potong}...")

        if i < len(tim_list):
            garis("·", 50)

    print()
    print(redup(f"  Tip: gunakan ID Tim di atas untuk melihat jadwal →"))
    print(redup(f"  python main.py --jadwal {tim_list[0].get('idTeam','')}"))

# ── Fitur 2: Jadwal Tim ───────────────────────────────────────────────────────
def jadwal_tim(id_tim, lalu=False):
    jenis = "Terakhir" if lalu else "Mendatang"
    header(f"Jadwal {jenis} — Tim ID: {id_tim}")

    endpoint = "eventslast.php" if lalu else "eventsnext.php"
    data = get(endpoint, {"id": id_tim})
    events = data.get("events")

    if not events:
        print(kuning(f"\n  Tidak ada jadwal {jenis.lower()} untuk ID tim '{id_tim}'."))
        print(redup("  Pastikan ID tim benar. Gunakan --tim untuk mencari ID."))
        return

    print(f"\n  {tebal(str(len(events)))} pertandingan {jenis.lower()}:\n")

    for ev in events:
        skor = ""
        if lalu and ev.get("intHomeScore") is not None:
            skor = f"  {hijau(tebal(str(ev['intHomeScore'])))}" \
                   f" - " \
                   f"{hijau(tebal(str(ev['intAwayScore'])))}"

        print(f"  {tebal(ev.get('strEvent','—'))}{skor}")
        baris = [
            ("Tanggal", ev.get("dateEvent", "—")),
            ("Waktu",   ev.get("strTime",  "—")),
            ("Venue",   ev.get("strVenue", "—")),
            ("Liga",    ev.get("strLeague","—")),
            ("Status",  ev.get("strStatus","—")),
        ]
        for label, val in baris:
            print(f"     {redup(label+':'): <22} {val}")
        garis("·", 50)

    print()

# ── Fitur 3: Klasemen Liga ────────────────────────────────────────────────────
def klasemen(nama_liga="premier league", musim=None):
    nama_lower = nama_liga.lower().strip()
    if nama_lower not in LIGA_TERSEDIA:
        print(merah(f"\n  ✗ Liga '{nama_liga}' tidak dikenal."))
        print(kuning("  Liga yang tersedia:"))
        for k, (_, nama) in LIGA_TERSEDIA.items():
            if k == nama.lower(): continue  # skip duplikat
            print(f"    • {k}  →  {nama}")
        sys.exit(1)

    id_liga, nama_resmi = LIGA_TERSEDIA[nama_lower]
    judul = f"Klasemen {nama_resmi}"
    if musim:
        judul += f" — Musim {musim}"
    header(judul)

    params = {"l": id_liga}
    if musim:
        params["s"] = musim
    data = get("lookuptable.php", params)
    tabel = data.get("table")

    if not tabel:
        print(kuning(f"\n  Data klasemen tidak tersedia untuk liga ini."))
        print(redup(f"  Kemungkinan penyebab:"))
        print(redup(f"    • Musim belum tersedia di TheSportsDB"))
        print(redup(f"    • Coba musim lain: --musim 2022-2023  atau  --musim 2021-2022"))
        print(redup(f"    • ID liga ({id_liga}) mungkin belum didukung penuh oleh API"))
        return

    print()
    # Header tabel
    print(
        f"  {'#': <4}"
        f"{'Tim': <28}"
        f"{'M': >4}"
        f"{'W': >4}"
        f"{'D': >4}"
        f"{'L': >4}"
        f"{'GF': >5}"
        f"{'GA': >5}"
        f"{'GD': >5}"
        f"  {'Pts': >4}"
    )
    garis("─", 72)

    for baris in tabel:
        rank  = int(baris.get("intRank",   0))
        nama  = baris.get("strTeam",       "—")[:26]
        main  = baris.get("intPlayed",     0)
        menang= baris.get("intWin",        0)
        seri  = baris.get("intDraw",       0)
        kalah = baris.get("intLoss",       0)
        gf    = baris.get("intGoalsFor",   0)
        ga    = baris.get("intGoalsAgainst",0)
        gd    = baris.get("intGoalDifference",0)
        pts   = baris.get("intPoints",     0)

        # Warna rank
        if rank == 1:
            rank_str = hijau(tebal(f"{rank: <3}"))
            pts_str  = hijau(tebal(f"{pts: >4}"))
        elif rank <= 4:
            rank_str = biru(f"{rank: <3}")
            pts_str  = biru(f"{pts: >4}")
        elif rank >= len(tabel) - 2:
            rank_str = merah(f"{rank: <3}")
            pts_str  = merah(f"{pts: >4}")
        else:
            rank_str = f"{rank: <3}"
            pts_str  = f"{pts: >4}"

        print(
            f"  {rank_str} "
            f"{nama: <28}"
            f"{main: >4}"
            f"{menang: >4}"
            f"{seri: >4}"
            f"{kalah: >4}"
            f"{gf: >5}"
            f"{ga: >5}"
            f"{gd: >5}"
            f"  {pts_str}"
        )

    print()
    print(redup("  M=Main  W=Menang  D=Seri  L=Kalah  GF=Gol Masuk  GA=Gol Keluar"))
    print(redup(f"  {hijau('■')} Juara  {biru('■')} Liga Champions  {merah('■')} Degradasi"))
    print()

# ── Fitur 4: Cari Pemain ──────────────────────────────────────────────────────
def cari_pemain(nama):
    header(f"Cari Pemain: {nama}")
    data = get("searchplayers.php", {"p": nama})
    pemain_list = data.get("player")

    if not pemain_list:
        print(kuning(f"\n  Tidak ada pemain ditemukan untuk '{nama}'."))
        print(redup("  Coba nama lain, mis. 'Messi', 'Ronaldo', 'Haaland'"))
        return

    print(f"\n  Ditemukan {tebal(str(len(pemain_list)))} pemain:\n")
    for i, p in enumerate(pemain_list[:8], 1):
        print(f"  {tebal(str(i))}. {hijau(tebal(p.get('strPlayer','—')))}")
        baris = [
            ("Tim",          p.get("strTeam",        "—")),
            ("Posisi",       p.get("strPosition",    "—")),
            ("Kebangsaan",   p.get("strNationality",  "—")),
            ("Tgl Lahir",    p.get("dateBorn",        "—")),
            ("Tinggi",       p.get("strHeight",       "—")),
            ("Berat",        p.get("strWeight",       "—")),
        ]
        for label, val in baris:
            print(f"     {redup(label+':'): <22} {val}")
        if i < min(len(pemain_list), 8):
            garis("·", 50)
    print()

# ── Argparse & main ───────────────────────────────────────────────────────────
def buat_parser():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="TheSportsDB CLI — data sepak bola langsung dari terminal",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    parser.add_argument(
        "--tim", metavar="NAMA",
        help="Cari informasi tim\n  Contoh: --tim Arsenal"
    )
    parser.add_argument(
        "--jadwal", metavar="ID_TIM",
        help="Jadwal pertandingan tim (gunakan ID dari --tim)\n  Contoh: --jadwal 133604"
    )
    parser.add_argument(
        "--lalu", action="store_true",
        help="Tampilkan pertandingan terakhir (dipakai bersama --jadwal)"
    )
    parser.add_argument(
        "--klasemen", action="store_true",
        help="Tampilkan klasemen liga\n  Contoh: --klasemen --liga 'La Liga'"
    )
    parser.add_argument(
        "--liga", metavar="NAMA", default="premier league",
        help="Liga untuk klasemen (default: premier league)\n"
             "  Pilihan: 'premier league', 'la liga', 'bundesliga',\n"
             "           'serie a', 'ligue 1', 'liga indonesia',\n"
             "           'eredivisie', 'primeira liga'"
    )
    parser.add_argument(
        "--musim", metavar="MUSIM", default=None,
        help="Musim untuk klasemen (default: terkini)\n  Contoh: --musim 2023-2024"
    )
    parser.add_argument(
        "--pemain", metavar="NAMA",
        help="Cari informasi pemain\n  Contoh: --pemain 'Erling Haaland'"
    )
    parser.add_argument(
        "--bantuan", "-h", "--help",
        action="store_true",
        help="Tampilkan bantuan ini"
    )
    return parser

def tampilkan_bantuan():
    print(f"""
{tebal('TheSportsDB CLI')}  {redup('— Tugas II Rekayasa Web')}
{redup('API publik, tanpa login, key: 123')}

{tebal('PENGGUNAAN:')}
  python main.py [perintah] [opsi]

{tebal('PERINTAH:')}
  {hijau('--tim')} NAMA          Cari informasi tim
  {hijau('--jadwal')} ID_TIM      Jadwal mendatang tim
  {hijau('--jadwal')} ID --lalu   Pertandingan terakhir
  {hijau('--klasemen')}           Klasemen liga
  {hijau('--pemain')} NAMA        Cari pemain

{tebal('OPSI KLASEMEN:')}
  {kuning('--liga')} NAMA          Pilih liga (default: premier league)
  {kuning('--musim')} XXXX-XXXX    Filter musim tertentu

{tebal('CONTOH:')}
  python main.py --tim Arsenal
  python main.py --tim "Manchester United"
  python main.py --jadwal 133604
  python main.py --jadwal 133604 --lalu
  python main.py --klasemen
  python main.py --klasemen --liga "la liga" --musim 2023-2024
  python main.py --klasemen --liga bundesliga
  python main.py --klasemen --liga "liga indonesia"
  python main.py --pemain "Erling Haaland"
  python main.py --pemain Messi

{tebal('ID TIM POPULER:')}
  {redup('133604')} Arsenal          {redup('133613')} Manchester City
  {redup('133612')} Chelsea          {redup('133616')} Liverpool
  {redup('133739')} Real Madrid      {redup('133600')} Barcelona
  {redup('133581')} Juventus         {redup('133919')} PSG
""")

def main():
    parser = buat_parser()
    args = parser.parse_args()

    if args.bantuan or len(sys.argv) == 1:
        tampilkan_bantuan()
        return

    if args.tim:
        cari_tim(args.tim)
    elif args.jadwal:
        jadwal_tim(args.jadwal, lalu=args.lalu)
    elif args.klasemen:
        klasemen(nama_liga=args.liga, musim=args.musim)
    elif args.pemain:
        cari_pemain(args.pemain)
    else:
        print(merah("  ✗ Perintah tidak dikenal."))
        tampilkan_bantuan()

if __name__ == "__main__":
    main()
