# Problem Monitoring Dashboard — Streamlit

Dashboard ini baca data langsung dari Google Sheets. Begitu ada yang edit
cell di sheet, dashboard akan ikut update (auto-refresh tiap 5 menit, atau
langsung kalau orangnya reload halaman).

## Langkah 1 — Siapkan Google Sheets

1. Buat 1 Google Sheet dengan kolom-kolom ini di baris pertama (nama boleh
   huruf besar/kecil bebas, nanti dinormalisasi otomatis):
   `bulan, customer, item, production_factory, problem, pic_1, pic_2, pic_3,
   analisa, action_plan, root_cause, problem_category`
2. Isi data kamu (boleh copy-paste dari file Excel yang sudah ada).
3. Klik **File > Share > Publish to web**.
4. Di dialog itu, pilih sheet yang benar, format **Comma-separated values (.csv)**,
   lalu klik **Publish**. Google akan kasih URL seperti:
   `https://docs.google.com/spreadsheets/d/e/2PACX-xxxxx/pub?output=csv`
5. Copy URL itu.

   Alternatif (kalau Publish to web di-disable oleh admin workspace), pakai
   sheet yang di-share "Anyone with the link can view" lalu pakai format:
   `https://docs.google.com/spreadsheets/d/<SHEET_ID>/gviz/tq?tqx=out:csv&sheet=<NAMA_SHEET>`

## Langkah 2 — Sambungkan ke app.py

Buka `app.py`, cari baris:
```python
SHEET_CSV_URL = "PASTE_URL_CSV_GOOGLE_SHEETS_DI_SINI"
```
Ganti dengan URL CSV dari Langkah 1.

## Langkah 3 — Push ke GitHub

1. Buat repo baru di GitHub (boleh public atau private), misal `problem-monitoring-dashboard`.
2. Upload 3 file ini ke repo: `app.py`, `requirements.txt`, `README.md`.

## Langkah 4 — Deploy ke Streamlit Community Cloud (gratis)

1. Buka https://share.streamlit.io dan login pakai akun GitHub kamu.
2. Klik **New app**.
3. Pilih repo, branch (`main`), dan file utama `app.py`.
4. Klik **Deploy**.
5. Setelah selesai build (1–2 menit), kamu akan dapat URL publik seperti:
   `https://problem-monitoring-dashboard.streamlit.app`
6. Link ini bisa dibagikan ke siapa saja — tidak perlu login untuk melihat
   dashboard-nya.

## Update data selanjutnya

Tim tinggal edit langsung di Google Sheets. Dashboard akan otomatis
menampilkan data terbaru dalam waktu maksimal 5 menit (bisa dipercepat
dengan reload halaman, karena cache di `app.py` pakai `ttl=300` detik).

## Kalau mau sambungkan ke database (bukan Google Sheets)

Ganti fungsi `load_data()` di `app.py` dengan query lewat `sqlalchemy` /
`psycopg2` ke database yang sama dengan yang dipakai Metabase, simpan
credential-nya di **Streamlit Cloud > App settings > Secrets** (jangan
ditulis langsung di kode).
