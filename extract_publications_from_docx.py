from Models.initialize import *
import Models.MsWordModel as WM
import Models.ImportModel as IM


directory = project_root + '/docx_files'
filenames = os.listdir(directory)
org_sheet = IM.original()


possible_types = {'Peer-reviewed publication':
                       ['peer-reviewed publications', 'bedömda artiklar', 'peer-reviewed articles',
                        'Peer-Reviewed Journals', 'Peer reviewed articles', 'peer reviewed original articles',
                        'peer reviewed original articles','Peer-reviewed scientific articles',
                        'Peer-reviewed original articles',
                        'Referee-reviewed published articles', 'peer-reviewed papers',
                        'peer reviewed journals', 'fackgranskade originalartiklar'],
                   'Publication': ['publications', 'publikationer'],
                   'Monograph':
                       ['monographs', 'monograph', 'monografier', 'manuscripts', 'manuskript'],
                   'Patent':
                       ['Patents', 'Patenter', 'patent'],
                   'Peer-reviewed conference contribution':
                       ['Peer-reviewed conference contributions', 'bedömda konferensbidrag', 'conference contributions',
                        'Conference presentations' ],
                   'Presentation':
                       ['Presentation', 'Presentations'],
                   'Computer software':
                       ['Egenutvecklade allmänt tillgängliga datorprogram',
                        'Open access computer programs', 'Publicly available computer programs', 'computer programs'],
                   'Popular science':
                       ['Popular science article', 'popular science', 'Popular-scientific articles',
                        'Popular-Science Articles', 'Populärvetenskapliga artiklar' ],
                   'Review articles, book chapters, books':
                       ['Review articles, book chapters, books', 'Reviews, book chapters, books', 'Book chapters'],
                   'Supervision':
                       ['supervision']
                   }


peer_review_flags = ['peer-reviewed', 'peer reviewed', 'referee-reviewed', 'referee reviewed',
                     'fackgranskade', 'bedömda', 'referee', 'referred', 'refereed',
                     'referee-granskad', 'referee-granskad', 'referee-bedömda', 'reviewed', 'journal']


possible_types2 = {
    'Publication':
        [r'article', r'articles', r'artikel', r'artiklar',
         r'publication', r'publications' r'publikation', r'publikationer',
         r'paper', r'papers'],
    'Monograph':
        [r'monograph', r'monographs', r'monograf', r'monografier', r'manuscripts', r'manuskript'],
    'Patent':
        [r'patent', r'patents', r'patenter'],
    'Conference contribution':
        [r'conference contribution', r'conference contributions',
         r'conference presentation', r'conference presentations',
         r'bedömda konferensbidrag', r'conference paper', r'conference papers',
         r'conference publication'],
    'Presentation':
        [r'presentation', r'presentations', r'presentationer'],
    'Computer software':
        [r'computer programs', r'datorprogram', r'dator program'],
    'Popular science':
        [r'popular[\s]?science', r'popular[\-\s]?scientific', r'populärvetenskaplig'],
    'Books, book chapter':
        [r'book', r'chapter', r'kapitel', r'bok', r'böcker', r'bokkapitel', r'bookchapter'],
    'Abstract':
        [r'abstract', r'abstracts'],
    'Online':
        [r'on[-]?line publication'],
    'Review':
        [r"referee-granskad review", r"reviews", r"peer[\s-]?review\b"]
}



# regex is allowed
# these we skip if there is no type determined prior, or if there
skip_flags = [r'number of', r'mostly cited', r'most cited', r'most important']
# these we skip for sure
strict_skip_flags = [ r'citations.*from.*google scholar', r'appendix c', r'citation index',
                      r'database.*google scholar', r'document.imagefile', r'docx.table',
                      r'\*\s?:\s?relevant']

