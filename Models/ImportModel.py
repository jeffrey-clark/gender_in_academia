from Models.initialize import *


class Row:
    def __init__(self, tuples):
        for t in tuples:
            value = t[1]
            if str(value).lower() in ['none', 'na', 'nan']:
                value = None
            setattr(self, t[0], value)

    def append_att(self, t):
        setattr(self, t, None)

    def get_cols(self):
        return list(object_atts_to_dic(self).keys())

    # control how the row output when we print
    def __str__(self):
        return json_obj(self, pref_order)



class Spreadsheet:
    def __init__(self, name, filepath=None, sheetname=None, specific_column_names=None):
        self.name = name
        self.rows = []
        self.col_names = []
        self.df = None

        if filepath != None:

            filename = re.search(r'[\\|\/]([^\\\/]*$)', filepath).group(1)
            print("importing from spreadsheet:", filename, '\n')

            # import the data
            self.df = pd.read_excel(filepath, sheet_name=sheetname)

            self.col_names = self.df.columns.tolist()
            self.update_col_order()


            for i in range(0, len(self.df)):
                progress_bar(i+1, len(self.df))
                tuples = []
                for col in self.col_names:
                    value = self.df[col][i]
                    if (str(value)[0] == "[" and str(value)[-1] == "]") or \
                        (str(value)[0] == "{" and str(value)[-1] == "}"):
                        #print("value is", value)
                        try:
                            value = json.loads(str(self.df[col][i]))
                        except:
                            value = None
                    tuples.append((col, value))

                self.rows.append(Row(tuples))

    def update_col_order(self):
        self.col_names = part_reorder_list(self.col_names, pref_order)

    def rename_cols(self, tuples):

        # update the value in self.col_names
        for t in tuples:
            i = self.col_names.index(t[0])
            self.col_names[i] = t[1]

        self.update_col_order()

        # now update the attribute name in all the rows
        for t in tuples:
            for r in self.rows:
                att_val = getattr(r, t[0])
                setattr(r, t[1], att_val)
                delattr(r, t[0])

    def get_col(self, col_name):
        output = [getattr(r, col_name) for r in self.rows]
        return output

    def get_cols(self, col_names_of_interest):
        output = []
        for r in self.rows:
            extracts = []
            for c in col_names_of_interest:
                extracts.append(getattr(r, c))
            output.append(tuple(extracts))
        return output

    # def add_col(self, col_name, after=None):
    #     if after == None:
    #         index = len(self.col_names) - 1
    #     else:
    #         index = self.col_names.index(after)
    #     # split the list on after
    #     before = self.col_names[0:(index + 1)]
    #     after = self.col_names[(index + 1):]
    #     self.col_names = before + [col_name] + after
    #
    #     for r in self.rows:
    #         r.append_att(col_name)

    def add_col(self, col_name):
        self.col_names = self.col_names + [col_name]

        for r in self.rows:
            r.append_att(col_name)

    def get_rows(self, tuples):
        output = self.rows.copy()
        for t in tuples:
            reduced_output = []
            att = t[0]
            val = t[1]
            for r in output:
                if getattr(r, att) == val:
                    reduced_output.append(r)
            output = reduced_output
        return output


    # only rows where the cols in col_list are not blank, are kept
    def filter_rows(self, col_list):
        input = self.rows.copy()
        output = []
        for row in input:
            append = True
            for c in col_list:
                x = getattr(row, c)
                if x == None:
                    append = False

            if append:
                output.append(row)
        return output



    def update_df(self):
        df_columns = []
        data = {}
        for p in pref_order:
            if p in self.col_names:
                data[p] = self.get_col(p)
                df_columns.append(p)
        for c in self.col_names:
            if c in pref_order:
                pass
            else:
                data[c] = self.get_col(c)
                df_columns.append(c)

        self.df = pd.DataFrame(data, columns=df_columns)


    def convert_bool_cols(self, int_col_list):
        for r in self.rows:
            for col_name in int_col_list:
                val = getattr(r, col_name)
                if val == 1:
                    new_val = True
                elif val == 0:
                    new_val = False
                elif val == None:
                    new_val = None
                else:
                    raise  ValueError("Problem in boolean conversion.")
                setattr(r, col_name, new_val)






def original():
    # Sepcify the spreadheet containing the original data #
    filename = 'VR-ansökningar 2012-2016.xlsx'
    filepath = project_root + '/Spreadsheets/' + filename
    sheet_index = 1
    cols = ['Dnr', 'Förnamn', 'Efternamn', 'Medelsförvaltare', 'ProjekttitelSv', 'ProjekttitelEn', 'Nyckelord']

    sheet = Spreadsheet('Researchers', filepath, sheet_index, cols)
    sheet.rename_cols([('Dnr', 'app_id'), ('Förnamn', 'name'), ('Efternamn', 'surname'),
                          ('Medelsförvaltare', 'financier'), ('ProjekttitelSv', 'project_title_swe'),
                          ('ProjekttitelEn', 'project_title_eng'), ('Nyckelord', 'keywords')])

    return sheet


