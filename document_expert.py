import easyocr

# 1. Reader ko tayyar karein (English language ke liye)
reader = easyocr.Reader(['en'])

print("🔍 EcoX Document Scanner is Active...")

# 2. Apne dataset se kisi bhi bill ki image ka rasta dein
# Check karein ke dataset/utility_bills/ mein konsi file maujood hai
image_path = 'dataset/utility_bills/image_35 (1).jpg'
# 3. Text nikalna
result = reader.readtext(image_path, detail=0)

print("\n--- Scanned Text ---")
print(result)