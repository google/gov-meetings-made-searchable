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
import json
import time
import base64
import requests
import httplib2
from google.cloud import pubsub
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials

service_account_json = "__Credential_JSON_File_Name__"
dirPath = os.path.normpath(os.getcwd())
service_account_path = os.path.join(dirPath, service_account_json)

projectId = "__GCP_Project_ID__"
topicName = "wordlistQueue"
subName = "word-list-creation-subscription"

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


def psCall(reqUrl, postPayload):
	scopesList = ["https://www.googleapis.com/auth/cloud-platform"]
	credentialsObj = ServiceAccountCredentials.from_json_keyfile_name(
		service_account_json,
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


def acknowledgeMsg(ackId):
	postPayload = {
		"ackIds": [ackId]
	}
	subStr = "projects/%s/subscriptions/%s" % (projectId, subName)
	reqUrl = "https://pubsub.googleapis.com/v1/%s:acknowledge" % subStr
	psMsg = psCall(reqUrl, postPayload)

	return "... Pubsub message acknowledged"


def get_api_results(globalId, orgIdentifier, prodTranscript):
	basePath = "accounts/" + orgIdentifier + "/enrichments/" + str(globalId) + "/transcripts/"
	cloudPath = basePath + str(prodTranscript) + "/"
	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)
	listObj = bucketObj.list_blobs(prefix=cloudPath)
	transcriptList = []
	for eachEntry in listObj:
		if ".json" in eachEntry.name:
			transcriptList.append(str(eachEntry.name))
			#print eachEntry.size

	return transcriptList


def results_files_to_string(transcriptList, exportType):
	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)

	fileCnt = 0

	masterStr = ""
	for eachFile in sorted(transcriptList, reverse=False):
		fileCnt += 1

		blobObj = bucketObj.get_blob(eachFile)
		blobStr = blobObj.download_as_string()
		jsonObj = json.loads(blobStr)

		if "response" in jsonObj:
			if "results" in jsonObj["response"]:
				for eachAlt in jsonObj["response"]["results"]:
					tmpStr = ""
					if exportType is "list":
						if "alternatives" in eachAlt:
							for eachWord in eachAlt["alternatives"][0]["words"]:
								tmpStr = eachWord["word"]
								tmpStr = tmpStr.lower()
								tmpStr = tmpStr.replace(".", "")
								tmpStr = tmpStr.replace(",", "")
								tmpStr = tmpStr.replace("?", "")
								tmpStr = tmpStr.replace("!", "")
								tmpStr = tmpStr + "\n"
								masterStr = masterStr + tmpStr
					if exportType is "long":
						tmpStr = eachAlt["alternatives"][0]["transcript"]
						masterStr = masterStr + " " + tmpStr
	masterStr = masterStr.replace("lewisville", "louisville")
	masterStr = masterStr.replace("Pro stack", "PROSTAC")
	masterStr = masterStr.replace("pro stack", "PROSTAC")
	masterStr = masterStr.replace("Pro Stacks", "PROSTAC")
	masterStr = masterStr.replace("pro Strat", "PROSTAC")
	masterStr = masterStr.replace("pro-sex", "PROSTAC")

	return masterStr, fileCnt


def write_string_to_gcs(globalId, orgIdentifier, prodTranscript, exportType, masterStr):
	basePath = "accounts/" + orgIdentifier + "/enrichments/" + str(globalId) + "/transcripts/"
	fileName = "rawTxt-" + str(globalId) + "-" + str(prodTranscript) + "-" + exportType + ".txt"
	newPath = basePath + fileName

	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)
	blobObj = bucketObj.blob(newPath)
	blobObj.upload_from_string(masterStr.strip())

	return "... file created in GCS"


def lookupMeeting(globalId):
	reqUrl = utility_service_url + "/meetingDetails"
	payloadObj = { 
		"gId": globalId
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text
	jsonObj = json.loads(respTxt)

	return jsonObj["prodTranscript"], jsonObj["orgIdentifier"]


def nextAction(globalId):
	reqUrl = utility_service_url + "/msgPublish"
	payloadObj = { 
		"msgAction": "create-wordcloud",
		"topicName": "wordcloudQueue",
		"gId": globalId
	}
	responseObj = requests.get(
		reqUrl,
		params = payloadObj
	)
	respTxt = responseObj.text
	respTxt = respTxt.replace("\r", "")
	respTxt = respTxt.replace("\n", "")

	return ".. next action initiated: " + str(respTxt)


def issue_transcript_error(globalId):
	reqUrl = utility_service_url + "/toggleTranscriptErr"
	payloadObj = { 
		"gId": globalId
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text

	return respTxt


def dispatchWorker(ackId, globalId):
	successFlag = None
	try:
		print ".. creating word list for meeting: " + str(globalId)
		prodTranscript, orgIdentifier = lookupMeeting(globalId)
		print "... word list will be created from transcript: " + str(prodTranscript)
		transcriptList = get_api_results(globalId, orgIdentifier, prodTranscript)
		print "... " + str(len(transcriptList)) + " files will be processed"
		masterStr, fileCnt = results_files_to_string(transcriptList, "list")

		print "... " + str(fileCnt) + " files processed"
		print ".... the masterStr is " + str(len(masterStr)) + " characters in length"
		if len(masterStr) > 0 and fileCnt > 0:
			print write_string_to_gcs(globalId, orgIdentifier, prodTranscript, "list", masterStr)
			successFlag = True
		else:
			print ".... something isn't right so issuing a transcriptErr"
			toggleResp = issue_transcript_error(globalId)
			print ".... " + str(toggleResp)
			successFlag = False

		print acknowledgeMsg(ackId)
	except Exception as e:
		print "something went wrong"
		print acknowledgeMsg(ackId)
		print "skip " + e.message
		successFlag = False

	return successFlag


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
			ackId = jsonObj["receivedMessages"][0]["ackId"]
			globalId = jsonObj["receivedMessages"][0]["message"]["attributes"]["globalId"]
			successFlag = dispatchWorker(ackId, globalId)
			if successFlag == True:
				print nextAction(globalId)
			else:
				print ".. not initiating next action"
			print ""
		except:
			pass
		time.sleep(4)


if __name__ == "__main__":
	main()
