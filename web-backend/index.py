from flask import Flask, jsonify, request, send_file
import scraper
from glob import glob
import os
from searcher import index_after_uploading

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
    return "you are a king"


@app.route("/upload", methods=["POST"])
def upload_doc():
    """
        call this to upload a new datasheet
        attach the name as an additional argument
    """
    file = request.files["file"]
    meta_data = {"name": request.form["name"].lower()}
    file_id = save_file(meta_data, file)
    print('file-id:  ' + file_id)
    index_after_uploading(file_id)
    return jsonify({"file_id": file_id})


@app.route("/search_by_fileid", methods=["GET"])
def search_by_fileid():
    """
        call this to search in a file using given keywords
        provide following arguments in a query:
            file-id = STRING
            keywords = TAG1;TAG2
    """
    file_id = request.form["file-id"]
    tags = [t.lower() for t in request.form["keywords"].split(";")]
    search_result = scraper.search(file_id, tags)
    return jsonify(search_result)



@app.route("/search", methods=["GET"])
def search():
    """
        call this to search in a file using given keywords
        provide following arguments in a query:
            component-name =
            keywords = TAG1;TAG2
    """
    component_name = request.args["component-name"].lower()
    print('compname:   ' + component_name)
    all_docs = request.args["all-docs-search"]
   # last_doc_only = request.args["prev-doc"]

    all_docs_flag = True if all_docs == 'true' else False
    print('all_docs:  ' + str(all_docs_flag))
    #last_doc_only_flag = True if last_doc_only == 'true' else False
    files = glob(scraper.get_file_link("*"))
    print('files:  ' + str(files))
    files.sort(key=os.path.getmtime)
    if component_name:
        matching_files = [f for f in files if component_name in f]
        print('matching files:  ' + str(matching_files))
        file_id = matching_files[-1]
    else:
        file_id = ""
    tags = [t.lower() for t in request.args["keywords"].split(";")]
    print(tags)
    if len(tags) < 1:
        return "ERROR: NO TAGS"
    search_result = scraper.search(file_id, tags, all_docs_flag)
    if (search_result == 'Nothing found'):
        return {}   #todo handler on frontend side
    else:
        return send_file("result.pdf", as_attachment=True)


@app.after_request
def after_request(response):
    header = response.headers
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


if __name__ == "__main__":
    app.run(host='127.0.0.1', port='5050', debug=True)
