import sqlite3
import dbmngr

def main():
    '''Initializes empty log database for the project
       Also removes the old database if it exists, i.e., reset.
    '''
    conn = dbmngr.connectDB("./data/","dblog",True)
    if conn is not None:
        #create vote
        d = {
                "id":       ["text","primary key","not null"],
                "event":    ["text","not null"],
                "datetime": ["text","not null"],
                "name":     ["text"],
                "stack":    ["text"],
                "content":  ["text"]
            }
        dbmngr.createTable(conn,"log",d,f)

        conn.close()
    return

if __name__ == "__main__":  main()
    

