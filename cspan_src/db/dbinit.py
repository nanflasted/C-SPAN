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
        dbmngr.createTable(conn,"legislators",d)

        #create committees table
        d = {
                "id":       ["int","primary key","not null"],
                "name":     ["text","not null"],
                "desc":     ["text"],
                "floor":    ["text"] #whether this is senate or house committees
            }
        dbmngr.createTable(conn,"committees",d)

        #create content table
        d = {
                "id":       ["text","primary key","not null"],
                "time":     ["text","not null"],
                "type":     ["text","not null"],
                "contents":  ["text","not null"],
                "memebg":   ["text"],
                "replyto":  ["text"],
                "author":   ["int","not null"],
                "committees":["int"]
            }
        f = {
                "replyto":  "contents(id)",
                "author":   "legislators(id)",
                "committees":"committees(id)"
            }
        dbmngr.createTable(conn,"contents",d,f)

        ##create relations
        #create participate
        d = {
                "id":       ["text","primary key","not null"],
                "cid":      ["int","not null"],
                "lid":      ["int","not null"],
                "role":     ["text"]
            }
        f = {
                "lid":      "legislators(id)",
                "cid":      "committees(id)"
            }
        dbmngr.createTable(conn,"participates",d,f)

        #create like
        d = {
                "id":       ["text","primary key","not null"],
                "lid":      ["int","not null"],
                "cid":      ["text","not null"]
            }
        f = {
                "lid":      "legislators(id)",
                "cid":      "contents(id)",
            }
        dbmngr.createTable(conn,"likes",d,f)

        #create vote
        d = {
                "id":       ["text","primary key","not null"],
                "lid":      ["int","not null"],
                "cid":      ["text","not null"],
                "votes":     ["text","not null"]
            }
        f = {
                "lid":      "legislators(id)",
                "cid":      "contents(id)",
            }
        dbmngr.createTable(conn,"votes",d,f)
        conn.close()
    return

if __name__ == "__main__":  main()
    

