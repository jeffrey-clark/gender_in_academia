import os, sys, re

import Models.ImportModel as IM


# all necessary imports
vr_scrape6 = IM.scrape6()

def app_id_to_id(app_id):
    # provide an app_id, and return the id
    row = vr_scrape6.get_rows([("app_id", app_id)])[0]
    id = row.ID
    return id

def derive_api_match_fp(id):
    all_files = os.listdir('Spreadsheets_October/Round_1_matches')
    print(all_files)

def get_pubs(app_id):
    id = app_id_to_id(app_id)
    derive_api_match_fp(id)

if __name__ == "__main__":
    get_pubs("2012-02583")