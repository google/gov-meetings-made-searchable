"""Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0
    
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""


import os
import re
import sys
import json
import time
import base64
import shutil
import calendar
import requests
import subprocess
from google.cloud import storage
from time import gmtime, strftime
from oauth2client.service_account import ServiceAccountCredentials

dirPath = os.path.normpath(os.getcwd())
credentialsJson = "__Credential_JSON_File_Name__"

projectId = "__GCP_Project_ID__"
topicName = "__Pubsub_Topic_Name__"
subName = "__Pubsub_Subscription_Name__"

bucketName = "__GCS_Storage_Bucket_Name__"
utility_service_url = "__Utility_Service_URL__"

segment_length_minutes = 180
segment_length_seconds = segment_length_minutes * 60


def psCall(reqUrl, postPayload):
	scopesList = ["https://www.googleapis.com/auth/cloud-platform"]
	credentialsObj = ServiceAccountCredentials.from_json_keyfile_name(
		credentialsJson,
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


def modifyDeadline(ackId, timeWindow):
	postPayload = {
		"ackIds": [ackId],
		"ackDeadlineSeconds": timeWindow
	}
	subStr = "projects/%s/subscriptions/%s" % (projectId, subName)
	reqUrl = "https://pubsub.googleapis.com/v1/%s:modifyAckDeadline" % subStr
	print ".... extending acknowledgement deadline by " + str(timeWindow) + " seconds"

	return psCall(reqUrl, postPayload)


def downloadFile(fileName, filePath, orgIdentifier):
	clientObj = storage.Client()
	bucketObj = clientObj.get_bucket(bucketName)
	cloudPath = "accounts/%s/video/" % orgIdentifier
	cloudPath = cloudPath + fileName
	print ".... defining cloud path for file"
	print "..... " + cloudPath
	blobObj = bucketObj.blob(cloudPath)
	print ".... downloading source file locally"
	print "..... " + filePath
	with open(filePath, "w") as fileObj:
		blobObj.download_to_file(fileObj)

	return


def uploadFiles(globalId, segmentsFlac, ackId, orgIdentifier, tsDir):
	clientObj = storage.Client()
	bucketObj = clientObj.get_bucket("municeps")
	flacList = os.listdir(segmentsFlac)
	print "... preparing to upload %s files" % str(len(flacList))
	for eachFile in os.listdir(segmentsFlac):
		print ".... " + eachFile
		cloudPath = "accounts/%s/enrichments/%s/transcodes/%s/%s" % (orgIdentifier, str(globalId), tsDir, eachFile)
		##print ".... " + cloudPath
		blobObj = bucketObj.blob(cloudPath)
		localPath = segmentsFlac + "/" + eachFile
		##print ".... " + localPath
		blobObj.upload_from_filename(localPath)
		modifyDeadline(ackId, 120)

	return


def nameSegments(videoName, segmentsWav):
	timeStamp = strftime("%Y%m%d-%H%M%S", gmtime())

	segmentName = videoName.lower()
	periodNum = len(segmentName.split("."))
	segmentName = segmentName[::-1]
	segmentName = segmentName.split(".")[periodNum - 1]
	segmentName = segmentName[::-1]
	segmentName = re.sub(r'[^\w]', "", segmentName)
	segmentName = timeStamp + "-" + segmentName + "-" + "%04d.wav"
	segmentPath = os.path.join(segmentsWav, segmentName)

	return segmentPath


def transcode(globalId, videoName, ackId, orgIdentifier, tsDir):
	workingDir = os.path.join(dirPath, str(globalId))
	if not os.path.exists(workingDir):
		os.makedirs(workingDir)
	filePath = os.path.join(workingDir, videoName)

	print "... preparing to download media"
	print ".... " + videoName
	downloadFile(videoName, filePath, orgIdentifier)
	print ".... media downloaded"

	print "... creating WAV directory locally"
	segmentsWav = os.path.join(workingDir, "segmentsWav")
	print ".... " + segmentsWav
	if os.path.exists(segmentsWav):
		shutil.rmtree(segmentsWav)
	if not os.path.exists(segmentsWav):
		os.makedirs(segmentsWav)

	print "... creating FLAC directory locally"
	segmentsFlac = os.path.join(workingDir, "segmentsFlac")
	print ".... " + segmentsFlac
	if os.path.exists(segmentsFlac):
		shutil.rmtree(segmentsFlac)
	if not os.path.exists(segmentsFlac):
		os.makedirs(segmentsFlac)

	print "... defining segments path"
	segmentPath = nameSegments(videoName, segmentsWav)
	print ".... " + segmentPath

	modifyDeadline(ackId, 120)

	print "... converting to WAV format"

	print ".... source file is in " + filePath[-4:] + " format"

	segmentCmd = "ffmpeg -loglevel error -i %s -f segment -segment_time %s -reset_timestamps 1 -ac 1 -ar %s %s" % (
		filePath,
		segment_length_seconds,
		"16000",
		segmentPath
	)

	subprocess.call(segmentCmd, shell=True)

	modifyDeadline(ackId, 120)

	print ".... preparing to convert " + str(len(os.listdir(segmentsWav))) + " files"
	for eachFile in os.listdir(segmentsWav):
		wavPath = os.path.join(segmentsWav, eachFile)
		if os.path.isfile(wavPath):
			if wavPath[-4:] == ".wav":

				flacName = wavPath[:-4] + ".flac"
				flacName = flacName.replace(segmentsWav, "")
				flacName = flacName[1:]
				flacPath = os.path.join(segmentsFlac, flacName)

				print "..... running ffmpeg - converting to FLAC format"
				convertCmd = "ffmpeg -loglevel error -i %s %s" % (
					wavPath,
					flacPath
				)
				subprocess.call(convertCmd, shell=True)

	modifyDeadline(ackId, 120)

	uploadFiles(globalId, segmentsFlac, ackId, orgIdentifier, tsDir)

	#Clean up
	if os.path.exists(workingDir):
		shutil.rmtree(workingDir)
	print "... process complete"
	print acknowledgeMsg(ackId)

	return


def acknowledgeMsg(ackId):
	postPayload = {
		"ackIds": [ackId]
	}
	subStr = "projects/%s/subscriptions/%s" % (projectId, subName)
	reqUrl = "https://pubsub.googleapis.com/v1/%s:acknowledge" % subStr
	psMsg = psCall(reqUrl, postPayload)

	return "... pubsub message acknowledged\n\n"


def lookupName(globalId):
	reqUrl = utility_service_url + "/meetingDetails?gId=%s" % globalId
	responseObj = requests.get(reqUrl)
	respTxt = responseObj.text
	jsonObj = json.loads(respTxt)
	videoName = jsonObj["videoName"]
	beenTranscoded = jsonObj["beenTranscoded"]
	orgIdentifier = jsonObj["orgIdentifier"]

	return videoName, beenTranscoded, orgIdentifier


def toggleTranscode(globalId):
	reqUrl = utility_service_url + "/toggleTranscode?gId=%s" % globalId
	responseObj = requests.get(reqUrl)
	respTxt = responseObj.text

	return respTxt


def assignId(globalId, prodTranscode):
	reqUrl = utility_service_url + "/idTranscode"
	payloadObj = { 
		"gId": globalId,
		"transcode": prodTranscode
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text

	return respTxt


def dispatchWorker(ackId, globalId):
	if 1==1:
		videoName, beenTranscoded, orgIdentifier = lookupName(globalId)
		print "... beenTranscoded: " + str(beenTranscoded)
		if beenTranscoded == 0:
			toggleResp = toggleTranscode(globalId)
			print "... transcode marker has been updated" + str(toggleResp)
			if videoName is not None:
				epochTime = calendar.timegm(time.gmtime())
				tsDir = str(epochTime) + "-" + str(segment_length_minutes) + "-mins"
				transcode(globalId, videoName, ackId, orgIdentifier, tsDir)
				assignId(globalId, tsDir)
			else:
				print "... there is no video name"
		else:
			print "... entry has already been transcoded"
			print acknowledgeMsg(ackId)


def nextAction(globalId):
	reqUrl = utility_service_url + "/msgPublish"
	payloadObj = { 
		"msgAction": "speechJob",
		"topicName": "speechQueue",
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
		time.sleep(10)


if __name__ == '__main__':
	main()


