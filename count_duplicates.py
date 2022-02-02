from Models.initialize import *
import Models.ImportModel as IM
import re
from statistics import *

filepath_nick = project_root + "/Spreadsheets/nicks_data.xlsx"
filepath_jeff = project_root + "/Spreadsheets/scrape_results_5.0.xlsm"
filepath_org = project_root + "/Spreadsheets/VR-ansökningar 2012-2016.xlsx"

# import Nicks
nicks = IM.Spreadsheet('nicks', filepath_nick, 0)
nicks.rename_cols([('Dnr', "app_id")])
# import Original
original = IM.Spreadsheet('original', filepath_org, 1)
original.rename_cols([('Dnr', 'app_id'), ('Förnamn', 'name'), ('Efternamn', 'surname')])

nick_unique_app_ids = unique(nicks.get_col('app_id'))


def make_duplicated_spreadsheet():

    duplicates = Counter()

    for i in range(0, len(original.rows)):
        dup_found = False
        name_i = original.rows[i].name
        surname_i = original.rows[i].surname
        app_id_i = original.rows[i].app_id
        fullname = str(name_i) + " " + str(surname_i)

        if fullname in list(duplicates.dic.keys()):
            continue

        for j in range(i+1, len(original.rows)):
            name_j = original.rows[j].name
            surname_j = original.rows[j].surname
            app_id_j = original.rows[j].app_id

            if (name_i == name_j) and (surname_i == surname_j):
                dup_found = True
                duplicates.add(fullname, app_id_j)

        if dup_found:
            duplicates.add(fullname, app_id_i)
            duplicates.ref[fullname] = part_reorder_list(duplicates.ref[fullname], [app_id_i])

        print("Completed", i, "of", len(original.rows))

    duplicates.compute()

    print(duplicates.dic)
    print(duplicates.ref)

    sheet = IM.Spreadsheet('Duplicates')
    for key in list(duplicates.dic.keys()):
        # get the name and surname
        app_id = duplicates.ref[key][0]
        sample = original.get_rows([('app_id', app_id)])[0]
        new_row = [('Name', sample.name), ("Surname", sample.surname), ("Count", duplicates.dic[key]),
                   ("App_ids", duplicates.ref[key])]
        sheet.rows.append(IM.Row(new_row))

    IM.export([sheet], 'Spreadsheets/count_duplicates.xlsx')


def check_duplicates_nick():
    filepath_dup = project_root + "/Spreadsheets/count_duplicates.xlsx"
    dup = IM.Spreadsheet('Duplicates', filepath_dup, 0 )

    for row in dup.rows:
        progress_bar(row, dup.rows)
        count = 0
        for a in row.App_ids:
            if a in nick_unique_app_ids:
                count += 1
        setattr(row, 'count', count)

    IM.export([dup], 'Spreadsheets/duplicates_2.xlsx')

# create a spreadsheet with names and occurances in the data
#make_duplicated_spreadsheet()

# import the duplicates spreadsheet and check occurances in Nicks
check_duplicates_nick()