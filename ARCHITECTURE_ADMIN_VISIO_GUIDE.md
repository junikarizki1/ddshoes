# Panduan Arsitektur Dashboard Admin DD Shoes — Visio Guide

Dokumen ini berisi deskripsi teks diagram arsitektur **sisi Admin** beserta panduan membuat ulangnya di Microsoft Visio, mengikuti format gambar referensi (seperti diagram Laravel Blade yang dikirimkan).

---

## BAGIAN 1 — DESKRIPSI TEKS DIAGRAM ADMIN

---

### AKTOR (sisi kiri, di luar kotak utama)

Dua elemen di sebelah kiri kanvas, di luar kotak besar:

1. **Web Browser** — kotak persegi panjang kecil
2. **Admin** — ikon orang/stick figure di bawah Web Browser

Keduanya dihubungkan panah ke kanan menuju kotak utama Django Admin Project.

---

### KOTAK BESAR UTAMA — "Dashboard Admin DD Shoes Store (Django Admin + Jazzmin)"

Ini adalah kotak terluar berwarna **hijau muda** (mengikuti warna gambar referensi untuk bagian Admin). Di dalamnya terdapat seluruh komponen admin.

**Judul kotak:** `Dashboard Admin DD Shoes Store (Django Admin + Jazzmin)`

---

#### BAGIAN ATAS DALAM KOTAK UTAMA — Alur Routing

Tiga kotak berurutan dari kiri ke kanan, dihubungkan panah:

**Kotak 1 — Global Layout Admin**
- Label: `Global Layout Admin`
- Sub-label: `(base_site.html / Jazzmin Theme)`
- Posisi: kiri atas dalam kotak besar
- Warna: merah muda muda (`#FFD6D6`) — seperti di gambar referensi
- Catatan: Template master admin, berisi sidebar Jazzmin, navbar atas, footer

**Kotak 2 — Admin Routing**
- Label: `Admin Routing`
- Sub-label: `(ddshoes/urls.py — Prefix /admin/)`
- Posisi: di kanan Kotak 1, dihubungkan panah dari Web Browser
- Warna: putih/abu muda
- Route: `/admin/` → Django Admin, `/admin/store/`, `/admin/order/`, `/admin/account/`

**Kotak 3 — Admin Pages**
- Label: `Admin Pages`
- Sub-label: `(Django Admin Views)`
- Posisi: di kanan Admin Routing
- Warna: putih/abu muda
- Simpul tengah yang menyebar ke Fitur & Komponen Admin dan ke Admin Parts

**Kotak 4 — Admin Parts**
- Label: `Admin Parts`
- Sub-label: `(Sidebar, Navbar, Footer — Jazzmin)`
- Posisi: di kanan Admin Pages
- Warna: putih/abu muda
- Berisi: sidebar navigasi Jazzmin, breadcrumbs, header topbar

Hubungkan semua dengan panah kanan.

---

#### KOTAK DALAM — "Fitur & Komponen Admin" (kotak biru/hijau muda besar)

Di bawah alur routing, di dalam kotak utama, terdapat satu kotak besar berlabel **"Fitur & Komponen Admin"** dengan border putus-putus. Di dalamnya tersusun grid 3 kolom.

**Kolom Kiri:**

| No | Label Kotak |
|----|------------|
| 1 | Autentikasi (Login Role Admin / Staff) |
| 2 | Kelola Master Produk (Tambah, Edit, Hapus Produk + Gallery inline) |
| 3 | Kelola Kategori & Brand (dengan thumbnail preview) |
| 4 | Kelola Pengguna (User & Konsumen — foto, ukuran sepatu, loyalitas) |
| 5 | Kelola Alamat User (Buku Alamat Multi-level Wilayah) |

**Kolom Tengah:**

| No | Label Kotak |
|----|------------|
| 1 | Dashboard Analitik (Grafik Penjualan, Omzet, Filter Periode) |
| 2 | Kelola Pesanan (Status: New → Accepted → Completed / Cancelled) |
| 3 | Kelola Retur Produk (Pending → Approved → Refunded / Rejected) |
| 4 | Kelola Voucher / Kupon (Loyalty LOYAL- & Manual) |
| 5 | Pengiriman (Input Resi → Trigger Email Otomatis ke Konsumen) |

**Kolom Kanan:**

