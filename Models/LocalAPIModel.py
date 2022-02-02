import re

from Models.initialize import *
import Models.ImportModel as IM

class data:
    def __init__(self):
        self.ID = None
        self.app_id = None
        self.fullname = None

        # only one big file at a time
        self.df_big_file = None

        # keep imports stored. Max 5 stored files
        self.df_initial_filenames = []
        self.df_initial_files = []
        self.df_active_initial_file = None
        # keep imports stored. Max 5 stored files
        self.df_name_filenames = []
        self.df_name_files = []
        self.df_active_name_file = None
        # keep imports stored. Max 5 stored files
        self.df_disc_filenames = []
        self.df_disc_files = []
        self.df_active_disc_file = None
        # keep imports stored. Max 5 stored files
        self.df_hyphen_filenames = []
        self.df_hyphen_files = []
        self.df_active_hyphen_file = None

        self.pub_data = None
        # will remain None if no data is found

    def load_data(self, researcher):
        # set relevant values for the researcher
        self.ID = researcher.ID
        self.app_id = researcher.app_id
        self.fullname = researcher.name + " " + researcher.surname

        # load the data
        self.load_big_file()
        self.load_initial_file()
        self.load_name_file()
        self.load_disc_file()
        self.load_hyphen_file()
        self.trim_file_lists()

        # extract all relevant rows
        self.extract_relevant_rows()


    def extract_relevant_rows(self):
        output_df = pd.DataFrame()

        dfs = [self.df_big_file, self.df_active_initial_file, self.df_active_name_file, self.df_active_hyphen_file,
               self.df_active_disc_file]

        for df in dfs:
            # if there is no big file, we need to skip it
            try:
                if df == None:
                    #print("skipping empty")
                    continue
            except:
                pass

            # select rows with matching app_id
            selection = df.loc[df['app_id'] == self.app_id]
            if selection.empty == False:
                if output_df.empty == True:
                    #print("copying df selection to output df")
                    output_df = selection
                else:
                    #print("appended selection to output df")
                    output_df = output_df.append(selection, ignore_index=True)
            else:
                #print("selection empty")
                pass

        if output_df.empty == True:
            self.pub_data = None
        else:
            self.pub_data = output_df



    def load_big_file(self):
        # first we check the bigfiles
        big_files_dir = project_root + '/Spreadsheets/API/Bigfiles'
        big_files = os.listdir(big_files_dir)
        # print(big_files)
        filename = self.app_id + "_bigfile.xlsx"
        filepath = big_files_dir + "/" + filename
        if filename in big_files:
            print("importing BIG FILE:", filename)
            self.df_big_file = pd.read_excel(filepath, sheet_name=0)
            #print(self.df_big_file)
            # convert the xlsx to a df
        else:
            self.df_big_file = None


    def load_initial_file(self):
        # if not big file, then we import the initials files
        initial_files_dir = project_root + '/Spreadsheets/API/Initial_copies'
        initial_files = os.listdir(initial_files_dir)
        for filename in initial_files:
            filename_no_prefix = re.sub(r'initial_', "", filename)
            filename_noext = re.sub(r'.xlsx', "", filename_no_prefix)
            id_range = filename_noext.split("-")

            if int(self.ID) >= int(id_range[0]) and int(self.ID) <= int(id_range[1]):
                print("The applicant", self.app_id, "with id", self.ID, "has initial data in the file", filename)

                # if already stored, set saved df as active df
                if filename in self.df_initial_filenames:
                    print("file is already stored, setting as active ")
                    index = self.df_initial_filenames.index(filename)
                    self.df_active_initial_file = self.df_initial_files[index]
                # esle, import the file
                else:
                    print("file is not stored, importing now")
                    self.df_initial_filenames.append(filename)
                    filepath = initial_files_dir + "/" + filename
                    self.df_initial_files.append(pd.read_excel(filepath, sheet_name=0))
                    self.df_active_initial_file = self.df_initial_files[-1]
                break


    def load_name_file(self):
        # identify the correct file
        name_files_dir = project_root + '/Spreadsheets/API/Name_copies'
        name_files = os.listdir(name_files_dir)
        for filename in name_files:
            filename_noext = re.sub(r'.xlsx', "", filename)
            id_range =  filename_noext.split("-")

            if int(self.ID) >=  int(id_range[0]) and int(self.ID) <= int(id_range[1]):
                print("The applicant", self.app_id, "with org_id", self.ID, "has name data in the file", filename)

                # if already stored, set saved df as active df
                if filename in self.df_name_filenames:
                    print("file is already stored, setting as active ")
                    index = self.df_name_filenames.index(filename)
                    self.df_active_name_file = self.df_name_files[index]
                # esle, import the file
                else:
                    print("file is not stored, importing now")
                    self.df_name_filenames.append(filename)
                    filepath = name_files_dir + "/" + filename
                    self.df_name_files.append(pd.read_excel(filepath, sheet_name=0))
                    self.df_active_name_file = self.df_name_files[-1]
                break

    def load_disc_file(self):
        # identify the correct file
        disc_files_dir = project_root + '/Spreadsheets/API/Discrepancies'
        disc_files = os.listdir(disc_files_dir)
        for filename in disc_files:
            filedisc_noext = re.sub(r'_nameorderdiscs.xlsx', "", filename)
            id_range = filedisc_noext.split("-")

            if int(self.ID) >= int(id_range[0]) and int(self.ID) <= int(id_range[1]):
                print("The applicant", self.app_id, "with ID", self.ID, "has dicrepancy data in the file", filename)

                # if already stored, set saved df as active df
                if filename in self.df_disc_filenames:
                    print("file is already stored, setting as active ")
                    index = self.df_disc_filenames.index(filename)
                    self.df_active_disc_file = self.df_disc_files[index]
                # esle, import the file
                else:
                    print("file is not stored, importing now")
                    self.df_disc_filenames.append(filename)
                    filepath = disc_files_dir + "/" + filename
                    self.df_disc_files.append(pd.read_excel(filepath, sheet_name=0))
                    self.df_active_disc_file = self.df_disc_files[-1]
                break

    def load_hyphen_file(self):
        # if there is a hyphen in the name we import from the hyphens directory
        if "-" in self.fullname:
            hyphen_files_dir = project_root + '/Spreadsheets/API/Hyphens'
            hyphen_files = os.listdir(hyphen_files_dir)
            for filename in hyphen_files:
                filename_no_prefix = re.sub(r'hyphen', "", filename)
                filename_noext = re.sub(r'.xlsx', "", filename_no_prefix)
                id_range = filename_noext.split("-")

                if int(self.ID) >= int(id_range[0]) and int(self.ID) <= int(id_range[1]):
                    print("The applicant", self.app_id, "with org_id", self.ID, "has hyphen data in the file", filename)

                    # if already stored, set saved df as active df
                    if filename in self.df_hyphen_filenames:
                        print("file is already stored, setting as active ")
                        index = self.df_hyphen_filenames.index(filename)
                        self.df_active_hyphen_file = self.df_hyphen_files[index]
                    # esle, import the file
                    else:
                        print("file is not stored, importing now")
                        self.df_hyphen_filenames.append(filename)
                        filepath = hyphen_files_dir + "/" + filename
                        self.df_hyphen_files.append(pd.read_excel(filepath, sheet_name=0))
                        self.df_active_hyphen_file = self.df_hyphen_files[-1]
                    break

    def trim_file_lists(self):
        if len(self.df_initial_files) > 5:
            self.df_initial_files = self.df_initial_files[1:]
        if len(self.df_name_files) > 5:
            self.df_name_files = self.df_name_files[1:]
        if len(self.df_hyphen_files) > 5:
            self.df_hyphen_files = self.df_hyphen_files[1:]
 

if __name__ == "__main__":
    pass