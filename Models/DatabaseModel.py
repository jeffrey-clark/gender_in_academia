import mysql.connector
import re

## NOTE ABOUT SQL: Sometimes we need to use the normal ' and sometimes we use back-ticks `
## If the code fails, try changing the quotes


class Database:
    def __init__(self):
        # set the database connection
        self.db = mysql.connector.connect(
            host="sql142.your-server.de",
            user="administrator",
            password="DYb9U95SyFGvBf9m",
            database="dissertation_scraper"
         )
        self.tables = {}

        # fill the self.tables dictionary
        self.get_tables()

    def get_tables(self):
        mycursor = self.db.cursor()
        sql_string = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES " \
                     "WHERE TABLE_TYPE = 'BASE TABLE'"
        mycursor.execute(sql_string)
        result_tuples = mycursor.fetchall()
        table_names = [x[0] for x in result_tuples]

        # now fill the tables dictionary
        for n in table_names:
            self.tables[n] = Table(self.db, n)


    def check_table(self, table_name):
        mycursor = self.db.cursor()
        sql_string = "SELECT COUNT(*) FROM information_schema.tables WHERE TABLE_NAME = '" + table_name + "'"
        mycursor.execute(sql_string)
        result = mycursor.fetchone()[0]
        if result == 1:
            #print("The table \"" + table_name + "\" exists!")
            return True
        else:
            #print("Table:", table_name, "does not exist.")
            return False

    def create_table(self, table_name, column_tuples, overwrite=False):
        if overwrite:
            self.overwrite_table(table_name)

        # create a cursor object
        mycursor = self.db.cursor()

        col_list = []
        for col, type in column_tuples:
            x = col + " " + type
            col_list.append(x)
        col_string = "(" + ", ".join(col_list) + ")"

        sql_string = "CREATE TABLE " + table_name + " " + col_string + "ENGINE = InnoDB CHARSET=utf8"

        mycursor.execute(sql_string)

        # now we append the table to the self.tables list
        self.tables[table_name] = Table(self.db, table_name)
        print("created table:", table_name)


    def overwrite_table(self, table_name):
            if self.check_table(table_name):
                self.drop_table(table_name)


    def drop_table(self, table_name):
        # create a cursor object
        mycursor = self.db.cursor()
        sql_string = "DROP TABLE " + table_name
        mycursor.execute(sql_string)
        print("deleted table:", table_name)



class Table:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.column_names = self.get_column_names()

    def set_primary_key(self, column):
        mycursor = self.db.cursor()
        sql_string = "ALTER TABLE `" + self.name + "` ADD PRIMARY KEY (`" + column + "`);"
        # ALTER TABLE `dissertation_scraper`.`Researchers` ADD PRIMARY KEY (`id`);
        mycursor.execute(sql_string)
        self.db.commit()

    # this function returns a list of column names
    def get_column_names(self):
        mycursor = self.db.cursor()
        sql_string = "SELECT column_name from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + self.name + "'"
        mycursor.execute(sql_string)
        result = [x[0] for x in mycursor.fetchall()]
        return result

    def add_column(self, column_tuple, after=None):
        if after == None:
            after = self.get_column_names()[-1]
        mycursor = self.db.cursor()
        sql_string = "ALTER TABLE `" + self.name + "` ADD `" + column_tuple[0] + "` " + column_tuple[1] + \
                     " NOT NULL AFTER `" + after + "`;"
        # print(sql_string)
        mycursor.execute(sql_string)

        #update the self.columns
        self.get_column_names()

    def insert(self, tuples):
        mycursor = self.db.cursor()
        # here we need to wrap in backtick quote `
        columns = [str("`" + str(x[0]) + "`") for x in tuples]
        col_string =  ", ".join(columns)
        # here we need to wrap in normal quotes '
        values = [str("'" + sanitize(x[1]) + "'") for x in tuples]
        val_string = ", ".join(values)

        sql_string = "INSERT INTO `" + self.name + "` (" + col_string + ") VALUES (" + val_string + ");"

        mycursor.execute(sql_string)
        self.db.commit()


    def select(self, column, value):
        mycursor = self.db.cursor()
        sql_string = "SELECT * FROM `" + self.name + "` WHERE `" + str(column) + "` = '" + str(value) + "';"
        mycursor.execute(sql_string)
        all_tuple = mycursor.fetchall()

        # convert the tuple to pretty dictionary format
        all = []
        for t in all_tuple:
            dic = {}
            for i in range(0, len(t)):
                dic[self.column_names[i]] = t[i]
            all.append(dic)

        if len(all) == 1:
            result = all[0]
        elif len(all) == 0:
            result = None
        else:
            result = all
        return result


    def count(self, column, value):
        mycursor = self.db.cursor()
        sql_string= "SELECT COUNT( * ) as \"Number of Rows\" FROM " + self.name + " WHERE " + column + "='" + \
                    str(value) + "';"
        mycursor.execute(sql_string)
        result = mycursor.fetchall()[0][0]
        return result





def sanitize(string):
    clean = re.sub(r"\'", "\\'", str(string))
    return clean


def sql_tuple_type_predictor(tuple):
    # input: ('id', 2) --> output: ('id', "INT")
    # input: ('name', 'Adam') --> output ('name', "VARCHAR(256)")
    x = tuple[1]
    type = None

    if isinstance(x, int):
        type = "INT"
    elif isinstance(x, float):
        type = "DOUBLE(50)"
    elif len(str(x)) < 80 or isinstance(x, bool):
        type = "VARCHAR(256)"
    else:
        type = "TEXT"

    return (tuple[0], type)


if __name__ == '__main__':

    mydb = Database()
    #mydb.get_tables()
    #mydb.create_table("test", [("id", "INT"), ("name", "VARCHAR(256)")], True)


    #test = mydb.tables['test']
    #test.set_primary_key("id")

    #test.add_column(('middle', 'VARCHAR(256)'), 'id')

    #print(test.get_column_names())

    #test.insert([('id', 1), ('middle', "jeffrey"), ('name', "clark")])

    #print(test.select(('id', 2)))

    #print(test.count('id', 1))


    keywords = mydb.tables['Keywords']

    print(keywords.select('app_id', "2013-06590"))

    #print("English:", count(mydb, table_name, "language", "english"))
    #print("Swedish:", count(mydb, table_name, "language", "swedish"))