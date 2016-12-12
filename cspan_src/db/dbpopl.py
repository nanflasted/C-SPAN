import httplib
import json
import sqlite3
import uuid
import os
import sys
import datetime
import subprocess
import random

import dbmngr
import csplog
import nwmngr

govhost = "www.govtrack.us"
nT,nB,nM,nR = 0,0,0,0
caucusnum = '114'

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
        print "scraped basic info from govtrack"

        endpoint = "/data/us/"+caucusnum+"/stats/sponsorshipanalysis_h.txt"
        conn.request("GET",endpoint)
        res = conn.getresponse()
        checkResponse(res,endpoint)
        ideo = res.read().split("\n")
        ideo = ideo[1:-1]
        print "scraped house ideology"

        endpoint = "/data/us/"+caucusnum+"/stats/sponsorshipanalysis_s.txt"
        conn.request("GET",endpoint)
        res = conn.getresponse()
        checkResponse(res,endpoint)
        ideo.extend(res.read().split("\n")[1:-1])
        print "scraped senate ideology"

        ideo = [k.split(",") for k in ideo]
        ideo = sorted(ideo,key = lambda l:l[1])
        binsize = len(ideo)//5
        for i in range(5):
            for j in range(binsize*i,binsize*(i+1)-1):
                ideo[j][1] = i
        for j in range(binsize*4,len(ideo)):
            ideo[j][1] = 4

        print "ideology formatted"
        conn.close()
        

        ideo = {int(p[0]):p[1] for p in ideo}

        formatted = [(p[u'person'][u'id'],(p[u'person'][u'firstname']+" "+p[u'person'][u'lastname']),p[u'person'][u'name'],p[u'role_type'],p[u'party'],p[u'state'],ideo[p[u'person'][u'id']],None) for p in data[u'objects']]
        if insert:
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            if not dbmngr.insertMany(dbc,"legislators",\
                    ["id","name","desc","role","party","state","ideology","image"],formatted):
                raise Exception("Database Insertion Error")
            dbc.close()
            return {p[u'person'][u'id']:p[u'person'][u'twitterid'] for p in data[u'objects']} 
        else:
            pass

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
        idcur = dbmngr.queryEntry(dbc,["id"],["legislators"])
        if idcur is None:
            raise Exception("Query Error at updateLegisImg")
        idlist = idcur.fetchall()
        updlist = [(sqlite3.Binary(getImg(conn,p)),p[0]) for p in idlist]
        if not dbmngr.updateMany(dbc,"legislators",["image"],updlist):
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
            if not dbmngr.insertMany(dbc,"committees",["id","name","desc","floor"],formatted):
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
                if not dbmngr.insertMany(dbc,"participates",["id","lid","cid","role"],formatted):
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
        
def genTweets(num,iden,insert = True, prime = None):
    '''generate and insert tweets under iden's name, according to iden's ideology'''
    def dict_factory(cursor, row):
        d = {}
        d[row[0]] = row[1]
        return d
    try:
        #acquire ideology blob
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        #dbc.row_factory = dict_factory
        idcur = dbmngr.queryEntry(dbc,["id","ideology"],["legislators"])
        if idcur is None:
            raise Exception("Query Error at genTweets")
        idict = idcur.fetchall()
        idict = {t[0]:t[1] for t in idict}
        modeldir = './data/twblobs/'+str(int(idict[iden[0]]))+'/model/'
        dbc.close()
        #generate tweets
        gentweets = []
        for i in range(num):
            numwords = random.choice(range(15,30))
            params = [
                "python","./rnn/sample.py",
                "--save_dir",modeldir,
                "-n",str(numwords),
                "--sample",str(1)
                ]
            if prime is not None:
                params += ["--prime",prime]
            gentweets += [subprocess.check_output(params).split("\n")[1]]
        print ("tweets" if insert else "reply") + " generation from model complete"

        collist = [
            "id",
            "time",
            "type",
            "contents",
            "author"
            ]
        contentlist = [[
            unicode(uuid.uuid3(uuid.NAMESPACE_DNS,t)),
            unicode(datetime.datetime.now()),
            u'post',
            t,
            iden[0]] for t in gentweets]
        if insert: 
        #insert into database
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            dbc.text_factory = str
            if not dbmngr.insertMany(dbc,"contents",collist,contentlist):
                raise Exception("Database Insertion Error at genTweets")
            dbc.close()

        return contentlist
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None
        

def genBills(num,committee,iden):
    try:
        res = []
        for i in range(num):
            #generate a random number k, k in [1,5]
            k = random.choice(range(1,6))
            #generate k bill title literals from bill blob
            literals = []
            modeldir = "./data/bills/model/"
            genlits = []
            for _ in range(k):
                numwords = random.choice(range(1,4))
                genlits += [subprocess.check_output([
                        "python","./rnn/sample.py",
                        "--save_dir",modeldir,
                        "-n",str(numwords),
                        "--sample",str(1)
                        ]).split("\n")[1].capitalize()]

            #concatenate literals
            res += [((", ".join(genlits[:-1]) + " and ") if k > 1 else "") + genlits[-1] + " Act of 2017"]
            print res
            print "{0}/{1} bills generated".format(i+1,num)
        #insert into database
        collist = [
                "id",
                "time",
                "type",
                "contents",
                "author",
                "committees"
                ]
        contentlist = [[
                unicode(uuid.uuid3(uuid.NAMESPACE_DNS,r)),
                unicode(datetime.datetime.now()),
                u'bill',
                r,
                iden[0],
                committee] for r in res]
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        dbc.text_factory = str
        if not dbmngr.insertMany(dbc,"contents",collist,contentlist):
            raise Exception("Database Insertion Error at genBills")
        dbc.close()
        print "Bills insertion complete"
        return contentlist
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None

