from flask import Flask, render_template, request
from io import BytesIO
from manga_ocr import MangaOcr
from PIL import Image
import base64
import re
import webbrowser
import yaml


def main():
    with open("config.yml", "r") as config_file:
        config_settings = yaml.safe_load(config_file)

    if (config_settings["use_local_model"]):
        mocr = MangaOcr(pretrained_model_name_or_path=config_settings["local_model_location"])
    else:
        mocr = MangaOcr()


    flask_app = Flask(__name__)

    @flask_app.route("/")
    def home():
        return render_template("home.html")

    @flask_app.route("/process", methods=['POST'])
    def process():
        image_base64 = re.sub("^data:image/.+;base64,", "", request.form["imageBase64"])
        image = Image.open(BytesIO(base64.b64decode(image_base64)))
        return mocr(image)


    webbrowser.open("http://127.0.0.1:{}".format(config_settings["flask_port"]))
    flask_app.run(debug=config_settings["flask_debug"], port=config_settings["flask_port"])


if __name__ == "__main__":
    main()
