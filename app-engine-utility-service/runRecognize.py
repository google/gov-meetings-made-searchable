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


import sys
import ujson
import urllib
import traceback
import utilities
from googleapiclient.discovery import build
from google.appengine.ext import vendor
vendor.add("lib")

import httplib2
from oauth2client.service_account import ServiceAccountCredentials


def runCycle(gcsLoc, jobId, globalId):
	credentialsJson = "__Credential_JSON_File_Name__"

	scopesList = ["https://www.googleapis.com/auth/cloud-platform"]
	credentialsObj = ServiceAccountCredentials.from_json_keyfile_name(
		credentialsJson,
		scopes = scopesList
	)

	payloadObj = {
		"audio": {
			"uri": gcsLoc
		},
		"config": {
			"languageCode": "en-US",
			"encoding": "FLAC",
			"sampleRateHertz": 16000,
			"enableWordTimeOffsets": True,
			"enableAutomaticPunctuation": True,
			"useEnhanced": True,
			"model": "video",
			"metadata": {
				"interaction_type": "DISCUSSION",
				"recording_device_type": "OTHER_INDOOR_DEVICE",
				"originalMediaType": "VIDEO"
			},
			"speechContexts": {
				"phrases": [
					"Louisville", "Weldona", "signage", "PROSTAC"
				]
			}
		}
	}

	try:
		httpObj = credentialsObj.authorize(httplib2.Http())
		serviceObj = build(
			serviceName = "speech",
			version = "v1p1beta1",
			http = httpObj,
			developerKey = "__Google_Speech_API_Key__"
		)
		responseObj = serviceObj.speech().longrunningrecognize(body = payloadObj).execute()

		print "job " + str(jobId) + " for global id " + str(globalId)

		apiName = responseObj["name"]
		print "request name " + str(apiName)

		sqlCmd = """update speechJobs set apiName = %s, beenProcessed = %s where jobId = %s"""
		sqlData = [apiName, 1, jobId]
		queryResp = utilities.dbExecution(sqlCmd, sqlData)
	except Exception as e:
		sqlCmd = """update speechJobs set jobStatus = %s, beenProcessed = %s where jobId = %s"""
		sqlData = ["longrunning api call failed", 1, jobId]
		queryResp = utilities.dbExecution(sqlCmd, sqlData)
		print "longrunning api call failed"


def main():
	sqlCmd = """select globalId, jobId, gcsLoc from speechJobs where beenProcessed = %s order by jobId limit 1"""
	sqlData = [0]
	queryResp = utilities.dbExecution(sqlCmd, sqlData)

	print "Content-type: text/plain; charset=UTF-8\n\n"

	if queryResp[2]:
		gcsLoc = queryResp[2][0][2].replace("'","")
		jobId = queryResp[2][0][1]
		globalId = queryResp[2][0][0]
		print globalId
		print gcsLoc
		print jobId
		runCycle(gcsLoc, jobId, globalId)
	else:
		print "No jobs to run."


if __name__ == "__main__":
	main()