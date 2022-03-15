# Thanks: https://github.com/viveksb007/camscanner_watermark_remover/blob/master/app.py
from app import app
from flask import (
    request,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    send_file,
)
from werkzeug.utils import secure_filename
import os, pathlib, io
from app import check

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/uploads/"
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/downloads/"
ALLOWED_EXTENSIONS = {"xlsx", "csv"}

# app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            print("No file attached in request")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            print("No file selected")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            sfile1 = pathlib.Path.cwd() / "app" / "uploads" / filename
            report_errors = check.process_marksbook(sfile1)
            os.remove(sfile1)
            #            return redirect(url_for("uploaded_file", filename=report_name))
            if len(report_errors) != 0:
                return render_template(
                    "public/report_page.html",
                    title="Report Check",
                    error_list=report_errors,
                )
            directory_path = pathlib.Path.cwd() / "app" / "downloads"
            dir_list = os.listdir(directory_path)
            if len(dir_list) != 0:
                filename = dir_list[0]
                return redirect(url_for("download_file", file_name=filename))
    return render_template("public/index.html")


# Not using this function, creates 'Save file' dialog, but does not delete uploaded.downloaded files from server
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["DOWNLOAD_FOLDER"], filename, as_attachment=True
    )


@app.route("/report/<error_list>")
def report(error_list):
    print(error_list)
    return render_template("public/report_page2.html", error_list=error_list)


@app.route("/about")
def about():
    return "All about Flask"


@app.route("/help")
def help():
    return render_template("public/help.html")


@app.route("/download/<file_name>")
def download_file(file_name):
    return_data = io.BytesIO()
    file_path = pathlib.Path.cwd() / "app" / "downloads" / file_name
    with open(file_path, "rb") as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)
    os.remove(file_path)
    return send_file(
        return_data,
        mimetype="application/pdf",
        attachment_filename=file_name,
    )
