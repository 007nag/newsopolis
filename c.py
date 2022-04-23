#from PIL import Image
import cv2
import numpy as np
import pytesseract


img = cv2.imread("1.jpeg")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
text = pytesseract.image_to_string(img)
print(text)