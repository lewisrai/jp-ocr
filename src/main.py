from io import BytesIO
from PIL import Image
import base64
import re
import webbrowser

from flask import Flask, request, render_template
from manga_ocr import MangaOcr
import toml


def main():
    with open("config.toml", "r") as config_file:
        config_settings = toml.load(config_file)

    if config_settings["model"]["use_local"]:
        mocr = MangaOcr(pretrained_model_name_or_path=config_settings["model"]["local_location"])
    else:
        mocr = MangaOcr()


    flask_app = Flask(__name__)

    @flask_app.route("/")
    def home():
        return render_template("index.html")

    @flask_app.route("/process", methods=['POST'])
    def process():
        image_base64 = re.sub("^data:image/.+;base64,", "", request.form["imageBase64"])
        image = Image.open(BytesIO(base64.b64decode(image_base64)))
        return mocr(image)


    webbrowser.open(f'http://127.0.0.1:{config_settings["flask"]["port"]}')
    flask_app.run(debug=config_settings["flask"]["debug"], port=config_settings["flask"]["port"])


if __name__ == "__main__":
    main()
