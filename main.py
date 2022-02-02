from Models.initialize import *
import Models.ImportModel as IM
import Models.DatabaseModel as DBM


def main():

    db = DBM.Database()

    original_sheet = IM.original()

    keyword_table = db.tables['Keywords']

    # import the formatted keywords (5 hour process), replace the trash
    for i in range(0, len(original_sheet.rows)):
        r = original_sheet.rows[i]
        # get the keyword list
        k = keyword_table.select('app_id', r.app_id)
        r.keywords = k['keywords']
        setattr(r, 'keyword_lang', k['language'])



    # extract a sample row and convert to list of tuples
    sample = object_atts_to_tuples(original_sheet.rows[1], ini.pref_order)

    # Figure out the SQL data types
    sql_tuples = []
    for t in sample:
        sql_tuples.append(DBM.sql_tuple_type_predictor(t))

    print(sql_tuples)

    db.create_table('clean_import', sql_tuples, True)

    clean_import = db.tables['clean_import']

    for i in range(0, len(original_sheet.rows)):
        clean_import.insert(object_atts_to_tuples(original_sheet.rows[x]))



if __name__ == "__main__":
    main()