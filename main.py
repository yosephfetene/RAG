import os
from pathlib import Path
import pdfplumber
def main():
    inputDir = Path("pdf/Biology")
    outputDir = Path("Output")

    files = []
    try:
        files = os.listdir(inputDir)
    except Exception as e:
        print("Error accessing directory:", e)
        return
    
    for file in files:
        pdfPath = inputDir / file
        baseName = os.path.splitext(file)[0]

        print(f"processing file: {pdfPath}")
        
        finalText = ""
        try: 
            with pdfplumber.open(pdfPath) as pdf:
                for i, page in enumerate(pdf.pages)
                text = page.extract_text() or ""
                finalText += f"\n--- Page: {i + 1}---\n"
        except Exception as err:
            print(f"Failed to extracct text from {file}:", err)
            continue
        outPath = os.path.join(outputDir, baseName + ".txt")
        with open(outPath, "w", encoding="utf-8") as f:
            f.write(finalText.strip())
        print(f"Saved and extracted text to: {outPath}")
if __name__ == "__main__":
    main()