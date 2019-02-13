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
import logging
import utilities
import ujson as json
from datetime import datetime


def lookupMeeting(urlIdentifier):
	globalId = str(urlIdentifier)
	sqlCmd = """select
		meetingDesc,
		meetingDate,
		youtubeId,
		wordCloud,
		publishedVideo,
		publishedTranscript,
		orgIdentifier,
		publishedAgenda,
		urlIdentifier,
		hasSegments from meetingRegistry
		where urlIdentifier = %s
		and youtubeId is not NULL
		limit 1"""
	sqlData = (urlIdentifier)
	resultList = utilities.dbExecution(sqlCmd, sqlData)

	return resultList[2][0]


def formatDate(meetingDate):
	datetimeObj = datetime.strptime(meetingDate, "%Y%m%d")
	formattedDate = datetimeObj.strftime("%B %d, %Y")
	weekDay = datetimeObj.strftime("%A")

	return formattedDate, weekDay


def main():
	errorFound = False

	passedArgs = cgi.FieldStorage()

	try:
		urlIdentifier = passedArgs["urlIdentifier"].value
		resultObj = lookupMeeting(urlIdentifier)
	except:
		meetingId = None
		errorFound = True

	try:
		hasSegments = resultObj[9]
		if hasSegments is None:
			hasSegments = 0

		formattedDate, weekDay = formatDate(resultObj[1])
		outputObj = {}
		outputObj["desc"] = resultObj[0]
		outputObj["dow"] = weekDay
		outputObj["date"] = formattedDate
		outputObj["youtubeId"] = resultObj[2]
		outputObj["urlIdentifier"] = urlIdentifier
		outputObj["wordCloud"] = resultObj[3]
		outputObj["videoUrl"] = resultObj[4]
		outputObj["transcriptUrl"] = resultObj[5]
		outputObj["agendaUrl"] = resultObj[7]
		outputObj["hasSegments"] = hasSegments
		orgIdentifier = resultObj[6]
		logging.info("loadMeeting")
	except:
		errorFound = True

	if errorFound is True:
		outputObj = {}
		outputObj["error"] = "Error"

	print "Content-Type: application/json\n"
	print json.dumps(outputObj)


if __name__ == "__main__":
	main()