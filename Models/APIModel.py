import requests
import json
import urllib.parse
import math
import re
import time

def search_wos(q, first_record, count, end_year, timeout, start_year=None):
    if timeout != None:
        time.sleep(timeout)

    if start_year == None:
        start_year = 1950

    url = "https://wos-api.clarivate.com/api/woslite/?databaseId=WOK&usrQuery="+ q +"&count="+ str(count) + \
          "&firstRecord=" + str(first_record) + "&publishTimeSpan=" + str(start_year) + "-01-01%2B" + \
          str(end_year) + "-12-30"

    headers = {'content-type': 'application/json',
               'Accept-Charset': 'UTF-8',
               'X-ApiKey': '15ec966703dce1d161225f9a0647589818983243'}
    r = requests.get(url, headers=headers)
    r = json.loads(r.text)

    print(r)
    return r


def search_incites(UT_list, timeout):
    if timeout != None:
        time.sleep(timeout)
    UT = "%2C".join(UT_list)

    # schema options: wos,
    schema = "wos"

    url = "https://incites-api.clarivate.com/api/incites/DocumentLevelMetricsByUT/json?UT=" + UT + \
          "&ver=2&schema=" + schema + "&esci=n"

    headers = {'content-type': 'application/json',
               'Accept-Charset': 'UTF-8',
               #'X-ApiKey': '8dd572a0b0e4104c9ae4d065804b26fd76b21251'
               'X-ApiKey': '5065f3690e5ee299b00f49122317435fbc0ab8f6'}
    r = requests.get(url, headers=headers)
    r = json.loads(r.text)

    print(r)

    result_list = r['api'][0]['rval']

    return result_list



def records_complete_api_search(query, end, timeout, start=None):

    query_clean = urllib.parse.quote(query)
    wos = search_wos(query_clean, 1, 100, end, timeout, start_year=start)

    result_summary = wos['QueryResult']

    # extract the number of found records
    records_found = result_summary['RecordsFound']

    return records_found

# if there is a maxaccept, we will skip queries with more returns than the argument value
# e.g. skip the download of 200,000 publications by wang, E.
def complete_api_search(query, end, timeout, max_accept=None, bybatch=False, batchid=1, bybatch_increment=5,
                        start=None):

    complete_output = []

    # run the WoS search
    query_clean = urllib.parse.quote(query)
    wos = search_wos(query_clean, 1, 100, end, timeout, start)

    result_summary = wos['QueryResult']

    # extract the number of found records
    records_found = result_summary['RecordsFound']

    # here we control for the max accept
    if records_found > max_accept:
        return ["skip", records_found]


    # now we print the results
    print(result_summary, '\n')


    # there is a maximum of 100 UT numbers per request to the incites API
    # so if there are more than 100 returns from WoS, we need to break them up into batches

    batches = math.ceil(records_found/100)

    loopstart = 0
    loopend = batches

    if bybatch == True:
        loopstart = batchid-1
        loopend = loopstart + bybatch_increment


    for b in range(loopstart, loopend):
        #print("batch is", b + 1)
        UT_list = []

        if b != 0:
            wos = search_wos(query_clean, b*100+1, 100, end, timeout, start)

        wos_batch = wos['Data']
        for d in wos_batch:
            UT_list.append(d['UT'][4:])


        #wos_batch = data[b * 100:100 * (b + 1)]
        #incites_batch = search_incites(UT_list[b * 100:100 * (b + 1)])
        incites_batch = search_incites(UT_list, timeout)

        incites_ids = [x["ACCESSION_NUMBER"] for x in incites_batch]

        # print(len(wos_batch))
        # print(len(incites_batch))

        # as not all returns from wos are found in incites, we need to stitch it all together

        for i in range(0, len(wos_batch)):
            # extract the wos_id i.e. UT e.g. 'WOS:A1996UJ65400007'
            wos_id = str(wos_batch[i]["UT"][4:])
            # now we search for the corresponding id among the incites results
            try:
                incites_index = incites_ids.index(wos_id)
                complete_output.append({"wos": wos_batch[i], "incites": incites_batch[incites_index]})
            except:
                complete_output.append({"wos": wos_batch[i], "incites": None})


    #for i in range(0, len(complete_output)):
    #    print(str(i+1)+":")
    #    print(complete_output[i]['wos'])
    #    print(complete_output[i]['incites'], '\n')

    return complete_output


