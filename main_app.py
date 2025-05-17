import tkinter as tk
from tkinter import filedialog, messagebox
import os
import boto3
import pymongo
import time
import matplotlib.pyplot as plt
import mimetypes
import shutil


from hashing_utils import generate_sha256
from huffman_utils import compress_file
from decompress import decompress_file
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION_NAME, BUCKET_NAME



# AWS and MongoDB Setup
session = boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)
s3 = session.client('s3')

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["cloud_storage"]
collection = db["file_hashes"]

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


class FileCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📁 File Compression & Cloud Retrieval")
        self.root.geometry("650x800")
        self.root.configure(bg="#f0f4f8")

        tk.Label(root, text="Cloud File Compression and Retrieval", font=("Arial", 16, "bold"), bg="#f0f4f8", fg="#333").pack(pady=10)

        self.file_path = tk.StringVar()
        tk.Label(root, text="Select a file to compress and upload:", bg="#f0f4f8").pack()
        tk.Button(root, text="Browse File", command=self.browse_file).pack(pady=5)
        tk.Label(root, textvariable=self.file_path, bg="#f0f4f8").pack()

        tk.Button(root, text="Compress & Upload", command=self.compress_and_upload, bg="#4CAF50", fg="white").pack(pady=10)

        self.selected_file = tk.StringVar()
        self.file_dropdown = tk.OptionMenu(root, self.selected_file, "")
        self.file_dropdown.pack(pady=5, fill=tk.X)

        tk.Button(root, text="🔄 Refresh Cloud File List", command=self.load_s3_file_list).pack()

        tk.Label(root, text="Or enter filename to retrieve:", bg="#f0f4f8").pack(pady=5)
        self.file_name_input = tk.Entry(root, width=50)
        self.file_name_input.pack(pady=5, fill=tk.X)

        tk.Button(root, text="Retrieve & Decompress", command=self.retrieve_and_decompress, bg="#FF5722", fg="white").pack(pady=10)

        self.download_button = tk.Button(root, text="Download File", command=self.download_file, state="disabled", bg="#2196F3", fg="white")
        self.download_button.pack(pady=10)

        self.text_display = tk.Text(root, wrap=tk.WORD, height=15, width=75)
        self.text_display.pack(pady=5, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(root, command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_data = []
        self.current_decompressed_file = None

        tk.Button(root, text="Show Original vs Compressed Size Graph", command=self.show_orig_vs_compressed_graph).pack(pady=10)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file:
            self.file_path.set(file)

    def compress_and_upload(self):
        original_path = self.file_path.get()
        if not original_path or not os.path.isfile(original_path):
            messagebox.showerror("Error", "Please select a valid file.")
            return

        try:
            file_hash = generate_sha256(original_path)

            existing = collection.find_one({"hash": file_hash})
            if existing:
                messagebox.showwarning("Duplicate", f"File already uploaded as: {existing['filename']}")
                return

            base, ext = os.path.splitext(original_path)
            compressed_path = base + "_compressed.huff"
            compress_file(original_path, compressed_path)

            original_size = os.path.getsize(original_path) / 1024
            compressed_size = os.path.getsize(compressed_path) / 1024
            messagebox.showinfo("Compression Info", f"Original: {original_size:.2f} KB → Compressed: {compressed_size:.2f} KB")

            self.file_data.append((os.path.basename(original_path), original_size, compressed_size))

            s3.upload_file(compressed_path, BUCKET_NAME, os.path.basename(compressed_path))
            os.remove(compressed_path)

            collection.insert_one({
                "filename": os.path.basename(compressed_path),
                "original": os.path.basename(original_path),
                "hash": file_hash
            })

            messagebox.showinfo("Success", "Uploaded and saved to MongoDB.")
            self.load_s3_file_list()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def retrieve_and_decompress(self):
        filename = self.selected_file.get() or self.file_name_input.get().strip()
        if not filename:
            messagebox.showerror("Error", "Please enter or select a filename.")
            return

        entry = collection.find_one({"filename": {"$regex": filename, "$options": "i"}})
        if not entry:
            messagebox.showerror("Error", "File not found in DB.")
            return

        file_hash = entry["hash"]
        compressed_path = os.path.join(CACHE_DIR, f"{file_hash}.huff")
        original_filename = entry.get("original", "file.txt")
        original_ext = os.path.splitext(original_filename)[1]  # e.g., ".txt"
        decompressed_path = os.path.join(CACHE_DIR, f"{file_hash}_decompressed{original_ext}")

        try:
            if os.path.exists(decompressed_path):
                self.current_decompressed_file = decompressed_path
                self.display_file_if_text(decompressed_path)
                self.download_button.config(state="normal")
                return

            elif os.path.exists(compressed_path):
                decompress_file(compressed_path, decompressed_path)
                self.current_decompressed_file = decompressed_path
                self.display_file_if_text(decompressed_path)
                self.download_button.config(state="normal")
                return

            start_time = time.time()
            s3.download_file(BUCKET_NAME, entry["filename"], compressed_path)
            decompress_file(compressed_path, decompressed_path)
            self.current_decompressed_file = decompressed_path
            total_time = time.time() - start_time

            decompressed_size = os.path.getsize(decompressed_path) / 1024
            messagebox.showinfo("Decompression Info", f"Decompressed Size: {decompressed_size:.2f} KB")

            plt.bar(["Retrieval Time"], [total_time], color=["#FF9800"])
            plt.ylabel("Seconds")
            plt.title("File Retrieval Time")
            plt.show()

            self.display_file_if_text(decompressed_path)
            self.download_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Retrieval Failed: {str(e)}")
        
    def display_file_if_text(self, filepath):
        mime_type, _ = mimetypes.guess_type(filepath)
        self.text_display.delete("1.0", tk.END)
        if mime_type and mime_type.startswith("text"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.show_file_content(content)
                self.download_button.config(state="normal")  # Enable download also for text files
            except Exception as e:
                self.text_display.insert(tk.END, "Failed to display text file.\n")
                self.text_display.insert(tk.END, str(e))
                self.download_button.config(state="normal")
        else:
            # For binary files, show a message in the text box and enable download
            self.text_display.insert(tk.END, "🔒 Binary file detected (e.g. .zip, .png, etc).\nClick 'Download File' to save it locally.")
            self.download_button.config(state="normal")





    def load_s3_file_list(self):
        try:
            response = s3.list_objects_v2(Bucket=BUCKET_NAME)
            files = [item['Key'] for item in response.get('Contents', [])]
            menu = self.file_dropdown["menu"]
            menu.delete(0, "end")
            for f in files:
                menu.add_command(label=f, command=lambda value=f: self.selected_file.set(value))
            messagebox.showinfo("Success", "S3 file list loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load S3 files: {str(e)}")






    def show_file_content(self, content):
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert(tk.END, content)





    def download_file(self):
        filename = self.selected_file.get() or self.file_name_input.get().strip()
        if not filename:
            messagebox.showerror("Error", "No file selected or entered for download.")
            return

        entry = collection.find_one({"filename": {"$regex": filename, "$options": "i"}})
        if not entry:
            messagebox.showerror("Error", "File info not found in DB.")
            return

        file_hash = entry["hash"]
        original_filename = entry.get("original", "file.txt")
        original_ext = os.path.splitext(original_filename)[1]  # e.g., ".txt"
        decompressed_path = os.path.join(CACHE_DIR, f"{file_hash}_decompressed{original_ext}")
        if not os.path.exists(decompressed_path):
            messagebox.showerror("Error", "File not loaded locally. Please retrieve it first.")
            return

        original_filename = entry.get("original", "downloaded_file")
        save_path = filedialog.asksaveasfilename(initialfile=original_filename)
        if not save_path:
            return

        try:
            mime_type, _ = mimetypes.guess_type(decompressed_path)
            if mime_type and mime_type.startswith("text"):
                content = self.text_display.get("1.0", tk.END)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                with open(decompressed_path, "rb") as src_file, open(save_path, "wb") as dest_file:
                    dest_file.write(src_file.read())

            messagebox.showinfo("Success", f"File saved successfully as:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")





    def show_orig_vs_compressed_graph(self):
        if not self.file_data:
            messagebox.showwarning("Warning", "No data to plot.")
            return

        filenames = [f"{x[0]} ({x[1]:.1f} KB)" for x in self.file_data]
        original_sizes = [x[1] for x in self.file_data]
        compressed_sizes = [x[2] for x in self.file_data]

        plt.figure(figsize=(12, 6))
        plt.plot(filenames, original_sizes, marker='o', label='Original Size (KB)', color='blue')
        plt.plot(filenames, compressed_sizes, marker='o', label='Compressed Size (KB)', color='red')
        plt.xlabel("Filename (Original Size)")
        plt.ylabel("Size (KB)")
        plt.title("Original vs Compressed File Sizes")
        plt.xticks(rotation=30, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCompressorApp(root)
    app.load_s3_file_list()
    root.mainloop()