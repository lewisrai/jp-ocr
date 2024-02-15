import base64
import jaconv
import re

from flask import Flask, request, render_template
from io import BytesIO
from PIL import Image
from transformers import AutoFeatureExtractor, AutoTokenizer, VisionEncoderDecoderModel


class MangaOcr:
    def __init__(self, pretrained_model_path="OCRModel"):
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(
            pretrained_model_path
        )
        self.model = VisionEncoderDecoderModel.from_pretrained(pretrained_model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_path)

    def __call__(self, img):
        img = img.convert("L").convert("RGB")
        img = self.feature_extractor(img, return_tensors="pt").pixel_values
        img = img.squeeze()

        x = self.model.generate(img[None].to(self.model.device), max_length=300)[
            0
        ].cpu()
        text = self.tokenizer.decode(x, skip_special_tokens=True)

        text = "".join(text.split())
        text = text.replace("…", "...")
        text = re.sub("[・.]{2,}", lambda x: (x.end() - x.start()) * ".", text)
        text = jaconv.h2z(text, ascii=True, digit=True)

        return text


def main():
    mocr = MangaOcr()

    flask_app = Flask(__name__)

    @flask_app.route("/")
    def home():
        return render_template("index.html")

    @flask_app.route("/api", methods=["POST"])
    def process():
        image_base64 = re.sub("^data:image/.+;base64,", "", request.form["imageBase64"])
        image = Image.open(BytesIO(base64.b64decode(image_base64)))
        return mocr(image)

    flask_app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()
