#!/usr/bin/python3
##################
# Author:Toshiki Hirao
# CreatedOn: 2015/12/01
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

### Validation
assert len(sys.argv) == 2

### Connect DB
cnct = MySQLdb.connect(db="qt",user="root", passwd="hirao") #openstack or qt
csr = cnct.cursor()

### Main
for project in open(sys.argv[1], "r"):
	### Init
	reviewer_class = defaultdict(lambda: 0)

	project = project.replace("\n", "")
	for Id in range(1, 70814): #70814 <- Number Of Qt project's patchsets #92985 <- Number Of Openstack's patchsets
		csr.execute("select ReviewId, Status from Review where ReviewId = '"+str(Id)+"' and project = '"+str(project)+"';")
		info = csr.fetchall()
		csr.execute("select ReviewId, AuthorId, Message from Comment where ReviewId = '"+str(Id)+"' order by WrittenOn asc;")
		comments = csr.fetchall()
		reviewers_written = []	# Reviewer which has already written a comment in the patch
		reviewers_List = [] 	# Reviewer which wrote comments in the patch Set (patch not equal patch Set)
		reviewers_score = []

		### Extract status
		assert len(info) == 0 or len(info) == 1
		status = ""
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
	### Culcurate Former and Latter
	#print float(agr_disCt)/70814
	#print "with_1_2:"+str(with_1_2)+"---"+"all_ct:"+"92985"
	#print float(with_1_2) / 92985
	### Output
	#print "ReviewId,PerOfCur,PerOfIncur"
	#n = 10
	#print ("Id,ProjectName,NumOfCur,NumOfIncur,NumOfAll,PerOfCur,PerOfIncur")
	for i in reviewer_class:
		sum = reviewer_class[i].cur + reviewer_class[i].incur
		print("%d,%s,%d,%d,%d,%f,%f" % (i, project, reviewer_class[i].cur, reviewer_class[i].incur, sum, reviewer_class[i].cur/float(sum), reviewer_class[i].incur/float(sum)))
		#if(sum < 120):
		#print("%d,%d,%d,%f,%f,%d" % (i, reviewer_class[i].cur, reviewer_class[i].incur,reviewer_class[i].cur/float(reviewer_class[i].cur+reviewer_class[i].incur), reviewer_class[i].incur/float(reviewer_class[i].cur+reviewer_class[i].incur), reviewer_class[i].cur+reviewer_class[i].incur))
		#if sum >= 20:
		#	reviewer_class[i].SetPerFormer(n)
		#	reviewer_class[i].SetPerLatter(n)
		#	print("%d,%f,%f" % (i,reviewer_class[i].per_former, reviewer_class[i].per_latter))
