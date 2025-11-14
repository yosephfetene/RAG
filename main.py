import os
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

    for file in files:
        pdfPath = os.path.join(inputDir, file)
        baseName = os.path.splitext(file)[0]
        print(f"processing {file}")

        finalText = ""

        try:
            pages = pdf2image.convert_from_path(pdfPath, dpi=300)
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page, lang='eng')
                finalText += f"\n--- Page: {i + 1} ---\n{text}\n"
        except Exception as err:
            print(f"Failed to extract {file}:", err)
            continue

        outPath = os.path.join(outputDir, baseName + ".txt")
        with open(outPath, "w", encoding="utf-8") as f:
            f.write(finalText.strip())

        print(f"Saved OCR result to: {outPath}")

if __name__ == "__main__":
    main()
