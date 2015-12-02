#!/usr/bin/python3
##################
# Author:Toshiki Hirao
# CreatedOn: 2015/09/18
# Summary: This program is to count the number of frequency in each project in Qt.
##################

#comment is not correct

### Import lib
import re
import sys
import csv
import time
import MySQLdb
from collections import defaultdict
from datetime import datetime
from Utils import ReviewerFunctions
from Class import ReviewerClass

### Connect DB
cnct = MySQLdb.connect(db="qt",user="root", passwd="hirao")
csr = cnct.cursor()

### Parse
for Id in range(1, 70814):
    csr.execute("select Project from Review where ReviewId = '"+str(Id)+"';")
    infos = csr.fetchall()
    for info in infos:
        project = info[0]
        print project
