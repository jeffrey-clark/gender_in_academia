import math
import re
import time

from Models.initialize import *
from Models import APIModel as API
from Models import ImportModel as IM
import datetime


def api_execute(existing_file = None, initial_only=False):
    d = datetime.datetime.now().date()
    t = datetime.datetime.now().time()
    hour = str(t.hour)
    if len(hour) == 1:
        hour = "0" + hour
    start_time_suffix = str(d.year)+str(d.month)+str(d.day)+"-"+hour+str(t.minute)+str(t.second)

    filename = 'scrape_results_6.0.xlsx'
    filepath = project_root + '/Spreadsheets/' + filename
    sheet_index = 0

    scrape_results = IM.Spreadsheet("scrape_results_6", filepath=filepath, sheetname=sheet_index)
    skipped_queries = IM.Spreadsheet("skipped_queries")


    if existing_file == None:
        api_output = IM.Spreadsheet('api_output')
        start_id = 1
        pickup_id = 0
    else:
        api_output = IM.Spreadsheet('api_output', filepath=existing_file, sheetname=0)
        # now we will compute the startid and pickup id
        start_app_id = api_output.rows[0].app_id
        start_id = scrape_results.get_rows([('app_id', start_app_id)])[0].ID

        pickup_app_id = api_output.rows[-1].app_id
        pickup_id = scrape_results.get_rows([('app_id', pickup_app_id)])[0].ID


    # parameters for the length of xlsx files

    temp_save_interval = 5
    xlsx_length = 25000
    current_length = len(api_output.rows)

    for r in scrape_results.rows[pickup_id:]:

        remaining = len(scrape_results.rows) - (scrape_results.rows.index(r) + 1)
        print("ID:", r.ID, "   app_id:", r.app_id, "(" + str(remaining) + " remaining)")

        if start_id == None:
            start_id = r.ID
        year = str(int(r.app_id[0:4]) + 2)

        if initial_only:
            name = r.Name[0]
            f_prefix = 'initial_'
        else:
            name = r.Name
            f_prefix = ''

        name_combos = fullname_combos(r.Surname, name)

        for combo in name_combos:
            print("searching combo", str(name_combos.index(combo) + 1), "of", str(len(name_combos)))


            print(combo)

            q = "AU=(" + combo + ")"
            api_result = API.complete_api_search(q, year, None, max_accept=10000)

            try:
                if api_result[0] == "skip":
                    print("skipping", r.app_id, combo )
                    skipped_queries.rows.append(IM.Row([('App_id', r.app_id),
                                                        ('name_combo', combo),
                                                        ('returns', api_result[1])]))

                    skipped_filepath = project_root + '/Spreadsheets/API/' + f_prefix + 'skipped_queies' + start_time_suffix + '.xlsx'

                    IM.export([skipped_queries], skipped_filepath)
                    continue
            except:
                pass


            for a in api_result:
                out_tuples = API.parse_api_return(a)
                api_output.rows.append(IM.Row([('app_id', r.app_id)] + out_tuples))

            current_length = current_length + len(api_result)
            print("current_length is:", current_length)


        if current_length > xlsx_length or remaining == 0:
            # export
            end_id = r.ID
            export_filepath = project_root + '/Spreadsheets/API/' + f_prefix + str(start_id) + '-' + str(end_id) + '.xlsx'
            IM.export([api_output], export_filepath)

            # create the new sheet
            api_output = IM.Spreadsheet('api_output')
            start_id = None
            current_length = 0
            end_id = None
        elif int(r.ID) % temp_save_interval == 0:
            export_filepath = project_root + '/Spreadsheets/API/' + f_prefix + str(start_id) + '-temp.xlsx'
            IM.export([api_output], export_filepath)


def identify_name_order_dis(skipped_filepath):
    # first we import the scrape results
    filename = 'scrape_results_6.0.xlsx'
    filepath = project_root + '/Spreadsheets/' + filename
    sheet_index = 0
    scrape_results = IM.Spreadsheet("scrape_results_6", filepath=filepath, sheetname=sheet_index)


    # we also import the excess app_ids
    skipped = IM.Spreadsheet("skipped", filepath=skipped_filepath, sheetname=0)
    skipped_ids = skipped.get_col('App_id')

    # create the spreadsheet that will contain the name order discs
    missing_ppl = IM.Spreadsheet('missing_people')


    # then we import all of the
    dir = os.listdir(project_root + '/Spreadsheets/API')
    files_of_interest = []
    for f in dir:
        if re.match(r'initial_\d+-\d+\.xlsx', f):
            s = int(re.match(r'initial_(\d+)-\d+\.xlsx', f).group(1))
            e = int(re.match(r'initial_\d+-(\d+)\.xlsx', f).group(1))
            insert = {'startid': s, 'endid': e, 'filename': f}
            files_of_interest.append(insert)

    newlist = sorted(files_of_interest, key=lambda k: k['startid'])
    for f in newlist:
        filepath = project_root + '/Spreadsheets/API/' + f['filename']
        sheet_index = 0
        segment = IM.Spreadsheet("segment", filepath=filepath, sheetname=sheet_index)

        app_ids = scrape_results.get_col('app_id')

        for i in app_ids[(f['startid']-1):f['endid']]:

            match = False
            if i in unique(segment.get_col('app_id')):
                match = True
            elif i in skipped_ids:
                match = True

            if match == False:
                missing_ppl.rows.append(IM.Row([('app_id', i)]))
                print("found a missing app_id:", i)

            #print((app_ids.index(i) + 1),  'app_id:', i, match )

    export_filepath = project_root + '/Spreadsheets/API/1-10000_nameorderdiscs.xlsx'
    IM.export([missing_ppl], export_filepath)