def scrape6():
    # Sepcify the spreadheet containing the original data #
    filename = 'scrape_results_6.0.xlsx'
    filepath = project_root + '/Spreadsheets/' + filename
    sheet_index = 0
    cols = ["ID", "app_id", "Surname", "Name"]
    sheet = Spreadsheet('Researchers', filepath, sheet_index, cols)
    sheet.rename_cols([('Surname', 'surname'), ('Name', 'name')])

    return sheet





# this function converts a string with keywords into a list
def clean_keywords(self):
# 1. Make a list to replace the self.keywords after all adjustments
    clean = []
# 2. Check if a row has valid keywords, if so, split on delimeter
    for i in range(0, len(self.keywords)):
        k = self.keywords[i]
        #print(str(i) + ":", self.app_id[i])
        to_append = None
        # the check_none function checks if the input is a irrelevant value like 0, None, Nan, etc.
        if check_none(k) == False:
            # the find_delim function identifes the delimiter
            d = find_delim(k)
            to_append = str(k).split(d)
# 3. (still in if-statement) check the last keyword in list is complete (at least 5 chars), if not delete
            if len(to_append[-1]) < 5:
                to_append[-1] = ''
            to_append = clean_str_list(to_append)

        clean.append(to_append)
        #print(to_append)
    if clean == [None]:
        clean = None
    self.keywords = clean




def export(spreadsheet_obj_list, export_filepath):
    try:
        filename = re.search(r'[\\|\/]([^\\\/]*$)', export_filepath).group(1)
    except:
        filename = export_filepath
    print("exporting Spreadsheet objects to:", filename, '\n')
    sheet_names = []
    dataframes = []

    for spreadsheet_obj in spreadsheet_obj_list:
        sheet_names.append(spreadsheet_obj.name)
        dic = {}

        # Lets check all the rows for any missed columns
        for row in spreadsheet_obj.rows:
            att_list = row.get_cols()
            for a in att_list:
                if a not in spreadsheet_obj.col_names:
                    spreadsheet_obj.col_names.append(a)

        for col in spreadsheet_obj.col_names:
            col_list = []
            for r in spreadsheet_obj.rows:
                try:
                    value = getattr(r, col)
                except:
                    value = None

                if isinstance(value, (list, dict, tuple)):
                    value = json.dumps(value, ensure_ascii=False, cls=Npencoder)

                col_list.append(value)

            dic[col] = col_list
        dataframes.append(pd.DataFrame(dic, ))

    # Create a new excel workbook
    writer = pd.ExcelWriter(export_filepath, engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    for df in dataframes:
        df.to_excel(writer, sheet_name=sheet_names[dataframes.index(df)], index=False)

    writer.save()


def export_df(df_list, sheet_names, export_filepath):
    # Create a new excel workbook
    writer = pd.ExcelWriter(export_filepath, engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    for df in df_list:
        df.to_excel(writer, sheet_name=sheet_names[df_list.index(df)], index=False)

    writer.save()





if __name__ == "__main__":



    data = original()
    print(data.df)
    data.update_df()
    print(data.df)

    x  = data.get_rows([('financier', 'Karolinska Institutet'), ('Beslut', 'Avslag')])
    y = data.get_rows([('financier', 'Karolinska Institutet'), ('Beslut', 'Beviljad')])
    acc_rate = len(y)/(len(x)+len(y))

    print("acceptance rate at karolinska:", acc_rate)

    # for i in range(22850, len(data.app_id)):
    #     try:
    #         keywords = data.keywords[i]
    #         if keywords != None:
    #
    #             language = identify_language_list(keywords)
    #             if language == None:
    #                 language = "unknown"
    #             print(language + ":", keywords)
    #
    #             to_insert = [('id', int(i+1)), ('app_id', data.app_id[i]), ('keywords', data.keywords[i]),
    #                          ('language', language)]
    #             db.insert(mydb, 'Keywords', to_insert)
    #         else:
    #             print("no keywords")
    #             to_insert = [('id', int(i + 1)), ('app_id', data.app_id[i]), ('keywords', data.keywords[i]),
    #                          ('language', "")]
    #             db.insert(mydb, 'Keywords', to_insert)
    #     except:
    #         print(data.app_id[i], "is already inserted")






    #for i in range(0,len(data.app_id)):
        #print(data.app_id[i] + ":", data.keywords[i])

    #print(data.semicolons)

    #print(str(None))