| No | Label Kotak |
|----|------------|
| 1 | Dashboard Statistik Pesanan (Pesanan Baru, Siap Kirim, Dikirim, Selesai) |
| 2 | Laporan & Grafik (Brand Terlaris, Kategori Terlaris, 5 Produk Terlaris) |
| 3 | Analitik User (Registrasi User, User Interest / Minat Produk) |
| 4 | Analitik Voucher (Status Dipakai/Belum, Total Diskon Diberikan) |
| 5 | Manajemen Ulasan (Rating 1-5, Tampilkan/Sembunyikan, Filter Ulasan) |

---

#### KOTAK "Utilities, Scripts & Styling" (kotak merah muda kecil)

Di dalam kotak utama, di bawah Fitur & Komponen. Berisi 4 kotak kecil (2×2):

| Posisi | Isi |
|--------|-----|
| Kiri atas | Bootstrap 5.3 (Grid / Theme — via Jazzmin) |
| Kanan atas | Admin Theme CSS (Jazzmin flatly, dark sidebar) |
| Kiri bawah | jQuery (AJAX & DOM — via Jazzmin bundle) |
| Kanan bawah | Chart.js (Grafik Data — Sales, Brand, Rating, dll.) |

---

#### KOTAK "Metode Rendering" (pojok kanan atas, di LUAR kotak utama)

Berisi 2 kotak kecil vertikal:

| Kotak | Isi |
|-------|-----|
| Atas | Client-Side Interactivity (AJAX & JS) — Filter periode dashboard, update status inline, print grafik |
| Bawah | Server-Side Rendering / SSR (Diproses Django Admin + Jazzmin Template Engine) |

---

### KOTAK DI KANAN LUAR — "Admin Controller (Views + Models)"

Di sebelah kanan kotak utama, posisi tengah. Dihubungkan panah dari AJAX dan dari Admin Pages.

- Label: `Admin Controller`
- Sub-label baris 2: `(Django Admin Views — Logika Bisnis)`
- Sub-label baris 3: `store · order · account`
- Warna: putih, border abu gelap, shadow ringan

Panah dari Controller ke bawah menuju:

1. **Database** — simbol silinder, label: `Database PostgreSQL (Prod) / SQLite (Dev)`
2. **Layanan Eksternal** — kotak kuning (lihat di bawah)

---

### KOTAK DI KANAN — "Layanan Eksternal" (kotak kuning)

Di bawah atau di samping Admin Controller. Berisi 2 kotak kecil:

| Kotak | Isi |
|-------|-----|
| 1 | Midtrans — Sinkronisasi Status Pembayaran (CoreApi polling) |
| 2 | Komerce / RajaOngkir — Data Wilayah & Ongkir (untuk input manual admin) |

Catatan: Gmail SMTP terhubung lewat signal otomatis (bukan dari Admin Panel langsung), sehingga bisa ditampilkan sebagai kotak kecil terpisah atau sub-bagian di Layanan Eksternal.

---

### PANAH-PANAH KONEKSI ANTAR KOMPONEN

| Dari | Ke | Label Panah |
|------|-----|-------------|
| Admin (orang) | Web Browser | HTTP Request |
| Web Browser | Admin Routing | HTTP Request |
| Admin Routing | Admin Pages | routing /admin/ |
| Admin Pages | Admin Parts | include Jazzmin |
| Admin Pages | Fitur & Komponen Admin | render views |
| Fitur & Komponen | AJAX (di Metode Rendering) | request dinamis |
| AJAX | Admin Controller | AJAX Request |
| Admin Pages | Admin Controller | SSR Request |
| Admin Controller | Database | ORM Query |
| Admin Controller | Midtrans | Status Check (CoreApi) |
| Admin Controller | Komerce | Data Wilayah |
| Order Admin (input resi) | Gmail SMTP | Email Notifikasi Otomatis (Signal) |

---

## BAGIAN 2 — PANDUAN LANGKAH DI MICROSOFT VISIO

### Persiapan Awal

1. Buka **Microsoft Visio**, pilih **Blank Drawing**
2. Ukuran halaman: **A3 Landscape** (File → Page Setup → A3, Landscape)
3. Aktifkan Grid dan Snap to Grid (View → Show → Grid)
4. Gunakan font **Arial** atau **Calibri** agar konsisten

---

### Langkah 1 — Buat Aktor (Sisi Kiri)

1. Buat **Rectangle** kecil di kiri kanvas → label: `Web Browser`
2. Di bawahnya, insert ikon orang (Insert → Icons → "person") atau gambar oval + garis sebagai stick figure
3. Tambah **Text Box** di bawah ikon: `Admin`
4. Sisakan ruang antara aktor dan kotak utama untuk panah

---

