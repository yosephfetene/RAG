import os
from pathlib import Path
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
        
        



main()