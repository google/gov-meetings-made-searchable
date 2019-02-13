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


def assignUrl(globalId, wcUrl):
	sqlCmd = """update meetingRegistry
		set wordCloud = %s
		where globalId = %s"""
	sqlData = (wcUrl, globalId)
	resultList = utilities.dbExecution(sqlCmd, sqlData)

	return resultList


def cleanInput(inputVal, inputLen):
	inputVal = str(inputVal)
	if len(inputVal) > inputLen:
		inputVal = inputVal[:inputLen]
	inputVal = inputVal.replace("\\", "")
	inputVal = inputVal.replace(";", "")

	return inputVal


def main():
	errorFound = False

	passedArgs = cgi.FieldStorage()

	try:
		globalId = int(passedArgs["gId"].value)
		globalId = cleanInput(globalId, 5)
		wcUrl = passedArgs["wcUrl"].value
		wcUrl = cleanInput(wcUrl, 150)
		resultObj = assignUrl(globalId, wcUrl)
	except:
		globalId = None
		errorFound = True

	print "Content-Type: application/json\n"
	if errorFound is False:
		print [resultObj[0], resultObj[1]]
	else:
		print "Nada"


if __name__ == "__main__":
	main()
