import sqlite3
import csplog
import sys
import os
import re

def sanitize(name):
    """Sanitizes input for safer sql
    Args:
        name:   the string to be sanitized
    Returns:
        safename:   sanitized, sql-safe name
    """
    return re.sub(r"\\\',",r"",name)

def connectDB(directory,name,new=True):
    """Connect to a given database, creates one if it doesn't exist
    Args:
        directory:  The directory of the database
        name:   The name (or intended name) of the database
        new:    Whether the method should create a new database
    Returns:
        conn:   The connection to the Database, None if database doesn't exist and the
                instruction is to not create one; or if there was an exception
    """
    try:
        namestr = directory+name+".db"
        if os.path.isfile(namestr) or new:
            conn = sqlite3.connect(directory+name+".db")
        else:
            return None
    except Exception:
        csplog.logexc(sys.exc_info()[0])
        return None
    return conn


def createTable(conn, name, col, foreign):
    '''Create a table with the given connection
    Example:
        createTable(conn, "example", {"col1":["INT"], "col2": ["int","primary","not null"]})
    Args:
        conn:   The Connection to the database
        name:   The name of the table
        col:    A dictionary to the columns, with the keys as names, and values as type and
                Keywords such as "PRIMARY," "NOT NULL" etc. Values must be iterable
        foreign:A dictionary to indicate which columns are foreign. Keys are the local columns,
                and Values are foreign columns
    Returns:
        bool: Whether the operation was successful
    '''
    try:
        c = conn.cursor()
        #name = sanitize(name)
        execstr = "create table "+name+ "("
        for (k,v) in col:
            execstr += k + " "
            execstr += " ".join(v)
            execstr += ","
        for (k,v) in foreign:
            execstr += "foreign key("+k+") references "+v+","
        execstr = execstr[:-1] + ");"
        c.execute(execstr)
        conn.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info()[0])
        return False
    return False

def insertEntry(conn, table, entry):
    '''Insert an entry into the database referred to by the connection
    Example:
        insertEntry(conn,"sampleTable",{"col1":2,"col2":0})
    Args:
        conn:   The connection to the database
        table:   The name of the table
        entry:  A dictionary of the columns that the entry has, and the respective values
    Returns:
        bool: whether the operation was successful
    '''
    try:
        c = conn.cursor()
        execstr = "insert into "+table
        col = "(";val = "("
        col += ",".join(entry.keys); val += ",".join(entry.values);
        col += ")"; val += ")";
        execstr += " " + col + " " + val + ");"
        c.execute(execstr)
        c.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info()[0])
        return False
    return False

def insertMany(conn,table,cols,entrylist):
    '''For inserting many rows at the same time
    Args:
        conn:   The connection to the database
        table:  The table to be inserted into
        cols:   List of columns related to the entry
        entrylist:  List of tuples of entry values to be inserted.
    Returns:
        bool:   Whether the operation was successful
    '''
    if len(cols)!=len(entrylist):   return False
    try:
        c = conn.cursor()
        colstr = "(" + ",".join(cols) + ")"
        qmstr = "(" +",".join(["?" for _ in xrange(len(entrylist))]) +")"
        execstr = "insert into "+table+" "+colstr+" values "+qmstr+";"
        c.executemany(execstr,entrylist)
        c.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info()[0])
        return False
    return False

def queryEntry(conn,tar,tab,cond,agg,aggcond):
    '''Query the database for the entries with the given conditions,
    Args:
        conn:   The connection to the database
        tar:    Target list
        tab:    "From" conditions
        cond:   "Where" conditions
        agg:    aggregation conditions
        aggcond:"having" conditions
    Returns:
        result: Cursor pointing to the query results
    '''
    try:
        c = conn.cursor()
        execstr =  "select " + ",".join(tar) + " "
        execstr += "from " + "(" + ",".join(tab) +") "
        execstr += "where " + "(" + cond + ") "
        if agg is not None:
            execstr += "group by " + "(" + ",".join(agg) + ") "
        if aggcond is not None:
            execstr += "having " + "(" + aggcond + ")"
        c.execute(execstr)
        return c 
    except Exception:
        csplog.logexc(sys.exc_info()[0])
        return None
    return None

def removeEntry(conn, table, cond):
    '''Remove all entries within the given table with the given conditions
    Args:
        conn:   The connection to the database
        table:  "From" clause conditions
        cond:   "Where"clause conditions
    Returns:
        bool:   Whether the operation was successfu;
    '''
    try:
        c = conn.cursor()
        execstr = "delete from "+table
        if cond is not None:
            execstr += " where " cond
        c.execute(execstr)
        c.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info()[0])
        return False
    return False

