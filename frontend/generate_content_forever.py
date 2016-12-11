from backend import *
import random, time

# Get all senator IDs
dbc = dbmngr.connectDB("./data/","cspdb",False)
idcur = dbmngr.queryEntry(dbc,["id"],["legislators"])
idlist = idcur.fetchall()
commcur = dbmngr.queryEntry(dbc,["id"],["committees"])
commlist = idcur.fetchall()
dbc.close()




last_post = None
memes = ["harambe","dos_equis","capitol","trump","obama"]
while(True):
    try:
        lid = random.choice(idlist)[0]
        lid = 300071
        print("Chose: " + str(lid))

        content_random = random.randint(1, 100)        

        if content_random < 40 or last_post == None:
            print("generating post")
            last_post = newTweet(1, lid, True, True)[0]
        elif content_random < 75:
            print("generating reply")
            newReply(1, lid, last_post,True)
        elif content_random < 90:
            print("generating meme")
            last_post = newMeme(1, lid, random.choice(memes), True, True)[0]
        else:
            print("generating bill")
            last_post = newBill(1, lid, random.choice(commlist), True, True)
    
    except Exception as e:
        print("Error:", e)
    #time.sleep(10)
