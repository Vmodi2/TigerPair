#-----------------------------------------------------------------------
# pair.py
# Author: Vikash
#-----------------------------------------------------------------------
# THIS IS A SIMPLE TEST FOR DATABASE.PY DO NOT USE
import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "TigerPair_dev",
                           passwd = "cos333",
                           db = "profiledb")
    c = conn.cursor()

    return c, conn