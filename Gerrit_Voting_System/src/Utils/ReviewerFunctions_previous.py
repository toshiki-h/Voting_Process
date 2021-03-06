#!/usr/bin/python3
##################
# Author:Toshiki Hirao
# CreatedOn: 2015/09/18
# Summary: This program is to define Functions for reviewer information.
##################
import re
import sys
import csv
import time
import MySQLdb
from collections import defaultdict
from datetime import datetime
from Class import ReviewerClass

### Define Functions
# JudgeVoteScore(m)
# @m:message
######
# If Score is '+1' -> return 1
# If Score is '-1' -> return -1
# If Score isn't '+1' or '-1' -> return 0
######
def JudgeVoteScore(m): # (Regular expression)
    # Score +1
	p1 = re.compile(r'Patch Set [1-9]*: Looks good to me, but someone else must approve') #
	p2 = re.compile(r'Patch Set [1-9]*: Works for me')
	p3 = re.compile(r'Patch Set [1-9]*: Verified')
	p4 = re.compile(r'Patch Set [1-9]*: Sanity review passed') #
	if p1.match(m) or p2.match(m) or p3.match(m) or p4.match(m):
		return 1

    # Score -1
	p1 = re.compile(r"Patch Set [1-9]*: I would prefer that you didn'*t submit this") #
	p2 = re.compile(r'Patch Set [1-9]*: Sanity problems found') #
	if p1.match(m) or p2.match(m):
		return -1

    # Score 0
	"""
	p1 = re.compile(r'Patch Set [1-9]*: No score')
	if p1.match(m):
		return 0
	"""
	# No Score
	return 0

# Judge whether the comment is Dicision or not
# @m:message
def JudgeDicisionMaking(m):
	# Score +2
	p1 = re.compile(r'Patch Set [1-9]*: Looks good to me, approved') #
	p2 = re.compile(r'Patch Set [1-9]*: Looks good to me<br>')

	if p1.match(m) or p2.match(m):
		return 2

	# Score -2
	p1 = re.compile(r"Patch Set [1-9]*: I would prefer that you didn'*t merge this") #
	p2 = re.compile(r'Patch Set [1-9]*: Do not submit') #
	p3 = re.compile(r'Patch Set [1-9]*: Major sanity problems found') #
	p4 = re.compile(r'Uploaded patch set [1-9]*') #
	if p1.match(m) or p2.match(m) or p3.match(m) or p4.match(m):
		return -2

	# Not JudgeDicisionMaking
	return 0

def IsReviewerClass(r, reviewer_class):
	assert r > 0
	if reviewer_class[r] != 0:
		return True
	else:
		return False

def MakeReviewerClass(r, reviewer_class):
	assert r > 0 and reviewer_class[r] == 0
	reviewer_class[r] = ReviewerClass.Reviewer(r)
	#print "MakeClass"+str(r)
	return r

def IsCorrectVoting(r, s, judge):
	if (s > 0 and judge > 0) or (s < 0 and judge < 0):
		assert (s == 1 and judge == 2) or (s == -1 and judge == -2)
		return True
	else:
		assert (s == -1 and judge == 2) or (s == 1 and judge == -2)
		return False
def IsAutoTest(author):
	# 1000049 -> Qt Sanity Bot
	# -1 	  -> Gerrit System
	# 1000060 -> Qt Continuous Integration System
	# 1000191 -> Qt Submodule Update Bot
	# 1002169 -> Qt Doc Bot
	if(author == 1000049 or author == -1 or author == 1000060 or author == 1000191 or author == 1002169):
		return 1	## The author is Auto Test.
	else:
		return 0
