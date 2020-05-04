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
    es = Elasticsearch()
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    answer = page_indexing(inputpdf, vision_url,
                           iam_token, folder_id, es, pdfname)

def search_pages(inputpdf, tags, pdfname):
    # my private data
    oauth_token = "AgAAAAADng-8AATuwdOGGyg3l0VHmz1w3Ighmvc"
    iam_token = get_iam_token(oauth_token)
    folder_id = my_folder_id
    es = Elasticsearch()
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    answer = page_indexing(inputpdf, vision_url,
                           iam_token, folder_id, es, pdfname)
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

def search_across_all_docs(tags, component_name):
    es = Elasticsearch()
    tags.append(component_name.split('_')[0])
    query_from_user = ' '.join(tags)
    indices = es.indices.get_alias("*")  # etract all created indexes
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

#inputpdf = PdfFileReader(open("swau123.pdf", "rb"))
# tags = ["development", "V"]
# pdfname = "swau123.pdf"

# if __name__ == '__main__':
#     search_in_download_doc(inputpdf, tags, pdfname)

#print(search_across_all_docs(tags))






# # coding: utf-8
# from requests import post
# import json
# import argparse
# import base64
# import os
# import glob
# from PyPDF2 import PdfFileWriter, PdfFileReader
# from pathlib import Path
# from elasticsearch import Elasticsearch
# import io


# # work with absolute links
# def get_link(*filename):
#     return os.path.join(os.path.dirname(__file__), *filename)

# ya_token='CggVAgAAABoBMxKABJj-UDYU2avSsGaGvJzz-4e59gU9sGOSXPa_XnsGmT8JVQP7x_1l2C8SeWuWNxcOG_KGfYV_4lZ1Xmlncw_VyifCupgGy04l0q3l58Pa30n6DxOOybWFpiaurM8QAXzv3grN2Mk-SXjrEm8ErHH74uQR1Z5E0C054oCZMuHx5k15nYnrZM-zK9RLqAjCgIEvV9FzLO6p24JhAwExyA-o84xSu64M7XHyQaENu-wR4XPYcFLo9mfyHMnq3QMpoAY8Kb2vS8-dg4PBh8MfXkzk62EoxWazxLfA6hj_8bzrsaKw98a9-u9-3EGdSTz0BxHOuK-RTLbf5JjT_tIiEEYmIZ9pmG-jU09iFND1zSSiXIw9cvA-mp6foit-IpeIPfZjjY0DHEtw53-kKiNQiiI7codPdfhrzON29mr1WZOWUCkue6LmbM2RtYNs7n1jTIsE_StJWBnN7VobdqDaKKWoFsJBubfwDj71p5HTTkCSlwWYapE3z_NivjaKvv_KSSFlGCCN9JfBdv25TDZDcUvXPgAT5Rn43loPmvZmuT0IDCuR0VwpVnnujylNP-jHHM7aR7YaNOR85iPmaAMYiwJlcPqg8b0NuPhjKm5Ms7DMULXez597iLwmwoxx7h-xHLbcPbIEciGuxYbe5scQYfQToMW5pwHiKx1GPbJ_vibEvCGmGiQQ1LC_9QUYlILC9QUiFgoUYWplaGcxc3QyZmZ2OGw1b29zMnU='
# #ya_token = 'CggVAgAAABoBMxKABI_sr1wuSaU42mVh69XVUTihZpHr8qZXfJPFIs4X3MZZSIn2i0fZJOY9ssRy-oJyRgZK52lyJr9IMLq0qcsv3x2i1tE2SYNGDv9bIsG37TvUTC13bZLkGd_jFXVCZbgnWB6erz9AcS0U22F1c8-eKYvxHAKwav6oVryrz0hbn8FhpBA1b9KuyPFnjnuE1oTo2HeLM6rFpS9n_3z5WOAjL-kr9SD1HGucBnB_rgjyMpWREgS0x6qOte37Zbyzl7liaCidNl8x2H4LlCrkRt7fyV7TT2xoAYUiGGaj8ualVcOg4izDhwwwMTGx8p9_j08aHnwDiDXexN3T3ecX998mAG5rDMKRjjVt-m6CFwt8zmAwRgM-5mefU4RoJ_cM5TH8OVzTuS8VwAaZYkDnSr7FYiJXNNk-y-UM7maQ9X64A6Y0w126zLw_fFluD9n_4lOimw_uTAFmU-UKsrT8fG4ycK7tR5WqlHjCOXD-zcADtUL-8WE5T9tyUuBMTlNQCY-V-n20BYkAebgUR9u38BEBf3NF3VKln342LR7S8ZneYk9NtbJVZzZntsOvdQhyULYNsoinyehR3l3ju1YX-mCAYRxpc9XtWmPU3ZkDrFPoPfjyw3PdjjcQIVgChvT5AjtewYiBqw09RuUomRuGNXJpQcqmSzd2GTMXn9I2a7Q5Ptn3GiQQyvu79QUYis2-9QUiFgoUYWplOHRpNTRmcjEwbG1jNWxncTc='
# my_folder_id = 'b1gcfjsk4iff6ub1luh8'

