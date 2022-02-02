from Models.initialize import *
from Models import APIModel as API
from Models import ImportModel as IM

filename = 'stickprov_foundation_API.xlsx'
filepath = project_root + '/Spreadsheets/' + filename
sheet_index = 0

scrape_results = IM.Spreadsheet("scrape_results_6", filepath=filepath, sheetname=sheet_index,)

api_output = IM.Spreadsheet('api_output')

# here we will define the excel columns



for row in scrape_results.rows[0:50]:
    year = row.app_id[0:4]

    if row.Errors == None:
        q = "AU=(" + row.Surname + ", " + row.Name + ")"
        api_result = API.complete_api_search(q, year)

        for a in api_result:
            out_tuples = API.parse_api_return(a)
            api_output.rows.append(IM.Row([('app_id', row.app_id)].extend(out_tuples)))

export_filepath = project_root + '/Spreadsheets/API/API_stickprov.xlsx'
IM.export([api_output], export_filepath )
