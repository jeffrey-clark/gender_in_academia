import re

from docxtractor import *


class API_obj:
    def __init__(self, title, year, authors):
        self.title = title
        self.pub_year = year
        self.authors = authors

class VR_obj:
    def __init__(self, publication, year):
        self.publication = publication
        self.year = year


def match_publications(row, pub):
    match_data = []

    comp = StringComp(row.title, pub.publication, 1, 0)

    # IF A COMPLETE SUBSET
    if comp.subset == True:
        print("pure match:", pub.publication)
        match_data.append({'data': row, 'confident': True})

    # IF WE ALLOW FOR SPELLING MISTAKES, WE REQUIRE MAX 1 YEAR DEVIATION AND ALL AUTHORS TO MATCH
    elif comp.max_percent_letters_matched > 70 and comp.max_percent_words_matched > 70:
        print("No match:", pub.publication)

        if pub.year not in ["multiple", None]:
            deviation = abs(int(row.pub_year) - int(pub.year))
            print("   year deviation is:", abs(int(row.pub_year) - int(pub.year)))
        elif pub.year == "multiple":
                deviation = 0
                print("  multiple years provided. Allowing for now")
        else:
            deviation = 100


        if deviation <= 1:
            # make sure that all the authors match as well
            # note: we might have to make et. al. adjustments in the future
            author_score = 0
            api_authors = json.loads(row.authors)
            for api_auth in api_authors:
                api_surname_full = api_auth.split(", ")[0].lower()
                api_surname_list = re.split(r"[\s-]+", api_surname_full)

                for api_surname in api_surname_list:
                    print("api_surname", api_surname)
                    if only_letters(api_surname) in only_letters(pub.publication):
                        author_score = author_score + 1
                        break

            print("AUTHOR SCORE IS:", author_score)
            print("TOTAL NUM AUTHORS:", len(api_authors))
            # requiring all api authors to match with exception of et al in pdf publication
            if author_score == len(api_authors) or re.search(r"et\.\s*al", pub.publication) != None:
                match_data.append({'data': row, 'confident': True})

            ### HERE WE NEED TO BREAK

    # IF match data is empty, we loosen even more the restriction, but note this will only be indicated as SIMILAR
    if len(match_data) == 0:

        if comp.max_percent_letters_matched > 50 and comp.max_percent_words_matched > 70:
            print("No match:", pub.publication)

            if pub.year not in ["multiple", None]:
                deviation = abs(int(row.pub_year) - int(pub.year))
                print("   year deviation is:", abs(int(row.pub_year) - int(pub.year)))
            elif pub.year == "multiple":
                deviation = 0
                print("  multiple years provided. Allowing for now")
            else:
                deviation = 100

            if deviation == 0:
                # make sure that all the authors match as well
                # note: we might have to make et. al. adjustments in the future
                author_score = 0
                api_authors = json.loads(row.authors)
                for api_auth in api_authors:
                    api_surname_full = api_auth.split(", ")[0].lower()
                    api_surname_list = re.split(r"[\s-]+", api_surname_full)

                    for api_surname in api_surname_list:
                        print("api_surname", api_surname)
                        if only_letters(api_surname) in only_letters(pub.publication):
                            author_score = author_score + 1
                            break

                print("AUTHOR SCORE IS:", author_score)
                print("TOTAL NUM AUTHORS:", len(api_authors))
                # requiring all api authors to match with exception of et al in pdf publication
                if author_score == len(api_authors) or re.search(r"et\.\s*al", pub.publication) != None:
                    match_data.append({'data': row, 'confident': False})

