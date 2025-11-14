import os
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import cv2
import numpy as np
from PIL import Image

def main():
    inputDir = './pdf/Biology'
    outputDir = './Output'

    try:
        files = os.listdir(inputDir)

    except Exception as error:
        print(f"fs.readdir didnt work and error reading directory {inputDir}", error)
        return
    
    if not files:
        print(f"Files in {inputDir} can't be found")
        return
    
    def remove_colored_boxes(img):
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

        orange_low  = np.array([5, 60, 50])
        orange_high = np.array([20, 255, 255])

        yellow_low  = np.array([20, 60, 80])
        yellow_high = np.array([35, 255, 255])

        blue_low  = np.array([85, 40, 40])
        blue_high = np.array([140, 255, 255])

        brown_low = np.array([8, 40, 40])
        brown_high = np.array([20, 255, 200])

        mask1 = cv2.inRange(hsv, orange_low, orange_high)
        mask2 = cv2.inRange(hsv, yellow_low, yellow_high)
        mask3 = cv2.inRange(hsv, blue_low, blue_high)
        mask4 = cv2.inRange(hsv, brown_low, brown_high)

        mask = mask1 | mask2 | mask3 | mask4
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w > 150 and h > 50:
                cv2.rectangle(cv_img, (x, y), (x+w, y+h), (255, 255, 255), -1)

        cleaned = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        return cleaned


    def clean_text(text):
        text = re.sub(r"--- Page: \d+ ---", "", text)
        text = re.sub(r"^\s*\d+\s+Grade\s+\d+\s*$", "", text,flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"(KEY WORDS|DID YOU KNOW\?)", "", text, flags=re.IGNORECASE)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"\n{2,}", "\n", text)

        return text.strip()
    
    for file in files:

        pdfPath = os.path.join(inputDir, file)
        baseName = os.path.splitext(file)[0]

        print(f"processing {file}")
        finalText = ""

        try:

            pages = convert_from_path(pdfPath, dpi=300)

            for i, page in enumerate(pages):
                cleaned_page = remove_colored_boxes(page)
                raw = pytesseract.image_to_string(cleaned_page, lang='eng')
                clean = clean_text(raw)
                finalText += f"\n--- Page: {i + 1} ---\n{clean}\n"

        except Exception as err:
            print(f"Failed to extract {file}:", err)
            continue

        outPath = os.path.join(outputDir, baseName + ".txt")

        with open(outPath, "w", encoding="utf-8") as f:
            f.write(finalText.strip())

        print(f"Saved OCR result to: {outPath}")

if __name__ == "__main__":
    main()
