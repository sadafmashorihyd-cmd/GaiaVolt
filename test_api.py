import requests

url = 'http://127.0.0.1:5000/upload-ecox'
# Apni laptop wali photo ka rasta dein
# Purani line: files = {'image': open('dataset/laptop_photo.jpg.jpg', 'rb')}
# Nayi line:
files = {'image': open('dataset/real_test.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())