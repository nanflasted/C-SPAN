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
    safename = re.sub(r'\"',r"",name)
    safename = re.sub(r"\'",r"",safename)
    safename = re.sub(r"\\",r"",safename)
    safename = re.sub(r",",r"",safename)
    return safename

def connectDB(directory,name,new=False):
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
        if os.path.isfile(namestr) and new:
            os.remove(namestr)
            conn = sqlite3.connect(namestr)
        elif os.path.isfile(namestr) or new:
            conn = sqlite3.connect(namestr)
        else:
            return None
    except Exception:
        csplog.logexc(sys.exc_info())
        return None
    return conn


def createTable(conn, name, col, foreign = None):
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
    execstr = ""
    try:
        c = conn.cursor()
        #name = sanitize(name)
        execstr = "create table "+name+ "("
        for k,v in col.iteritems():
            execstr += k + " "
            execstr += " ".join(v)
            execstr += ","
        if foreign is not None:
            for (k,v) in foreign.iteritems():
                execstr += "foreign key("+k+") references "+v+","
        execstr = execstr[:-1] + ")"
        c.execute(execstr)
        conn.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        print execstr
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
    execstr = ""
    try:
        c = conn.cursor()
        execstr = "insert into "+table
        col = "(";val = "("
        col += ",".join(entry.keys()); 
        v = entry.values()
        v = ["'"+w+"'" for w in v]
        val += ",".join(v);
        col += ")"; val += ")";
        execstr += " " + col + " values " + val + ";"
        c.execute(execstr)
        conn.commit()
        return True
    except Exception:
        print execstr
        csplog.logexc(sys.exc_info())
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
    execstr = ""
    try:
        if len(cols)!=len(entrylist[0]):   return False
        c = conn.cursor()
        colstr = "(" + ",".join(cols) + ")"
        qmstr = "(" +",".join(["?" for _ in xrange(len(entrylist[0]))]) +")"
        execstr = "insert into "+table+" "+colstr+" values "+qmstr+";"
        c.executemany(execstr,entrylist)
        conn.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        print execstr
        return False
    return False

def queryEntry(conn,tar,tab,cond=None,agg=None,aggcond=None):
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
    execstr = ""
    try:
        c = conn.cursor()
        execstr =  "select " + ",".join(tar) + " "
        execstr += "from " + "(" + ",".join(tab) +") "
        if cond is not None:
            execstr += "where " + "(" + cond + ") "
        if agg is not None:
            execstr += "group by " + "(" + ",".join(agg) + ") "
        if aggcond is not None:
            execstr += "having " + "(" + aggcond + ")"
        c.execute(execstr)
        return c 
    except Exception:
        csplog.logexc(sys.exc_info())
        print execstr
        return None
    return None

def updateMany(conn, table, cols, vals):
    '''Update certain columns on certain entries in the given table, with the given values.
    Example:
    Args:
        conn:   connection to the database
        table:  the table to be targeted for updates
        cols:   the columns to be updated
        vals:   the values to be inserted as the update, format: (value1,value2,...,valuen,id)
    Returns:
        bool:   whether the operation was successful
    '''
    execstr = ""
    try:
        if len(cols)!=len(vals[0])-1: return False
        c = conn.cursor()
        execstr = "update " + table + " set "
        for col in cols:
            execstr += col + "= ?,"
        execstr = execstr[:-1]+" where id = ?;"
        c.executemany(execstr,vals)
        conn.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        print execstr
        return False
    return False

def removeEntry(conn, table, cond):
    '''Remove all entries within the given table with the given conditions
    Args:
        conn:   The connection to the database
        table:  "From" clause conditions
        cond:   "Where"clause conditions
    Returns:
        bool:   Whether the operation was successfu;
    '''
    execstr = ""
    try:
        c = conn.cursor()
        execstr = "delete from "+table
        if cond is not None:
            execstr += " where " +cond
        c.execute(execstr)
        conn.commit()
        return True
    except Exception:
        csplog.logexc(sys.exc_info())
        print execstr
        return False
    return False

