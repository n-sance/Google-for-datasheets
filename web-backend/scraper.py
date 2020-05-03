""" file with the main scraping & searching logic """
import searcher


def get_file_link(filename):
    import os
    return os.path.join(os.path.dirname(__file__), "files", filename)


def search(filename="swau123.pdf", tags=["RESET", "33"]):
    """
        does operations with DB and Yandex Vision and returns the result
        :returns: {RESULT}
    """
    file_location = filename
    #return {"pdf_result": "https://wp.gravityhub.org", "confidence": 0.5}
    return searcher.main(file_location, tags)
