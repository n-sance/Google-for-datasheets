""" file with the main scraping & searching logic """
import searcher
from PyPDF2 import PdfFileWriter, PdfFileReader


def get_file_link(filename):
    import os
    return os.path.join(os.path.dirname(__file__), "files", filename)


def search(filename="swau123.pdf", tags=["RESET", "33"]):
    """
        does operations with DB and Yandex Vision and returns the result
        :returns: {RESULT}
    """
    filename = filename.rsplit("/", 1)[-1]
    resp = searcher.main(filename, tags) # [{2: 1.0015404}]
    page_number = list(resp[0].keys())[0] - 1

    output_writer = PdfFileWriter()

    inputpdf = PdfFileReader(open(get_file_link(filename), "rb"))
    output_writer.addPage(inputpdf.getPage(page_number))

    with open("result.pdf", "wb") as outputStream:
        output_writer.write(outputStream)

    return resp