# # Функция возвращает IAM-токен для аккаунта на Яндексе. В данный момент не используется

# def get_iam_token(iam_url='https://iam.api.cloud.yandex.net/iam/v1/tokens', oauth_token='AgAEA7qjPwAEAATuwSCkTldfjEPjj-L75YCrLnY'):
#     response = post(iam_url, json={"yandexPassportOauthToken": oauth_token})
#     print('get_iam_token_response:   ' + str(response))
#     json_data = json.loads(response.text)
#     if json_data is not None and 'iamToken' in json_data:
#         return json_data['iamToken']
#     return None

# # Функция отправляет на сервер запрос на распознавание изображения и возвращает ответ сервера.


# def request_analyze(vision_url, iam_token, folder_id, image_data, is_pdf=False):
#     json_body = {
#         'folderId': folder_id,
#         'analyzeSpecs': [
#             {
#                 'content': image_data,
#                 'features': [
#                     {
#                         'type': 'TEXT_DETECTION',
#                         'textDetectionConfig': {'languageCodes': ['*']}
#                     }
#                 ],
#             }
#         ]}

#     # check pdf file and add mime_type
#     if is_pdf:
#         json_body["analyzeSpecs"][0]["mime_type"] = "application/pdf"
#     response = post(vision_url, headers={
#                     'Authorization': 'Bearer '+iam_token}, json=json_body)
#     return response.text


# def extract_values(obj, key):
#     """Pull all values of specified key from nested JSON."""
#     arr = []

#     def extract(obj, arr, key):
#         """Recursively search for values of key in JSON tree."""
#         if isinstance(obj, dict):
#             for k, v in obj.items():
#                 if isinstance(v, (dict, list)):
#                     extract(v, arr, key)
#                 elif k == key:
#                     arr.append(v)
#         elif isinstance(obj, list):
#             for item in obj:
#                 extract(item, arr, key)
#         return arr
#     results = extract(obj, arr, key)
#     return results


# def addToElasticSearch(pdfName, page, text_result, es):
#     doc = {"text": text_result}
#     res = es.index(index=str.lower(pdfName), id=page, body=doc)


# def pageIndexing(inputpdf, vision_url, iam_token, folder_id, es, pdfname):
#     for page in range(inputpdf.getNumPages()):
#         print(page)
#         writer = PdfFileWriter()
#         writer.addPage(inputpdf.getPage(page))
#         writer.write(open('page.pdf', 'wb'))
#         with open('page.pdf', 'rb') as page_pdf:
#             image_data = base64.b64encode(page_pdf.read()).decode('utf-8')
#             response = request_analyze(
#                 vision_url, iam_token, folder_id, image_data, is_pdf=True)
#             print('response  ' + response)
#             response_json = json.loads(response)
#             text_result = ' '.join(
#                 map(str, extract_values(response_json, 'text')))
#             print(text_result)
#             addToElasticSearch(pdfname, page, text_result, es)


# def search_pages(inputpdf, tags, pdfname):
#     # my private data
#     iam_token = ya_token
#     folder_id = my_folder_id
#     es = Elasticsearch()
#     vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
#     answer = pageIndexing(inputpdf, vision_url, iam_token, folder_id, es, pdfname)
#     print('answer from yaV: ' + str(answer))
#     query_from_user = ' '.join(tags)
#     res = es.search(index= pdfname, body={"query": {
#         "query_string": {
#             "query": query_from_user
#         }}})
#     pages = []
#     for hit in res['hits']['hits']:
#         pages.append({int(hit["_id"])+1 : hit["_score"]})
#     print('pages:' + str(pages))
#     return pages


# def main(filename="swau123.pdf", tags=["RESET", "33"]):
#     inputpdf = PdfFileReader(open(get_link("files", filename), "rb"))
#     pdfname = filename
#     pages = search_pages(inputpdf, tags, pdfname)
#     return pages


# if __name__ == '__main__':
#     main()
