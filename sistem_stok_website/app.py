from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "ganti-dengan-secret-key-acak"
DB_PATH = Path(__file__).with_name("stok_barang.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode TEXT NOT NULL UNIQUE,
                nama TEXT NOT NULL,
                stok INTEGER NOT NULL DEFAULT 0 CHECK (stok >= 0),
                stok_min INTEGER NOT NULL DEFAULT 0 CHECK (stok_min >= 0)
            )
        """)
        # Data contoh dimasukkan hanya saat tabel masih kosong.
        total = conn.execute("SELECT COUNT(*) FROM barang").fetchone()[0]
        if total == 0:
            conn.executemany(
                "INSERT INTO barang (kode, nama, stok, stok_min) VALUES (?, ?, ?, ?)",
                [
                    ("B01", "Kertas A4", 15, 5),
                    ("B02", "Pulpen", 3, 5),
                ],
            )


def status_stok(barang):
    if barang["stok"] == 0:
        return "Habis"
    if barang["stok"] <= barang["stok_min"]:
        return "Menipis"
    return "Aman"


@app.route("/")
def index():
    with get_db() as conn:
        barang = conn.execute(
            "SELECT * FROM barang ORDER BY kode COLLATE NOCASE"
        ).fetchall()
    daftar = [dict(row) for row in barang]
    for item in daftar:
        item["status"] = status_stok(item)

    total_barang = len(daftar)
    total_stok = sum(item["stok"] for item in daftar)
    stok_menipis = sum(1 for item in daftar if item["status"] == "Menipis")
    stok_habis = sum(1 for item in daftar if item["status"] == "Habis")

    return render_template(
        "index.html",
        barang=daftar,
        total_barang=total_barang,
        total_stok=total_stok,
        stok_menipis=stok_menipis,
        stok_habis=stok_habis,
    )


@app.route("/tambah", methods=["POST"])
def tambah_barang():
    kode = request.form.get("kode", "").strip().upper()
    nama = request.form.get("nama", "").strip()

    try:
        stok = int(request.form.get("stok", ""))
        stok_min = int(request.form.get("stok_min", ""))
    except ValueError:
        flash("Stok dan batas minimum harus berupa angka bulat.", "error")
        return redirect(url_for("index"))

    if not kode or not nama:
        flash("Kode dan nama barang wajib diisi.", "error")
    elif stok < 0 or stok_min < 0:
        flash("Stok tidak boleh bernilai negatif.", "error")
    else:
        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO barang (kode, nama, stok, stok_min) VALUES (?, ?, ?, ?)",
                    (kode, nama, stok, stok_min),
                )
            flash(f"Barang {nama} berhasil ditambahkan.", "success")
        except sqlite3.IntegrityError:
            flash(f"Kode barang {kode} sudah digunakan.", "error")

    return redirect(url_for("index"))


@app.route("/transaksi", methods=["POST"])
def transaksi():
    kode = request.form.get("kode", "").strip().upper()
    jenis = request.form.get("jenis", "")
    try:
        jumlah = int(request.form.get("jumlah", ""))
    except ValueError:
        flash("Jumlah transaksi harus berupa angka bulat.", "error")
        return redirect(url_for("index"))

    if jenis not in ("masuk", "keluar"):
        flash("Jenis transaksi tidak valid.", "error")
        return redirect(url_for("index"))
    if jumlah <= 0:
        flash("Jumlah transaksi harus lebih dari 0.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        barang = conn.execute(
            "SELECT * FROM barang WHERE kode = ?", (kode,)
        ).fetchone()

        if barang is None:
            flash("Barang tidak ditemukan.", "error")
        elif jenis == "masuk":
            conn.execute(
                "UPDATE barang SET stok = stok + ? WHERE kode = ?",
                (jumlah, kode),
            )
            flash(f"Stok {barang['nama']} bertambah {jumlah}.", "success")
        elif barang["stok"] >= jumlah:
            conn.execute(
                "UPDATE barang SET stok = stok - ? WHERE kode = ?",
                (jumlah, kode),
            )
            flash(f"Stok {barang['nama']} berkurang {jumlah}.", "success")
        else:
            flash(
                f"Stok tidak mencukupi. Stok {barang['nama']} saat ini {barang['stok']}.",
                "error",
            )

    return redirect(url_for("index"))


@app.route("/hapus/<int:barang_id>", methods=["POST"])
def hapus_barang(barang_id):
    with get_db() as conn:
        barang = conn.execute(
            "SELECT nama FROM barang WHERE id = ?", (barang_id,)
        ).fetchone()
        if barang:
            conn.execute("DELETE FROM barang WHERE id = ?", (barang_id,))
            flash(f"Barang {barang['nama']} berhasil dihapus.", "success")
        else:
            flash("Barang tidak ditemukan.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