### Langkah 2 — Buat Kotak Besar Utama (Hijau Muda)

1. Buat **Rectangle besar** memenuhi hampir seluruh halaman
2. Ukuran: kira-kira 70% lebar halaman, 85% tinggi
3. Fill: **hijau muda** — warna hex `#D5E8D4` atau `#E2F0D9`
4. Border: **hijau tua** `#82B366`, ketebalan **2pt**
5. Judul di kiri atas: `Dashboard Admin DD Shoes Store (Django Admin + Jazzmin)`
   - Format: Bold, 12pt, warna hitam

---

### Langkah 3 — Alur Routing di Bagian Atas

Di dalam kotak besar, bagian atas:

**Kotak "Global Layout Admin":**
- Rectangle kecil, fill: **merah muda muda** `#FFD6D6`, border merah muda tua
- Label baris 1: `Global Layout Admin`
- Label baris 2 (italic kecil): `(base_site.html / Jazzmin Theme)`

**Kotak "Admin Routing":**
- Rectangle kecil, fill: putih, border abu
- Label: `Admin Routing` + sub: `(ddshoes/urls.py — /admin/)`

**Kotak "Admin Pages":**
- Rectangle kecil, fill: putih, border abu
- Label: `Admin Pages` + sub: `(Django Admin Views)`

**Kotak "Admin Parts":**
- Rectangle kecil, fill: putih, border abu
- Label: `Admin Parts` + sub: `(Sidebar, Navbar, Footer — Jazzmin)`

Hubungkan semua dengan panah ke kanan. Tambah panah dari Web Browser ke Admin Routing berlabel `HTTP Request`.

---

### Langkah 4 — Kotak "Fitur & Komponen Admin" (Kotak Besar di Dalam)

1. Di bawah alur routing, buat **Rectangle besar** kedua di dalam kotak utama
2. Fill: **biru muda sangat muda** `#DAE8FC` atau kuning muda `#FFF2CC`
3. Border: **biru tua** `#6C8EBF`, style **dashed** (putus-putus), ketebalan 1.5pt
4. Judul kiri atas: `Fitur & Komponen Admin`, Bold

**Buat 15 kotak kecil di dalamnya (3 kolom × 5 baris):**

Ukuran seragam tiap kotak: ±4 x 1.5 cm

Kolom Kiri (dari atas ke bawah):
- `Autentikasi (Login Role Admin / Staff)`
- `Kelola Master Produk` + sub: `(Edit, Hapus, Tambah, Gallery Inline)`
- `Kelola Kategori & Brand` + sub: `(Thumbnail Preview)`
- `Kelola Pengguna` + sub: `(Foto, Ukuran Sepatu, Loyalitas)`
- `Kelola Alamat User` + sub: `(Multi-level Wilayah)`

Kolom Tengah (dari atas ke bawah):
- `Dashboard Analitik` + sub: `(Grafik, Omzet, Filter Periode)`
- `Kelola Pesanan` + sub: `(New → Accepted → Completed / Cancelled)`
- `Kelola Retur Produk` + sub: `(Pending → Approved → Refunded)`
- `Kelola Voucher / Kupon` + sub: `(LOYAL- & Manual)`
- `Pengiriman` + sub: `(Input Resi → Email Otomatis)`

Kolom Kanan (dari atas ke bawah):
- `Statistik Pesanan` + sub: `(Baru, Siap Kirim, Dikirim, Selesai)`
- `Laporan & Grafik` + sub: `(Brand, Kategori, 5 Produk Terlaris)`
- `Analitik User` + sub: `(Registrasi, User Interest)`
- `Analitik Voucher` + sub: `(Status, Total Diskon)`
- `Manajemen Ulasan` + sub: `(Rating 1-5, Tampilkan/Sembunyikan)`

> TIP: Buat satu kotak, format sesuai, lalu Ctrl+D berulang. Setelah semua kotak selesai, pilih semua → Home → Arrange → Distribute Horizontally & Vertically untuk meratakan otomatis.

---

### Langkah 5 — Kotak "Utilities, Scripts & Styling"

1. Di bawah Fitur & Komponen, di dalam kotak utama
2. Rectangle sedang, judul: `Utilities, Scripts & Styling`
3. Fill: merah muda muda `#FFE6E6`, border merah muda, dashed
4. Di dalamnya 4 kotak kecil (2×2):
   - `Bootstrap 5.3 (Grid / Theme)`
   - `Admin Theme CSS (Jazzmin flatly)`
   - `jQuery (AJAX & DOM)`
   - `Chart.js (Grafik Data)`

