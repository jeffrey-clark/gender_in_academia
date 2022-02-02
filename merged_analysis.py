from Models.initialize import *
import Models.ImportModel as IM
import re
from statistics import *

filepath_nick = project_root + "/Spreadsheets/nicks_data.xlsx"
filepath_jeff = project_root + "/Spreadsheets/scrape_results_5.0.xlsm"
filepath_org = project_root + "/Spreadsheets/VR-ansökningar 2012-2016.xlsx"
filepath_nick_new = project_root + "/Spreadsheets/collected_publications.xlsm"

# import Nicks
nicks = IM.Spreadsheet('nicks', filepath_nick_new, 0)
nicks.rename_cols([('Dnr', "app_id")])
# import Original
original = IM.Spreadsheet('original', filepath_org, 1)
original.rename_cols([('Dnr', 'app_id')])


c_org = Counter()
c_nick = Counter()
c_intersection = Counter()


# count the subject area distribution in original sheet
for row in original.rows:
    c_org.add(getattr(row, 'Ämnesområde'))
c_org.compute()
print("original distribution", c_org.distribution())
print("Total:", c_org.total)

nick_unique_app_ids = unique(nicks.get_col("app_id"))

# now we compute the intersection
for row in original.rows:
    if row.app_id in nick_unique_app_ids:
        c_intersection.add(getattr(row, 'Ämnesområde'))
c_intersection.compute()
print("intersection distribution", c_intersection.distribution())
print("Total:", c_intersection.total)


# compute the relative values
output = {}
for key in list(c_intersection.dic.keys()):
    o_val = c_org.dic[key]
    i_val = c_intersection.dic[key]
    output[key] = str(round((100*i_val/o_val), 1))

print(output)


print("nicks cols", nicks.col_names)
print("original cols", original.col_names)

c_year = Counter()

for pub in nicks.rows:
    year = pub.PublicationYear
    org_dnr = original.get_rows([('app_id', pub.app_id)])[0]
    if int(year) > int(int(pub.app_id[0:4])):
        c_year.add("after")
    elif int(year) == int(int(pub.app_id[0:4])):
        c_year.add("equal")
    else:
        c_year.add("before")

c_year.compute()
print(c_year.distribution())