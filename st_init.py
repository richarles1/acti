import os
import easyocr

print("Pre-downloading EasyOCR models...")
# This forces EasyOCR to download the files to the server before the app opens
easyocr.Reader(['en'])
print("Models downloaded successfully!")