def execute_name_order_disc(disc_ids_filepath, existing_file = None):

    filename = 'scrape_results_6.0.xlsx'
    filepath = project_root + '/Spreadsheets/' + filename
    sheet_index = 0

    scrape_results = IM.Spreadsheet("scrape_results_6", filepath=filepath, sheetname=sheet_index)

    specialid = disc_ids_filepath[-1]
    path_in = disc_ids_filepath + ".xlsx"

    target_ids = IM.Spreadsheet("target_id", filepath=path_in, sheetname=0)



    if existing_file == None:
        api_output = IM.Spreadsheet('api_output')
        index=0
        current_length = 0
    else:
        path_existing = existing_file + ".xlsx"
        
        api_output = IM.Spreadsheet('api_output', filepath=path_existing, sheetname=0)
        # now we will compute the startid and pickup id
        pickup_app_id = api_output.rows[-1].app_id

        # now get the index of the app_id
        index = target_ids.get_col('app_id').index(pickup_app_id)

        current_length = (index + 1)

    # parameters for the length of xlsx files

    temp_save_interval = 10

    for r in target_ids.rows[index:]:

        scrape_row = scrape_results.get_rows([('app_id', r.app_id)])[0]
        firstname = scrape_row.Name
        surname = scrape_row.Surname
        print(r.app_id, firstname, surname)

        # now run all combinations of all names
        name_combos = fullname_combos(firstname, surname[0])

        year = str(int(r.app_id[0:4]) + 2)

        for combo in name_combos:
            print("searching combo", str(name_combos.index(combo) + 1), "of", str(len(name_combos)))
            print(firstname, surname[0])


            q = "AU=(" + combo + ")"
            api_result = API.complete_api_search(q, year, None, max_accept=10000)

            try:
                if api_result[0] == "skip":
                    print("skipping", r.app_id, combo)
                    continue
            except:
                pass

            for a in api_result:
                out_tuples = API.parse_api_return(a)
                api_output.rows.append(IM.Row([('app_id', r.app_id)] + out_tuples))

            current_length = target_ids.rows.index(r) + 1
            print("current_length is:", current_length)

        if current_length % temp_save_interval == 0 or current_length == len(target_ids.rows):
            #export
            export_filepath = project_root + '/Spreadsheets/API/' + '20000-27229_nameorderdiscs2' + str(specialid) +'.xlsx'
            IM.export([api_output], export_filepath)


def discover_latest_bigfile(bigfilepath):
    target_ids = IM.Spreadsheet("target_id", filepath=bigfilepath, sheetname=0)
    master_ids = unique(target_ids.get_col('Master_id'))
    latest = None
    directory = os.listdir(project_root + '/Spreadsheets/API/Bigfiles')

    for m in master_ids:
        f_name = str(m) + "_bigfile.xlsx"
        if f_name in directory:
            latest = m
    print("latest is", latest)
    return latest



