import requests
url = 'http://127.0.0.1:5000/upload-ecox'
files = {'image': open('dataset/real_test.jpg', 'rb')} # Asli photo
response = requests.post(url, files=files)
print("\n--- ✅ ECOX VERIFICATION ---")
print(response.json())