import re


def combinations(list):
    output = []
    length = len(list)
    level = 1
    #print(length)
    while length > 0:
      for lev in range(0, (level) ):
        output.append(list[(lev):(length+lev)])
        #print(output)
      #print("finished")
      length = length - 1
      level = level + 1
    return  output


def split_string_to_combos(string):
    string_list = string.split(" ")

    # remove any (fd and )
    if "(fd" in string:
        string_clean = re.sub(r'\(fd\s', "", string)
        string_clean = re.sub(r'\)', "", string_clean)
        string_list = string_clean.split(" ")

    # remove any whitespace from the split
    while "" in string_list:
        string_list.remove("")

    string_list_combos = combinations(string_list)
    string_combos = [" ".join(x) for x in string_list_combos]

    return string_combos


def clean_names(string):
    to_remove = [r'\(\s*tidigare', r'\(\s*f\s*d', r'\)', r'\(\s*also',
                 r'\(\s*previously', r'\(f\.*d\.*', r'\)',
                 r'\(maiden', r'\)', r'\(tid', r'\)', r'\(']
    output = string
    for x in to_remove:
        output = re.sub(x, "", output)
    # now we remove any duplicate spaces
    output = re.sub(r"\s+", " ", output)
    return  output





def fullname_combos(surname, firstname):
    output = []
    for s in split_string_to_combos(clean_names(surname)):
        for f in split_string_to_combos(clean_names(firstname)):
            output.append(s + ", " + f)
    return output

if __name__ == "__main__":

    #print(fullname_combos('de Albuquerque Moreira',"milena harris"))
    print(clean_names("van den Bosch (tid Annerstedt)"))