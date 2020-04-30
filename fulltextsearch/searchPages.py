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

ya_token = 'CggVAgAAABoBMxKABDM8yywhBhQWajzMY2w5Xl7MZYc15h8MrgWk2ulgXIm-cLbFVqRYDtnhK3DdYqtZ_HxafBSemnlDI_e_4fSRgDEfGKMGfPA14sow4XqPMVa6BcvWXEqz-cWd_JxtBF4jI42eGvE0PZxzP9TM-8B0ZLavTkPd21Fn5UEM4CXE_aC_o70p7Yc5XqfGJSxKOZf5kSuasSnvlXdrfXx-nkt6N2Tr8gnBZPw8Cx_0bsG-GfW7DNQr19Fmbyi5PPnsPfNyytjcxNi1T_Sm8MGw-ezeltHQodgYLRa11rNcsxL8t6DmhJxrsqb0-MwKo9sxrF1Y-8d3h_xu3RdSg90lf_muXCZlEXoV1JzLzTQgaGfdZCC-uc5Xa90ZNE-yApMxj10gdH50OCL5ogA2_tjOVibBumd3MPpZoXNBvflXxEujt5D-165_MCXycsVg_bD-c877sku6p_tdz0B96HfELK5giHh3JHHAh4wmKxhkuxIE4blAbjovfRHGYZJ8sz4E_PhAhJIVmq-REb0w2WrWaFODEpZXHZI77Msic4c9viZTxcy2vPrmr8SzLvNDm897B-hxrAWbHuCp1XVA-bA8Hp-g7A9AcTNmaF3IdjgVyu6d-pRw_XH7ZxDwYpSmlVufqsKlTqzmQ93KPFaRW8SNqilUhAi26L8GXIsXDgz_BeoRzOtuGiQQ69-p9QUYq7Gs9QUiFgoUYWplOHRpNTRmcjEwbG1jNWxncTc='
my_folder_id = 'b1gcfjsk4iff6ub1luh8'

# Функция возвращает IAM-токен для аккаунта на Яндексе. В данный момент не используется


def get_iam_token(iam_url, oauth_token):
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


def addToElasticSearch(pdfName, page, text_result, es):
    doc = {"text": text_result}
    res = es.index(index=str.lower(pdfName), id=page, body=doc)


def pageIndexing(inputpdf, vision_url, iam_token, folder_id, es, pdfname):
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
            addToElasticSearch(pdfname, page, text_result, es)


def searchPages(inputpdf, tags, pdfname):
    # my private data
    iam_token = ya_token
    folder_id = my_folder_id
    es = Elasticsearch()
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    answer = pageIndexing(inputpdf, vision_url, iam_token, folder_id, es, pdfname)
    query_from_user = ' '.join(tags)
    res = es.search(index= pdfname, body={"query": {
        "query_string": {
            "query": query_from_user
        }}})
    pages = []
    for hit in res['hits']['hits']:
        pages.append({int(hit["_id"])+1 : hit["_score"]})
    return pages


def main():
    inputpdf = PdfFileReader(open("swau123.pdf", "rb"))
    tags = ["RESET", "33"]
    pdfname = "swau123.pdf"
    pages = searchPages(inputpdf, tags, pdfname)
    print("serach tags:" + str(tags), pages)
    return pages


if __name__ == '__main__':
    main()
