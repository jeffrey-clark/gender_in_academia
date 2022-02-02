import os

import docxtractor as dxtr
import Models.ImportModel as IM
import threading
import math
import sys
import subprocess
import datetime


def call_exe(start_index, end_index):

    command = "python " + os.getcwd() + "\docxtractor_thread_exe.py " + str(start_index) + " " + str(end_index)
    print([command])
    x = subprocess.run(command, capture_output=True)
    print(x)


def main():

    # import spreadsheet object of researcher data
    #org_sheet = IM.scrape6()

    start_time = datetime.datetime.now()
    print("start time:", start_time)

    start_num = 25001
    end_num = 27229
    per_thread = 500
    num_threads = 7


    max_thread_count = math.ceil((end_num - start_num + 1) / per_thread)
    if num_threads > max_thread_count:
        num_threads = max_thread_count
        print("WE SET THE MAX NUM THREADS TO", num_threads)


    # split into 50 threads
    # then we run the threads
    threads = []

    for i in range(0, max_thread_count):

        start_index = (start_num - 1) + per_thread * i
        end_index =  (start_num - 1) + per_thread * (i+1)
        if i == (max_thread_count - 1):
            end_index = end_num


        t = threading.Thread(target=call_exe, args=(start_index, end_index))
        t.daemon = True
        threads.append(t)


    start_thread = 0
    while True:
        end_thread = start_thread + num_threads
        if end_thread >= max_thread_count:
            end_thread = max_thread_count

        for t in threads[start_thread:end_thread]:
            t.start()
        for t in threads[start_thread:end_thread]:
            t.join()

        start_thread = start_thread + num_threads
        if end_thread == max_thread_count:
            break


    end_time = datetime.datetime.now()
    diff = end_time-start_time
    minutes = diff.total_seconds() / 60
    seconds = diff.total_seconds() % 60


    print("start_time:", start_time)
    print("end time:", end_time)

    print(f"time taken: {math.floor(minutes)} minutes and {math.floor(seconds)} seconds." )

if __name__ == "__main__":
    main()