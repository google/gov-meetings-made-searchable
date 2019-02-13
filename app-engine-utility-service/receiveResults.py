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


import ujson
import utilities
from googleapiclient.discovery import build

from google.appengine.ext import vendor
vendor.add("lib")
import httplib2
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials

bucketName = "__GCS_Storage_Bucket_Name__"


def runCycle(jobId, apiName, gcsLoc, globalId, batchId):
	credentialsJson = "__Credential_JSON_File_Name__"

	scopesList = ["https://www.googleapis.com/auth/cloud-platform"]
	credentialsObj = ServiceAccountCredentials.from_json_keyfile_name(
		credentialsJson,
		scopes = scopesList
	)

	payloadObj = {
		"key": "__Google_Speech_API_Key__"
	}

	httpObj = credentialsObj.authorize(httplib2.Http())
	serviceObj = build(
		serviceName = "speech",
		version = "v1p1beta1",
		http = httpObj,
		developerKey= "__Google_Speech_API_Key__"
	)

	reqObj = serviceObj.operations().get(name=apiName).execute()

	try:
		if reqObj["metadata"]["progressPercent"] == 100:
			clientObj = storage.Client()
			bucketObj = clientObj.get_bucket(bucketName)
			cloudPath = gcsLoc.replace("'", "")
			cloudPath = cloudPath.replace(".flac", ".json")
			bucketPrexif = "gs://" + bucketName + "/"
			cloudPath = cloudPath.replace(bucketPrexif, "")
			cloudPath = cloudPath.replace("transcodes/", "")

			globalDir = "/" + str(globalId) + "/"
			transDir = globalDir + "transcripts/" + str(batchId) + "-"
			newPath = cloudPath.replace(globalDir, transDir)

			blobObj = bucketObj.blob(newPath)
			blobObj.upload_from_string(ujson.dumps(reqObj))

			sqlCmd = """update speechJobs set respExported = %s where jobId = %s"""
			sqlData = [1, jobId]
			queryResp = utilities.dbExecution(sqlCmd, sqlData)

			return "... job " + str(jobId) + " finished"
		else:
			return "... job " + str(reqObj["metadata"]["progressPercent"]) + "% complete"
	except Exception, e:
		return "... job queued"


def nextAction(globalId):
	projectName = "__GCP_Project_ID__"
	topicName = "wordlistQueue"
	msgAction = "create-word-list"

	return utilities.publishMsg(projectName, globalId, topicName, msgAction)


def main():
	print "Content-type: text/plain; charset=UTF-8\n\n"

	sqlCmd = """select jobId, apiName, gcsLoc, globalId, batchId from speechJobs
		where beenProcessed = %s
		and respExported = %s
		and jobStatus is %s
		order by queueTimestamp asc limit 2"""
	sqlData = [1, 0, None]
	queryResp = utilities.dbExecution(sqlCmd, sqlData)

	for eachEntry in queryResp[2]:
		jobId = eachEntry[0]
		##print jobId
		apiName = eachEntry[1]
		gcsLoc = eachEntry[2]
		globalId = eachEntry[3]
		batchId = eachEntry[4]

		if jobId:
			print "global Id: " + str(globalId)
			print "... job " + str(jobId)
			print runCycle(jobId, apiName, gcsLoc, globalId, batchId)

			sqlCmd = """select count(*) from speechJobs
				where respExported = %s
				and jobStatus is %s
				and globalId = %s"""
			sqlData = [0, None, globalId]
			queryResp = utilities.dbExecution(sqlCmd, sqlData)

			print "... " + str(queryResp[2][0][0]) + " jobs still in the queue"
			if queryResp[2][0][0] == 0:
				print nextAction(globalId)
			print ""


if __name__ == "__main__":
	main()
