""" file with the main scraping & searching logic """
import searcher
from PyPDF2 import PdfFileWriter, PdfFileReader


def get_file_link(filename):
    import os
    return os.path.join(os.path.dirname(__file__), "files", filename)


def search(filename="swau123.pdf", tags=["RESET", "33"], alldocs= False):
    print('aldocs:   ' + str(alldocs))
    """
        does operations with DB and Yandex Vision and returns the result
        :returns: {RESULT}
    """
    filename = filename.rsplit("/", 1)[-1]
    print('filename' + filename)

    # try:
    if (alldocs == True):
        print('inside')
        resp = searcher.search_across_all_docs(tags, filename)

        print('_________resp content: ' + str(resp))
        filename, page = resp[max(list(resp.keys()))]
        print('single_doc:filename:  ' + str(filename))
        print('single_doc:page:    ' + str(page))
        #print('pagenumber:  ' + str(resp[p][1]))
        #print('pagenumber:  ' + str(page_number))
        page_number = int(page)
        output_writer = PdfFileWriter()

        inputpdf = PdfFileReader(open(get_file_link(filename), "rb"))
        output_writer.addPage(inputpdf.getPage(page_number))

        with open("result.pdf", "wb") as outputStream:
            output_writer.write(outputStream)
            print("pdf file has been rewritted")

        return resp
    else:
        resp = searcher.search_in_download_doc(tags, filename) # [{2: 1.0015404}]
        print('response_text_single_doc: ' + str(resp))
        #page_number = list(resp[0].keys())[0] - 1
        filename, page = resp[max(list(resp.keys()))]
        print('single_doc:filename:  ' + str(filename))
        print('single_doc:page:    ' + page)
        #print('pagenumber:  ' + str(resp[p][1]))
        #print('pagenumber:  ' + str(page_number))
        page_number = int(page)
        output_writer = PdfFileWriter()

        inputpdf = PdfFileReader(open(get_file_link(filename), "rb"))
        output_writer.addPage(inputpdf.getPage(page_number))

        with open("result.pdf", "wb") as outputStream:
            output_writer.write(outputStream)
            print("pdf file has been rewritted")
        return resp
    # except:
        # return('Nothing found')




