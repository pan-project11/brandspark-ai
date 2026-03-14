import os, uuid
from google.cloud import storage

_client = None

def get_client():
    global _client
    if _client is None:
        _client = storage.Client(project="gen-lang-client-0134408223")
    return _client

async def upload_to_gcs(data: bytes, content_type: str, prefix: str = "assets") -> str:
    bucket_name = os.getenv("GCS_BUCKET", "pitchforge-assets-0134408223")
    ext = "png" if "image" in content_type else "mp3"
    blob_name = f"{prefix}/{uuid.uuid4().hex}.{ext}"
    blob = get_client().bucket(bucket_name).blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)
    return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"