import os
import sys
import time
from pathlib import Path

import requests


base_url = os.environ.get("VISION_BASE_URL", "http://localhost:8000").rstrip("/")
document_path = Path(os.environ.get("VISION_TEST_DOCUMENT", "test_documents/2_Simple_Text.pdf"))

url_upload = f"{base_url}/v1/documents/upload"
url_status = f"{base_url}/v1/documents/{{}}/status"
url_search = f"{base_url}/v1/search/"

if not document_path.exists():
    print(f"Test document not found: {document_path}")
    sys.exit(1)

print(f"Uploading document to {url_upload}")
with document_path.open("rb") as file_handle:
    response = requests.post(url_upload, files={"file": file_handle}, timeout=60)

if response.status_code != 200:
    print("Upload failed:", response.text)
    sys.exit(1)

document_id = response.json()["id"]
print("Upload successful, document ID:", document_id)

print("Polling ingestion status...")
for _ in range(90):
    time.sleep(2)
    status_response = requests.get(url_status.format(document_id), timeout=15)
    status_response.raise_for_status()
    status = status_response.json()["status"]
    print(f"Status: {status}")
    if status == "indexed":
        print("Processing complete")
        break
    if status == "failed":
        print("Processing failed:", status_response.json().get("error_message"))
        sys.exit(1)
else:
    print("Timeout waiting for document processing")
    sys.exit(1)

print("Testing search...")
response = requests.post(url_search, json={"query": "dummy", "limit": 2}, timeout=60)
response.raise_for_status()
print("Search results:", response.json())
