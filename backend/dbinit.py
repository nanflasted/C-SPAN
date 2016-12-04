import sqlite3
import dbmngr

def main():
    '''Initializes empty databases for the project
       Also removes the old database if it exists, i.e., reset.
    '''
    conn = dbmngr.connectDB("./data/","cspdb",True)
    if conn is not None:
       
        ##Entities
        #Create Legislator table
        d = {   "id":       ["int","primary key","not null"],
                "name":     ["text","not null"],
                "desc":     ["text"],
                "role":     ["text","not null"],
                "party":    ["text","not null"],
                "state":    ["text"],
                "ideology": ["real"],
                "image":    ["text"]
            }
        dbmngr.createTable(conn,"legislator",d)

        #create committee table
        d = {
                "id":       ["int","primary key","not null"],
                "name":     ["text","not null"],
                "desc":     ["text"],
                "floor":    ["text"] #whether this is senate or house committee
            }
        dbmngr.createTable(conn,"committee",d)

        #create content table
        d = {
                "id":       ["text","primary key","not null"],
                "time":     ["text","not null"],
                "type":     ["text","not null"],
                "content":  ["text","not null"],
                "memebg":   ["text"],
                "replyto":  ["text"],
                "author":   ["int","not null"],
                "committee":["int"]
            }
        f = {
                "replyto":  "content(id)",
                "author":   "legislator(id)",
                "committee":"committee(id)"
            }
        dbmngr.createTable(conn,"content",d,f)

        ##create relations
        #create participate
        d = {
                "id":       ["text","primary key","not null"],
                "cid":      ["int","not null"],
                "lid":      ["int","not null"],
                "role":     ["text"]
            }
        f = {
                "lid":      "legislator(id)",
                "cid":      "committee(id)"
            }
        dbmngr.createTable(conn,"participate",d,f)

        #create like
        d = {
                "id":       ["int","primary key","not null"],
                "lid":      ["int","not null"],
                "cid":      ["int","not null"]
            }
        f = {
                "lid":      "legislator(id)",
                "cid":      "content(id)",
            }
        dbmngr.createTable(conn,"like",d,f)

        #create vote
        d = {
                "id":       ["int","primary key","not null"],
                "lid":      ["int","not null"],
                "cid":      ["int","not null"]
            }
        f = {
                "lid":      "legislator(id)",
                "cid":      "content(id)",
            }
        dbmngr.createTable(conn,"vote",d,f)
    return

if __name__ == "__main__":  main()
    

