import tweepy 
import twcred
import csplog
import sys
import subprocess
import re
import time
import dbmngr

def removeLinks(text):
    text = re.sub(r'((mailto:|(news|(ht|f)tp(s?))://){1}\S+)',"",text)
    text = re.sub(r'&amp;',"and",text)
    if text.split(" ")[-1].find("\xe2") != -1:
        text = " ".join(text.split(" ")[:-1])
    #text = re.sub(r'((\xe2){1}\S+)',"",text)
    return text

def getAllTweets(screen_name,filename):
    try:
        #Twitter only allows access to a users most recent 3240 tweets with this method
        consumer_key, consumer_secret, access_key, access_secret = twcred.auth()
        #authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        alltweets = [];i=0
        for s in screen_name:
            try:
                alltweets.extend(api.user_timeline(screen_name = s, count = 200))
                i+=1
                print str(i) + "/" +str(len(screen_name)) + " done"
            except Exception as e:
                print s,e
        outtweets = [tweet.text.encode("utf-8") for tweet in alltweets]
        outtweets = map(removeLinks,outtweets)
        with open(filename,'w+') as f:
            for t in outtweets:
                f.write(t+'\n')
        return True
    except Exception as e:
        csplog.logexc(sys.exc_info())
        return False
    return False

def genTweetBlobs(twaccnts):
    try:
        dbc = dbmngr.connectDB("./data/","cspdb",False)
        idcur = dbmngr.queryEntry(dbc,["id","ideology"],["legislators"])
        if idcur is None:
            raise Exception("Query Error at updateLegisImg")
        idlist = idcur.fetchall()
        print "query for id, ideology done"
        for i in range(5):
            acclist = [twaccnts[k[0]] for k in idlist if int(k[1]) == i]
            datadir = './data/twblobs/'+str(i) + '/'
            getAllTweets(acclist,datadir+'input.txt')
            print "input file generation for ideology "+str(i)+" success"
            res = subprocess.call(["python",
                "./rnn/train.py",
                "--data_dir="+datadir,
                "--save_dir="+datadir+'model/',
                "--rnn_size=" + str(32),
                "--num_epochs=" + str(1),
                "--seq_length=" + str(10),
                "--learning_rate="+str(0.003),
                "--model=lstm"
                ])
            if res != 0: raise Exception("Training subprocess call Error at genTweetBlobs")
            print "model trained for ideology "+str(i)
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False

def genBillBlobs():
    try:
        datadir = './data/bills/'
        res = subprocess.call(["python",
                "./rnn/train.py",
                "--data_dir="+datadir,
                "--save_dir="+datadir+'model/',
                "--rnn_size=" + str(64),
                "--num_epochs=" + str(3),
                "--seq_length=" + str(10),
                "--learning_rate="+str(0.003),
                "--model=lstm"
                ])
        if res != 0: raise Exception("Training subprocess call Error at genBillBlobs")
        print "model trained for bills"
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        return False
    return False
        
