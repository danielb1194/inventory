# entry point for flask
import os
from flask import Flask, flash, request, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
import qrcode

#  config
UPLOADS_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# app init
app = Flask(__name__)
app.config["UPLOADS_FOLDER"] = UPLOADS_FOLDER
app.config["STATIC_FOLDER"] = UPLOADS_FOLDER


def allowed_file(filename):
    """check if file is allowed to be uploaded"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/images/<string:filename>")
def uploaded_file(filename: str = None):
    """serve uploaded files"""
    if not filename:
        return "no file specified"
    # read the description from data.txt
    description = "Boo, no description"
    with open(os.path.join(app.config["UPLOADS_FOLDER"], "data.txt"), "r") as f:
        for line in f.readlines():
            if line.startswith(filename):
                description = line.split("=")[1]
                break

    return f"<h1>{description}</h1><img src='{url_for('static', filename=filename, _external=True)}' />"


@app.route("/", methods=["GET", "POST"])
def save():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOADS_FOLDER"], filename))

            # save the description
            description = request.form.get("description") or "Boo, no description"
            with open(
                os.path.join(app.config["UPLOADS_FOLDER"], "data.txt"), "r+"
            ) as f:
                for line in f.readlines():
                    if line.startswith(filename):
                        # replace the line
                        line = f"{filename}={description}\n"
                        break
                else:
                    # no line found, append to the end
                    line = f"{filename}={description}\n"
                f.write(line)

            # create the qr code
            url = url_for("uploaded_file", filename=filename, _external=True)
            print("generated url: ", url)
            qr = qrcode.make(url)
            qr.save(os.path.join(app.config["UPLOADS_FOLDER"], filename + "_qr.png"))
            return send_from_directory(
                app.config["UPLOADS_FOLDER"], filename + "_qr.png"
            )
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=text name=description>
      <input type=submit value=Upload> 
    </form>
    """
