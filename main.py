import os
import re
import pdf2image
import pytesseract

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

            pages = pdf2image.convert_from_path(pdfPath, dpi=300)

            for i, page in enumerate(pages):
                raw = pytesseract.image_to_string(page, lang='eng')
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
