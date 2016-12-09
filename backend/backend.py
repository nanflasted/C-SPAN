import csplog
import dbmngr
import dbinit
import loginit
import dbpopl
import nwmngr

import os
import sys
import subprocess

#basic functions for managing the backend database

def hardreset():
    '''Nuke everything, basically
    "Our words are backed with NUCLEAR WEAPONS" --Mahatma Gandhi
    Args:
        None
    Returns:
        bool: whether the operation was successful
    '''
    try:
        subprocess.call(['rm','-rf','./data/'])
        subprocess.call(['rm','-rf','./log/'])
        os.mkdir('./data')
        subprocess.call(['cp','./prestored/noimg.jpeg','./data/'])
        os.mkdir('./data/bills')
        subprocess.call(['cp','./prestored/bills.txt','./data/bills/input.txt'])
        os.mkdir('./data/bills/model')
        os.mkdir('./twblobs')
        for i in range(5):
            os.mkdir('./twblobs/{0}'.format(i))
            os.mkdir('./twblobs/{0}/model/'.format(i))
        os.mkdir('./log/')
        dbinit.main()
        loginit.main()
        return True
    except Exception:
        return False
    return False

def softreset():
    '''Remove everything except for hard trained neural nets
    Args:
        None
    Returns:
        bool: whether the operation was successful
    '''
    try:
        subprocess.call(['rm','./data/cspdb.db'])
        dbinit.main()
        csplog.logevent("softreset","Database was soft reset")
        return True
    except Exception:
        return False
    return False

def generateNN():
    '''Generate Neural Network Blobs for Tweets and Bills
    Args:
        None
    Returns:
        bool: whether the operation was successful
    '''
    try:
        twac = dbpopl.getBasicInfo(False)
        nwmngr.genTweetBlobs(twac)
        nwmngr.genBillBlobs()
        csplog.logevent("neuralnet","Neural Networks generated")
        return True
    except Exception:
        return False
    return False

def populate(t=5,m=0,b=10,r=1):
    '''Populate the database
    Currently unsupported: populate memes initially
    Args:
        t:      Number of tweets
        m:      Number of memes
        b:      Number of bills
        r:      Number of replies
    Returns:
        bool:   whether the operation was successful
    '''
    try:
        twac = dbpopl.getBasicInfo()
        dbpopl.updateLegisImg()
        com = dbpopl.getCommInfo()
        dbpopl.getParticipation(com)
        dbpopl.populate(t,r,True)
        for _ in range(b):
            bill = dbpopl.genBills(1,random.choice(com),(random.choice(twac.keys()),))
            genVotes(bill[0][0],twac.keys())
            genLikes(bill[0][0],twac.keys())
        csplog.logevent("populate","Basic Database population finished")
        return True 
    except Exception:
        return False
    return False

def getIdeology():
    '''Get all of the legislators' ideology score
    Args:
        None
    Returns:
        dict:       A dictionary with {id->ideology}, None if operation failed
    '''
    try:
        dbc = dbmngr.connectDB('./data/','cspdb',False)
        idcur = dbmngr.queryEntry(dbc,["id","ideology"],["legislators"]).fetchall()
        dbc.close()
        iddict = {i[0]:i[1] for i in idcur}
        csplog.logevent("query","queried all ideologies")
        return iddict
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return None
    

def newTweet(num,legis_id,insert = True,likes=True):
    '''Generate and maybe insert new tweets for given legislator
    Args:
        num:        Number of tweets to be generated
        legis_id:   id of the legislator, should be int
        insert:     Whether to insert the generated tweets into the db
        likes:      Whether to also generate the 'like' relations
    Returns:
        content:    ids of the generated contents if successful, None otherwise
    '''
    try:
        res = dbpopl.genTweets(num,(legis_id,),insert)
        res = [t[0] for t in res]
        if likes:
            idict = getIdeology()
            for r in res:
                dbpopl.genLikes(r,idict.keys(),idict[legis_id],idict.values())
        return res
    except Exception:
        return None
    return None

def newMeme(num,legis_id,bg,insert = True,likes=True):
    '''Similar to newTweet, but in the meme form
    Args:
        num:        Number of memes to be generated
        legis_id:   id of the legislator, should be int
        bg:         the encoded string for the background of the meme
        insert:     Whether to insert the generated memes into the db
        likes:      Whether to also generate the 'like' relations
    Returns:
        content:    ids of the generated contents if successful, None otherwise
    '''
    try:
        res = dbpopl.genMemes(num,(legis_id,),bg,insert)
        res = [m[0] for m in res]
        if likes:
            idict = getIdeology()
            for r in res:
                dbpopl.genLikes(r,idict.keys(),idict[legis_id],idict.values())
        return res
    except Exception:
        return None
    return None

def newBill(num,legis_id,com_id,likes=True):
    '''Generate new bills, and have all the members vote on it
        Note the lack of 'insert' parameter here, any bill generated will be
        automatically inserted.
    Args:
        num:        Number of memes to be generated
        legis_id:   id of the legislator, should be int
        com_id:     id of the committee, should be int
        likes:      Whether to also generate the 'like' relations
    Returns:
        content:    ids of the generated contents if successful, None otherwise
    '''
    try:
        res = dbpopl.genBills(num,com_id,(legis_id,))
        res = [b[0] for b in res]
        idict = getIdeology()
        for r in res:
            dbpopl.genVotes(r,idict.keys())
            if likes:
                dbpopl.genLikes(r,idict.keys(),idict[legis_id],idict.values())
        return res
    except Exception:
        return None
    return None

def newReply(num,legis_id,oc_id,likes=True):
    '''Generate replies to a content
    Args:
        num:        Number of memes to be generated
        legis_id:   id of the legislator, should be int
        oc_id:      id of the content being replied to, should be string of some uuid
        likes:      Whether to also generate the 'like' relations
    Returns:
        content:    ids of the generated contents if successful, None otherwise
    '''
    try:
        res = dbpopl.genReplies(num,(legis_id,),oc_id)
        res = [r[0] for r in res]
        if likes:
            idict = getIdeology()
            for r in res:
                dbpopl.genLikes(r,idict.keys(),idict[legis_id],idict.values())
        return res
    except Exception:
        return None
    return None

def server():
    '''Use this script as a server
    Currently unfinished
    Args:
        None
    Returns:
        None
    '''
    pass

def main():
    hardreset()
    populate()
    return

if __name__ == "main":  main()


 
    
 
