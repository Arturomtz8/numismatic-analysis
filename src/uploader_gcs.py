import os

from google.cloud import storage


def upload_csv_to_gcs(bucket_name, source_file_path, gcs_key):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_key)
    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded")


if __name__ == "__main__":
    bucket_name = os.getenv("NUMISMATIC_BUCKET")
    path_file = "billetes.csv"
    gcs_key = os.getenv("NUMISMATIC_RAW")

    upload_csv_to_gcs(bucket_name, path_file, gcs_key)