# string goes in.
# each keyword in possible type is looped
# as soon as match, we break and return the type
def identify_type(string):
    p_match = False
    type = None

    # lets check for the peer reviewed flag
    for p_word in peer_review_flags:
        p_match = re.search(re.escape(p_word), string.lower())
        if p_match:
            p_match = True

    # now we will check for other structural dividers
    matched_word = None
    for t in list(possible_types2.keys()):
        for word in possible_types2[t]:
            match = re.search(word, string.lower())
            if match != None:
                matched_word = match.group(0)
                # adjustment for "conference paper" overwriting "paper", basically all publication words can be
                # overwritten if they match at a later instance of the possible_types dictionary
                if type in ["Publication", "Peer-reviewed publication"] or type == None:
                    if p_match:
                        type = 'Peer-reviewed ' + str(t).lower()
                    else:
                        type = t
                    break
                else:
                    type = "ERROR "
                    break

    return type


# old version
# def identify_type(string):
#     type = None
#     for t in list(possible_types.keys()):
#         for word in possible_types[t]:
#             match = re.search(word.lower(), string.lower())
#             if match:
#                 type = t
#                 break
#     return type



# old function that we used to get index of document
def index_document_df(df):
    dic = {}
    for i, row in df.iterrows():
        index = i
        value = row['para_text']
        #print("Index:", index)
        #print("Value:", value)

        type = identify_type(value)
        #print("TYPE:", type)

        if type != None:
            dic[type] = i
    return dic