def execute_bigfiles(bigfilepath, start_app_id=None):

    target_ids = IM.Spreadsheet("target_id", filepath=bigfilepath, sheetname=0)

    if start_app_id == None:
        run_api = True
        api_output = IM.Spreadsheet("api_output")
        records = 0
    else:
        run_api = False
        latest_path = str(project_root + '/Spreadsheets/API/Bigfiles/' + start_app_id + "_bigfile.xlsx")
        api_output = IM.Spreadsheet('api_output', filepath=latest_path, sheetname=0)
        records = len(api_output.rows)

    master_ids = unique(target_ids.get_col('Master_id'))
    print(master_ids)

    for m in master_ids:

        row = target_ids.get_rows([('App_id', m)])[0]

        year = str(int(row.App_id[0:4]) + 2)

        if run_api == False:
            if row.App_id == start_app_id:
                run_api = True

        if run_api == True:
            combo = row.name_combo

            q = "AU=(" + combo + ")"

            sum_total_records = int(API.records_complete_api_search(q, year, None, 1950))
            print("sum_total_records is:", sum_total_records)


            split_decades = False
            if sum_total_records > 90000:
                split_decades = True


            if split_decades == True:
                records_so_far = 0
                decades = [1950,1960,1970,1980,1990,1995,2000, 2005, 2010]
                for y in decades:
                    decade_records = 0
                    y_index = decades.index(y)
                    if y_index == (len(decades) - 1):
                        e = year
                    else:
                        e = decades[y_index+1] - 1
                    s = y

                    total_records = int(API.records_complete_api_search(q, str(e), None, str(s)))

                    if records > records_so_far:
                        records_so_far = records_so_far + total_records
                        continue

                    while decade_records < total_records:

                        print("records:", records, "out of", sum_total_records)

                        if total_records - decade_records >= 5000 :
                            inc = 50
                        else:
                            inc = math.ceil((total_records - decade_records)/100)

                        batch_id = int(math.ceil(decade_records/100))

                        api_result = API.complete_api_search(q, str(e), None, max_accept=1000000, bybatch=True,
                                                             batchid=(batch_id+1),
                                                             bybatch_increment=inc, start=str(s))

                        for a in api_result:
                            out_tuples = API.parse_api_return(a)
                            api_output.rows.append(IM.Row([('app_id', row.App_id)] + out_tuples))

                        export_filepath = project_root + '/Spreadsheets/API/Bigfiles/' + str(row.Master_id) + \
                                          '_bigfile.xlsx'
                        IM.export([api_output], export_filepath)

                        decade_records = decade_records + len(api_result)
                        records = records + len(api_result)
                        records_so_far = records

                    records = 0
                    api_output = IM.Spreadsheet("api_output")

            else:

                while records < sum_total_records:

                    print("records:", records, "out of", sum_total_records)

                    if sum_total_records - records >= 5000:
                        inc = 50
                    else:
                        inc = math.ceil((sum_total_records - records) / 100)

                    batch_id = int(math.ceil(records / 100))

                    api_result = API.complete_api_search(q, year, None, max_accept=1000000, bybatch=True,
                                                         batchid=(batch_id + 1),
                                                         bybatch_increment=inc, start=1950)

                    for a in api_result:
                        out_tuples = API.parse_api_return(a)
                        api_output.rows.append(IM.Row([('app_id', row.App_id)] + out_tuples))

                    export_filepath = project_root + '/Spreadsheets/API/Bigfiles/' + str(row.Master_id) + \
                                      '_bigfile.xlsx'
                    IM.export([api_output], export_filepath)

                    records = records + len(api_result)

                records = 0
                api_output = IM.Spreadsheet("api_output")


#def pickup_excess(input_filepath):

    # filename = 'scrape_results_6.0.xlsx'
    # filepath = project_root + '/Spreadsheets/' + filename
    # sheet_index = 0
    # #scrape_results = IM.Spreadsheet("scrape_results_6", filepath=filepath, sheetname=sheet_index)
    #
    # skipped_queries = IM.Spreadsheet("skipped_queries", filepath=input_filepath, sheetname=0)
    #
    # for r in skipped_queries.rows:


if __name__ == "__main__":


    # if we will continue on a file
    #existing_filename = "initial_9853-temp.xlsx"
    #existing_filepath = project_root + '/Spreadsheets/API/' + existing_filename

    #api_execute(existing_file=existing_filepath, initial_only=True)

    #excess_filename = 'initial_skipped_queries10000_19999.xlsx'
    #excess_filepath = project_root + '/Spreadsheets/API/' + excess_filename


    #disc_id_filename = '20000-27229_nameorder_appids1'
    #disc_id_filepath = project_root + '/Spreadsheets/API/Discrepancies/' + disc_id_filename

    #existing_file
    #disc_filename = '20000-27229_nameorderdiscs1'
    #disc_filepath = project_root + '/Spreadsheets/API/Discrepancies/' + disc_filename


    #execute_name_order_disc(disc_ids_filepath=disc_id_filepath, existing_file=None)
    #exit()

    #
    #
    # while True:
    #
    #     try:
    #         execute_name_order_disc(disc_ids_filepath=disc_id_filepath, existing_file=disc_filepath)
    #     except:
    #         execute_name_order_disc(disc_ids_filepath=disc_id_filepath, existing_file=None)
    #     time.sleep(20)
    #
    # exit()

    big_filename = 'initial_skipped_queries20000-27229_2.xlsx'
    big_filepath = project_root + '/Spreadsheets/API/Bigfiles/' + big_filename


    while True:
        try:
            execute_bigfiles(big_filepath, start_app_id=discover_latest_bigfile(big_filepath))
        except:
            time.sleep(10)
            pass
