import httplib
import json
import sqlite3
import uuid
import os
import sys

import dbmngr
import csplog
import twdmpr

govhost = "www.govtrack.us"
nTweets,nMemes,nBills,nReplies = 0,0,0,0

def checkResponse(res,endpoint):
    if res.status != 200:
        raise (Exception("HTTP connection error: "+str(res.status),endpoint))
        return False
    return True

def gUID(num1,num2):
    return str(uuid.uuid3(uuid.NAMESPACE_DNS,str(num1)+'-'+str(num2)))
        
def getBasicInfo(insert = True):
    try:
        conn = httplib.HTTPSConnection(govhost)
        endpoint = "/api/v2/role?"+\
                "current=true&"+\
                "role_type__in=senator|representative&"+\
                "fields=person__firstname,person__lastname,state,person__twitterid,person__id,person__name,party,role_type&"+\
                "limit=600"
                
        conn.request("GET",endpoint)
        res = conn.getresponse()
        checkResponse(res,endpoint)
        data = json.loads(res.read())
        formatted = [(p[u'person']['id'],(p[u'person'][u'firstname']+" "+p[u'person']['lastname']),\
                p[u'person']['name'],p[u'role_type'],p[u'party'],p[u'state'],None,None)\
                for p in data[u'objects']]

        if insert:
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            if not dbmngr.insertMany(dbc,"legislator",\
                    ["id","name","desc","role","party","state","network","image"],formatted):
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
        '''handle the situation where person doesn't have an image on govtrack'''
        return open("./data/noimg.jpeg","rb").read()

    def getImg(conn,iden):
        '''Gets the person 'iden's image from govtrack'''
        endpoint = "/data/photos/"+str(iden[0])+"-200px.jpeg"
        try:
            conn.request("GET",endpoint)
            res = conn.getresponse()

            if res.status != 200:
                #means this person doesn't have an image on the govtrack database
                if res.status == 404:
                    print endpoint
                    return buffer(nonexist())
                else:
                    raise Exception("HTTP error:"+str(res.status)+" at updateLegisImg",endpoint)
            return res.read()
        except Exception as e:
            print endpoint
            return buffer(nonexist())

    try:
        conn = httplib.HTTPSConnection(govhost)
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

def getCommInfo(insert = True):
    try:
        conn = httplib.HTTPSConnection(govhost)
        endpoint = "/api/v2/committee?obsolete=false&committee=null&limit=300"
        conn.request("GET",endpoint)
        res = conn.getresponse()
        jd = json.loads(res.read())
        formatted = [
                (c[u'id'],c[u'name'],c[u'jurisdiction'],c[u'committee_type']) 
                for c in jd[u'objects']
                ]
        if insert:
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            if not dbmngr.insertMany(dbc,"committee",["id","name","desc","floor"],formatted):
                raise Exception("Database Insertion Error")
        else:
            pass
        dbc.close()
        conn.close()
        return formatted
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None

def getParticipation(commInfo,insert = True):
    try:
        conn = httplib.HTTPSConnection(govhost)
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        res,jd = None,None
        for c in commInfo:
            endpoint = "/api/v2/committee_member?"
            endpoint += "committee=" + str(c[0])
            endpoint += "&limit=300"
            conn.request("GET",endpoint)
            res = conn.getresponse()
            checkResponse(res,endpoint)

            jd = json.loads(res.read())
            formatted = [
                (gUID(p[u'person'][u'id'],p[u'committee'][u'id']),
                p[u'person'][u'id'],p[u'committee'][u'id'],p[u'role']) for p in jd[u'objects']
            ]
            if insert:
                if not dbmngr.insertMany(dbc,"participate",["id","lid","cid","role"],formatted):
                    raise Exception("Database Insertion Error")
            else:
                pass
        dbc.close()
        conn.close()
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False

def genTweets(num,iden):
    pass

def genBills(num):
    pass

def genMemes(num,iden):
    pass

def genReplies(num,iden):
    pass

def populate(t,m,b,r,insert = True):
    pass
        
    

def parseargs():
    nT,nM,nB,nR= 0,0,0,0
    nT= int(sys.argv[1])
    nM= int(sys.argv[2])
    nB= int(sys.argv[3])
    nR= int(sys.argv[4])
    return nT, nM, nB, nR

def main():
    parseargs()
    getBasicInfo()
    updateLegisImg()
    committee = getCommInfo()
    getParticipation(committee)
    populate(nT,nM,nB,nR)
    return 
        
if __name__ == "__main__":  main()