def analyze(obj, app_id, fullname, name_list, surname_list, WordDocument):
    col = []

    # make a boolean indicating if there ever has existed a type
    never_type = True

    df = WordDocument.compressed_df


    # check for personnummer in the header
    personnummer = None
    try:
        personnummer = re.search(r'\b([\d]{2}[0|1][\d][0-3][\d]-[\d]{4})\b', WordDocument.header_text).group(1)
    except:
        pass

    for i, row in df.iterrows():
        blank = None
        reason = None
        index = i
        value = row['para_text']

        f_strict_end = None

        # first we get the personnummer
        if personnummer == None:
            try:
                personnummer = re.search(r'\b([\d]{2}[0|1][\d][0-3][\d]-[\d]{4})\b', value).group(1)
            except:
                personnummer = None


        # count the number of quotation marks
        num_quotes = len(re.findall(r'([\"\'])', value))
        if num_quotes > 2:
            f_title = "x"
        else:
            f_title = None



        # look for indications of a reference ending
        pagenumbers = re.findall(r"p.\s*\d+\s*\-*\s*\d*", value.lower())
        if pagenumbers == []:
            pagenumbers = re.findall(r"s.\s*\d+\s*\-*\s*\d*", value.lower())
        volumenumbers = re.findall(r"[\d:;-]{6,}", value.lower())
        volumenumbers_weak = re.findall(r"[\d\:\;\-\s\,]{6,}", value.lower())
        if personnummer in volumenumbers or personnummer in volumenumbers_weak:
            volumenumbers.remove(personnummer)
        #print("pagenumbers", pagenumbers)
        #print("volumenumbers", volumenumbers)
        end_digit = re.findall(r"\d$", value.lower())

        if pagenumbers != [] or volumenumbers != [] or value[-3:] == "(*)" or end_digit != [] or volumenumbers_weak != []:
            f_end = "x"
        else:
            f_end = None


        other_endings = [r"in press", r"submitted to .{,25}$", r"\*$", r'forthcoming']
        for e in other_endings:
            match = re.search(e, value.lower())
            if match != None:
                f_end = "x"
                f_strict_end = "x"
                break


        # lets get the number of citations
        citation_patterns = [r"citations\s?[:=]\s*(\d+)", r"citation number\s*=\s*(\d+)",
                             r"citations\s?[:=]\s*\(([\d,\w\s\/]+)\)",
                             r"gsh:\s?(\d+)",
                             r"citations\s?n\s?[=:\s]?(\d+)",
                             r"\d+\scitations"]


        citations = None
        for pattern in citation_patterns:
            try:
                citations = re.search(pattern, value.lower()).group(1)
                if ", " in citations:
                    cit_list = citations.split(", ")
                    int_cit_list = []
                    for x in cit_list:
                        try:
                            int_cit_list.append(int(x))
                        except:
                            pass
                    if int_cit_list != []:
                        citations = max(int_cit_list)
            except:
                pass

            if citations != None:
                break


        # lets compute the impact factor

        impact_factor_patters = [r"impact factor\s?[:=\s]\s*([\d\,\.]*\d)", r"if\s?[:=\s]\s*([\d\,\.]*\d)"]
        impact_factor = None
        for pattern in impact_factor_patters:
            try:
                impact_factor = re.search(pattern, value.lower()).group(1)
                impact_factor = int(re.sub(r"\,", ".", impact_factor))
            except:
                pass

            if impact_factor != None:
                break



        # lets look for a citations ending or google scholar
        citation_end = re.search(r"citations:\s*\(?\s*[\d,\s]+\s*\)?.{,5}$", value.lower())
        if citation_end == None:
            citation_end = re.search(r"citations:\s*\d+\s*\(*.{,20}\)*.{,5}", value.lower())
        if citation_end != None:
            f_end = "x"



        name_flag = None
        for s in surname_list:
            try:
                name_flag = re.search(s, value)
                if name_flag:
                    name_flag = "x"
            except:
                pass

        # this is to deal with name-order-discrepancies
        if name_flag == None:
            for n in name_list:
                try:
                    name_flag = re.search(n, value)
                    if name_flag:
                        name_flag = "x"
                except:
                    pass

        year = re.search(r'\b(19[\d]{2}|20[\d]{2})\b', value)
        if year:
            year_index = year.span()[0]
            location = 'begining'
            if year_index >= len(value) * 0.5:
                location = 'end'
            year = "YEAR " + location


        if value in nonelist:
            blank = "x"


        type = identify_type(value)
        try:
            if type[0:5] == 'ERROR':
                reason = "TYPE " + str(type)
                type = None
        except:
            pass


        # Do a parenthesis check (to check for false positives
        if type != None:
            # remove possible leading "peer-reviewed" from e.g. "Peer-reviewed publication"
            stripped_type_name = re.sub(r"Peer-reviewed", "", type).strip().capitalize()
            for word in possible_types2[stripped_type_name]:
                parenthesis_match = re.search(r"\(\b.{,30}" + re.escape(word.lower()) + r".{,30}\b\)", value.lower())
                if parenthesis_match != None and (name_flag != None or year != None):
                    type = None
                    reason = "Type removal"
            # controlling for possiblity that the type trigger-word might be part of a title
            if name_flag != None and year != None and f_end != None:
                type = None


        if type != None:
            s_match = None
            s_match_strict = None
            for s in skip_flags:
                s_match = re.search(s.lower(), value.lower())
                if s_match != None:
                    break
            if s_match != None and never_type == False:
                structure = None
                blank = "x"
                reason = s_match
            else:
                structure = type
        else:
            structure = None


        # Now do strict flags, but for all rows
        for s in strict_skip_flags:
            s_match_strict = re.search(s.lower(), value.lower())
            if s_match_strict != None:
                structure = None
                blank = "x"
                reason = s_match_strict
                type = None
                break
            else:
                structure = type


        if type != None:
            never_type = False


        obj.rows.append(IM.Row([('app_id', app_id),('fullname', fullname),('text', value), ('blank', blank),
                                ('structure', structure), ('f_year', year),
                                ('f_name', name_flag), ('f_end', f_end), ("f_strict_end", f_strict_end), ('f_personnummer', personnummer),
                                ('citations', citations), ('impact_factor', impact_factor), ('reason', reason)]))


def read_docs(export_filepath, reduced=None):

    if reduced != None:
        start = reduced['start']
        if reduced['end'] == None:
            end = len(filenames)
        else:
            end = reduced['end']

        filenames_to_run = filenames[start:end]
    else:
        filenames_to_run = filenames
        start = 0
        end = len(filenames)

    sheet = IM.Spreadsheet('analysis')
    print("Reading documents")
    i = 0
    for filename in filenames_to_run:
        i += 1
        progress_bar(i, (end-start+1))
        # first we identify the app_id from the file name
        app_id = re.search(r'(.*)\.docx', filename).group(1)
        #print(app_id)

        # now we get the name of the researcher
        application = org_sheet.get_rows([('app_id', app_id)])[0]
        name = str(application.name)
        surname = str(application.surname)
        fullname = name + " " + surname
        # generate a surname list for doc identification
        surname_list = surname.split(" ")

        # generate a name list to deal with name order discrepancies
        name_list = name.split(" ")

        # import the word document
        filepath = directory + "/" + filename
        d = WM.Docx_df(filepath)

        # here we do the analysis
        analyze(sheet, app_id, fullname, name_list, surname_list, d)

    IM.export([sheet],export_filepath )


