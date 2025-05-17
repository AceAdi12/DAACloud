import os
import boto3
import pymongo
from hashing_utils import generate_sha256
from decompress import decompress_file
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION_NAME, BUCKET_NAME

# AWS session
session = boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)
s3 = session.client('s3')

# MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["cloud_storage"]
collection = db["file_hashes"]

# Cache folder
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Input
user_input = input("Enter original filename (e.g., File1.txt): ")

# MongoDB lookup
entry = collection.find_one({"filename": {"$regex": user_input}})
if not entry:
    print("❌ File not found in database.")
else:
    filename = entry["filename"]
    file_hash = entry["hash"]
    is_compressed = filename.endswith(".huff")
    cached_path = os.path.join(CACHE_DIR, f"{file_hash}_final.txt")

    if os.path.exists(cached_path):
        print(f"✅ File retrieved from cache: {cached_path}")
        # Display the file's contents to the user
        with open(cached_path, "r", encoding="utf-8") as f:
            print("\nFile Contents:")
            print(f.read())  # This will display the file's content to the user

    else:
        temp_path = os.path.join(CACHE_DIR, filename)
        try:
            print("📥 Attempting to download:", filename)
            s3.download_file(BUCKET_NAME, filename, temp_path)
            print("📦 File downloaded from S3.")

            if is_compressed:
                decompress_file(temp_path, cached_path)
                print(f"📂 Decompressed to: {cached_path}")
                os.remove(temp_path)
            else:
                os.rename(temp_path, cached_path)
                print(f"📁 Moved to cache: {cached_path}")

            # Verify hash
            retrieved_hash = generate_sha256(cached_path)
            if retrieved_hash == file_hash:
                print("🔒 File integrity verified (hash matched).")
            else:
                print("⚠️ Warning: Hash mismatch!")

        except Exception as e:
            print("❌ Error downloading file:", e)
