import datetime
import sys
import os
import uuid
import traceback
import dbmngr

def logexc(exc, verbose = True):
    try:
        dbc = dbmngr.connectDB("./log/","log",False)
        collist = [
                "id",
                "event",
                "datetime",
                "name",
                "stack"
                ]
        ins = [
                unicode(uuid.uuid3(uuid.NAMESPACE_DNS,str(hash(exc)))),
                u'exception',
                unicode(datetime.datetime.now()),
                unicode(dbmngr.sanitize(str(exc[1]))),
                unicode(dbmngr.sanitize(str(traceback.format_tb(exc[2])[0])))
                ]
        entry = {collist[i]:ins[i] for i in range(len(ins))}
        dbmngr.insertEntry(dbc,"log",entry)
        if verbose:
            print datetime.datetime.now()
            print "exception:",exc[1]
            print "stack:",traceback.print_tb(exc[2])
            print traceback.print_exc(exc[2])
        dbc.close()
        return True
    except Exception as e:
        print "rekt",e
        print traceback.print_tb(sys.exc_info()[2])
        return False
    return False
        
def logevent(event,description,verbose = True):
    try:
        dbc = dbmngr.connectDB("./log/","log",False)
        collist = [
                "id",
                "event",
                "datetime",
                "name",
                "content"
                ]
        ins = [
                unicode(uuid.uuid3(uuid.NAMESPACE_DNS,str(hash(event)+hash(datetime.datetime.now())))),
                u'event',
                unicode(datetime.datetime.now()),
                unicode(event),
                unicode(description)
                ]
        entry = {collist[i]:ins[i] for i in range(len(ins))}
        dbmngr.insertEntry(dbc,"log",entry)
        if verbose:
            print event
            print description
        dbc.close()
        return True
    except Exception:
        logexc(sys.exc_info())
        return False
    return False




