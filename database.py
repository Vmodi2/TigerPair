#!/usr/bin/env python

#---------------------------------------------------------------------
# database.py
#---------------------------------------------------------------------

from mysql import connector
from sys import argv, stderr, exit
from os import path

class Database:
    def __init__(self):
        self._connector = None

    def connect(self):
        DATABASE_NAME = '?' ## FILL THIS OUT LATER
        # if connection to database fails
        if not path.isfile(DATABASE_NAME):
            raise Exception('Database connection failed')
        self._connector = connector.connect(DATABASE_NAME)

    def disconnect(self):
        self._connector.close()

    def insert(argv):
        firstname = argv[0]
        lastname = argv[1]
        email = argv[2]
        major = argv[3]
        career = argv[4]

        # deal with escape characters maybe?

        try:
            connection = connect(DATABASE_NAME)
            c = connection.cursor()
        except Exception as e:
            print(str(e), file=stderr)
            exit(1)

        ## add names:

        query = "INSERT INTO student_table \
                 VALUES ? ? ? ? "

        cursor.execute(query, (firstname, lastname, email, major, career))
        cursor.close()
