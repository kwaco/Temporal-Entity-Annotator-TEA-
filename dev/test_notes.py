"""Debugging TimeNote
"""

# temporary until NN interface is updated
import cPickle

import re
import sys
import os

TEA_HOME_DIR = os.path.join(*([os.path.dirname(os.path.abspath(__file__))] +['..']))

sys.path.insert(0, TEA_HOME_DIR)

from code.config import env_paths

# this needs to be set. exit now so user doesn't wait to know.
if env_paths()["PY4J_DIR_PATH"] is None:
    sys.exit("PY4J_DIR_PATH environment variable not specified")

import argparse
import glob
import cPickle

timenote_imported = False


def main():

    global timenote_imported

    """ Process command line arguments and then generate trained models (4, one for each pass) on files provided.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("notes_dir",
                        help="Directory containing training input and gold annotations")
    parser.add_argument("newsreader_annotations",
                        help="Where newsreader pipeline parsed file objects go")
    parser.add_argument("annotations",
                        help="Where annotated notes are written")

    args = parser.parse_args()

    if os.path.isdir(args.notes_dir) is False:
        sys.exit("invalid path for time note dir")
    if os.path.isdir(args.newsreader_annotations) is False:
        sys.exit("invalid stashed notes dir")

    notes_dir = None
    newsreader_dir = args.newsreader_annotations

    print
    print "\t\tNotes DIR: ",args.notes_dir
    print

    notes_dir = args.notes_dir + '/*'

    # get files in directory
    files = glob.glob(notes_dir)

    gold_files = {}
    tml_files  = {}

    for f in files:
        if "TE3input" in f:
            k = re.sub(".TE3input","",os.path.basename(f))
            tml_files[k] = f
        else:
            gold_files[os.path.basename(f)] = f

    print
    print "\t\tGold Files: ",gold_files
    print

    print
    print "\t\tRaw Files: ", tml_files
    print

    #sys.exit("done")

    pickled_timeml_notes = [os.path.basename(f) for f in glob.glob(args.newsreader_annotations + "/*")]

    print
    print "\t\tPickled Files: ", pickled_timeml_notes
    print

    #sys.exit("done")

    notes = []

    for tml in tml_files:

        # print tml + ".parsed.pickle"

        if tml + ".parsed.pickle" in pickled_timeml_notes:
            tmp_note = cPickle.load(open(newsreader_dir + "/" + tml + ".parsed.pickle", "rb"))
            notes.append(tmp_note)
        else:
            if timenote_imported is False:
                from code.notes.TimeNote import TimeNote
                timenote_imported = True
            tmp_note = TimeNote(tml_files[tml],gold_files[tml])
            notes.append(tmp_note)
            cPickle.dump(tmp_note, open(newsreader_dir + "/" + tml + ".parsed.pickle", "wb"))

    #sys.exit("done")

    print notes

#    sys.exit("done")

    for note in notes:
        # get entity pairs, offsets, tokens, and event/timex entities
        tlink_pair = note.get_tlink_id_pairs()
        offsets = note.get_token_char_offsets()

        # flatten list of tokens
        tokenized_text = note.get_tokenized_text()
        tokens = []
        for line in tokenized_text:
            tokens += tokenized_text[line]

        event_timex_labels = []
        # flatten list of labels
        for label_list in note.get_labels():
            event_timex_labels += label_list

        tlink_labels = note.get_tlink_labels()

        # write(self, timexEventLabels, tlinkLabels, idPairs, offsets, tokens, output_path)
        note.write(event_timex_labels, tlink_labels, tlink_pair, offsets, tokens, args.annotations)


if __name__ == "__main__":
    main()
