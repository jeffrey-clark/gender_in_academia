import datetime

from Models.initialize import *
import Models.ImportModel as IM
import Models.LocalAPIModel as Local_API
import docxtractor as dxtr
import pandas

def match(analysis_filename, core, total_cores, id_overwrite = None):

    id_extraction = re.search(r'_(\d+)_(\d+).xlsx', analysis_filename)
    start_id = id_extraction.group(1)
    end_id = id_extraction.group(2)


    # IMPORT THE ANALYSIS SPREADSHEET AS DATAFRAMES
    analysis_filepath = project_root + "/Spreadsheets/new_docx_analysis/threaded/" + analysis_filename
    raw = IM.Spreadsheet('Raw', analysis_filepath, 'Raw')
    pub = IM.Spreadsheet('Publications', analysis_filepath, 'Publications')
    researcher = IM.Spreadsheet("Researchers", analysis_filepath, "Researchers")

    # CREATE A DOC_DATA OBJECT FROM THE DFs
    doc_data = dxtr.Doc_data()
    doc_data.import_dfs(raw.df, pub.df, researcher.df)

    # create LAPI instance
    LAPI = Local_API.data()

    i = 0
    while i  < len(doc_data.pubs):
        print("i is", i)
        if doc_data.pubs[i] == []:
            i = i + 1
            continue

        print(i, doc_data.pubs[i][0].app_id, doc_data.researchers[i].app_id)
        if doc_data.pubs[i][0].app_id != doc_data.researchers[i].app_id:
            if doc_data.researchers[i].extracted_pubs == None:
                doc_data.pubs = doc_data.pubs[:i] + [[]] + doc_data.pubs[i:]
                i = i - 1
            else:
                if int(doc_data.researchers[i].extracted_pubs) == 0:
                    doc_data.pubs = doc_data.pubs[:i] + [[]] + doc_data.pubs[i:]
                    i = i - 1
                else:
                    raise ValueError("MISMATCH IN RESEARCHER AND PUBS IN THE MATCHING API PROCESS")
                # to resolve, investigate the symmetry of the df.researchers and df.pubs lists
        i = i + 1

    # print("PUBS ARE FINALLY:")
    # print(doc_data.pubs)


    r_start = math.floor(len(doc_data.researchers) / total_cores) * (int(core) - 1)
    r_end = math.floor(len(doc_data.researchers) / total_cores) * (int(core))
    if int(core) == int(total_cores):
        r_end = len(doc_data.researchers)


    if id_overwrite != None:
        r_start = int(id_overwrite['start']) - int(start_id)
        r_end = int(id_overwrite['end']) - int(start_id) + 1
        print("START OVERWRITE IS", r_start)
        print("END OVERWRITE IS", r_end)

    subsample = doc_data.researchers[r_start:r_end]

    id = int(start_id) + int(r_start)
    r_id = int(r_start)
    for r in subsample:
        # here r is the researcher row in the Scrape6 spreadsheet
        print(id, ":", r.app_id, r.name)

        # Fetch df with API all found API data
        r.ID = id
        r.r_ID = r_id
        LAPI.load_data(r)
        api_pubs = LAPI.pub_data

        # now we will match publications with API data
        doc_data.match_publications(api_pubs, r)

        export_fp = "api_matched/" + analysis_filename[:-5] + "_core_" + str(core) + ".xlsx"
        doc_data.export(export_fp)

        id = str(int(id) + 1)
        r_id = str(int(r_id) + 1)

if __name__ == "__main__":
    starttime = datetime.datetime.now()
    try:
        filename = sys.argv[1]
        core = int(sys.argv[2])
        total_cores = int(sys.argv[3])
    except:
        start_id = 15001
        end_id = 20000
        filename = "analysis_" + str(start_id) + "_" + str(end_id) + ".xlsx"
        core = 1
        total_cores = 1

    match(filename, core, total_cores)

    #match(filename, 1, 1, {'start': 377, 'end': 378})
    print("start time", starttime)
    print("end time", datetime.datetime.now())