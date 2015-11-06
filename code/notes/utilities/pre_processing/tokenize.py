
import subprocess
import os
import re
import sys

xml_utilities_path = os.environ["TEA_PATH"] + "/code/notes/utilities"
sys.path.insert(0, xml_utilities_path)

import xml_utilities
import timeml_utilities
import news_reader

def _get_text_element(ixa_tok_output):

   xml_root = xml_utilities.get_root_from_str(ixa_tok_output)

   text_element = None

   for e in xml_root:
       if e.tag == "text":
           text_element = e
           break

   return text_element


def _get_naf_tokens(ixa_tok_output):

    text_element = _get_text_element(ixa_tok_output)

    naf_tokens = []

    for e in text_element:
        naf_tokens.append(e)

    return naf_tokens


def get_tokens(ixa_tok_output):

    tokens = []

    for naf_token in _get_naf_tokens(ixa_tok_output):

        sentence_num = int(naf_token.attrib["sent"])
        id_string    = naf_token.attrib["id"]

        tok_start    = int(naf_token.attrib["offset"])
        token_end    = tok_start + int(naf_token.attrib["length"]) - 1

        token_text   = naf_token.text

        tokens.append({"token":token_text, "id":id_string, "sentence_num":sentence_num, "start_offset":tok_start, "end_offset":token_end})

    return tokens


if __name__ == "__main__":
    text = timeml_utilities.get_text("APW19980219.0476.tml")
    print text
    print get_tokens(news_reader.pre_process(text))
    pass
# EOF
