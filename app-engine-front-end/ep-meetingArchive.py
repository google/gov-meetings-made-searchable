#!/usr/bin/env python

# This is not an officially supported Google product, though support
# will be provided on a best-effort basis.

# Copyright 2018 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.

# You may obtain a copy of the License at:

#    https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import cgi
import utilities
import ujson as json
from datetime import datetime


def getMeetings(qryLimit, qryOffset, orgIdentifier):
	sqlCmd = """select
		meetingDesc,
		meetingDate,
		urlIdentifier,
		globalId from meetingRegistry
		where orgIdentifier = %s
		and youtubeId is not NULL
		order by meetingDate DESC
		limit %s
		offset %s"""
	sqlData = (orgIdentifier, int(qryLimit), int(qryOffset))
	resultList = utilities.dbExecution(sqlCmd, sqlData)

	lastDate = None
	dateCnt = 0

	meetingDict = {}
	for eachEntry in resultList[2]:
		meetingDate = eachEntry[1]

		dateIncr = meetingDate
		if lastDate == meetingDate:
			dateCnt = dateCnt + 1
		else:
			dateCnt = 0
		dateIncr = str(meetingDate) + str(dateCnt).zfill(3)

		formattedDate, weekDay = formatDate(meetingDate)

		meetingObj = {}
		meetingObj["desc"] = eachEntry[0]
		meetingObj["date"] = formattedDate
		meetingObj["dow"] = weekDay
		meetingObj["meetingId"] = eachEntry[3]
		meetingObj["urlIdentifier"] = eachEntry[2]
		
		meetingDict[dateIncr] = meetingObj
		lastDate = meetingDate

	return meetingDict


def formatDate(meetingDate):
	datetimeObj = datetime.strptime(meetingDate, "%Y%m%d")
	formattedDate = datetimeObj.strftime("%B %d, %Y")
	weekDay = datetimeObj.strftime("%A")

	return formattedDate, weekDay


def main():
	passedArgs = cgi.FieldStorage()

	try:
		lastMeeting = int(passedArgs["lastMeeting"].value)
		orgIdentifier = passedArgs["orgId"].value
	except:
		lastMeeting = 0
		orgIdentifier = None

	if lastMeeting == 0:
		meetingTotal = 3
	else:
		meetingTotal = 6

	jsonObj = getMeetings(meetingTotal, lastMeeting, orgIdentifier)

	keyList = jsonObj.keys()
	keyList.sort(reverse=True)
	targetMeeting = lastMeeting + meetingTotal

	outputObj = {}
	outputObj["meetingList"] = jsonObj

	print "Content-Type: application/json\n"
	print json.dumps(outputObj)


if __name__ == "__main__":
	main()
