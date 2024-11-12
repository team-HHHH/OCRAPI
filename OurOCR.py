#수정
import json
import os
import sys
import time

import dotenv
import BetterOCR.betterocr.__init__

OPENAPI_KEY = ""


def getImg(path="Img"):
    ret_flist = []
    for a, b, c in os.walk(path):
        for item in c:
            ret_flist.append(os.path.join(a, item))
    return ret_flist

def returnErr(mode, args):
    if mode == "direrror":
        return f'"errorCode": 1\nerror: It is not existed : {args}'
def ocrToGPTAPI(path):
    global OPENAPI_KEY
    if not os.path.isfile(path):
        print(f"It is not existed Directory : {path}")
        return json.dumps(returnErr("direrror", path))

    print(f"Hello, your key : {dotenv.load_dotenv('OPENAI_API_KEY')}")
    fList = getImg()

    image_path = path
    text = BetterOCR.betterocr.detect_text(
        image_path,
        ["ko", "en"],  # language codes (from EasyOCR)
        context="",  # (optional) context
        tesseract={
            # Tesseract options here
            "config": "--tessdata-dir ./tessdata"
        },
        openai={
            # OpenAI options here

            # `os.environ["OPENAI_API_KEY"]` is used by default
            "API_KEY": OPENAPI_KEY,
            # rest are used to pass params to `client.chat.completions.create`
            # `{"model": "gpt-4"}` by default
            "model": "gpt-4o-mini",
        },
    )

    print("return --- > ")
    return text


def imgToJson(path: str):
    jsonF = ocrToGPTAPI(path)

    outputName = os.path.basename(path).rsplit(".", maxsplit=1)[0] + ".json"

    dirName = os.path.join(os.getcwd(), "output")

    if not os.path.isdir(dirName):
        os.makedirs(dirName)

    extractFile = os.path.join(dirName, outputName)
    print(f"extract : {extractFile}")

    with open(extractFile, "w", encoding="utf-8") as fp:
        fp.write(json.dumps(jsonF, ensure_ascii=False))

    print("Finish")







if __name__ == "__main__":
    dotenv.load_dotenv()
    start = time.time()
    OPENAPI_KEY = os.environ.get("OPENAI_API_KEY")
    #imgToJson(sys.argv[1])
    imgToJson("./Img/1.jfif")
    end = time.time()
    print(f"start = {start}, end={end} : == {end - start}")