def parse_api_return(a):

    try:
        id = a['wos']['UT']
    except:
        id = None

    try:
        title = a['wos']['Title']['Title'][0]
        if type(title) == list:
            title = title[0]
        if title[0] == "[":
            title = re.sub(r'[\[\]]', "", title)
    except:
        title = None

    try:
        title_secondary = a['wos']['Title']['Title'][1]
        if type(title_secondary) == list:
            title_secondary = title_secondary[0]
            if title_secondary[0] == "[":
                title_secondary = re.sub(r'[\[\]]', "", title_secondary)
    except:
        title_secondary = None

    try:
        doctype = a['wos']['Doctype']['Doctype'][0]
    except:
        doctype = None

    try:
        journal = a['wos']['Source']['SourceTitle'][0]
    except:
        journal = None

    try:
        issue = a['wos']['Source']['Issue'][0]
    except:
        issue = None

    try:
        pages = a['wos']['Source']['Pages'][0]
    except:
        pages = None

    try:
        volume = a['wos']['Source']['Volume'][0]
    except:
        volume = None

    try:
        pub_date = a['wos']['Source']['Published.BiblioDate'][0]
    except:
        pub_date = None

    try:
        pub_year = a['wos']['Source']['Published.BiblioYear'][0]
    except:
        pub_year = None

    try:
        authors = a['wos']['Author']['Authors']
    except:
        authors = None

    try:
        keywords = a['wos']['Keyword']['Keywords']
    except:
        keywords = None

    try:
        doi = a['wos']['Other']['Identifier.Doi'][0]
    except:
        doi = None

    ## Here we do the incites part of the API return

    try:
        is_international_collab = a['incites']['IS_INTERNATIONAL_COLLAB']
    except:
        is_international_collab = None

    try:
        times_cited = a['incites']['TIMES_CITED']
    except:
        times_cited = None

    try:
        impact_factor = a['incites']['IMPACT_FACTOR']
    except:
        impact_factor = None

    try:
        journal_expected_citations = a['incites']['JOURNAL_EXPECTED_CITATIONS']
    except:
        journal_expected_citations = None

    try:
        open_access = a['incites']['OPEN_ACCESS']['OA_FLAG']
    except:
        open_access = None

    try:
        is_industry_collab = a['incites']['IS_INDUSTRY_COLLAB']
    except:
        is_international_collab = None

    try:
        jnci = a['incites']['JNCI']
    except:
        jnci = None

    try:
        percentile = str(a['incites']['PERCENTILE'])
    except:
        percentile = None

    # print(a)
    # print('\n', 'id:', id,
    #       '\n', 'title:', title,
    #       '\n', 'title_secondary:', title_secondary,
    #       '\n', 'doctype:', doctype,
    #       '\n', 'journal:', journal,
    #       '\n', 'issue:', issue,
    #       '\n', 'volume:', volume,
    #       '\n', 'pub_date:', pub_date,
    #       '\n', 'pub_year:', pub_year,
    #       '\n', 'authors:', authors,
    #       '\n', 'keywords:', keywords,
    #       '\n', 'is_international_collab:', is_international_collab,
    #       '\n', 'times_cites:', times_cited,
    #       '\n', 'impact_factor:', impact_factor,
    #       '\n', 'journal_expected_citations:', journal_expected_citations,
    #       '\n', 'open_access:', open_access,
    #       '\n', 'jnci:', jnci,
    #       '\n', 'percentile:', percentile,
    #       '\n', '\n', )

    # return a list of tuples:
    tuple_list = [
        ('api_id', id),
        ('title', title),
        ('title_secondary', title_secondary),
        ('doctype', doctype),
        ('journal', journal),
        ('issue', issue),
        ('volume', volume),
        ('pub_date', pub_date),
        ('pub_year', pub_year),
        ('authors', authors),
        ('keywords', keywords),
        ('is_international_collab', is_international_collab),
        ('times_cites', times_cited),
        ('impact_factor', impact_factor),
        ('journal_expected_citations', journal_expected_citations),
        ('open_access', open_access),
        ('jnci', jnci),
        ('percentile', percentile),
        ('raw_result', str(a))
    ]


    return tuple_list


if __name__ == "__main__":
    query = "AU=(Wallenius, Ville)"
    year = 2013

    complete_api_search(query, year, 5)

# run the incites search
#print(search_incites(["000282071900010", "000265174600030"]))