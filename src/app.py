from io import BytesIO
from PIL import Image
import base64
import re

from flask import Flask, request, render_template
from manga_ocr import MangaOcr


def main():
    mocr = MangaOcr(pretrained_model_name_or_path="OCRModel")


    flask_app = Flask(__name__)

    @flask_app.route("/")
    def home():
        return render_template("index.html")

    @flask_app.route("/api", methods=['POST'])
    def process():
        image_base64 = re.sub("^data:image/.+;base64,", "", request.form["imageBase64"])
        image = Image.open(BytesIO(base64.b64decode(image_base64)))
        return mocr(image)


    print("\nhttp://127.0.0.1:5000\n")
    flask_app.run()


if __name__ == "__main__":
    main()
