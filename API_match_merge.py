import os
import re
import sys
import Models.ImportModel as IM
import pandas as pd
import numpy as np

def clean_df(df):
    for index in range(0, len(df)):
        #for col in list(df.columns):
        for col in ['api_match']:
            val = df.loc[index, col]
            try:
                if np.isnan(val):
                    df.loc[index, col] = None
            except:
                pass
    return df


def append_to_df(original, temporary):
    for index in range(0, len(original)):
        # check a relevant col is not empty in the temporary
        api_match_temp = temporary.loc[index, 'api_match']
        try:
            if np.isnan(api_match_temp):
                api_match_temp = None
        except:
            pass

        if api_match_temp != None:

            for col in list(original.columns):
                #val = original.loc[index, col]
                val_temp = temporary.loc[index, col]
                original.loc[index, col] = val_temp

    return original



def main(server_id, custom_indices=None):

    downloads_path = "C:/Users/Jeffrey/PycharmProjects/Dreber_deployers/server_downloads/server_" + str(server_id) + "/api_matched"
    print("DOWNLOADS PATH", downloads_path)
    export_base = "C:/Users/Jeffrey/PycharmProjects/Dreber_deployers/server_downloads/server_" + str(server_id)
    files = os.listdir(downloads_path)

    # sort the list by section, then core
    detailed = []
    #print("FILES ARE", files)
    for f in files:
        if "analysis" == f[0:8]:
            #print("f is", f)
            q = re.search(r"_(\d+)_(\d+)_core_(\d+)", f)
            start = q.group(1)
            end = q.group(2)
            core = q.group(3)
            detailed.append({'filename': f, 'start': int(start), 'end': int(end), 'core': int(core)})
    detailed = sorted(detailed, key=lambda x: (x['start'], x['core']))
    files = [x['filename'] for x in detailed]

    core_batches = []
    startnum = None
    batch_to_append = []
    for d in detailed:
        if startnum != d['start']:
            if startnum != None:
                core_batches.append(batch_to_append)
            startnum = d['start']
            batch_to_append = [d]
        else:
            batch_to_append.append(d)
            if detailed.index(d) == (len(detailed) - 1):
                core_batches.append(batch_to_append)

    if custom_indices != None:
        reduced = []
        for i in range(0, len(core_batches)):
            if i in custom_indices:
                reduced.append(core_batches[i])
        core_batches = reduced.copy()


    for batch in core_batches:
        files = [x['filename'] for x in batch]
        # we import the first file in its entirety, this is the file that we will build on
        f = files[0]
        files = files[1:]
        fp = downloads_path + "/" + f
        raw = IM.Spreadsheet('Raw', fp, 'Raw').df
        pub = IM.Spreadsheet('Publications', fp, 'Publications').df
        print("Cleaning:", fp)
        pub = clean_df(pub)
        researcher = IM.Spreadsheet("Researchers", fp, "Researchers").df

        for f in files:
            fp = downloads_path + "/" + f
            pub_temp = IM.Spreadsheet('Publications', fp, 'Publications').df
            pub = append_to_df(pub, pub_temp)


        # before saving, we should compute the number of matched and total for the authors

        app_id = None
        total_count = 0
        match_count = 0
        for index in range(0, len(pub)):
            row_app_id = pub.loc[index, 'app_id']
            if app_id != row_app_id:
                if app_id != None:
                    # push the match and pub data to the researcher sheet
                    researcher.loc[researcher['app_id'] == app_id, 'extracted_pubs'] = total_count
                    researcher.loc[researcher['app_id'] == app_id, 'matched_pubs'] = match_count
                app_id = row_app_id
                total_count = 0
                match_count = 0

            total_count = total_count + 1
            if pub.loc[index, 'api_match'] != None:
                match_count = match_count + 1

            if index == (len(pub) - 1):
                researcher.loc[researcher['app_id'] == app_id, 'extracted_pubs'] = total_count
                researcher.loc[researcher['app_id'] == app_id, 'matched_pubs'] = match_count


        export_fp = export_base + "/API_match_" + str(batch[0]['start']) + "_" + str(batch[0]['end']) + ".xlsx"
        print("Exporting:", export_fp)
        writer = pd.ExcelWriter(export_fp)
        raw.to_excel(writer, 'Raw', index=False)
        pub.to_excel(writer, 'Publications', index=False)
        researcher.to_excel(writer, 'Researchers', index=False)
        writer.save()


if __name__ == "__main__":

    try:
        server_id = int(sys.argv[1])
        indices = None
    except:
        server_id = None
        #server_id = 2
        #indices = [1,2,4,5,6,7]

    main(server_id, indices)
