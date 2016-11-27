import httplib
import json
import os
import sys
import dbmngr
import sqlite3
import csplog
import twdmpr

def getBasicInfo(insert = True):
    try:
        conn = httplib.HTTPSConnection("www.govtrack.us")
        reqstr = "/api/v2/role?current=true&role_type__in=senator|representative&fields=person__firstname,person__lastname,state,person__twitterid,person__id,person__name,party,role_type&limit=600"
        conn.request("GET",reqstr)
        res = conn.getresponse()
        if res.status != 200:
            raise (Exception("HTTP connection error: "+str(res.status),reqstr))
        data = json.loads(res.read())
        formatted = [(p[u'person']['id'],(p[u'person'][u'firstname']+" "+p[u'person']['lastname']),\
                p[u'person']['name'],p[u'role_type'],p[u'party'],p[u'state'],None,None)\
                for p in data[u'objects']]
        if insert:
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            if not dbmngr.insertMany(dbc,"legislator",["id","name","desc","role","party","state","network","image"],formatted):
                raise Exception("Database Insertion Error")
            return {p[u'person'][u'id']:p[u'person'][u'twitterid'] for p in data[u'objects']} 
        else:
            pass
        dbc.close()
        conn.close()
        return formatted
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None

def updateLegisImg():
    def nonexist():
        return open("./data/noimg.jpeg","rb").read()
    def getImg(conn,iden):
        reqstr = "/data/photos/"+str(iden[0])+"-200px.jpeg"
        try:
            conn.request("GET",reqstr)
            res = conn.getresponse()
            if res.status != 200:
                if res.status == 404:
                    print reqstr
                    return buffer(nonexist())
                else:
                    raise Exception("HTTP error:"+str(res.status)+" at updateLegisImg",reqstr)
            return res.read()
        except Exception as e:
            print reqstr
            return buffer(nonexist())
    try:
        conn = httplib.HTTPSConnection("www.govtrack.us")
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        idcur = dbmngr.queryEntry(dbc,["id"],["legislator"])
        if idcur is None:
            raise Exception("Query Error at updateLegisImg")
        idlist = idcur.fetchall()
        updlist = [(sqlite3.Binary(getImg(conn,p)),p[0]) for p in idlist]
        if not dbmngr.updateMany(dbc,"legislator",["image"],updlist):
            raise Exception("Update Error at updateLegisImg")
        conn.close()
        dbc.close()
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False

def getCommInfo():
    try:
        conn = httplib.HTTPSConnection("https://www.govtrack.us")
        endpoint = "/api/v2/committee?obsolete=false&limit=300"
        conn.request("GET",endpoint)
        res = conn.getresponse()
        jd = json.loads(res.read())
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False
        

def main():
    updateLegisImg()
        
if __name__ == "__main__":  main()
