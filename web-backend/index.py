from flask import Flask, jsonify, request, send_file
import scraper

app = Flask(__name__)


ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def random_id():
    import random
    rid, required_len = "", 12
    syms_collection = "qwertyuiopasdfghjklzxcvbnm123456789"
    for n in range(required_len):
        rid += syms_collection[random.randint(0, len(syms_collection)-1)]
    return rid


def save_file(meta, file):
    if not allowed_file(file.filename):
        raise("not allowed file format")
    filename = meta["name"] + "_" + random_id() + "." + file.filename.rsplit('.', 1)[1].lower()
    file.save(scraper.get_file_link(filename))
    return filename


@app.route("/")
def index():
    return "test text"


@app.route("/upload", methods=["POST"])
def upload_doc():
    """
        call this to upload a new datasheet
        attach the name as an additional argument
    """
    file = request.files["file"]
    meta_data = {"name": request.form["name"]}
    file_id = save_file(meta_data, file)
    return jsonify({"file_id": file_id})


@app.route("/search", methods=["GET"])
def search():
    """
        call this to search in a file using given keywords
        provide following arguments in a query:
            component-name =
            keywords = TAG1;TAG2
    """
    componentName = request.args["component-name"]
    tags = [t.lower() for t in request.args["keywords"].split(";")]
    search_result = scraper.search(componentName, tags)
    return send_file(search_result, as_attachment=True)


@app.after_request
def after_request(response):
    header = response.headers
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5050', debug=True)
