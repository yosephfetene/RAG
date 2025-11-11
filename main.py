import os
from pathlib import Path

inputDir = Path("/pdf/Biology")
outputDir = Path("/Output")

for file in os.listdir(inputDir):
    filePath = inputDir / file
    exctractText(filePath, outputDir)



def extractText(filePath, outputDir):


#Continue on making the path functionality first make it all one function if it is too hard