###################



    print("length of the match data is", len(match_data))
    # Now we will remove duplicates in the match_data
    unique_match_data = []
    match1_index = 0
    for match1 in match_data:
        # run against all previous matches, and skip appending if duplicate discovered
        append_status = True
        match2_index = 0
        for match2 in match_data[:(match1_index +1)]:
            if match1_index == match2_index:
                continue
            elif match1['data'].api_id == match2['data'].api_id:
                # the api_id has already been appended, i.e. the match is a duplicate
                # do not append
                append_status = False

                # If the already appended match is missing raw_result, but the current match has raw_result
                # then remove the existing match, and set append to True
                for unique_match in unique_match_data.copy():
                    if unique_match['data'].api_id == match1['data'].api_id:
                        if (unique_match['data'].raw_result == None or unique_match['data'].raw_result == "") and \
                                (match1['data'].raw_result != None or match1['data'].raw_result == ""):
                            unique_match_data.remove(unique_match)
                            print("conducting OVERWRITE")
                            print("from:", unique_match['data'])
                            print("to:", match1['data'])
                            append_status = True

            match2_index = match2_index + 1
        if append_status == True:
            unique_match_data.append(match1)
        match1_index = match1_index + 1

    # now if the length of the unique_match_data is 1, we add the match data to the pub
    print("Processing:", pub.publication)
    if len(unique_match_data) == 1:
        if unique_match_data[0]['confident'] == True:
            pub.api_match = "EXACT"
        else:
            pub.api_match = "SIMILAR"
        # print("SINGLE MATCH:", unique_match_data)
        api_record = unique_match_data[0]['data']
        pub.api_id = api_record.api_id
        pub.title = api_record.title
        pub.doctype = api_record.doctype
        pub.journal = api_record.journal
        pub.issue = api_record.issue
        pub.volume = api_record.volume
        pub.pub_date = api_record.pub_date
        pub.pub_year = api_record.pub_year
        pub.authors = api_record.authors
        pub.keywords = api_record.keywords
        pub.is_international_collab = api_record.is_international_collab
        # not spelling mistake in the api data below
        pub.times_cited = api_record.times_cites
        pub.impact_factor = api_record.impact_factor
        pub.journal_expected_citations = api_record.journal_expected_citations
        pub.open_access = api_record.open_access
        pub.api_raw = api_record.raw_result

        # authors	keywords	is_international_collab	times_cites	impact_factor	journal_expected_citations	open_access	jnci	percentile	raw_result
    # if the lenght of the unique_match_data is > 1, then we need to investigate, push a flag.
    elif len(unique_match_data) > 1:
        if unique_match_data[0]['confident'] == True:
            pub.api_match = "MULTIPLE"
        else:
            pub.api_match = "MULTIPLE SIMILAR"
        # print("MULTIPLE MATCH:", unique_match_data)
    else:
        pub.api_match = "MISSING"

    total_missing = 0
    for pub in pubs:
        if pub.api_match == "MISSING":
            total_missing = total_missing + 1

    researcher.matched_pubs = researcher.extracted_pubs - total_missing



