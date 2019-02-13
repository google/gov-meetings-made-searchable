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


def lookupFiles(urlIdentifier):
	sqlCmd = """select
		globalId from meetingRegistry
		where urlIdentifier = %s"""
	sqlData = (urlIdentifier)
	resultList = utilities.dbExecution(sqlCmd, sqlData)

	globalId = resultList[2][0][0]
	globalId = str(globalId)

	sqlCmd = """select
		fileId,
		fileName,
		mimeType,
		webViewLink,
		thumbnailLink,
		pageIndex from relatedFiles
		where globalId = %s
		order by fileName ASC"""
	sqlData = (globalId)
	resultList = utilities.dbExecution(sqlCmd, sqlData)

	return resultList[2]


def main():
	errorFound = False

	passedArgs = cgi.FieldStorage()

	try:
		urlIdentifier = passedArgs["urlIdentifier"].value
		resultObj = lookupFiles(urlIdentifier)
	except:
		meetingId = None
		errorFound = True
		resultObj = None

	try:
		outputObj = {}
		for eachResult in resultObj:
			pageIndex = eachResult[5].zfill(2)
			fileObj = {}
			fileObj["fileId"] = eachResult[0]
			fileObj["fileName"] = eachResult[1]
			fileObj["fileType"] = eachResult[2]
			fileObj["webViewLink"] = eachResult[3]
			fileObj["thumbnailLink"] = eachResult[4]
			outputObj[pageIndex] = fileObj
	except:
		errorFound = True

	if errorFound is True:
		outputObj = {}
		outputObj["error"] = "Error"

	print "Content-Type: application/json\n"
	print json.dumps(outputObj)


if __name__ == "__main__":
	main()