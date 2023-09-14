from flask import Flask, render_template, request
from io import BytesIO
from manga_ocr import MangaOcr
from PIL import Image
import base64
import re


app = Flask(__name__)
# mocr = MangaOcr()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/process", methods=['POST'])
def process():
    img_b64 = re.sub("^data:image/.+;base64,", "", request.form["imageBase64"])
    img = Image.open(BytesIO(base64.b64decode(img_b64)))
    img.save("downloaded.png")
    return ""


if __name__ == "__main__":
    app.run(debug=True, port=8000)
