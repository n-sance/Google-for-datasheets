""" file with the main scraping & searching logic """


def get_file_link(filename):
    import os
    return os.path.join(os.path.dirname(__file__), "files", filename)


def search(filename, tags):
    """
        does operations with DB and Yandex Vision and returns the result
        :returns: {RESULT}
    """
    file_location = get_file_link(filename)
    #return {"pdf_result": "https://wp.gravityhub.org", "confidence": 0.5}
    return (file_location)
