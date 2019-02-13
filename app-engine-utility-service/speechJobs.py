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


import time
import base64
import logging
import calendar
import utilities

from google.appengine.ext import vendor
vendor.add("lib")
from gcloud import storage

bucketName = "__GCS_Storage_Bucket_Name__"


def lookupTranscode(globalId):
	sqlCmd = """select prodTranscode from meetingRegistry where globalId = %s"""
	sqlData = [globalId]
	resultObj = utilities.dbExecution(sqlCmd, sqlData)

	return resultObj[2][0][0]


def runCycle(globalId, prodTranscode, batchId):
	clientObj = storage.Client()
	bucketObj = clientObj.get_bucket(bucketName)
	listObj = bucketObj.list_blobs(prefix="accounts/townofsuperior/enrichments/" + str(globalId) + "/transcodes/" + prodTranscode)
	fileCnt = 0
	for eachEntry in listObj:

		if ".flac" in eachEntry.name:
			gcsLoc = "gs://" + eachEntry.bucket.name + "/" + eachEntry.name
			sqlCmd = """insert into speechJobs (globalId, orgIdentifier, gcsLoc, beenProcessed, batchId) values (%s, %s, %s, %s, %s)"""
			sqlData = [globalId, "townofsuperior", gcsLoc, 0, batchId]
			utilities.dbExecution(sqlCmd, sqlData)
			fileCnt += 1

	return fileCnt


def markTranscript(globalId, prodTranscript, batchId):
	prodTranscript = str(batchId) + "-" + prodTranscript
	sqlCmd = """update meetingRegistry set beenTranscribed = %s, prodTranscript = %s where globalId = %s"""
	sqlData = [1, prodTranscript, globalId]
	resultObj = utilities.dbExecution(sqlCmd, sqlData)

	return resultObj


def main():
	projectName = "__GCP_Project_ID__"
	subName = "speech-job-subscription"

	print "Content-type: text/plain; charset=UTF-8\n\n"

	respObj = utilities.pullMsg(projectName, subName, True)
	if respObj:
		receivedMessage = respObj.get("receivedMessages")[0]
		msgObj = receivedMessage.get("message")
		print ".. pubsub message id: " + str(msgObj.get("messageId"))
		msgType = base64.b64decode(str(msgObj.get("data")))
		print ".. message type: " + msgType
		globalId = msgObj.get("attributes")["globalId"]

		ackId = receivedMessage.get("ackId")
		utilities.ackMsg(projectName, subName, ackId)

		if globalId:
			epochTime = calendar.timegm(time.gmtime())
			batchId = str(epochTime)
			print "... creating Speech API jobs for meeting: " + str(globalId)

			prodTranscript = lookupTranscode(globalId)
			logging.info(prodTranscript)
			print ".... production trascript is: " + prodTranscript

			jobCnt = runCycle(globalId, prodTranscript, batchId)
			print ".... created " + str(jobCnt) + " Speech API jobs"

			markTranscript(globalId, prodTranscript, batchId)
			print ".... updated meetingRegistry table"
	else:
		print "No Messages to Handle"


if __name__ == '__main__':
	main()