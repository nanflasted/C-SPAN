from backend import *
import random, time

# Get all senator IDs
dbc = dbmngr.connectDB("./data/","cspdb",False)
idcur = dbmngr.queryEntry(dbc,["id"],["legislators"])
idlist = idcur.fetchall()
last_post = None
while(True):
    try:
        lid = random.choice(idlist)[0]
        print("Chose: " + str(lid))

        content_random = random.randint(1, 100)        
        if content_random < 50 or last_post == None:
            last_post = newTweet(1, lid, True, True)[0]
        elif content_random < 85:
            newReply(1, lid, last_post,True)
        else:
            newMeme(1, lid, "harambe", True, True)
    except Exception as e:
        print("Error:", e)
    time.sleep(1)
