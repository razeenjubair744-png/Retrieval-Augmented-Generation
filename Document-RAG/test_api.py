import requests
import json
import time

API_URL = "http://localhost:8000"

def test():
    print("1. Creating dummy url.txt...")
    with open("url.txt", "w") as f:
        f.write("This is a dummy url.txt file with some content.")
        
    print("2. Uploading to /api/init/files...")
    with open("url.txt", "rb") as f:
        files = {"files": ("url.txt", f, "text/plain")}
        data = {"chunk_size": 500, "chunk_overlap": 50}
        res = requests.post(f"{API_URL}/api/init/files", files=files, data=data)
        
    print("Init response:", res.status_code, res.text)
    
    time.sleep(1)
    
    print("3. Querying /api/chat...")
    res = requests.post(f"{API_URL}/api/chat", json={"question": "What is in the urls?", "history": []})
    print("Chat response:", res.status_code)
    try:
        print(json.dumps(res.json(), indent=2))
    except:
        print(res.text)

if __name__ == "__main__":
    test()
