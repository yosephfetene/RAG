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
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

        # --- COLOR RANGES (same as yours) ---
        colors = [
            (np.array([5, 60, 50]),   np.array([20, 255, 255])),   # orange
            (np.array([20, 60, 80]),  np.array([35, 255, 255])),   # yellow
            (np.array([85, 40, 40]),  np.array([140, 255, 255])),  # blue
            (np.array([8, 40, 40]),   np.array([20, 255, 200])),   # brown
            (np.array([15, 20, 180]), np.array([25, 120, 255])),   # light orange
            (np.array([70, 0, 150]),  np.array([100, 90, 255]))    # blue2
        ]

        # Combine all masks
        mask = None
        for low, high in colors:
            m = cv2.inRange(hsv, low, high)
            mask = m if mask is None else (mask | m)

        # --- FIX: Dilate mask to capture ALL of the colored region ---
        kernel = np.ones((25, 25), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # Remove the masks — paint white over them
        cv_img[mask > 0] = (255, 255, 255)

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
