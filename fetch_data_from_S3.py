
import boto3
import os

ACCESS_KEY = ""
SECRET_KEY = ""
BUCKET_NAME = "crypto-project12"

# Save files into current project folder
save_dir = os.getcwd()   # project root (where you run the script)

s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="us-east-1"  # change if needed
)

# List and download files
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="rsi_data/")

if "Contents" in response:
    for obj in response["Contents"]:
        key = obj["Key"]
        if key.endswith("/"):  # skip folder placeholder
            continue
        filename = os.path.join(save_dir, os.path.basename(key))
        print(f"Downloading {key} -> {filename}")
        s3.download_file(BUCKET_NAME, key, filename)
else:
    print("No files found in that folder.")


