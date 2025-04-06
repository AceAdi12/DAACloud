import boto3
import boto3.session
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION_NAME, BUCKET_NAME
session=boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)

s3=session.client('s3')
file_path='Fil1.txt'
key='File1.txt'
try:
    s3.upload_file(file_path,BUCKET_NAME,key)
    print("✅ File uploaded successfully!")
except Exception as e:
    print("❌ Upload failed:", e)