import os
import numpy as np
from PIL import Image, ImageOps
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import random

app = Flask(__name__)
app.secret_key = "secret"
app.config['UPLOAD_FOLDER'] = "./static/uploads/"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def insertion_sort(color_tuple: tuple, color_count: int, top_10_color_counts: list, top_10_color_tuples: list[tuple]):
    if color_tuple in top_10_color_tuples:
        i = top_10_color_tuples.index(color_tuple)
    else:
        i = 9

    while i > 0 and top_10_color_counts[i - 1] < color_count:
        top_10_color_counts[i] = top_10_color_counts[i - 1]
        top_10_color_tuples[i] = top_10_color_tuples[i - 1]
        i -= 1
    top_10_color_counts[i] = color_count
    top_10_color_tuples[i] = color_tuple


def analyse_image(file_path):
    my_image = Image.open(file_path).convert('RGB')
    size = my_image.size
    if size[0] >= 1200 or size[1] >= 1200:
        my_image = ImageOps.scale(image=my_image, factor=0.2)
    elif size[0] >= 800 or size[1] >= 800:
        my_image = ImageOps.scale(image=my_image, factor=0.1)
    my_image = ImageOps.posterize(my_image, 4)
    img_arr = np.array(my_image)

    color_d = {}
    top_10_color_tuples = []
    top_10_color_counts = []

    # print(img_arr)

    for row in img_arr:
        for col in row:
            color_tuple = (col[0], col[1], col[2])

            # Update dictionary
            if color_d.get(color_tuple):
                color_d[color_tuple] += 1
            else:
                color_d[color_tuple] = 1

            # Update List of Top 10
            current_count = color_d[color_tuple]

            if color_tuple in top_10_color_tuples:
                idx = int(top_10_color_tuples.index(color_tuple))
                top_10_color_counts[idx] += 1
                insertion_sort(top_10_color_tuples[idx], current_count, top_10_color_counts, top_10_color_tuples)
            elif len(top_10_color_counts) < 10:
                top_10_color_counts.append(current_count)
                top_10_color_tuples.append(color_tuple)
            elif current_count > top_10_color_counts[-1]:
                insertion_sort(color_tuple, current_count, top_10_color_counts, top_10_color_tuples)

    # print(top_10_color_tuples)
    return top_10_color_tuples


@app.route("/", methods=["GET", "POST"])
def home():
    heading_color = []
    for i, word in enumerate("Image Color Palette Detector".split()):
        heading_color.append([word, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))])

    print(heading_color)
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect("/")

        file = request.files['file']
        if file.filename == '':
            return redirect("/")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # top_colors = analyse_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('loading', filename=filename))
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect("/")

    return render_template("index.html", loading=False, heading_color=heading_color)


@app.route("/loading/<filename>")
def loading(filename):
    heading_color = []
    for i, word in enumerate("Image Color Palette Detector".split()):
        heading_color.append([word, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))])
    return render_template('loading.html', filename=filename, heading_color=heading_color)


@app.route("/result/<filename>")
def result(filename):
    top_colors = analyse_image(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    heading_color = []
    for i, word in enumerate("Image Color Palette Detector".split()):
        heading_color.append([word, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))])
    return render_template('result.html', filename=filename, top_colors=top_colors, heading_color=heading_color)


if __name__ == "__main__":
    app.run(debug=True)
