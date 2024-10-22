from paddleOCR import PaddleOCR

def job_paddle_ocr(_options):
    ocr = PaddleOCR(lang="korean")

    img_path = _options["path"]
    items = ocr.ocr(img_path, cls=False)

    text = ""
    for item in items:
        for element in item:
            props = element[-1][1]
            if props > 0.8:
                text += f"\n{element[-1][0]}"##dfd

    print("[*] job_easy_paddle_ocr", text)
    return text
