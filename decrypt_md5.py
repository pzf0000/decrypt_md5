from hashlib import md5
from string import ascii_letters, digits
from itertools import permutations
import threading
import multiprocessing
import time
import os

all_letters = ascii_letters + digits + '.,;*@#'

md5_value = 'e522214d32eabe3fda854da213c62d5f'
min_len = 8
max_len = 18
worker_num = 8
thread_num = 8
taskq = multiprocessing.Queue()
resultq = multiprocessing.Queue()
len_q = multiprocessing.Queue()
record = []


class Decrypt(threading.Thread):
    def __init__(self, name, taskq):
        threading.Thread.__init__(self)
        self.name = name
        self.taskq = taskq

    def run(self):
        while True:
            text = self.taskq.get()
            print("Get ==> " + str(text), end="\t")
            if md5(text.encode()).hexdigest() == md5_value:
                print(text)
                resultq.put((True, text))
                return True, text
            else:
                print("False")


def do_task(taskq):
    thread_list = []
    for i in range(thread_num):
        name = str(os.getpid()) + "_" + str(i)
        thread = Decrypt(name, taskq)
        # thread.setDaemon(True)
        thread.start()
        thread_list.append(thread)
    while taskq.empty():
        return
    # for t in thread_list:
    #     t.join()


def put_task(taskq, len_q):
    while True:
        k = len_q.get()
        for item in permutations(all_letters, k):
            item = ''.join(item)
            # print("Put ==> " + str(item))
            taskq.put(item)
        # time.sleep(1000)
        # exit(0)


if __name__ == '__main__':
    if len(md5_value) != 32:
        print('error')
        exit(0)
    for i in range(min_len, max_len):
        len_q.put(i)

    md5_value = md5_value.lower()
    multiprocessing.freeze_support()
    for i in range(int(worker_num / 2)+1):
        multiprocessing.freeze_support()
        process = multiprocessing.Process(target=put_task, args=(taskq, len_q,))
        process.start()
        record.append(process)

    for i in range(int(worker_num / 2)-1):
        name = "pro_" + str(i)
        process = multiprocessing.Process(target=do_task, name=name, args=(taskq,))
        process.start()
        record.append(process)
    result = resultq.get()
    for process in record:
        process.join()
    print(result)
