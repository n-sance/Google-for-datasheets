# coding: utf-8
from requests import post
import json
import argparse
import base64
import os
import glob
from PyPDF2 import PdfFileWriter, PdfFileReader
from pathlib import Path
from elasticsearch import Elasticsearch
import io

my_folder_id = 'b1gcfjsk4iff6ub1luh8'
elasticSearchAddress =  None
# Функция возвращает IAM-токен для аккаунта на Яндексе. В данный момент не используется


def get_iam_token(oauth_token):
    iam_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    response = post(iam_url, json={"yandexPassportOauthToken": oauth_token})
    json_data = json.loads(response.text)
    if json_data is not None and 'iamToken' in json_data:
        return json_data['iamToken']
    return None

# Функция отправляет на сервер запрос на распознавание изображения и возвращает ответ сервера.


def request_analyze(vision_url, iam_token, folder_id, image_data, is_pdf=False):
    json_body = {
        'folderId': folder_id,
        'analyzeSpecs': [
            {
                'content': image_data,
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                        'textDetectionConfig': {'languageCodes': ['*']}
                    }
                ],
            }
        ]}

    # check pdf file and add mime_type
    if is_pdf:
        json_body["analyzeSpecs"][0]["mime_type"] = "application/pdf"
    response = post(vision_url, headers={
                    'Authorization': 'Bearer '+iam_token}, json=json_body)
    return response.text


def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    results = extract(obj, arr, key)
    return results


def add_to_elasticSearch(pdfName, page, text_result, es):
    doc = {"text": text_result}
    print('before adding')
    res = es.index(index=str.lower(pdfName), id=page, body=doc)
    print('res:  ' + str(res))


def page_indexing(inputpdf, vision_url, iam_token, folder_id, es, pdfname):
    for page in range(inputpdf.getNumPages()):
        print(page)
        writer = PdfFileWriter()
        writer.addPage(inputpdf.getPage(page))
        writer.write(open('page.pdf', 'wb'))
        with open('page.pdf', 'rb') as page_pdf:
            image_data = base64.b64encode(page_pdf.read()).decode('utf-8')
            response = request_analyze(
                vision_url, iam_token, folder_id, image_data, is_pdf=True)
            response_json = json.loads(response)
            text_result = ' '.join(
                map(str, extract_values(response_json, 'text')))
            print(text_result)
            add_to_elasticSearch(pdfname, page, text_result, es)


def index_after_uploading(pdfname):
    inputpdf = PdfFileReader(open(get_link("files", pdfname), "rb"))
    oauth_token = "AgAAAAADng-8AATuwdOGGyg3l0VHmz1w3Ighmvc"
    iam_token = get_iam_token(oauth_token)
    folder_id = my_folder_id
    print("before elstic")
    es = Elasticsearch()
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    answer = page_indexing(inputpdf, vision_url,
                           iam_token, folder_id, es, pdfname)


def search_pages(inputpdf, tags, pdfname):
    es = Elasticsearch()

    query_from_user = ' '.join(tags)
    res = es.search(index=str.lower(pdfname), body={"query": {
        "query_string": {
            "query": query_from_user
        }}})
    more_appropriate_page = {}
    for hit in res['hits']['hits']:
        more_appropriate_page[hit["_score"]] = [pdfname,hit["_id"]]
    # pages = []
    # for hit in res['hits']['hits']:
    #     pages.append({int(hit["_id"]): hit["_score"]})
    print('res___ :  ' + str(res))
    print('more_appr:   ' + str(more_appropriate_page) + '  ' + str(tags))
    return more_appropriate_page



# def search_pages(inputpdf, tags, pdfname):
#     # my private data
#     oauth_token = "AgAAAAADng-8AATuwdOGGyg3l0VHmz1w3Ighmvc"
#     iam_token = get_iam_token(oauth_token)
#     folder_id = my_folder_id
#     es = Elasticsearch()
#     vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
#     answer = page_indexing(inputpdf, vision_url,
#                            iam_token, folder_id, es, pdfname)
#     query_from_user = ' '.join(tags)
#     res = es.search(index=str.lower(pdfname), body={"query": {
#         "query_string": {
#             "query": query_from_user
#         }}})
#     more_appropriate_page = {}
#     for hit in res['hits']['hits']:
#         more_appropriate_page[hit["_score"]] = [pdfname,hit["_id"]]
#     # pages = []
#     # for hit in res['hits']['hits']:
#     #     pages.append({int(hit["_id"]): hit["_score"]})
#     print('res___ :  ' + str(res))
#     print('more_appr:   ' + str(more_appropriate_page) + '  ' + str(tags))
#     return more_appropriate_page



def search_across_specific_docs(tags, component_name):
    es = Elasticsearch()
    print('component name inside ES:  ' + str(component_name) + ' ' + str(type(component_name)))
    # if component_name:
    #     tags.append(component_name[0].split('_')[0])
    query_from_user = ' '.join(tags)
    indices = es.indices.get_alias("*")  # etract all created indexes
    filtered_indices = {}
    for k, v in indices.items():
        if k.startswith(component_name):
            filtered_indices[k] = v
    print('indices:   ' + str(indices) + ' ' + str(type(indices)))
    print('filtered indices' + str(filtered_indices))
    search_result = {}
    print('query from user:' + str(query_from_user))
    for index in filtered_indices:
        res = es.search(index=index, body={"query": {
            "query_string": {
                "query": query_from_user
            }}})
        pages = []
        for hit in res['hits']['hits']:
            pages.append({int(hit["_id"]): hit["_score"]})
        search_result[index] = pages
    more_appropriate_page = {}
    for index in search_result:
        for pages in search_result[index]:
            for page in pages:
                score = pages[page]
                more_appropriate_page[score] = [index,page]
    return more_appropriate_page


def search_across_all_docs(tags, component_name):
    es = Elasticsearch()
    print('component name inside ES:  ' + str(component_name) + ' ' + str(type(component_name)))
    if component_name:
        tags.append(component_name)
    query_from_user = ' '.join(tags)
    indices = es.indices.get_alias("*")  # etract all created indexes
    print('indices:   ' + str(indices) + ' ' + str(type(indices)))
    search_result = {}
    print('query from user:' + str(query_from_user))
    for index in indices:
        res = es.search(index=index, body={"query": {
            "query_string": {
                "query": query_from_user
            }}})
        pages = []
        for hit in res['hits']['hits']:
            pages.append({int(hit["_id"]): hit["_score"]})
        search_result[index] = pages
    more_appropriate_page = {}
    for index in search_result:
        for pages in search_result[index]:
            for page in pages:
                score = pages[page]
                more_appropriate_page[score] = [index,page]
    return more_appropriate_page
# # work with absolute links
def get_link(*filename):
    return os.path.join(os.path.dirname(__file__), *filename)

def search_in_download_doc(tags, pdfname):
    inputpdf = PdfFileReader(open(get_link("files", pdfname), "rb"))
    print(inputpdf)
    pages = search_pages(inputpdf, tags, pdfname)
    return pages
