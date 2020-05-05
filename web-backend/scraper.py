""" file with the main scraping & searching logic """
import searcher
from PyPDF2 import PdfFileWriter, PdfFileReader


def get_file_link(filename):
    import os
    return os.path.join(os.path.dirname(__file__), "files", filename)


def search(filename, tags=[], searching_mode='Latest'):
    """
        does operations with DB and Yandex Vision and returns the result
        :returns: {RESULT}
    """
        # list_of_names = []
        # for i in filename:
        #     list_of_names.append(i.rsplit('/', 1)[-1])
        # print('list of names:  ' + str(list_of_names))

    filename = filename.rsplit('/', 1)[-1]
    print('filename after splitting' + str(filename))

    try:
        if (searching_mode == 'All'):
            print('inside All mode')
            resp = searcher.search_across_all_docs(tags, filename) # todo switch to string listofnames

            print('_________resp content: ' + str(resp))
            filen, page = resp[max(list(resp.keys()))]
            print('single_doc:filename:  ' + str(filen))
            print('single_doc:page:    ' + str(page))
            #print('pagenumber:  ' + str(resp[p][1]))
            #print('pagenumber:  ' + str(page_number))
            page_number = int(page)
            output_writer = PdfFileWriter()

            inputpdf = PdfFileReader(open(get_file_link(filen), "rb"))
            output_writer.addPage(inputpdf.getPage(page_number))

            with open("result.pdf", "wb") as outputStream:
                output_writer.write(outputStream)
                print("pdf file has been rewritted")

            return resp
        elif (searching_mode == 'Components'):
            print('inside Components mode')
            resp = searcher.search_across_specific_docs(tags, filename) # todo switch to string listofnames
            print('response_text_single_doc: ' + str(resp))
            #page_number = list(resp[0].keys())[0] - 1
            filen, page = resp[max(list(resp.keys()))]
            print('single_doc:filename:  ' + str(filen))
            print('single_doc:page:    ' + str(page))
            #print('pagenumber:  ' + str(resp[p][1]))
            #print('pagenumber:  ' + str(page_number))
            page_number = int(page)
            output_writer = PdfFileWriter()

            inputpdf = PdfFileReader(open(get_file_link(filen), "rb"))
            output_writer.addPage(inputpdf.getPage(page_number))

            with open("result.pdf", "wb") as outputStream:
                output_writer.write(outputStream)
                print("pdf file has been rewritted")
            return resp
        else:
            print('inside latest mode')
            resp = searcher.search_in_download_doc(tags, filename) # todo switch to string listofnames
            print('response_text_single_doc: ' + str(resp))
            #page_number = list(resp[0].keys())[0] - 1
            filen, page = resp[max(list(resp.keys()))]
            print('single_doc:filename:  ' + str(filen))
            print('single_doc:page:    ' + page)
            #print('pagenumber:  ' + str(resp[p][1]))
            #print('pagenumber:  ' + str(page_number))
            page_number = int(page)
            output_writer = PdfFileWriter()

            inputpdf = PdfFileReader(open(get_file_link(filen), "rb"))
            output_writer.addPage(inputpdf.getPage(page_number))

            with open("result.pdf", "wb") as outputStream:
                output_writer.write(outputStream)
                print("pdf file has been rewritted")
            return resp

    except:
        print('nothing was found')
        return('Nothing found')




