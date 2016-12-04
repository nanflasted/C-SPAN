import httplib
import json
import sqlite3
import uuid
import os
import sys
import datetime
import subprocess

import dbmngr
import csplog
import twdmpr

govhost = "www.govtrack.us"
nTweets,nMemes,nBills,nReplies = 0,0,0,0
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
        
        endpoint = "/data/us/"+caucusnum+"/stats/sponsorshipanalysis_h.txt"
        conn.request("GET",endpoint)
        res = conn.getresponse()
        checkResponse(res,endpoint)
        ideo = res.read().split("\n")
        ideo = ideo[1:-1]

        endpoint = "/data/us/"+caucusnum+"/stats/sponsorshipanalysis_s.txt"
        conn.request("GET",endpoint)
        res = conn.getresponse()
        checkResponse(res,endpoint)
        ideo.extend(res.read().split("\n")[1:-1])
        ideo = [k.split(",") for k in ideo]
        ideo = sorted(ideo,key = lambda l:l[1])
        binsize = len(ideo)//5
        for i in range(5):
            for j in range(binsize*i,binsize*(i+1)-1):
                ideo[j][1] = i
        for j in range(binsize*4,len(ideo)):
            ideo[j][1] = 4

        conn.close()

        ideo = {int(p[0]):p[1] for p in ideo}

        formatted = [(p[u'person'][u'id'],(p[u'person'][u'firstname']+" "+p[u'person'][u'lastname']),p[u'person'][u'name'],p[u'role_type'],p[u'party'],p[u'state'],ideo[p[u'person'][u'id']],None) for p in data[u'objects']]
        if insert:
            dbc = dbmngr.connectDB("./data/","cspdb",False)
            if not dbmngr.insertMany(dbc,"legislator",\
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

def genTweetBlobs(twaccnts):
    try:
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        idcur = dbmngr.queryEntry(dbc,["id","ideology"],["legislator"])
        if idcur is None:
            raise Exception("Query Error at updateLegisImg")
        idlist = idcur.fetchall()
        for i in range(5):
            acclist = [twaccnts[k[0]] for k in idlist if k[1] == i]
            datadir = './data/twblobs/'+str(i) + '/'
            twdmpr.getAllTweets(acclist,datadir+'input.txt')
            print "input file generation for ideology "+str(i)+" success"
            res = subprocess.call(["python",
                "./rnn/train.py",
                "--data_dir="+datadir,
                "--save_dir="+datadir+'model/',
                "--rnn_size=" + str(128),
                "--num_epochs=" + str(50),
                "--learning_rate="+str(0.03),
                ])
            if res != 0: raise Exception("Training subprocess call Error at genTweetBlobs")
            print "model trained for ideology "+str(i)
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False
        
def genTweets(num,iden,insert = True):
    '''generate and insert tweets under iden's name, according to iden's ideology'''
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    try:
        #acquire ideology blob
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        dbc.row_factory = dict_factory
        idcur = dbmngr.queryEntry(dbc,["id","ideology"],["legislator"])
        if idcur is None:
            raise Exception("Query Error at genTweets")
        idict = idcur.fetchall()
        modeldir = './data/twblobs/'+str(idict[iden])+'/model/'

        #generate tweets
        gentweets = []
        for i in range(num):
            numwords = random.choice(range(15,30))
            gentweets += [subprocess.check_output([
                "./rnn/sample.py",
                "--save_dir="+modeldir,
                "-n="+str(numwords),
                "--sample=" + str(1)
                ]).split("\n")[1]]
        print "tweets generation from model complete"

        if insert: 
            #insert into database
            collist = [
                "id",
                "time",
                "type",
                "content",
                "author"
                ]
            contentlist = [(
                uuid.uuid3(uuid.NAMESPACE_DNS,t),
                str(datetime.datetime.now()),
                "post",
                t,
                iden) for t in gentweets]

            if not dbmngr.insertMany(dbc,"content",collist,contentlist):
                raise Exception("Database Insertion Error at genTweets")

        dbc.close()
        return gentweets
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None
        

def genBills(num):
    '''generate a random bill title, and insert into database'''
    #generate a random number k, k in [1,5]
    #generate k bill title literals from bill blob
    #concatenate literals
    #insert into database
    pass

def genMemes(num,iden):
    #generate tweets with genTweets(num,iden)
    #break up tweets into 2 parts randomly
    #generate a number for meme background
    #insert into database
    pass


def genReplies(num,iden,replyto):
    try:
        #generate with genTweets
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        replies = genTweets(num,iden,False)
        #insert into database
        collist = [
                    "id",
                    "time",
                    "type",
                    "content",
                    "author",
                    "replyto",
                    ]
        contentlist = [(
            uuid.uuid3(uuid.NAMESPACE_DNS,t),
            str(datetime.datetime.now()),
            "reply",
            t,
            iden,
            replyto) for t in replies]

        if not dbmngr.insertMany(dbc,"content",collist,contentlist):
            raise Exception("Database Insertion Error at genTweets")

        dbc.close()
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False
        

def populate(t,m,b,r,insert = True):
    try:
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        idlist = dbmngr.queryEntry(dbc,["id"],["legislator"])
        dbc.close()
        for l in idlist:
            tweets = genTweets(t,l,True)
            for tw in tweets:
                reper = random.choice(idlist)
                genReplies(r,reper,tw[0])
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
    parseargs()
    twac = getBasicInfo()
    print "Legislator information scraped"
    genTweetBlobs(twac)
    print "Ideology based tweet generator blob made"
    updateLegisImg()
    print "Legislator images generated"
    committee = getCommInfo()
    print "Committee information scraped"
    getParticipation(committee)
    print "Committee participation information inserted"
    populate(nT,nM,nB,nR)
    print "Done"
    return 
        
if __name__ == "__main__":  main()
