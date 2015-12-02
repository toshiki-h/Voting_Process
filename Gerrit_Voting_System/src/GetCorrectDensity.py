#!/usr/bin/python3
##################
# Author:Toshiki Hirao
# CreatedOn: 2015/09/18
# Summary: This program is to count current judge and incurrent judge.
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

### Init
reviewer_class = defaultdict(lambda: 0)
if len(sys.argv) != 2 or (sys.argv[1] != "-y" and sys.argv[1] != "-n"):
	print "Error:You should put option only '-y' or '-n'"
	exit()

### Connect DB
cnct = MySQLdb.connect(db="openstack",user="root", passwd="hirao")
csr = cnct.cursor()

### Main
pre = 1
agr_disCt = 0
votes_ct = 0
with_1_2 = 0
for Id in range(1, 92985): #70814 <- Number Of Qt project's patchsets #92985 <- Number Of Openstack's patchsets
	csr.execute("select ReviewId, Status from Review where ReviewId = '"+str(Id)+"';")
	info = csr.fetchall()
	csr.execute("select ReviewId, AuthorId, Message from Comment where ReviewId = '"+str(Id)+"' order by WrittenOn asc;")
	comments = csr.fetchall()
	reviewers_written = []	# Reviewer which has already written a comment in the patch
	reviewers_List = [] 	# Reviewer which wrote comments in the patch Set (patch not equal patch Set)
	reviewers_score = []
	#### Hirao
	votes_ct = 0
	noScoreCt = 0
	#### Toshiki
	###---###
	minus = 0
	plus = 0
	###---###
	### Extract status
	assert len(info) == 0 or len(info) == 1
	for information in info:
		status = information[1]

	### Analysis
	if status == "merged" or status == "abandoned": # We target the patches which were decided merged or abandoned
		for comment in comments:
			m = comment[2].replace("\n", "<br>")

			# Judge whether or not this patch was desided by decision comment<"merged, abandoned"> which mean [status] of reviewdata.
			# And, We regard that "updated ---" comment is also decision comment.
			# And, We regard that +2 score comment is the same as "merged", -2 score comment is the same as "abandoned".
			# Summary -> "merged, abandoned, 'updated --- ', +2, -2" is {JudgeDicisionMaking commnet}
			judge = ReviewerFunctions.JudgeDicisionMaking(m)
			if judge == 0:
				s = ReviewerFunctions.JudgeVoteScore(m)
				if(s == 1 or s == -1):
					###---###
					if s == 1:
						plus = 1
					else:
						minus = 1
					votes_ct = votes_ct + 1
					###---###
					#### Hirao
					noScoreCt = noScoreCt + 1
					#### Toshiki
					reviewer = comment[1]
					#print str(reviewer)+":"+str(m)
					if reviewer in reviewers_written:	# A new Reviewer for this patch
						pass
					else:					# A Reviewer who has already written for this patch
						reviewers_List.append(reviewer)
						reviewers_score.append(s)
						reviewers_written.append(reviewer)

			else:
				assert len(reviewers_List) == len(reviewers_score)
				for (r, s) in zip(reviewers_List, reviewers_score):
					if ReviewerFunctions.IsReviewerClass(r, reviewer_class):
						if ReviewerFunctions.IsCorrectVoting(r, s, judge):
							reviewer_class[r].addCur()
						else:
							#print type(reviewer_class[r])
							reviewer_class[r].addIncur()
					else:
						ReviewerFunctions.MakeReviewerClass(r, reviewer_class)
						#print str(Id)+"nothing"
						if ReviewerFunctions.IsCorrectVoting(r, s, judge):
							reviewer_class[r].addCur()
						else:
							reviewer_class[r].addIncur()
				# Init reviewers_List, reviewers_score
				# If you want to use all comment per a reviewer, you should remove this two sentences.
				if sys.argv[1] == "-y":
					reviewers_List = []
					reviewers_score = []
				elif sys.argv[1] == "-n":
					pass
		###
		for (r, s) in zip(reviewers_List, reviewers_score):
			if status == "merged":
				judge = 2
			elif status == "abandoned":
				judge = -2
			if ReviewerFunctions.IsReviewerClass(r, reviewer_class):
				if ReviewerFunctions.IsCorrectVoting(r, s, judge):
					reviewer_class[r].addCur()
				else:
					reviewer_class[r].addIncur()
			else:
				ReviewerFunctions.MakeReviewerClass(r, reviewer_class)
				if ReviewerFunctions.IsCorrectVoting(r, s, judge):
					reviewer_class[r].addCur()
				else:
					reviewer_class[r].addIncur()
	###---###
	if(plus == 1 and minus == 1):
		#print Id
		agr_disCt = agr_disCt + 1
	if votes_ct < 4:
		with_1_2 = with_1_2 + 1
	###---###
		# Init reviewers_List, reviewers_score
		#reviewers_List = []
		#reviewers_score = []
		#### Hirao
		#if noScoreCt == 0:
		#	print Id
		#### Toshiki
### Culcurate Former and Latter
#print float(agr_disCt)/70814
print "with_1_2:"+str(with_1_2)+"---"+"all_ct:"+"92985"
print float(with_1_2) / 92985
"""
### Output
print "ReviewId,PerOfCur,PerOfIncur"
n = 10
#print ("id,NumOfCur,NumOfIncur,PerOfCur,PerOfIncur,NumOfVotes")
for i in reviewer_class:
	sum = reviewer_class[i].cur + reviewer_class[i].incur
	#if(sum < 120):
	#print("%d,%d,%d,%f,%f,%d" % (i, reviewer_class[i].cur, reviewer_class[i].incur,reviewer_class[i].cur/float(reviewer_class[i].cur+reviewer_class[i].incur), reviewer_class[i].incur/float(reviewer_class[i].cur+reviewer_class[i].incur), reviewer_class[i].cur+reviewer_class[i].incur))
	if sum >= 20:
		reviewer_class[i].SetPerFormer(n)
		reviewer_class[i].SetPerLatter(n)
		print("%d,%f,%f" % (i,reviewer_class[i].per_former, reviewer_class[i].per_latter))
"""
