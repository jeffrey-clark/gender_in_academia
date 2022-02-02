import os, io, re
from Functions.j_functions import *

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

#en_dic = project_root + "/Dictionaries/english.dic"
en_dics = project_root + "/Dictionaries/english"
sv_dics = project_root + "/Dictionaries/swedish"


def get_filepaths(directory_filepath):
    paths = []
    contents = os.listdir(directory_filepath)
    for c in contents:
        p = directory_filepath + "/" + c
        paths.append(p)
    return paths

def get_file_contents(filepath):
    file = io.open(filepath, "r", encoding='utf-8')
    lines = file.read()
    return lines

def check_dic(dic, word):
    #re_code = re.compile(r'(^' + word + '$)')
    reg = re.search(r'\n\b' + re.escape(word.lower()) + r'\b\n', dic.lower())

    if reg != None:
        # print("found")
        return True
    else:
        # print("not found")
        return False


def check_dics(language, word):
    found = False
    map = {"en": en_dics, "sv": sv_dics}
    for f in get_filepaths(map[language]):
        dic = get_file_contents(f)
        found = check_dic(dic, word)
        if found:
            break
    return found



def check_english(word):
    found = check_dics("en", word)
    return found

def check_swedish(word):
    # found is True if the word is found
    found = check_dics("sv", word)

    # if not found we make the following adjustments
    if not found:
        # make singular
        plural_endings = ['ar', 'er']
        if word[-2:] in plural_endings:
            word = word[:-2]
            found = check_dics("sv", word)

    return found


def identify_language(word):
    en = check_english(word)
    sv = check_swedish(word)

    if en and not sv:
        return "english"
    elif sv and not en:
        return "swedish"
    elif sv and en:
        return "both"
    else:
        return None


def identify_language_list(list):
    total = Counter()
    for x in list:
        # check if there are mulitple words in the list cell
        words = str(x).split(" ")
        for w in words:
            lang = identify_language(w)
            total.add(lang, w)
    total.compute()

    # print the lists of words belonging to respective language
    #print(total.ref)

    # determine which language
    keys = total.dic.keys()
    if 'english' not in keys:
        total.dic['english'] = 0
    if 'swedish' not in keys:
        total.dic['swedish'] = 0
    if 'both' not in keys:
        total.dic['both'] = 0

    swedish = total.dic['both'] + total.dic['swedish']
    english = total.dic['both'] + total.dic['english']

    identified = None
    if (english >= swedish) and (english != 0):
        identified = 'english'
    elif (swedish > english) and (swedish != 0):
        identified = 'swedish'

    return identified



if __name__ == "__main__":


    words = ["Hygiene", "mango", "health"]

    for w in words:
        lang = identify_language(w)
        if lang == "both":
            print(w, "is both a swedish and an english word!")
        elif lang == "english":
            print(w, "is an english", "word!")
        elif lang == "swedish":
            print(w, "is a swedish", "word!")
        else:
            print( w, "was not found...")

    list = ['Aging phenotypes', 'Disability', 'Frailty', 'Latent variable mixture modeling', 'Multimorbidity']

    print(identify_language_list(list))