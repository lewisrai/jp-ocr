import base64
import numpy

from io import BytesIO
from manga_ocr.manga_ocr import MangaOcr
from PIL import Image


class OverlaySource:
    def __init__(self):
        self.manga_ocr = MangaOcr()

    def __call__(self, image_base64):
        image = Image.open(BytesIO(base64.b64decode(image_base64)))
        image = numpy.array(image)
        image = image[:, :, ::-1].copy()

        return {"key": "value", "array": [1, 2]}