---

### Langkah 6 — Kotak "Metode Rendering" (Kanan Atas, Luar)

1. Di luar kotak utama, pojok kanan atas
2. Rectangle sedang, judul: `Metode Rendering`
3. Fill: putih, border abu, shadow
4. Di dalamnya 2 kotak vertikal:
   - Atas: `Client-Side Interactivity (AJAX & JS)` + sub: `Filter periode · Update status inline · Print grafik`
   - Bawah: `Server-Side Rendering (SSR)` + sub: `Diproses Django Admin + Jazzmin`

---

### Langkah 7 — Kotak "Admin Controller"

1. Di sebelah kanan kotak utama, posisi tengah
2. Rectangle sedang, fill: putih, border abu gelap, shadow ringan
3. Label baris 1: `Admin Controller` (Bold)
4. Label baris 2: `(Django Admin Views — Logika Bisnis)`
5. Label baris 3 (kecil): `store · order · account`

---

### Langkah 8 — Database (Silinder)

1. Di bawah Admin Controller
2. Gunakan shape **Cylinder** (Database)
   - Shapes panel → cari "cylinder" atau stencil Network/Database
3. Label: `Database` + `PostgreSQL (Prod)` + `SQLite (Dev)`
4. Fill: merah muda `#F8CECC`, border merah

---

### Langkah 9 — Kotak "Layanan Eksternal" (Kuning)

1. Di sebelah kanan / di bawah Admin Controller
2. Rectangle besar, judul: `Layanan Eksternal`
3. Fill: kuning muda `#FFFACD`, border oranye, 2pt
4. Di dalamnya 2 kotak kecil vertikal:
   - `Midtrans — Sinkronisasi Status Pembayaran` + sub: `(CoreApi polling dari halaman konfirmasi)`
   - `Komerce / RajaOngkir — Data Wilayah` + sub: `(untuk keperluan verifikasi pengiriman)`

---

### Langkah 10 — Hubungkan Semua Panah

Gunakan tool **Connector** (Ctrl+Shift+3 atau ikon panah di toolbar).

| Dari | Ke | Label Panah |
|------|-----|-------------|
| Admin | Web Browser | (kosong) |
| Web Browser | Admin Routing | HTTP Request |
| Admin Routing | Admin Pages | routing /admin/ |
| Global Layout Admin | Admin Pages | extend template |
| Admin Pages | Admin Parts | include Jazzmin |
| Admin Pages | Fitur & Komponen Admin | render views |
| Fitur & Komponen Admin | Utilities | digunakan oleh |
| Fitur & Komponen Admin | AJAX (Metode Rendering) | request dinamis |
| AJAX | Admin Controller | AJAX Request |
| Admin Pages | Admin Controller | SSR Request |
| Admin Controller | Database | ORM Query |
| Admin Controller | Midtrans | Status Check |
| Admin Controller | Komerce | Data Wilayah |
| Pengiriman (input resi) | Gmail | Email Otomatis (Signal) |

> TIP: Untuk label panah, klik dua kali di tengah garis panah → ketik label. Atur posisi dengan drag label.

---

### Langkah 11 — Finishing

**Warna per komponen (panduan konsisten):**

| Elemen | Fill | Border |
|--------|------|--------|
| Kotak utama besar | Hijau muda `#D5E8D4` | Hijau tua `#82B366` |
| Global Layout Admin | Merah muda muda `#FFD6D6` | Merah muda `#B85450` |
| Kotak routing lain | Putih `#FFFFFF` | Abu `#AAAAAA` |
| Fitur & Komponen | Biru muda `#DAE8FC` | Biru `#6C8EBF` |
| Kotak fitur kecil | Putih `#FFFFFF` | Abu muda `#CCCCCC` |
| Utilities | Merah muda muda `#FFE6E6` | Merah muda `#D60000` |
| Layanan Eksternal | Kuning muda `#FFFACD` | Oranye `#D6930A` |
| Database (silinder) | Merah muda `#F8CECC` | Merah `#B85450` |
| Admin Controller | Putih | Abu gelap `#666666` |
| Metode Rendering | Putih | Abu `#999999` |

**Font:**
- Judul kotak besar: Bold, 11–12pt
- Label kotak fitur: Regular, 9–10pt
- Sub-label keterangan: Italic, 8pt, warna abu `#666666`

**Panah:**
- Panah utama: ketebalan 1.5pt, hitam
- Panah AJAX/API: ketebalan 1pt, biru, bisa dashed

