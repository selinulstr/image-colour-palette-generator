import os.path
from flask import Flask, render_template, request
from scipy.spatial import KDTree
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb, name_to_hex


app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET_KEY"


def palette(img):
    arr = np.asarray(img)
    palette, index = np.unique(asvoid(arr).ravel(), return_inverse=True)
    palette = palette.view(arr.dtype).reshape(-1, arr.shape[-1])
    count = np.bincount(index)
    order = np.argsort(count)
    return palette[order[::-1]]


def asvoid(arr):
    arr = np.ascontiguousarray(arr)
    return arr.view(np.dtype((np.void, arr.dtype.itemsize * arr.shape[-1])))


def convert_rgb_to_names(rgb_tuple):
    css3_db = CSS3_HEX_TO_NAMES
    names = []
    rgb_values = []
    for color_hex, color_name in css3_db.items():
        names.append(color_name)
        rgb_values.append(hex_to_rgb(color_hex))

    kdt_db = KDTree(rgb_values)
    distance, index = kdt_db.query(rgb_tuple)
    return names[index].title()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_colors", methods=["GET", "POST"])
def get_colors():

    if request.method == "POST":
        f = request.files["file"]
        f.save(os.path.join("static", secure_filename(f.filename)))
        img = Image.open(f, "r").convert("RGB")
        color_codes = palette(img)
        colors = {}
        for code in color_codes:
            if convert_rgb_to_names(code) not in colors and len(colors) < 10:
                name = convert_rgb_to_names(code)
                hex = name_to_hex(convert_rgb_to_names(code))
                colors[hex] = name

        return render_template("color.html", colors=colors, filename=f.filename)


if __name__ == "__main__":
    app.run(debug=True)