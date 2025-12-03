import os
import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import cv2
import numpy as np

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
        lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
        a = lab[:, :, 1].astype(np.int16) - 128
        b = lab[:, :, 2].astype(np.int16) - 128
        chroma = np.sqrt(a * a + b * b).astype(np.uint8)

        _, color_mask = cv2.threshold(chroma, 8, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        color_mask = cv2.dilate(color_mask, kernel, iterations=2)

        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w > 100 and h > 30 and cv2.contourArea(c) > 500:
                cv2.rectangle(cv_img, (x, y), (x + w, y + h), (255, 255, 255), -1)

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
