import os
import boto3.session
from config import AWS_ACCESS_KEY,AWS_SECRET_KEY,REGION_NAME,BUCKET_NAME
from hashing_utils import generate_sha256
from huffman_utils import compress_file
import boto3
import pymongo

# SETUP OF AWS AND mongoDB START HERE::---->>

session =boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)
s3=session.client('s3')

client=pymongo.MongoClient("mongodb://localhost:27017/")
db = client["cloud_storage"]
collection = db["file_hashes"]

#FILE DETAILS::-->>
# Original File
original_path = "Fil1.txt"
compressed_path = "File1_compressed.huff"

# Step 1: Compress
compressed_file_path = compress_file(original_path, compressed_path)
print(f"📦 Compressed file saved to: {compressed_file_path}")

# Step 2: Generate hash of compressed file
file_hash = generate_sha256(compressed_file_path)
# Debug: print hash
print(f"DEBUG: Generated hash = {file_hash}")

# Check for duplicates
existing = collection.find_one({"hash": file_hash})

if existing:
    print(f"⚠️ File already uploaded before as: {existing['filename']}")
else:
    try:
        s3.upload_file(compressed_file_path,BUCKET_NAME,os.path.basename(compressed_file_path))
        print("✅File uploaded successfully!")
        collection.insert_one({
            "filename": os.path.basename(compressed_file_path),
            "original": os.path.basename(original_path),
            "hash": file_hash
        })
    except Exception as e:
        print("❌Upload failed:",e)