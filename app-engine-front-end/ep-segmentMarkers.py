#!/usr/bin/env python

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
		segmentJson from videoSegments
		where urlIdentifier = %s"""
	sqlData = (urlIdentifier)
	resultList = utilities.dbExecution(sqlCmd, sqlData)

	segmentJson = resultList[2][0][0]

	return segmentJson


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
		outputObj = json.loads(resultObj)
	except:
		errorFound = True

	if errorFound is True:
		outputObj = {}
		outputObj["error"] = "Error"

	print "Content-Type: application/json\n"
	print json.dumps(outputObj)


if __name__ == "__main__":
	main()