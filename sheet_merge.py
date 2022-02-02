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
original.rename_cols([('Dnr', 'app_id')])

nick_unique_app_ids = unique(nicks.get_col('app_id'))

def original_to_nick():

    atts_to_add = original.col_names
    atts_to_add.remove('app_id')
    atts_to_add = part_reorder_list(atts_to_add, ['Ämnesområde'])

    nicks.col_names = nicks.col_names + atts_to_add

    # now we will extend each row in Nicks data
    for row in nicks.rows:
        current = nicks.rows.index(row) + 1
        print("processing", current, "out of", len(nick_unique_app_ids))
        o = original.get_rows([('app_id', row.app_id)])[0]
        # print(row)
        # print(o)
        for att in atts_to_add:
            o_value = getattr(o, att)
            setattr(row, att, o_value)
        print(row)

    IM.export([nicks], 'Spreadsheets/test.xlsx')


def nicks_to_original():
    # now we generate some new variables
    for row in original.rows:
        print("processing", str(int(original.rows.index(row) + 1)), "out of", len(original.rows))
        # get all the publications in nicks data
        pubs = nicks.get_rows([('app_id', row.app_id)])

        pubs_exist = False
        # dummy for existence of publications
        if pubs != []:
            setattr(row, 'publikationer_finns', 1)
            pubs_exist = True
        else:
            setattr(row, 'publikationer_finns', 0)

        # total number of publications
        setattr(row, 'total_publikationer', len(pubs))

        first_author_pubs = []
        for pub in pubs:
            if getattr(pub, 'AuthorOrder') == 1:
                first_author_pubs.append(pub)

        # set the numer of publications as first author
        setattr(row, 'total_förstaförfattare', len(first_author_pubs))

        # citations
        citations = []
        for pub in pubs:
            if pub.TimesCited != -1:
                citations.append(pub.TimesCited)
        setattr(row, 'total_citeringar', sum(citations))

        # citations as first author
        citations_first_author = []
        for pub in first_author_pubs:
            if pub.TimesCited != -1:
                citations_first_author.append(pub.TimesCited)
        setattr(row, 'citeringar_förstaförfattare', sum(citations_first_author))


        # Total impact
        impact = []
        for pub in pubs:
            if pub.ImpactFactor != -1:
                impact.append(pub.ImpactFactor)
        setattr(row, 'total_impact', sum(impact))


        # Impact as first author
        impact_first_author = []
        for pub in first_author_pubs:
            if pub.ImpactFactor != -1:
                impact_first_author.append(pub.ImpactFactor)
        setattr(row, 'citeringar_förstaförfattare', sum(impact_first_author))



    IM.export([original], 'Spreadsheets/original_med _publikationer.xlsx')


nicks_to_original()

# x = nicks.get_cols(['app_id', 'TimesCited'])
#
# print(original.col_names)
# sub = original.get_cols(['app_id', 'Ämnesområde'])
#
# sub_headers = list(set(original.get_col('Ämnesområde')))
#
# counter = Counter()
#
# for a in nick_unique_app_ids:
#     for s in sub:
#         if s[0] == a:
#             counter.add(s[1], a)
#
# counter.compute()
#
# print(counter.dic)
# print(counter.ref)


# r_citation_averages = []
#
# for a in nick_unique:
#     vals = []
#     for t in x:
#         if t[0] == a:
#             vals.append(int(t[1]))
#     avg = mean(vals)
#     try:
#         sd = (variance(vals, avg))**(0.5)
#     except:
#         sd = None
#     print(a, vals, avg, sd)
#     if (sd == None) or (-1 in vals):
#         pass
#     else:
#         r_citation_averages.append((avg, sd))
#
#
# mean_avg = mean([t[0] for t in r_citation_averages])
# sd_avg = mean([t[1] for t in r_citation_averages])
#
# print("Mean mean:", mean_avg, "  Mean sd:", sd_avg)

#for a in nick_unique:
#    nicks.get_col()

#export_fp = project_root + "/Spreadsheets/output.xlsx"
#IM.export([nicks], export_fp)