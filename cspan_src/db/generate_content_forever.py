from backend import *
import random, time

# Get all senator IDs
dbc = dbmngr.connectDB("./data/","cspdb",False)
idcur = dbmngr.queryEntry(dbc,["id"],["legislators"])
idlist = idcur.fetchall()

commcur = dbmngr.queryEntry(dbc,["id"],["committees"])
commlist = commcur.fetchall()
dbc.close()


last_post = None
memes = [["harambe","Harambe"],["dos_equis","I don't always"],["capitol", "Congress"],["trump","Trump"],["obama","Obama"]]

while(True):
    try:
        lid = random.choice(idlist)[0]
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
            meme_tuple = random.choice(memes)
            last_post = newMeme(1, lid,meme_tuple[0], True, True, meme_tuple[1])[0]
        else:
            print("generating bill")
            last_post = newBill(1, lid, random.choice(commlist)[0], True)
    
    except Exception as e:
        print("Error:", e)

