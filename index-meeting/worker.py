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
import json
import time
import urllib
import base64
import requests
from google.cloud import pubsub
from google.cloud import storage
from elasticsearch import helpers
from elasticsearch import Elasticsearch
from oauth2client.service_account import ServiceAccountCredentials

service_account_json = "__Credential_JSON_File_Name__"
dirPath = os.path.normpath(os.getcwd())
service_account_path = os.path.join(dirPath, service_account_json)

projectId = "__GCP_Project_ID__"
topicName = "indexQueue"
subName = "index-meeting-subscription"

bucketName = "__GCS_Storage_Bucket_Name__"
utility_service_url = "__Utility_Service_URL__"

psClient = pubsub.SubscriberClient()

topicPath = psClient.topic_path(
	projectId,
	topicName
)

subPath = psClient.subscription_path(
	projectId,
	subName
)

subObj = psClient.subscribe(
	subPath
)

cummTime = None

searchClient = Elasticsearch(
	["https://7b76c3d47a7445119d54a4089ae9e9a3.us-central1.gcp.cloud.es.io:9243/"],
	http_auth = (
		"elastic",
		"EbJ3suYnJ5YdTIJRM9i38Swu"
	)
)


def psCall(reqUrl, postPayload):
	scopesList = ["https://www.googleapis.com/auth/cloud-platform"]
	credentialsObj = ServiceAccountCredentials.from_json_keyfile_name(
		service_account_path,
		scopes = scopesList
	)

	accessToken = "Bearer %s" % credentialsObj.get_access_token().access_token
	headerObj = {
		"authorization": accessToken,
	}

	reqObj = requests.post(
		reqUrl,
		data = json.dumps(postPayload),
		headers = headerObj
	)

	return reqObj.text


def processFile(jsonObj, globalId, orgIdentifier, meetingDate, meetingDesc, urlIdentifier):
	maxTime = 0
	global cummTime
	indexList = []
	if "response" in jsonObj:
		if "results" in jsonObj["response"]:
			for eachAlt in jsonObj["response"]["results"]:
				if "alternatives" in eachAlt:
					transcriptStr = eachAlt["alternatives"][0]["transcript"]
					videoTimestamp = eachAlt["alternatives"][0]["words"][0]["startTime"]

					videoTimestamp = str(videoTimestamp).replace("s", "")
					videoTimestamp = float(videoTimestamp)


					wordsLen = len(eachAlt["alternatives"][0]["words"]) - 1
					endTime = eachAlt["alternatives"][0]["words"][wordsLen]["endTime"]
					endTime = str(endTime).replace("s", "")
					endTime = float(endTime)

					segLen = round(endTime - videoTimestamp)

					displayTime = videoTimestamp + float(cummTime)
					maxTime = videoTimestamp

					transcriptStr = transcriptStr.replace("Lewisville", "Louisville")
					transcriptStr = transcriptStr.replace("Pro stack", "PROSTAC")
					transcriptStr = transcriptStr.replace("pro stack", "PROSTAC")
					transcriptStr = transcriptStr.replace("Pro Stacks", "PROSTAC")
					transcriptStr = transcriptStr.replace("pro Strat", "PROSTAC")
					transcriptStr = transcriptStr.replace("pro-sex", "PROSTAC")

					indexEntry = {
						"_index": orgIdentifier,
						"_type": "meeting-transcript",
						"_source": {
							"globalId": int(globalId),
							"mediaTimestamp": displayTime,
							"segmentLength": segLen,
							"meetingDesc": meetingDesc,
							"transcriptStr": transcriptStr,
							"meetingDate": meetingDate,
							"urlIdentifier": urlIdentifier						
						}
					}
					indexList.append(indexEntry)

	return indexList


