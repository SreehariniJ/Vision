import requests
import time
import sys

url_upload = "http://localhost:8000/v1/documents/upload"
url_status = "http://localhost:8000/v1/documents/{}/status"
url_search = "http://localhost:8000/v1/search/"

file_path = r"c:\Users\Sreeharini\vision\test_documents\2_Simple_Text.pdf"

print("Uploading document...")
with open(file_path, "rb") as f:
    res = requests.post(url_upload, files={"file": f})
    
if res.status_code != 200:
    print("Upload Failed:", res.text)
    sys.exit(1)
    
doc_id = res.json()["id"]
print("Upload successful, Document ID:", doc_id)

print("Polling status...")
for i in range(30):
    time.sleep(2)
    s_res = requests.get(url_status.format(doc_id))
    status = s_res.json()["status"]
    print(f"Status: {status}")
    if status == 'completed':
        print("Processing complete!")
        break
    elif status == 'error':
        print("Processing failed!")
        sys.exit(1)
else:
    print("Timeout waiting for processing")
    sys.exit(1)

print("Testing search...")
res = requests.post(url_search, json={"query": "dummy", "limit": 2})
print("Search Results:", res.json())
