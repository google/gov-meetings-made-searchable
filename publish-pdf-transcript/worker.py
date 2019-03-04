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
import pdfkit
import base64
import requests
from datetime import datetime
from google.cloud import pubsub
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials

service_account_json = "__Credential_JSON_File_Name__"
dirPath = os.path.normpath(os.getcwd())
service_account_path = os.path.join(dirPath, service_account_json)

projectId = "__GCP_Project_ID__"
topicName = "publish-transcript-queue"
subName = "publish-transcript-subscription"

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


def mkPdf(inputFile):
	outputFile = inputFile.replace(".html", ".pdf")
	optionsObj = {
	    "page-size": "Letter",
    	"margin-top": "0.75in",
	    "margin-right": "0.75in",
	    "margin-bottom": "1.00in",
	    "margin-left": "0.75in",
	    "footer-center": "page [page]/[topage]",
	    "footer-font-name": "Roboto",
	    "footer-font-size": "8",
	    "footer-spacing": "10"
	}
	pdfkit.from_file(
		inputFile, outputFile,
		options=optionsObj
	)

	return outputFile


def lookupMeeting(globalId):
	reqUrl = utility_service_url + "/meetingDetails"
	payloadObj = { 
		"gId": globalId
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text
	jsonObj = json.loads(respTxt)

	return jsonObj["prodTranscript"], jsonObj["meetingDate"], jsonObj["orgIdentifier"]
	

def formatDate(meetingDate):
	datetimeObj = datetime.strptime(meetingDate, "%Y%m%d")
	formattedDate = datetimeObj.strftime("%B %d, %Y")
	weekDay = datetimeObj.strftime("%A")

	return formattedDate, weekDay


def meetingDetails(globalId):
	reqUrl = utility_service_url + "/meetingDetails"
	payloadObj = { 
		"gId": globalId
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text
	jsonObj = json.loads(respTxt)
	
	formattedDate, weekDay = formatDate(jsonObj["meetingDate"])

	return jsonObj["meetingDesc"], formattedDate, weekDay


def gcsUpload(globalId, orgIdentifier, fileName, filePath):
	cloudPath = "accounts/" + orgIdentifier + "/enrichments/" + str(globalId) + "/transcripts/" + fileName
	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)
	blobObj = bucketObj.blob(cloudPath)

	metadataStr = "inline; filename='%s'" % fileName
	blobObj.content_disposition = metadataStr

	blobObj.upload_from_filename(filePath)
	blobObj.make_public()

	return blobObj.public_url


def assignUrl(globalId, transcriptUrl):
	reqUrl = utility_service_url + "/idTranscript"
	payloadObj = {
		"gId": globalId,
		"transcriptUrl": transcriptUrl
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text

	return respTxt


def runCycle(globalId, orgIdentifier, prodTranscript):
	basePath = "accounts/" + orgIdentifier + "/enrichments/" + str(globalId) + "/transcripts/"
	cloudPath = basePath + str(prodTranscript) + "/"
	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)
	listObj = bucketObj.list_blobs(prefix=cloudPath)
	print "!!! length of listObj: " + str(listObj)
	transcriptList = []
	for eachEntry in listObj:
		if ".json" in eachEntry.name:
			transcriptList.append(str(eachEntry.name))

	fileCnt = 0

	htmlStr = ""
	for eachFile in sorted(transcriptList, reverse=False):
		fileCnt += 1
		blobObj = bucketObj.get_blob(eachFile)
		blobStr = blobObj.download_as_string()
		jsonObj = json.loads(blobStr)

		if "response" in jsonObj:
			if "results" in jsonObj["response"]:
				for eachAlt in jsonObj["response"]["results"]:
					tmpStr = ""
					timeVal = None
					if "alternatives" in eachAlt:
						timeVal = eachAlt["alternatives"][0]["words"][0]["startTime"]
						timeVal = timeVal.replace("s", "")
						timeVal = float(timeVal)
						if fileCnt > 1:
							timeVal = timeVal + ((fileCnt - 1) * 10800)
						displayTime = time.strftime("%H:%M:%S", time.gmtime(timeVal))
						transcriptStr = eachAlt["alternatives"][0]["transcript"]
						transcriptStr = transcriptStr.strip()
						transcriptStr = transcriptStr.replace("Lewisville", "Louisville")
						transcriptStr = transcriptStr.replace("Pro stack", "PROSTAC")
						transcriptStr = transcriptStr.replace("pro stack", "PROSTAC")
						transcriptStr = transcriptStr.replace("Pro Stacks", "PROSTAC")
						transcriptStr = transcriptStr.replace("pro Strat", "PROSTAC")
						transcriptStr = transcriptStr.replace("pro-sex", "PROSTAC")
						htmlStr += "<h4>%s</h4>" % displayTime
						htmlStr += """<p class="transcriptTxt">%s</p>""" % transcriptStr

	#newPath = basePath + "rawTxt-" + str(globalId) + "-" + exportType + "-" + str(prodTranscript) + ".txt"
	##newPath = basePath + fileName
	##blobObj = bucketObj.blob(newPath)
	##blobObj.upload_from_string(masterStr.strip())

	return htmlStr


def mkTranscript(globalId):
	prodTranscript, rawDate, orgIdentifier = lookupMeeting(globalId)
	meetingDesc, meetingDate, weekDay = meetingDetails(globalId)


	htmlStr = """
	<html>
		<head>
			<style>
				@font-face { 
					font-family: "Roboto";
					src: url("./fonts/Roboto-Regular.ttf") format("truetype");
				}
				@font-face { 
					font-family: "Roboto-Bold";
					src: url("./fonts/Roboto-Bold.ttf") format("truetype");
				}
				body {
					font-family: "Roboto";
					font-size: 0.79em;
				}
				h1 {
					font-family: "Roboto-Bold";
				}
				h2 {
					font-family: "Roboto-Bold";
				}
				h3 {
					font-family: "Roboto-Bold";
				}
				h4 {
					font-family: "Roboto-Bold";
					margin-left: 10px;
					padding-top: 0px;
					padding-bottom: 0px;
				}
				.transcriptTxt {
					font-family: "Roboto";
					margin-left: 20px;
					padding-top: 0px;
					padding-bottom: 8px;

				}
			</style>
		</head>
		<body>
	"""

	htmlStr += "<center>"
	htmlStr += "<h1>Superior, Colorado</h1>"
	htmlStr += "<h2>%s</h2>" % meetingDesc
	htmlStr += "<h3>%s, %s</h3>" % (weekDay, meetingDate)
	htmlStr += "<br>"
	htmlStr += "--------------------------------------------------------------------------------------------------------------------------------------------------------"
	htmlStr += "<br>"
	htmlStr += "<i>This transcript was generated automatically using cutting edge speech-to-text technology, which isn't yet on par with human transcription. This transcript may not accurately reflect the contents of the meeting proceedings.</i>"
	htmlStr += "<br>"
	htmlStr += "--------------------------------------------------------------------------------------------------------------------------------------------------------"
	htmlStr += "</center>"
	htmlStr += "<br><br>"

	htmlStr += runCycle(globalId, orgIdentifier, prodTranscript)

	htmlStr += """
		</body>
	</html>
	"""
	meetingDesc = meetingDesc.replace(" ", "-")
	meetingDesc = meetingDesc.replace("/", "-")
	meetingDesc = meetingDesc.replace(",", "")
	fileName = "Superior-" + str(rawDate) + "-" + meetingDesc + "-Transcript.html"

	htmlPath = os.path.join(dirPath, fileName)
	htmlFile = open(htmlPath, "w")
	htmlFile.write(htmlStr.encode("ascii", "ignore"))
	htmlFile.close()

	pdfName =  mkPdf(fileName)
	print "pdfName: " + pdfName
	pdfPath = os.path.join(dirPath, pdfName)
	print "pdfPath: " + pdfPath
	transcriptUrl = gcsUpload(globalId, orgIdentifier, pdfName, pdfPath)
	print assignUrl(globalId, transcriptUrl)
	os.remove(htmlPath)
	os.remove(pdfPath)


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


def acknowledgeMsg(ackId):
	postPayload = {
		"ackIds": [ackId]
	}
	subStr = "projects/%s/subscriptions/%s" % (projectId, subName)
	reqUrl = "https://pubsub.googleapis.com/v1/%s:acknowledge" % subStr
	psMsg = psCall(reqUrl, postPayload)

	return "... Pubsub message acknowledged"


def dispatchWorker(ackId, globalId):
	try:
		mkTranscript(globalId)
		print acknowledgeMsg(ackId)
	except Exception as e:
		print "erroring out"
		print acknowledgeMsg(ackId)
		print "skip " + e.message


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
		except:
			pass
		time.sleep(10)


if __name__ == "__main__":
	main()