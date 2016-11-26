import datetime
import sys
import os
import traceback

def logexc(exc,detailed = False):
    print datetime.datetime.now()
    print "exception:",exc[1]
    print "stack:",traceback.print_tb(exc[2])
    if detailed:
        print traceback.print_exc(exc[2])

#TODO:finish this


