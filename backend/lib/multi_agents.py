#!/usr/bin/env python3

import multiprocessing
import subprocess
import sys, getopt
import atexit
from signal import signal, SIGINT

def usage():
    print("Usage:")
    print("\t-i <net_interface>")
    print("\t-n <device_num>")
    print("\t-s <start_id>")
    print("Example:")
    print("\tpython multi_agents.py -i wlp2s0 -n 5 -s 5566")

def worker(inf, id):
    """thread worker function"""
    if inf:
        subprocess.run(["./agent_example", "--net", inf, "--id", str(id)])
    else:
        subprocess.run(["./agent_example", "--id", str(id)])
    return

def sig_handler(arg1, arg2):
    for p in multiprocessing.active_children():
        p.terminate()
    sys.exit()

def main(args):
    try:
        opts, args = getopt.getopt(args, "hi:n:s:", ["help", "interface=", "num=", "start_id="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    interface = ""
    number = 1
    start_id = 1
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--interface"):
            interface = a
        elif o in ("-n", "--number"):
            number = int(a)
        elif o in ("-s", "--start_id"):
            start_id = int(a)
        else:
            assert False, "unhandled option"

    print("interface=%s, number=%d, start_id=%d" % (interface, number, start_id))

    jobs = []
    for i in range(number):
        p = multiprocessing.Process(target=worker, args=(interface, (start_id+i),))
        jobs.append(p)
        p.start()

    signal(SIGINT, sig_handler)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        usage()
    else:
        main(args)

