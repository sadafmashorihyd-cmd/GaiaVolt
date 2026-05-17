import requests
url = 'http://127.0.0.1:5000/upload-ecox'
files = {'image': open('dataset/new_test.jpg', 'rb')} # Purani photo
response = requests.post(url, files=files)
print("\n--- 🛡️ ECOX SECURITY CHECK ---")
print(response.json())