def extract_pubs(import_filepath, export_filepath):
    docsheet = IM.Spreadsheet('docsheet', import_filepath, 0)

    pubsheet = IM.Spreadsheet('cv_publications')

    # get the personnummer
    personnummer_rows = docsheet.filter_rows(['f_personnummer'])

    pnums = Counter()
    for r in personnummer_rows:
        pnums.add(r.f_personnummer, r.app_id)
    pnum_registry = {}
    for key in list(pnums.ref.keys()):
        pnum_registry[pnums.ref[key][0]] = key



    type = None
    merge_happening = False
    do_append = False
    pnum = None
    c = {'text': None, 'year': None, 'name': None, 'end':None, 'citations': None , 'impact_factor': None}


    for i in range(0, len(docsheet.rows)):
        row = docsheet.rows[i]
        if row.text in nonelist:
            continue

        #skip a row before even considering a merge
        # note that if there is a blank row in the middle of an entry, the entry will be split
        if row.blank != None:
            continue



        # here we set the structure
        if row.structure in ["Peer-reviewed publication", "Publication", "Monograph"]:
            type = row.structure
            continue
        elif row.structure != None:
            type = None
            do_append = False
            #overwrite merge_happening if there is a structrual thing
            merge_happening = False



        if merge_happening:
            c['text'] = c['text'] + " " + str(row.text).strip()
            # update any potentially incomplete keys
            if c['year'] == None:
                c['year'] = row.f_year
            if c['name'] == None:
                c['name'] = row.f_name
            if c['end'] == None:
                c['end'] = row.f_end
            if c['citations'] == None:
                c['citations'] = row.citations
            if c['impact_factor'] == None:
                c['impact_factor'] = row.impact_factor
        else:
            c = {'text': str(row.text), 'year': row.f_year, 'name': row.f_name, 'end':row.f_end,
                 'citations': row.citations, 'impact_factor': row.impact_factor}

        # make sure that the next row is valid
        try:
            j = 0
            valid_next_row = True
            while True:
                j += 1
                next_row = docsheet.rows[i+j]
                if next_row.blank != None:
                   continue

                if next_row.structure != None:
                    valid_next_row = False
                if next_row.app_id != row.app_id:
                    valid_next_row = False
                if str(next_row.text) in nonelist:
                    valid_next_row = False
                break
        except:
            next_row = None
            valid_next_row = False


        print(row)
        print(next_row)
        print("valid next row", valid_next_row)
        print('\n')



        # if a row meets our conditions that it is a monograph or a peer reviewed paper
        if type != None:

            # get the personnummer from the registry
            try:
                pnum = pnum_registry[row.app_id]
            except:
                pnum = None


            # if we have a strict ending, we just append right away
            if row.f_strict_end != None:
                do_append = True
                merge_happening = False

            else:

                # if we have a perfect row, we append it
                if c['year'] != None and c['name'] != None:
                    do_append = True

                    if valid_next_row:
                        # check if the next row is just some weird ending
                        if (next_row.f_year == None) and (next_row.f_name == None) and \
                                (next_row.f_end != None) and (len(str(next_row.text)) <51):
                            # this is a sign that we should wait and merge
                            do_append = False
                            merge_happening = True
                            continue
                        # sometimes the year is part of the weird ending
                        elif next_row.f_year != None and next_row.f_name == None and next_row.f_end != None:
                            try:
                                current_year = re.findall(r"[12][901]\d{2}", c['text'])[0]
                                ending_numberstrings = re.findall(r"[\d:-]*[12][901]\d{2}[\d:-]*", next_row.text)
                                print("r_years are", ending_numberstrings)
                                overlap = re.findall(current_year, ending_numberstrings[0])
                                print("overlap is", overlap)
                                if (overlap != []) and (len(next_row.text) < 51) and (next_row.f_end != None):
                                    do_append = False
                                    merge_happening = True
                                    continue
                            except:
                                pass


                # if we only have a name flag
                if c['year'] == None and c['name'] != None:
                    if valid_next_row:
                        # check if we have an intermediary or a weird ending
                        if next_row.f_year == None and next_row.f_name == None:
                            do_append = False
                            merge_happening = True
                            continue
                        # check if we have a complementary entry
                        elif next_row.f_year != None and next_row.f_name == None:
                            do_append = False
                            merge_happening = True
                            continue
                        # however if we have the a substitute entry (name flag in next row), we append
                        elif next_row.f_name != None:
                            do_append = True
                    else:
                        do_append = True

                elif c['year'] != None and c['name'] == None:
                    if valid_next_row:
                        # check if we have an intermediary or a weird ending
                        if next_row.f_year == None and next_row.f_name == None:
                            do_append = False
                            merge_happening = True
                            continue
                        # check if we have a complementary entry
                        elif next_row.f_year == None and next_row.f_name != None:
                            do_append = False
                            merge_happening = True
                            continue
                        # however if we have the a substitute entry (name flag in next row), we append
                        elif next_row.f_year != None:
                            # but if the next row has an ending, like volume info, containing the year,
                            # and if the text length is <= 50, we accept is as an ending and merge
                            try:
                                current_year = re.findall(r"[12][901]\d{2}", c['text'])
                            except:
                                current_year = []
                            try:
                                ending_numberstrings = re.findall(r"[\d:-]*[12][901]\d{2}[\d:;-]*", str(next_row.text))
                                print("r_years are", ending_numberstrings)
                                overlap = re.findall(re.escape(current_year[0]), ending_numberstrings[0])
                            except:
                                overlap = []

                            print("overlap is", overlap)
                            if (overlap != []) and (len(next_row.text) < 51) and (next_row.f_end != None):
                                do_append = False
                                merge_happening = True
                                continue
                            else:
                                do_append = True
                        else:
                            do_append = True
                    else:
                        do_append = True

                # If we have no year and no author, we proceed with merge
                elif c['year'] == None and c['name'] == None and c['text'] != None and row.structure == None:
                    if valid_next_row:
                        do_append = False
                        merge_happening = True
                        continue
                    else:
                        do_append = True

                else:
                    pass




        # here we append an approved publication row
        if do_append:

            try:
                c['citations'] = int(c['citations'])
            except:
                pass
            try:
                c['impact_factor'] = float(c['impact_factor'])
            except:
                pass

            pubsheet.rows.append(IM.Row([("app_id", row.app_id),
                                         ("fullname", row.fullname),
                                         ("personnummer", pnum),
                                         ("type", type),
                                         ("publication", c['text']),
                                         ("citations", c['citations']),
                                         ("impact_factor", c['impact_factor'])
                                         ]))
            do_append = False
            merge_happening = False
            if next_row != None:
                if row.app_id != next_row.app_id:
                    type = None


    IM.export([pubsheet], export_filepath )


qoo = [
        [{'start': 0, 'end': 5000}, 1],
        [{'start': 5000, 'end': 10000}, 2],
        [{'start': 10000, 'end': 15000}, 3],
        [{'start': 15000, 'end': 20000}, 4],
        [{'start': 20000, 'end': 25000}, 5],
        [{'start': 25000, 'end': None}, 6]
      ]
qoo = [ [{'start': 25000, 'end': None}, 6] ]

for q in qoo:

    #filename of document analysis
    da_filepath = project_root + '/Spreadsheets/new_docx_analysis/doc_analysis_test' + str(q[1]) + '.xlsx'
    #filename of publications
    pub_filepath = project_root + '/Spreadsheets/new_docx_analysis/publications_test' + str(q[1]) + '.xlsx'
    # reduce to a subset of researcher from VR.xlsx
    subset = q[0]


    read_docs(da_filepath, subset)
    extract_pubs(da_filepath, pub_filepath)