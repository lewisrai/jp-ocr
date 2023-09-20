from flask import Flask, render_template, request
from io import BytesIO
from manga_ocr import MangaOcr
from PIL import Image
import base64
import re
import webbrowser
import yaml


with open("config.yml", "r") as configFile:
    configSettings = yaml.safe_load(configFile);


if (configSettings["useLocalModel"]):
    mocr = MangaOcr(pretrained_model_name_or_path="mocrModel")
else:
    mocr = MangaOcr()


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/process", methods=['POST'])
def process():
    img_b64 = re.sub("^data:image/.+;base64,", "", request.form["imageBase64"])
    img = Image.open(BytesIO(base64.b64decode(img_b64)))
    return mocr(img)


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:{}".format(configSettings["port"]))
    app.run(debug=configSettings["debug"], port=configSettings["port"])
