# ☁️ Cloud File Storage Optimization System using Huffman Coding

This project is a cloud-based file storage solution that uses **Huffman compression**, **SHA-256 hashing**, and **AWS S3 integration** to optimize storage and retrieval of files. It prevents duplicate uploads and speeds up file access using caching and MongoDB-based metadata tracking.

---

## 🧠 Key Features

- ✅ Compress files using **Huffman coding** (greedy algorithm)
- ✅ Calculate **SHA-256 hash** to detect and skip duplicate files
- ✅ Upload compressed files to **AWS S3**
- ✅ Store file metadata (name, original name, hash) in **MongoDB**
- ✅ Retrieve and **decompress files** with cache-first approach
- ✅ Visualize **compression efficiency** using graphs
- ✅ Fully interactive **Tkinter GUI**

---

## 📦 Technology Stack

| Category         | Tools / Tech                |
|------------------|-----------------------------|
| Programming      | Python                      |
| Cloud Storage    | AWS S3                      |
| Hashing          | SHA-256 (`hashlib`)         |
| Compression      | Huffman Coding              |
| Database         | MongoDB                     |
| GUI              | Tkinter                     |
| Visualization    | Matplotlib                  |
| File Operations  | Pickle, OS, File I/O        |

---

## 📊 Project Progress

- ✅ File upload with hashing
- ✅ Huffman compression implemented
- ✅ Duplicate check using MongoDB
- ✅ AWS S3 integration complete
- ✅ GUI fully functional
- ✅ File retrieval + decompression done
- ✅ Graph plotting added

---

## 🧪 Testing Summary

| Test Type              | Status     | Notes                                   |
|------------------------|------------|-----------------------------------------|
| Upload (new file)      | ✅ Pass     | Compressed and uploaded to S3           |
| Upload (duplicate)     | ✅ Pass     | Detected and skipped                    |
| Decompression          | ✅ Pass     | Restores file from `.huff` format       |
| Cache check            | ✅ Pass     | Fast retrieval from local cache         |
| Graph plotting         | ✅ Pass     | Shows original vs compressed size       |
| GUI interaction        | ✅ Pass     | All buttons and features responsive     |

---

## 📁 Folder Structure
📦 DAACloudProject/
├── hashing_utils.py
├── huffman_utils.py
├── decompress.py
├── s3_upload_with_hash.py
├── file_retrieval.py
├── main_app.py
├── config.py
├── README.md
└── cache/ # Local cache folder


---

## 📌 How to Run

1. Clone the repo
2. Install dependencies (boto3, pymongo, matplotlib)
3. Ensure MongoDB is running
4. Set your AWS keys in `config.py`
5. Run:  
   ```bash
   python gui_app.py

---
Sample Output
File1.txt → File1_compressed.huff

Original size: 48 KB → Compressed: 16 KB

Retrieval time: 1.02 seconds

Duplicate upload: Skipped

