# Sistem Stok Barang (Website)

Aplikasi web sederhana untuk mengelola stok barang menggunakan Python, Flask, dan SQLite.

## Fitur
- Melihat daftar barang dan status stok (Aman, Menipis, Habis).
- Menambahkan barang baru.
- Mencatat barang masuk dan barang keluar.
- Mencegah stok menjadi negatif.
- Menghapus barang.
- Menyimpan data secara lokal di file `stok_barang.db`.

## Cara menjalankan di Windows

1. Pastikan Python 3 sudah terpasang.
2. Ekstrak ZIP ini.
3. Buka CMD atau Terminal di folder `sistem_stok_website`.
4. (Opsional tetapi disarankan) Buat virtual environment:

   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```

5. Install Flask:

   ```bash
   pip install -r requirements.txt
   ```

6. Jalankan aplikasi:

   ```bash
   python app.py
   ```

7. Buka browser dan kunjungi:

   `http://127.0.0.1:5000`

Tekan `Ctrl + C` di terminal untuk menghentikan server.

## Catatan
- Database `stok_barang.db` dibuat otomatis saat aplikasi pertama kali dijalankan.
- Dua data contoh (Kertas A4 dan Pulpen) hanya dimasukkan ketika database masih kosong.
- Aplikasi ini berjalan secara lokal di komputer. Agar bisa diakses orang lain melalui internet, aplikasi perlu di-deploy ke hosting/server dan konfigurasi keamanan perlu diperkuat.
- Sebelum digunakan untuk produksi, ganti `app.secret_key` di `app.py` dengan secret key acak dan matikan `debug=True`.