def runIndexing(globalId, prodTrans, orgIdentifier, meetingDate, meetingDesc, urlIdentifier):
	cloudPath = "accounts/townofsuperior/enrichments/" + str(globalId) + "/transcripts/"  + str(prodTrans) + "/"
	
	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)
	listObj = bucketObj.list_blobs(prefix = cloudPath)
	transcriptList = []

	for eachEntry in listObj:
		if ".json" in eachEntry.name:
			transcriptList.append(eachEntry.name)

	global cummTime
	cummTime = 0
	maxTime = 0
	fileCnt = 0

	fileList = []
	for eachFile in sorted(transcriptList, reverse=False):
		fileCnt += 1
		fileList.append(eachFile)

		blobObj = bucketObj.get_blob(eachFile)
		blobStr = blobObj.download_as_string()
		jsonObj = json.loads(blobStr)

		indexList = processFile(
			jsonObj,
			globalId,
			orgIdentifier,
			meetingDate,
			meetingDesc,
			urlIdentifier
		)

		helpers.bulk(searchClient, indexList)

		cummTime = float(cummTime) + 10800

	return cloudPath, fileList, fileCnt, len(indexList)


def dispatchWorker(ackId, globalId):
	try:
		reqUrl = utility_service_url + "/meetingDetails?gId=%s" % globalId
		responseObj = requests.get(reqUrl)
		respTxt = responseObj.text

		jsonObj = json.loads(respTxt)

		prodTrans = jsonObj["prodTranscript"]
		orgIdentifier = jsonObj["orgIdentifier"]
		meetingDate = jsonObj["meetingDate"]
		meetingDesc = jsonObj["meetingDesc"]
		beenIndexed = jsonObj["beenIndexed"]
		urlIdentifier = jsonObj["urlIdentifier"]

		if beenIndexed == 0:
			toggleResp = toggleIndex(globalId)
			print "... index marker has been updated " + str(toggleResp)
			cloudPath, fileList, fileCnt, indexLen = runIndexing(
				globalId,
				prodTrans,
				orgIdentifier,
				meetingDate,
				meetingDesc,
				urlIdentifier
			)

			print globalId
			print ""
			print cloudPath
			print ""
			print fileList
			print ""

			print str(fileCnt) + " files processed"
		else:
			print "... entry has already been indexed"
		postPayload = {
			"ackIds": [ackId]
		}
		subStr = "projects/%s/subscriptions/%s" % (projectId, subName)
		reqUrl = "https://pubsub.googleapis.com/v1/%s:acknowledge" % subStr
		psMsg = psCall(reqUrl, postPayload)
		print "... Pubsub message acknowledged"
	except Exception as e:
		print "skip " + e.message


def toggleIndex(globalId):
	reqUrl = utility_service_url + "/toggleIndex?gId=%s" % globalId
	responseObj = requests.get(reqUrl)
	respTxt = responseObj.text

	return respTxt


def nextAction(globalId):
	reqUrl = utility_service_url + "/msgPublish"
	payloadObj = { 
		"msgAction": "publish-transcript",
		"topicName": "publish-transcript-queue",
		"gId": globalId
	}
	responseObj = requests.get(
		reqUrl,
		params = payloadObj
	)
	respTxt = responseObj.text

	return respTxt


def main():
	postPayload = {
		"returnImmediately": True,
		"maxMessages": 1
	}
	subStr = "projects/%s/subscriptions/%s" % (projectId, subName)
	reqUrl = "https://pubsub.googleapis.com/v1/%s:pull" % subStr

	while True:
		psMsg = psCall(reqUrl, postPayload)
		try:
			jsonObj = json.loads(psMsg)
			msgType = base64.b64decode(jsonObj["receivedMessages"][0]["message"]["data"])
			print "Message Received. Type = '%s'" % str(msgType)
			ackId = jsonObj["receivedMessages"][0]["ackId"]
			globalId = jsonObj["receivedMessages"][0]["message"]["attributes"]["globalId"]
			print ackId
			print globalId
			dispatchWorker(ackId, globalId)
			print nextAction(globalId)
		except:
			pass
		time.sleep(4)


if __name__ == "__main__":
	main()