if __name__ == "__main__":

    api_id = "WOS:000352147800008"
    api_title = "Global health care use by patients with type-2 diabetes: Does the type of comorbidity matter?"
    api_year = "2015"
    api_authors = '["Calderon-Larranaga, A.", "Abad-Diez, J. M.", "Gimeno-Feliu, L. A.", "Marta-Moreno, J.", "Gonzalez-Rubio, F.", "Clerencia-Sierra, M.", "Poblador-Plou, B.", "Poncel-Falco, A.", "Prados-Torres, A."]'


    vr_publication  = "(*) Calderón A, Abad JM, Gimeno LA, Marta J, González F, Clerencia M, Poblador B, Poncel A, Prados A. Global health care use by patients with type 2 diabetes: does the type of comorbidity matter? Eur J Intern Med 2015;26(3):203-10. IF: 2.30"
    vr_year = "2015"



    API = API_obj(api_title, api_year, api_authors)
    VR = VR_obj(vr_publication, vr_year)

    match_publications(API, VR)




   #
   # def match_publications(self, df_api_data, researcher):
   #      # take the last pubs list, as we want to match for each researcher as they are added.
   #      pubs = None
   #      for p in self.pubs:
   #          if p != []:
   #              if p[0].app_id == researcher.app_id:
   #                  pubs = p
   #                  break
   #
   #      if pubs == None:
   #          raise ValueError("ERROR IN SELECTING THE PUBS TO MATCH")
   #
   #      # for pub in pubs[0:2]:
   #      for pub in pubs:
   #          #print(pub.publication)
   #
   #          # now we loop through the api data and find matching titles
   #          match_data = []
   #          for index, row in df_api_data.iterrows():
   #              comp = StringComp(row.title, pub.publication, 1, 0)
   #
   #              # IF A COMPLETE SUBSET
   #              if comp.subset == True:
   #                  print("pure match:", pub.publication)
   #                  match_data.append({'data': row, 'confident': True})
   #
   #              # IF WE ALLOW FOR SPELLING MISTAKES, WE REQUIRE MAX 1 YEAR DEVIATION AND ALL AUTHORS TO MATCH
   #              elif comp.max_percent_letters_matched > 70 and comp.max_percent_words_matched > 70:
   #                  print("No match:", pub.publication)
   #                  try:
   #                      deviation = abs(int(row.pub_year) - int(pub.year))
   #                      print("   year deviation is:", abs(int(row.pub_year) - int(pub.year)))
   #                  except:
   #                      if pub.year == "multiple":
   #                          deviation = 0
   #                          print("  multiple years provided. Allowing for now")
   #                      else:
   #                          deviation = 100
   #
   #
   #                  if deviation <= 1:
   #                      # make sure that all the authors match as well
   #                      # note: we might have to make et. al. adjustments in the future
   #                      author_score = 0
   #                      api_authors = json.loads(row.authors)
   #                      for api_auth in api_authors:
   #                          api_surname = api_auth.split(", ")[0].lower()
   #                          print("Surname is:", api_surname)
   #                          if only_letters(api_surname) in only_letters(pub.publication):
   #                              author_score = author_score + 1
   #                      print("AUTHOR SCORE IS:", author_score)
   #                      print("TOTAL NUM AUTHORS:", len(api_authors))
   #                      # requiring all api authors to match with exception of et al in pdf publication
   #                      if author_score == len(api_authors) or re.search(r"et\.\s*al", pub.publication) != None:
   #                          match_data.append({'data': row, 'confident': True})
   #
   #              # IF match data is empty, we loosen even more the restriction, but note this will only be indicated as SIMILAR
   #              if len(match_data) == 0:
   #                  if comp.max_percent_letters_matched > 50 and comp.max_percent_words_matched > 70:
   #                      print("No match:", pub.publication)
   #                      try:
   #                          deviation = abs(int(row.pub_year) - int(pub.year))
   #                          print("   year deviation is:", abs(int(row.pub_year) - int(pub.year)))
   #                      except:
   #                          if pub.year == "multiple":
   #                              deviation = 0
   #                              print("  multiple years provided. Allowing for now")
   #                          else:
   #                              deviation = 100
   #
   #                      if deviation == 0:
   #                          # make sure that all the authors match as well
   #                          # note: we might have to make et. al. adjustments in the future
   #                          author_score = 0
   #                          api_authors = json.loads(row.authors)
   #                          for api_auth in api_authors:
   #                              api_surname = api_auth.split(", ")[0].lower()
   #                              print("Surname is:", api_surname)
   #                              if only_letters(api_surname) in only_letters(pub.publication):
   #                                  author_score = author_score + 1
   #                          print("AUTHOR SCORE IS:", author_score)
   #                          print("TOTAL NUM AUTHORS:", len(api_authors))
   #                          # requiring all api authors to match with exception of et al in pdf publication
   #                          if author_score == len(api_authors) or re.search(r"et\.\s*al", pub.publication) != None:
   #                              match_data.append({'data': row, 'confident': False})
   #
   #          #print("length of the match data is", len(match_data)
   #
   #          # Now we will remove duplicates in the match_data
   #          unique_match_data = []
   #          match1_index = 0
   #          for match1 in match_data:
   #              # run against all previous matches, and skip appending if duplicate discovered
   #              append_status = True
   #              match2_index = 0
   #              for match2 in match_data[:(match1_index+1)]:
   #                  if match1_index == match2_index:
   #                      continue
   #                  elif match1['data'].api_id == match2['data'].api_id:
   #                      # the api_id has already been appended, i.e. the match is a duplicate
   #                      # do not append
   #                      append_status = False
   #
   #                      # If the already appended match is missing raw_result, but the current match has raw_result
   #                      # then remove the existing match, and set append to True
   #                      for unique_match in unique_match_data.copy():
   #                          if unique_match['data'].api_id == match1['data'].api_id:
   #                              if (unique_match['data'].raw_result == None or unique_match['data'].raw_result == "") and (match1['data'].raw_result != None or match1['data'].raw_result == ""):
   #                                  unique_match_data.remove(unique_match)
   #                                  print("conducting OVERWRITE")
   #                                  print("from:", unique_match['data'])
   #                                  print("to:", match1['data'])
   #                                  append_status = True
   #
   #                  match2_index = match2_index + 1
   #              if append_status == True:
   #                  unique_match_data.append(match1)
   #              match1_index = match1_index + 1
   #
   #          # now if the length of the unique_match_data is 1, we add the match data to the pub
   #          print("Processing:", pub.publication)
   #          if len(unique_match_data) == 1:
   #              if unique_match_data[0]['confident'] == True:
   #                  pub.api_match = "SINGLE"
   #              else:
   #                  pub.api_match = "SIMILAR"
   #              #print("SINGLE MATCH:", unique_match_data)
   #              api_record = unique_match_data[0]['data']
   #              pub.api_id = api_record.api_id
   #              pub.title = api_record.title
   #              pub.doctype = api_record.doctype
   #              pub.journal = api_record.journal
   #              pub.issue = api_record.issue
   #              pub.volume = api_record.volume
   #              pub.pub_date = api_record.pub_date
   #              pub.pub_year = api_record.pub_year
   #              pub.authors = api_record.authors
   #              pub.keywords = api_record.keywords
   #              pub.is_international_collab = api_record.is_international_collab
   #              # not spelling mistake in the api data below
   #              pub.times_cited = api_record.times_cites
   #              pub.impact_factor = api_record.impact_factor
   #              pub.journal_expected_citations = api_record.journal_expected_citations
   #              pub.open_access = api_record.open_access
   #              pub.api_raw = api_record.raw_result
   #
   #              # authors	keywords	is_international_collab	times_cites	impact_factor	journal_expected_citations	open_access	jnci	percentile	raw_result
   #          # if the lenght of the unique_match_data is > 1, then we need to investigate, push a flag.
   #          elif len(unique_match_data) > 1:
   #              if unique_match_data[0]['confident'] == True:
   #                  pub.api_match = "MULTIPLE"
   #              else:
   #                  pub.api_match = "MULTIPLE SIMILAR"
   #              #print("MULTIPLE MATCH:", unique_match_data)
   #          else:
   #              pub.api_match = "MISSING"
   #
   #      total_missing = 0
   #      for pub in pubs:
   #          if pub.api_match == "MISSING":
   #              total_missing = total_missing + 1
   #
   #      researcher.matched_pubs = researcher.extracted_pubs - total_missing


