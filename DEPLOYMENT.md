# Panduan Deployment DD Shoes ke Coolify

Dokumen ini menjelaskan langkah-langkah lengkap untuk men-deploy aplikasi **DD Shoes** ke VPS menggunakan [Coolify](https://coolify.io) — platform self-hosted PaaS berbasis Docker.

---

## Daftar Isi

1. [Prerequisites](#1-prerequisites)
2. [Membuat Aplikasi di Coolify](#2-membuat-aplikasi-di-coolify)
3. [Environment Variables](#3-environment-variables)
4. [Persistent Volume untuk Media](#4-persistent-volume-untuk-media)
5. [Database PostgreSQL di Coolify](#5-database-postgresql-di-coolify)
6. [Deploy Pertama Kali](#6-deploy-pertama-kali)
7. [Verifikasi Deployment](#7-verifikasi-deployment)
8. [Health Check](#8-health-check)
9. [Development Lokal](#9-development-lokal)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

Sebelum memulai, pastikan kondisi berikut sudah terpenuhi:

- **VPS** dengan Coolify sudah terinstall dan dapat diakses melalui browser (biasanya di port `8000` atau `3000` tergantung konfigurasi)
- **PostgreSQL** tersedia — bisa dibuat sebagai service di dalam Coolify, atau menggunakan database eksternal
- **Repo Git** project DD Shoes dapat diakses secara publik (atau sudah dikonfigurasi SSH key di Coolify jika private)
- **Domain** (opsional, tapi direkomendasikan) — Coolify dapat generate subdomain otomatis jika tidak punya domain sendiri

---

## 2. Membuat Aplikasi di Coolify

Ikuti langkah-langkah berikut di dashboard Coolify:

1. Klik **New Resource** di sidebar atau halaman utama
2. Pilih **Public Git Repository** (atau **Private** jika repo private)
3. Paste URL repo Git, contoh:
   ```
   https://github.com/username/ddshoes
   ```
4. Pilih **branch** yang akan di-deploy (biasanya `main` atau `master`)
5. Pada bagian **Build Pack**, pilih **Dockerfile** — Coolify akan menggunakan `Dockerfile` yang ada di root repo
6. Pada bagian **Port**, isi dengan `8000` — ini adalah port yang diexpose oleh Gunicorn di dalam container
7. Klik **Save** atau **Continue**

> **Catatan:** Jangan deploy dulu sampai environment variables dan persistent volume sudah dikonfigurasi (lihat bagian 3 dan 4).

---

## 3. Environment Variables

Setelah aplikasi dibuat, buka tab **Environment Variables** di halaman aplikasi Coolify. Isi semua variabel berikut:

| Variabel | Wajib | Contoh Nilai | Keterangan |
|---|---|---|---|
| `SECRET_KEY` | ✅ Ya | `your-very-long-random-secret-key-here-minimum-50-chars` | Generate dengan: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | ✅ Ya | `False` | Harus `False` di production |
| `ALLOWED_HOSTS` | ✅ Ya | `yourdomain.com,www.yourdomain.com` | Domain/subdomain Coolify, pisahkan dengan koma tanpa spasi |
| `CSRF_TRUSTED_ORIGINS` | ✅ Ya | `https://yourdomain.com,https://www.yourdomain.com` | Harus pakai `https://`, pisahkan dengan koma |
| `DATABASE_URL` | ✅ Ya | `postgres://ddshoes_user:password@host:5432/ddshoes` | Connection string ke PostgreSQL (lihat bagian 5) |
| `MIDTRANS_CLIENT_KEY` | ✅ Ya | `Mid-client-xxxxxxxxxxxx` | Dari [dashboard Midtrans](https://dashboard.midtrans.com) → Settings → Access Keys |
| `MIDTRANS_SERVER_KEY` | ✅ Ya | `Mid-server-xxxxxxxxxxxx` | Dari dashboard Midtrans yang sama |
| `EMAIL_HOST_USER` | ✅ Ya | `your-email@gmail.com` | Akun Gmail untuk kirim email |
| `EMAIL_HOST_PASSWORD` | ✅ Ya | `xxxx-xxxx-xxxx-xxxx` | **App Password** Gmail, bukan password akun biasa. Buat di [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `KOMERCE_API_KEY` | ✅ Ya | `your-komerce-api-key` | Dari [app.komerce.id](https://app.komerce.id) → API Settings |
| `MEDIA_ROOT` | Opsional | `/app/media` | Sudah default ke `/app/media`, hanya ubah jika path volume berbeda |

Salin file `.env.example` di repo sebagai referensi lengkap dengan komentar penjelasan untuk setiap variabel.

---

## 4. Persistent Volume untuk Media

> ⚠️ **Bagian paling penting.** Tanpa persistent volume, semua foto produk dan file yang di-upload user akan **hilang setiap kali ada rebuild** karena container di-recreate dari scratch.

### Mengapa ini diperlukan?

Setiap kali Coolify melakukan deployment baru (misalnya karena ada push commit), container lama dihapus dan container baru dibuat dari image terbaru. Semua file yang tersimpan di dalam container (termasuk folder `/app/media/`) ikut terhapus. Persistent volume adalah storage Docker yang terpisah dari container — ia tetap ada meskipun container dihapus atau di-recreate.

### Cara Mengkonfigurasi di Coolify

1. Buka halaman aplikasi DD Shoes di Coolify
2. Klik tab **Storages** (atau **Persistent Storage**)
3. Klik **Add Storage** / **Add Volume**
4. Isi form sebagai berikut:
   - **Source Path (Host Path):** Kosongkan — biarkan Coolify yang membuat volume Docker secara otomatis
   - **Destination Path (Container Path):** `/app/media`
5. Klik **Save**
6. Klik **Redeploy** agar container baru berjalan dengan volume yang sudah ter-mount

### Verifikasi Volume Terpasang

Setelah redeploy, lihat logs container. Pada startup pertama dengan volume kosong, Anda akan melihat:

```
==> Checking media volume...
==> Media volume is empty — seeding from /app/media_seed/ ...
==> Seed complete.
```

Ini berarti foto produk default dari repo sudah disalin ke volume. Deployment berikutnya akan menampilkan:

```
==> Media volume already populated — skipping seed.
```

---

## 5. Database PostgreSQL di Coolify

### Membuat Service PostgreSQL di Coolify

1. Di Coolify, klik **New Resource**
2. Pilih **Database** → **PostgreSQL**
3. Isi nama database, username, dan password sesuai keinginan
4. Klik **Create** dan tunggu hingga service running

### Mendapatkan Connection String

1. Buka service PostgreSQL yang baru dibuat
2. Cari bagian **Connection** atau **Connection String**
3. Copy connection string dalam format:
   ```
   postgres://USERNAME:PASSWORD@HOST:PORT/DBNAME
   ```
4. Paste connection string tersebut sebagai nilai variabel `DATABASE_URL` di environment variables aplikasi DD Shoes (lihat bagian 3)

> **Catatan:** Jika PostgreSQL dan aplikasi berada dalam satu project/network Coolify, gunakan hostname internal (biasanya nama service). Jika database eksternal, gunakan IP atau domain publik.

---

## 6. Deploy Pertama Kali

Setelah semua konfigurasi selesai (environment variables, persistent volume, dan database), lakukan deploy:

1. Di halaman aplikasi Coolify, klik tombol **Deploy**
2. Buka tab **Logs** untuk memantau proses build dan startup
3. Proses build akan menjalankan `collectstatic` dan menyiapkan image
4. Setelah build selesai, container akan start dan menjalankan entrypoint script

### Output Startup yang Berhasil

Pada deployment pertama yang sukses, logs akan menampilkan:

```
==> Running database migrations...
Operations to perform:
  Apply all migrations: account, admin, auth, cart, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  ...
==> Checking media volume...
==> Media volume is empty — seeding from /app/media_seed/ ...
==> Seed complete.
==> Starting Gunicorn...
[INFO] Starting gunicorn 21.x.x
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: sync
[INFO] Booting worker with pid: ...
```

Jika Anda melihat output seperti di atas, deployment berhasil.

---

## 7. Verifikasi Deployment

Gunakan checklist berikut untuk memastikan deployment berjalan dengan benar:

- [ ] Buka URL aplikasi di browser — halaman beranda muncul tanpa error
- [ ] Foto produk tampil dengan benar (tidak ada gambar broken/kosong)
- [ ] Buka `/admin/` — halaman login admin Django muncul
- [ ] Login ke admin dengan superuser, coba upload foto baru lewat admin
- [ ] Lakukan push commit baru ke repo (trigger rebuild otomatis di Coolify)
- [ ] Setelah redeploy selesai, buka kembali URL aplikasi
- [ ] Verifikasi foto yang di-upload sebelumnya masih tampil (tidak hilang setelah rebuild)

---

## 8. Health Check

Dockerfile sudah mendefinisikan `HEALTHCHECK` yang secara otomatis dibaca oleh Coolify:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1
```

Artinya:
- Setiap **30 detik**, Docker mengirim request ke `http://localhost:8000/`
- Jika tidak ada respons dalam **10 detik**, dianggap gagal
- Container punya waktu **60 detik** untuk startup sebelum health check mulai
- Jika gagal **3 kali berturut-turut**, container ditandai sebagai **unhealthy**

Coolify membaca status health check ini secara otomatis. Jika container ditandai unhealthy, Coolify akan menampilkan status error pada dashboard dan Anda dapat melihat detail di tab Logs.

Tidak diperlukan konfigurasi tambahan di sisi Coolify untuk health check — cukup pastikan `Dockerfile` berisi instruksi `HEALTHCHECK` yang sudah ada.

---

## 9. Development Lokal

Untuk menjalankan aplikasi di mesin lokal:

1. Copy file `.env.example` menjadi `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit file `.env` dengan nilai yang sesuai untuk development:

   ```dotenv
   # Aktifkan debug mode untuk development
   DEBUG=True

   # Secret key bisa nilai acak apa saja untuk local
   SECRET_KEY=local-dev-secret-key-tidak-perlu-aman

   # Terima semua host di local
   ALLOWED_HOSTS=localhost,127.0.0.1

   # CSRF origins untuk local
   CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

   # Database lokal — pastikan PostgreSQL sudah berjalan
   DATABASE_URL=postgres://postgres:root@localhost:5432/ddshoes

   # Biarkan MEDIA_ROOT kosong atau hapus baris ini
   # Dengan DEBUG=True, aplikasi akan pakai BASE_DIR/media secara otomatis
   # MEDIA_ROOT=/app/media

   # Isi dengan nilai development / test jika diperlukan
   MIDTRANS_CLIENT_KEY=Mid-client-xxxxxxxxxxxx
   MIDTRANS_SERVER_KEY=Mid-server-xxxxxxxxxxxx
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
   KOMERCE_API_KEY=your-komerce-api-key
   ```

3. Install dependencies dan jalankan server:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

> **Catatan:** Di development lokal, `MEDIA_ROOT` default ke `BASE_DIR/media` (folder `media/` di root project). File media yang di-upload saat development tersimpan di sana dan tidak mempengaruhi production.

---

## 10. Troubleshooting

### Foto tidak tampil setelah deployment

**Gejala:** Halaman muncul tapi gambar broken atau kosong.

**Penyebab:** Persistent volume belum terpasang, atau terpasang ke path yang salah.

**Solusi:**
1. Buka Coolify → aplikasi DD Shoes → tab **Storages**
2. Pastikan ada entry dengan **Destination Path** `/app/media`
3. Jika belum ada, tambahkan (lihat bagian 4) lalu redeploy
4. Jika sudah ada, periksa logs — cari baris `Media volume is empty` atau `already populated`

---

### Error: `SECRET_KEY required` atau `KeyError: 'SECRET_KEY'`

**Gejala:** Container gagal start, logs menampilkan error `KeyError: 'SECRET_KEY'`.

**Solusi:** Set environment variable `SECRET_KEY` di Coolify dengan nilai yang panjang dan acak. Generate dengan:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

### Error: `DisallowedHost` atau `Invalid HTTP_HOST header`

**Gejala:** Browser menampilkan error 400, logs menampilkan `DisallowedHost`.

**Solusi:** Tambahkan domain Anda ke environment variable `ALLOWED_HOSTS` di Coolify:
```
yourdomain.com,www.yourdomain.com
```
Redeploy setelah mengubah env var.

---

### Error: `CSRF verification failed` saat login atau submit form

**Gejala:** Muncul halaman error "CSRF verification failed. Request aborted."

**Solusi:** Tambahkan domain HTTPS Anda ke environment variable `CSRF_TRUSTED_ORIGINS`:
```
https://yourdomain.com,https://www.yourdomain.com
```
Pastikan menggunakan prefix `https://`. Redeploy setelah mengubah env var.

---

### File media dari seed ada, tapi upload baru tidak tersimpan

**Gejala:** Foto produk default tampil, tapi foto yang di-upload lewat admin hilang setelah halaman di-refresh atau setelah redeploy.

**Penyebab:** Volume mungkin tidak ter-mount dengan benar — seed berjalan karena menyalin dari dalam image, tapi upload baru disimpan ke dalam container (bukan ke volume).

**Solusi:**
1. Pastikan Destination Path di Storages adalah `/app/media` (bukan `/app/media/` dengan trailing slash, meskipun biasanya tidak masalah)
2. Pastikan environment variable `MEDIA_ROOT` (jika diset) mengarah ke `/app/media`
3. Cek di logs apakah volume ter-mount: jalankan command `df -h` di terminal container Coolify dan cari entry untuk `/app/media`
4. Jika tetap bermasalah, hapus volume dan buat ulang, lalu redeploy

---

### Container terus restart (crash loop)

**Gejala:** Di Coolify, status container terus berubah menjadi "Restarting".

**Solusi:** Buka tab **Logs** di Coolify dan cari pesan error. Kemungkinan penyebab:
- `DATABASE_URL` salah atau database tidak dapat dijangkau — periksa koneksi database
- `SECRET_KEY` tidak disetel — lihat solusi di atas
- Migration gagal — periksa apakah skema database kompatibel dengan versi kode
