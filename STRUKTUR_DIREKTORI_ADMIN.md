# DD Shoes Store (Struktur Direktori Backend Admin)

## Panduan Membuat di Visio

Format: Kotak-kotak grid berlapis, seperti gambar referensi.
Judul besar di atas: **DD Shoes Store (Struktur Direktori Backend Admin)**

---

## LAPISAN 1 — Folder Utama Django Apps
*(Baris kotak biru muda — 4 kotak sejajar)*

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     store/      │  │     order/      │  │    account/     │  │    ddshoes/     │
│  (App Produk)   │  │  (App Pesanan)  │  │  (App Akun)     │  │  (Konfigurasi)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Warna:** Biru muda — `#DAE8FC`, border biru `#6C8EBF`

---

## LAPISAN 2 — File Konfigurasi Utama
*(Baris kotak oranye/kuning — 4 kotak sejajar)*

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   settings.py   │  │    urls.py      │  │   .env.example  │  │  docker-compose │
│  (Konfigurasi)  │  │ (URL Router)    │  │  (Environment)  │  │     .yml        │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Warna:** Oranye muda — `#FFE6CC`, border oranye `#D6790A`

---

## LAPISAN 3 — Admin Classes (Logika Admin)
*Label section (teks abu di atas kotak): "isi folder admin.py — Logika Backend Admin"*
*(Kotak teal/biru kehijauan — grid 3 kolom × 4 baris)*

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   store/admin.py     │  │   order/admin.py     │  │  account/admin.py    │
│   ProductAdmin       │  │    OrderAdmin        │  │   AccountAdmin       │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   store/admin.py     │  │   order/admin.py     │  │  account/admin.py    │
│   CategoryAdmin      │  │  OrderProductInline  │  │   AddressAdmin       │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   store/admin.py     │  │   order/admin.py     │  │   order/admin.py     │
│   BrandAdmin         │  │  ReturnRequestAdmin  │  │   CouponAdmin        │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   store/admin.py     │  │   order/admin.py     │  │   order/admin.py     │
│  ReviewRatingAdmin   │  │  get_dashboard_data()│  │  custom_index()      │
│  UserInterestAdmin   │  │  (Statistik & Grafik)│  │  (Override Dashboard)│
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

**Warna:** Teal/biru kehijauan — `#D5E8D4` (atau `#B2DFDB`), border teal `#4DB6AC`

---

## LAPISAN 4 — Admin Templates (Tampilan Admin)
*Label section: "isi folder templates/admin/ — Tampilan Backend Admin"*
*(Kotak hijau muda — grid 4 kolom × 3 baris)*

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  admin/          │  │  order/          │  │  order/          │  │  order/          │
│  index.html      │  │  checkout.html   │  │  payments.html   │  │  confirmation    │
│ (Custom Dashboard│  │                  │  │ (Midtrans Snap)  │  │       .html      │
│  + Chart.js)     │  │                  │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  order/          │  │  order/          │  │  order/          │  │  order/          │
│  my_orders.html  │  │ invoice_pdf.html │  │ submit_return    │  │ shipping_email   │
│ (Riwayat Pesanan)│  │ (Cetak PDF)      │  │      .html       │  │      .html       │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  store/          │  │  account/        │  │  account/        │  │  account/        │
│  new_product     │  │  edit_profile    │  │  address_form    │  │  loyalty_program │
│  _email.html     │  │       .html      │  │  address_list    │  │      .html       │
│(Broadcast Email) │  │  (Profil User)   │  │       .html      │  │  (Saldo & Kupon) │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Warna:** Hijau muda — `#D5E8D4`, border hijau `#82B366`

---

## KETERANGAN WARNA UNTUK VISIO

| Lapisan | Warna Fill | Warna Border | Isi |
|---------|-----------|--------------|-----|
| Baris 1 — Folder Apps | Biru muda `#DAE8FC` | Biru `#6C8EBF` | store/ · order/ · account/ · ddshoes/ |
| Baris 2 — File Config | Oranye muda `#FFE6CC` | Oranye `#D6790A` | settings.py · urls.py · .env · docker-compose.yml |
| Baris 3 — Admin Classes | Teal `#D5EAD5` | Teal tua `#4DB6AC` | Semua ModelAdmin class per app |
| Baris 4 — Admin Templates | Hijau muda `#D5E8D4` | Hijau `#82B366` | Semua template terkait admin & pesanan |

---

## CATATAN ISI KHUSUS ADMIN

### Dashboard Custom (admin/index.html)
Template ini meng-override halaman index Django Admin bawaan dan menampilkan:
- Kartu statistik: Pesanan Baru, Siap Kirim, Dikirim, Selesai, Omzet, Total Order, Dibatalkan, Stok Habis
- Kartu retur: Menunggu, Diproses, Berhasil, Ditolak
- Grafik Chart.js: Penjualan, Brand Terlaris, Kategori Terlaris, 5 Produk Terlaris, Registrasi User, Status Voucher, Rating, User Interest
- Filter periode: Hari Ini / 7 Hari / Bulan / Tahun / Range Custom

### Alur Status Pesanan (yang dikelola Admin)
```
New (baru masuk)
  → Accepted (pembayaran berhasil — via Midtrans sync)
      → [Admin isi tracking_number] → Dikirim (+ Email otomatis ke konsumen)
          → Completed (Admin konfirmasi) → Trigger Loyalty Signal
          → Returned (jika Retur di-Refunded)
  → Cancelled (gagal bayar / admin batalkan → stok otomatis dikembalikan)
```

### Signal Otomatis dari Admin
- **Input resi** di OrderAdmin → `send_shipping_notification` signal → Email Gmail ke konsumen
- **Order Completed** → `handle_loyalty_logic` signal → loyalty_balance + generate Coupon LOYAL-
- **Produk baru disimpan** → `broadcast_new_product_email` signal → Email blast ke konsumen relevan

---

## PANDUAN CEPAT VISIO

1. Buat **Rectangle besar** sebagai kotak luar (border abu, fill putih)
2. Tambah judul di atas: **DD Shoes Store (Struktur Direktori Backend Admin)** — Bold, 14pt, tengah
3. **Baris 1 (Biru):** 4 kotak sejajar horizontal — `store/`, `order/`, `account/`, `ddshoes/`
4. **Baris 2 (Oranye):** 4 kotak sejajar — `settings.py`, `urls.py`, `.env.example`, `docker-compose.yml`
5. **Teks label section** italic abu kecil: "isi folder admin.py — Logika Backend Admin"
6. **Baris 3 (Teal):** 12 kotak (3 kolom × 4 baris) — setiap kotak berisi nama ModelAdmin class
7. **Teks label section**: "isi folder templates/ — Tampilan Backend Admin"
8. **Baris 4 (Hijau):** 12 kotak (4 kolom × 3 baris) — nama file template
9. Gunakan **Home → Arrange → Distribute Horizontally** untuk meratakan otomatis
10. Untuk teks 2 baris dalam kotak: klik kotak → klik dua kali → ketik baris 1, Enter, ketik baris 2