def genMemes(num,iden,background,insert = True,primer=None):
    try:
        #generate tweets with genTweets(num,iden)
        tw = genTweets(num,iden,False,primer)
        #break up tweets into 2 parts randomly
        for t in tw:
            k = random.choice(range(1,len(t[-2].split(" "))-2))
            t[-2] = "<MEME>".join(t[-2].split(t[-2].split(" ")[k]))
        print "top/bottom text generated, separated by string <MEME>"
        collist = [
            "id",
            "time",
            "type",
            "contents",
            "author",
            "memebg"
            ]
        contentlist = [[
            unicode(uuid.uuid3(uuid.NAMESPACE_DNS,t[-2])),
            unicode(datetime.datetime.now()),
            u'meme',
            t[-2],
            iden[0],
            background] for t in tw]
        #insert into database
        if insert:
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            dbc.text_factory = str
            if not dbmngr.insertMany(dbc,"contents",collist,contentlist):
                raise Exception("Database Insertion Error at genMemes")
            dbc.close()
        print "Meme generation completed"
        return contentlist
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None

def genReplies(num,iden,replyto):
    try:
        #generate with genTweets
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        dbc.text_factory = str
        replies = genTweets(num,iden,False)
        #insert into database
        collist = [
                    "id",
                    "time",
                    "type",
                    "contents",
                    "author",
                    "replyto",
                    ]
        contentlist = [[
            unicode(uuid.uuid3(uuid.NAMESPACE_DNS,t[-2])),
            unicode(datetime.datetime.now()),
            u"reply",
            t[-2],
            iden[0],
            replyto] for t in replies]

        if not dbmngr.insertMany(dbc,"contents",collist,contentlist):
            raise Exception("Database Insertion Error at genReplies")

        dbc.close()
        return contentlist
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None

def genVotes(billid,voters):
    try:
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        dbc.text_factory = str
        collist = [
                "id",
                "lid",
                "cid",
                "votes"
                ]
        voteres = [[
            unicode(uuid.uuid3(uuid.NAMESPACE_DNS,str(i)+str(billid))),
            i,
            billid,
            "yea" if random.choice(range(2))>0 else "nay"
            ] for i in voters]
        if not dbmngr.insertMany(dbc,"votes",collist,voteres):
            raise Exception("Database Insertion Error at genVotes")
        dbc.close()
        return voteres
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None
        
def genLikes(contentid, idlist, authorideo=None, ideolist=None):
    try:
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        dbc.text_factory = str
        collist = [
                "id",
                "lid",
                "cid"
                ]
        problist = []
        if authorideo is not None and ideolist is not None:
            problist = [0.01*(4-abs(i-authorideo)) for i in ideolist]
        else:
            problist = [0.05 for _ in idlist]
        
        likes = [idlist[i] for i in xrange(len(idlist)) if random.random() < problist[i]]
        likelist = [[
            unicode(uuid.uuid3(uuid.NAMESPACE_DNS,str(i)+str(contentid)+'l')),
            i,
            contentid
            ] for i in likes]
        if not dbmngr.insertMany(dbc,"likes",collist,likelist):
            raise Exception("Database Insertion Error at genVotes")
        dbc.close()
        return likes
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None
                   


def populate(t,r,insert = True):
    try:
        idlist = None
        if r > 0:
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            idlist = dbmngr.queryEntry(dbc,["id"],["legislators"]).fetchall()
            dbc.close()
        if t == 0:  return True
        for l in idlist:
            tweets = genTweets(t,l,True)
            if r == 0:  continue
            for tw in tweets:
                reper = random.choice(idlist)
                genReplies(r,reper,tw[0])
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False

def parseargs():
    nT,nM,nB,nR= 0,0,0,0
    nT= int(sys.argv[1])
    nM= int(sys.argv[2])
    nB= int(sys.argv[3])
    nR= int(sys.argv[4])
    return nT, nM, nB, nR

def main():
    global nT,nM,nB,nR
    nT,nM,nB,nR=parseargs()
    twac = getBasicInfo()
    print "Legislator information scraped"
    nwmngr.genTweetBlobs(twac)
    print "Ideology based tweet generator blob made"
    updateLegisImg()
    print "Legislator images updated"
    committee = getCommInfo()
    print "Committee information scraped"
    getParticipation(committee)
    print "Committee participation information inserted"
    populate(nT,nR)
    print "Done"
    return 
        
if __name__ == "__main__":  main()
