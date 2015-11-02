
import xml.etree.ElementTree as ET
from note_utils import valid_path

import xml_utilities

def get_text_element(timeml_doc):

    root = xml_utilities.get_root(timeml_doc)

    text_element = None

    for e in root:
        if e.tag == "TEXT":

            text_element = e
            break

    return text_element

def get_text(timeml_doc):
    """ gets raw text of document, xml tags removed """

    text_e = get_text_element(timeml_doc)

    text_e = text_e

    string = list(ET.tostring(text_e, encoding='utf8', method='text'))

    # retains a newline after <TEXT> tag...
    if string[0] == '\n':
        string.pop(0)

    if string[-1] == '\n':
        string.pop(len(string) - 1)

    return "".join(string)


def get_tagged_entities(timeml_doc):
    """ gets tagged entities within timeml text """

    text_element = get_text_element(timeml_doc)

    elements = []

    for element in text_element:

        elements.append(element)

    return elements

if __name__ == "__main__":
    print "nothing to do here"

# EOF

