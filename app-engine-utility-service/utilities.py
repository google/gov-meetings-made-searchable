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
import urllib
import base64
import MySQLdb
from google.appengine.api import urlfetch

from google.appengine.ext import vendor
vendor.add("lib")
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

MySQLdb.escape_string("'")


def issueReq(reqUrl):
	responseStr = urlfetch.fetch(reqUrl)

	return responseStr.content


def cleanInput(inputVal, inputLen):
	inputVal = str(inputVal)
	if len(inputVal) > inputLen:
		inputVal = inputVal[:inputLen]
	inputVal = inputVal.replace("/", "")
	inputVal = inputVal.replace("\\", "")
	inputVal = inputVal.replace(";", "")

	return inputVal


def pubsubObj():
	credentials = GoogleCredentials.get_application_default()
	serviceObj = build("pubsub", "v1", credentials = credentials)

	return serviceObj


def publishMsg(projectName, gId, topicName, msgAction):
	serviceObj = pubsubObj()
	credentialsObj = GoogleCredentials.get_application_default()

	serviceObj = build("pubsub", "v1", credentials = credentialsObj)
	topicStr = "projects/%s/topics/%s" % (projectName, topicName)

	msgStr = base64.b64encode(msgAction)
	bodyObj = {"messages":
		[{
			"attributes": {
				"globalId": str(gId)
			},
			"data": msgStr
		}]
	}
	respObj = serviceObj.projects().topics().publish(
		topic = topicStr,
		body = bodyObj
	).execute()

	return respObj


def pullMsg(projectName, subName, returnImmediately):
	serviceObj = pubsubObj()
	subStr = "projects/%s/subscriptions/%s" % (projectName, subName)

	bodyObj = {
		"returnImmediately": returnImmediately,
		"maxMessages": 1
	}

	resp = serviceObj.projects().subscriptions().pull(
		subscription = subStr,
		body = bodyObj
	).execute()

	return resp


def ackMsg(projectName, subName, ackId):
	serviceObj = pubsubObj()
	subStr = "projects/%s/subscriptions/%s" % (projectName, subName)
	ackBody = {"ackIds": [ackId]}
	serviceObj.projects().subscriptions().acknowledge(
		subscription = subStr,
		body = ackBody
	).execute()	


def dbExecution(sqlCmd, sqlData):

	sqlInstance = "__Cloud_SQL_Instance_Connection_Name__"

	if os.getenv("SERVER_SOFTWARE", "").startswith("Google App Engine/"):
		connection = MySQLdb.connect(	unix_socket = "/cloudsql/" + sqlInstance,
										user = "__Cloud_SQL_Username__",
										passwd = "__Cloud_SQL_User_Password__",
										db = "prodDb")
	else:
		connection = MySQLdb.connect(	host = "__Cloud_SQL_Public_IP_Address__",
										user = "__Cloud_SQL_Username__",
										passwd = "__Cloud_SQL_User_Password__",
										db = "prodDb")
	cursor = connection.cursor()
	if len(sqlData) > 0:
		try:
			cmdExecution = cursor.execute(sqlCmd, *[sqlData])
		except:
			cmdExecution = cursor.execute(sqlCmd, [sqlData])
	else:
		cmdExecution = cursor.execute(sqlCmd)
	connection.commit()
	numResults = cursor.rowcount
	resultRows = cursor.fetchall()
	cursor.close()
	connection.close()
	resultList = [cmdExecution, numResults, resultRows]

	return resultList


if __name__ == "__main__":
	main()