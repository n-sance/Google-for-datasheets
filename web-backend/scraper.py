""" file with the main scraping & searching logic """
import searcher
from PyPDF2 import PdfFileWriter, PdfFileReader


def get_file_link(filename):
    import os
    return os.path.join(os.path.dirname(__file__), "files", filename)


def search(filename="swau123.pdf", tags=["RESET", "33"], alldocs= False):
    """
        does operations with DB and Yandex Vision and returns the result
        :returns: {RESULT}
    """
    filename = filename.rsplit("/", 1)[-1]
    print('filename' + filename)
    resp = searcher.search_in_download_doc(tags, filename) # [{2: 1.0015404}]
    print('response_text: ' + str(resp))
    try:
        if (alldocs ==True):
            resp = searcher.search_across_all_docs(tags, filename)
            print('alldocs?')
        else:
            #page_number = list(resp[0].keys())[0] - 1
            p = next(iter(resp))

            print('pagenumber:  ' + str(resp[p][1]))
            #print('pagenumber:  ' + str(page_number))
            page_number = int(resp[p][1])
            output_writer = PdfFileWriter()

            inputpdf = PdfFileReader(open(get_file_link(filename), "rb"))
            output_writer.addPage(inputpdf.getPage(page_number))

            with open("result.pdf", "wb") as outputStream:
                output_writer.write(outputStream)
                print("pdf file has been rewritted")

            return resp
    except IndexError:
        return('Nothing found')




