from paddleocr import PaddleOCR

'''
pip install

albumentations
paddlepaddle
paddleocr
'''

def jobsPaddle(path):
    ocr = PaddleOCR(lang="korean")

    img_path = "Img/hard.png"
    items = ocr.ocr(img_path, cls=False)

    strings = ""
    for item in items:
        for element in item:
            props = element[-1][1]
            if props > 0.8:
                strings += f" {element[-1][0]}"


