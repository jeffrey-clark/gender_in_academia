import json
import wsgiref.simple_server
import subprocess
import threading
import docAPImatcher_exe as exe

from docAPImatcher import *

def get_id():
    # read file
    with open('server_id.json', 'r') as file:
        data = file.read()
    # parse file
    obj = json.loads(data)
    # show values
    return int(obj["id"])

def get_file():
    server_id = get_id()
    detailed = []
    files = os.listdir(project_root + "/Spreadsheets/new_docx_analysis/threaded")
    for f in files:
        start_index = re.search(r"_(\d+)_", f).group(1)
        detailed.append({'filename': f, 'start_index': start_index})
    detailed = sorted(detailed , key = lambda i: i['start_index'])
    files = [x['filename'] for x in detailed]
    file = files[(server_id-1)]
    return file

#def call_exe_server(filename, process, ftr):
#    command = "nohup python3 " + project_root + "/docAPImatcher_exe.py " + filename + " " + str(process) + " 8" + " " + ftr + " &"
#    subprocess.run(command)

def call_exe(filename, process):
    command = "python " + project_root + "\docAPImatcher_exe.py " + filename + " " + str(process) + " " + "4"
    print([command])
    x = subprocess.run(command, capture_output=True)
    print(x)


def main_local():
    filename = get_file()

    threads = []
    for process in range(1, 9):
        # for local computer test
        t = threading.Thread(target=call_exe, args=(filename, process))
        t.daemon = True
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()



def main(from_id, to_id):

    id = int(from_id)
    files_to_run = []
    while True:
        plus_fvhundred = id + 499
        filename = "analysis_" + str(id) + "_" + str(plus_fvhundred) + ".xlsx"
        files_to_run.append(filename)
        id = plus_fvhundred + 1
        if id > int(to_id):
            break

    filename = files_to_run[0]

    threads = []
    for core in range(1, 9):
        #exe.main(filename, core, 8, files_to_run)
        t = threading.Thread(target=exe.main, args=(filename, core, 8, files_to_run))
        t.daemon = True
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    try:
        from_id = sys.argv[1]
        to_id = sys.argv[2]
    except:
        from_id = 5001
        to_id = 10000

    main(from_id, to_id)