---

## BAGIAN 3 — PETA POSISI VISUAL (Layout Kasar)

Bayangkan halaman A3 landscape:

```
                                              ┌──────────────────────────┐
                                              │  Metode Rendering         │
                                              │  [Client-Side AJAX]       │
                                              │  [Server-Side SSR]        │
                                              └──────────────────────────┘

[Admin]   ┌──────────────────────────────────────────────────────────────┐
          │  Dashboard Admin DD Shoes Store (Django Admin + Jazzmin)      │
[Web   ]→ │  (KOTAK HIJAU MUDA BESAR)                                    │
[Browser] │                                                               │
          │  [Global Layout]→[Admin Routing]→[Admin Pages]→[Admin Parts] │ →[Admin Controller]→[Database]
          │  (merah muda)     (putih)          (putih)       (putih)     │    (putih, shadow)   (silinder)
          │                       ↓                                       │
          │  ┌──────────────────────────────────────────────────────┐    │  ┌──────────────────────┐
          │  │  Fitur & Komponen Admin (kotak biru muda, dashed)    │    │  │  Layanan Eksternal   │
          │  │                                                       │    │  │  (kuning)            │
          │  │ [Autentikasi]  [Dashboard Analitik] [Statistik Order]│    │  │  · Midtrans          │
          │  │ [Kelola Produk][Kelola Pesanan]     [Laporan & Grafik]│   │  │  · Komerce/RajaOngkir│
          │  │ [Kel.Kategori] [Kelola Retur]       [Analitik User]  │    │  └──────────────────────┘
          │  │ [Kelola User]  [Kelola Voucher]     [Analitik Voucher]│   │
          │  │ [Kelola Alamat][Pengiriman/Resi]    [Kelola Ulasan]  │    │
          │  └──────────────────────────────────────────────────────┘    │
          │                                                               │
          │  ┌────────────────────────────────────┐                      │
          │  │  Utilities, Scripts & Styling       │                      │
          │  │  [Bootstrap 5.3]  [Admin Theme CSS] │                      │
          │  │  [jQuery]         [Chart.js]        │                      │
          │  └────────────────────────────────────┘                      │
          └──────────────────────────────────────────────────────────────┘
```

---

## BAGIAN 4 — CATATAN KHUSUS FITUR ADMIN DD SHOES

Beberapa hal yang membedakan Admin DD Shoes dari admin generik, dan perlu dimunculkan di diagram:

### Dashboard Custom (Override Index Django Admin)
Admin panel DD Shoes memiliki **custom dashboard** yang menimpa halaman index bawaan Django. Dashboard ini menampilkan:
- Kartu statistik: Pesanan Baru, Siap Kirim, Sedang Dikirim, Selesai, Omzet, Total Order, Dibatalkan, Stok Habis
- Filter periode: Hari Ini, 7 Hari, Bulan, Tahun, atau range custom (tanggal bebas)
- Grafik interaktif menggunakan Chart.js: Grafik Penjualan, Brand Terlaris, Kategori Terlaris, 5 Produk Terlaris, Registrasi User, Status Voucher, Distribusi Rating, User Interest

Komponen ini sebaiknya dimunculkan sebagai **kotak khusus** dalam diagram dengan label `Dashboard Analitik Custom (Chart.js + Filter Periode)`.

### Status Pesanan (State Machine)
Order admin memiliki alur status yang bisa direpresentasikan sebagai catatan kecil di diagram:
```
New → (Pembayaran) → Pending → (Admin Proses) → Accepted → (Admin Input Resi) → [Dikirim]
                                                                ↓
                                                    Completed ← (Admin Konfirmasi Selesai)
                                                    Cancelled ← (Admin/Midtrans Batalkan)
                                                    Returned ← (Retur Approved → Refunded)
```

### Trigger Email Otomatis (Signal)
Saat admin mengisi `tracking_number` di halaman edit Order, sebuah Django Signal otomatis mengirim email ke konsumen. Ini bisa dimunculkan sebagai panah putus-putus dari "Pengiriman (Input Resi)" ke "Gmail SMTP" dengan label `Django Signal (otomatis)`.

### Jazzmin (Admin Theme)
Seluruh tampilan admin menggunakan **Jazzmin** (flatly theme, dark sidebar) — bukan Django Admin bawaan. Ini penting disebutkan di kotak "Global Layout Admin".

---

Dokumen ini sudah cukup sebagai panduan lengkap untuk menggambar diagram Admin DD Shoes dari nol di Visio.
