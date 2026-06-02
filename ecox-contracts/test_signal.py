import requests

url = "http://127.0.0.1:8000/mint-signal"

# 'r' lagane se backslashes asani se handle ho jate hain
payload = {
    "decision": "YES", 
    "image_path": "contracts/image_test_2.png"
}

response = requests.post(url, json=payload) 
print(response.json())