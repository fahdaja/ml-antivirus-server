# MangoDefend API Documentation

Dokumentasi ini menjelaskan cara menggunakan API yang tersedia pada aplikasi server (backend) MangoDefend. Secara default, aplikasi berjalan di `http://localhost:8000`.

## Base URL

```
http://localhost:8000
```

---

## 1. Cek Status API

Mengecek apakah server API sedang berjalan dengan baik.

- **URL:** `/`
- **Method:** `GET`
- **Response Success (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Welcome to MangoDefend API! System is up and running."
  }
  ```

---

## 2. Scan File (Upload & Deteksi)

Mengunggah file untuk dideteksi oleh model Machine Learning (ML) dan menyimpan hasilnya ke database. Endpoint ini memiliki fitur deduplikasi, sehingga jika file yang sama (berdasarkan hash) pernah di-scan sebelumnya, API akan langsung mengembalikan hasil yang sudah ada di database tanpa melakukan proses scan ulang.

- **URL:** `/api/v1/scan`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Request Body (Form Data):**
  - `file` (File, _Required_): File biner yang ingin di-scan.
  - `app_platform` (String, _Optional_): Platform dari aplikasi yang di-scan (contoh: `"Desktop"`, `"Mobile"`). setiap apps wajib set platformnya untuk dikirim sebagai value nya pada saat proses upload.

- **Response Success (200 OK):**
  ```json
  {
    "id": 1,
    "filename": "malicious_app.exe",
    "file_size": 1048576,
    "status": "completed",
    "prediction": "malware",
    "app_platform": "Desktop",
    "created_at": "2026-04-26T14:44:58.000Z"
  }
  ```
  _(Catatan: `prediction` dapat bernilai `"malware"` atau `"benign"`)._

---

## 3. Lihat Riwayat Scan

Mengambil riwayat scan dari database dengan fitur paginasi (pagination) dan filter berdasarkan platform.

- **URL:** `/api/v1/history`
- **Method:** `GET`
- **Query Parameters:**
  - `skip` (Integer, _Optional_): Jumlah data yang akan dilewati (offset). Default: `0`.
  - `limit` (Integer, _Optional_): Jumlah maksimal data yang dikembalikan. Default: `10`.
  - `app_platform` (String, _Optional_): Filter riwayat berdasarkan platform tertentu (contoh: `"Desktop"`). Jika tidak diisi, akan mengembalikan semua platform.

- **Response Success (200 OK):**
  ```json
  {
    "total": 15,
    "page": 1,
    "size": 10,
    "items": [
      {
        "id": 2,
        "filename": "clean_app.apk",
        "file_size": 2048576,
        "status": "completed",
        "prediction": "benign",
        "app_platform": "Mobile",
        "created_at": "2026-04-26T15:00:00.000Z"
      },
      ...
    ]
  }
  ```

---

## 4. Hapus Riwayat Scan

Menghapus data hasil scan dari database secara manual berdasarkan ID.

- **URL:** `/api/v1/{scan_id}`
- **Method:** `DELETE`
- **Path Parameters:**
  - `scan_id` (Integer, _Required_): ID dari data scan yang ingin dihapus.

- **Response Success (200 OK):**
  ```json
  {
    "message": "Data deleted successfully"
  }
  ```
- **Response Not Found (404 Not Found):**
  ```json
  {
    "detail": "Scan data not found"
  }
  ```

---

## Dokumentasi Interaktif (Swagger UI)

Karena aplikasi dibangun menggunakan FastAPI, Anda juga dapat mengakses dokumentasi interaktif (Swagger UI) untuk melakukan uji coba endpoint langsung dari browser.

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
