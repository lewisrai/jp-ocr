from base64 import b64decode
from flask import Flask, request, render_template
from io import BytesIO
from manga_ocr import MangaOcr
from PIL import Image


def main():
    manga_ocr = MangaOcr()

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/", methods=["POST"])
    def api():
        image_base64 = request.get_data(as_text=True).split(",")[1]
        image = Image.open(BytesIO(b64decode(image_base64)))

        return manga_ocr(image)

    app.run()


if __name__ == "__main__":
    main()
