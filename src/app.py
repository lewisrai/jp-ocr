from flask import Flask, request, render_template
from overlay_source import OverlaySource


def main():
    overlay_source = OverlaySource()

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api", methods=["POST"])
    def api():
        image_base64 = request.get_data(as_text=True).split(",")[1]

        return overlay_source(image_base64)

    app.run()


if __name__ == "__main__":
    main()
