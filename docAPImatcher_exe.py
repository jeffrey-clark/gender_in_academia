
from docAPImatcher import *
import subprocess

def main(filename, core, total_cores, files_to_run=None):
    if files_to_run != None:
        for f in files_to_run:
            command = "python3 " + project_root + "/docAPImatcher.py " + f + " " + str(core) + " " + str(total_cores)
            #command = "nohup python3 " + project_root + "/docAPImatcher.py " + f + " " + str(core) + " " + str(total_cores) + " &"
            subprocess.run(command, shell=True)
            time.sleep(2700)


if __name__ == "__main__":
    pass


