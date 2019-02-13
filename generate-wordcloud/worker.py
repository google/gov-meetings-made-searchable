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
import time
import json
import base64
import random
import requests
import calendar
from scipy.misc import imsave
from scipy.misc import imresize
from google.cloud import pubsub
from collections import Counter
from google.cloud import storage
from nltk.corpus import stopwords
from wordcloud import WordCloud, ImageColorGenerator
from matplotlib.colors import LinearSegmentedColormap
from oauth2client.service_account import ServiceAccountCredentials

service_account_json = "__Credential_JSON_File_Name__"
dirPath = os.path.normpath(os.getcwd())
service_account_path = os.path.join(dirPath, service_account_json)


projectId = "__GCP_Project_ID__"
topicName = "wordcloudQueue"
subName = "wordcloud-creation-subscription"

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


def recolorBlue(**kwargs):
	return "hsl(%d, %d%%, %d%%)" % (
		random.randint(210, 230),
		random.randint(60, 90),
		random.randint(35, 45))


def getStopwords():
	stopwordsPath = os.path.join(dirPath, "stopwords-20180109-133115.json")
	with open(stopwordsPath) as stopwordFile:    
		contentsStr = stopwordFile.read()
	jsonObj = json.loads(contentsStr)
	stopwordList = []
	for eachEntry in jsonObj:
		stopwordList.append(eachEntry["word"])

	return stopwordList


def generateStr(globalId, prodTranscript):
	masterStr = ""
	stopWords = set(stopwords.words("english"))

	fileName = "rawTxt-" + str(globalId) + "-" + prodTranscript + "-list.txt"
	cloudPath = "accounts/townofsuperior/enrichments/" + str(globalId) + "/transcripts/" + fileName
	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)
	blobObj = bucketObj.blob(cloudPath)
	masterStr = blobObj.download_as_string()

	masterStr = masterStr.strip()
	masterStr = masterStr.replace("\n", " ")

	#masterStr = masterStr.replace("lewisville", "louisville")

	stopwordList = getStopwords()
	stopWords.update(
		stopwordList
	)

	cleanList = [i for i in masterStr.lower().split() if i not in stopWords]
	#cleanList = []
	#for eachEntry in masterStr.lower().split():
	#	if eachEntry not in stopWords:
	#		cleanList.append(eachEntry)

	c = Counter(cleanList)
	cleanStr = " ".join(cleanList)

	return [cleanStr, fileName, len(masterStr.lower().split()), len(cleanList), c.most_common(10)]


def generateWordcloud(wordStr, outputFile):

	themeList = {}
	theme01 = {}
	theme01["bgColor"] = "#341c01"
	theme01["colorList"] = ["#fffff0", "#d0aa3a", "#cea92e", "#c1762e", "#aea764", "#d59733", "#e9e3cd"]
	themeList["theme01"] = theme01

	theme02 = {}
	theme02["bgColor"] = "#fff"
	theme02["colorList"] = ["#03318c", "#021f59", "#61a2ca", "#30588c", "#32628c"]
	themeList["theme02"] = theme02

	theme03 = {}
	theme03["bgColor"] = "#223564"
	theme03["colorList"] = ["#f7e4be", "#f0f4bc", "#9a80a4", "#848da6"]
	themeList["theme03"] = theme03

	theme04 = {}
	theme04["bgColor"] = "#091c2b"
	theme04["colorList"] = ["#edecf2", "#c1d4f2", "#6d98ba", "#3669a2", "#8793dd"]
	themeList["theme04"] = theme04

	theme05 = {}
	theme05["bgColor"] = "#000"
	theme05["colorList"] = ["#b95c28", "#638db2", "#f0f0f0", "#dbcc58", "#1b3c69", "#d5a753"]
	themeList["theme05"] = theme05

	theme06 = {}
	theme06["bgColor"] = "#262626"
	theme06["colorList"] = ["#468966", "#fff0a5", "#ffb03b", "#b64926", "#8e2800"]
	themeList["theme06"] = theme06


	theme07 = {}
	theme07["bgColor"] = "#fff"
	theme07["colorList"] = ["#438D9C", "#E8A664", "#9C6043", "#171717", "#c00000"]
	themeList["theme07"] = theme07
	#colorList = ["#d35400", "#c0392b", "#e74c3c", "#e67e22", "#f39c12"]
	#colorList = ["#f39c12", "#e67e22", "#e74c3c", "#c0392b", "#d35400"]

	liveTheme = "theme07"
	bgColor = themeList[liveTheme]["bgColor"]
	colorList = themeList[liveTheme]["colorList"]

	#colorList = ["#f1e3be", "#f1f3be", "#927fa1", "#858ca4"]

	colorMap = LinearSegmentedColormap.from_list("mycmap", colorList)

	fontPath = os.path.join(dirPath, "fonts/LilitaOne-Regular.ttf")

	wordcloudObj = WordCloud(
		font_path = fontPath,
		mode = "RGBA",
		width = 1200,
		height = 852,
		margin = 16,
		random_state = 0,
		background_color = bgColor,
		normalize_plurals = True,
		colormap = colorMap
	).generate(wordStr)


	#wordcloudObj.recolor(
	#	color_func = recolorBlue,
	#	random_state = 5
	#)

	smallerImg = imresize(wordcloudObj, [382, 538])
	imsave(outputFile, smallerImg)


def gcsUpload(globalId, fileName, filePath):
	cloudPath = "accounts/townofsuperior/enrichments/" + str(globalId) + "/wordclouds/" + fileName
	clientObj = storage.Client.from_service_account_json(service_account_path)
	bucketObj = clientObj.get_bucket(bucketName)
	blobObj = bucketObj.blob(cloudPath)

	metadataStr = "inline; filename='%s'" % fileName
	blobObj.content_disposition = metadataStr

	blobObj.upload_from_filename(filePath)
	blobObj.make_public()

	return blobObj.public_url


def assignUrl(globalId, wcUrl):
	reqUrl = utility_service_url + "/ep-idWordcloud"
	payloadObj = { 
		"gId": globalId,
		"wcUrl": wcUrl
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text

	return respTxt


def lookupMeeting(globalId):
	reqUrl = utility_service_url + "/meetingDetails"
	payloadObj = { 
		"gId": globalId
	}
	responseObj = requests.get(reqUrl, params=payloadObj)
	respTxt = responseObj.text
	jsonObj = json.loads(respTxt)

	return jsonObj["prodTranscript"]


def dispatchWorker(ackId, globalId):
	successFlag = None
	try:
		print ".. creating word cloud for meeting: " + str(globalId)
		prodTranscript = lookupMeeting(globalId)
		print "... word cloud will be made from transcript: " + str(prodTranscript)

		epochTime = calendar.timegm(time.gmtime())
		outputFile =  str(epochTime) + "-" + str(globalId) + "-wordcloud-538-by-382.png"
		filePath = os.path.join(dirPath, outputFile)

		outputList = generateStr(globalId, prodTranscript)
		print "... pulling words from file: " + outputList[1]
		print ".... " + str(outputList[2]) + " words identified"
		if outputList[2] > 0:
			print ".... " + str(outputList[3]) + " significant words identified"
			print ".... ten most common words: "
			for eachEntry in outputList[4]:
				print "..... " + str(eachEntry)
			wordStr = outputList[0]
			generateWordcloud(wordStr, filePath)

			wcUrl = gcsUpload(globalId, outputFile, filePath)
			os.remove(filePath)
			print "... word cloud URL: " + wcUrl
			print "... URL assigned in database: " + str(assignUrl(globalId, wcUrl))
			successFlag = True
		else:
			print ".... stopping now because no words were identified"
			successFlag = False
		print acknowledgeMsg(ackId)
	except Exception as e:
		print acknowledgeMsg(ackId)
		print "skip " + e.message
		successFlag = False

	return successFlag

def acknowledgeMsg(ackId):
	postPayload = {
		"ackIds": [ackId]
	}
	subStr = "projects/%s/subscriptions/%s" % (projectId, subName)
	reqUrl = "https://pubsub.googleapis.com/v1/%s:acknowledge" % subStr
	psMsg = psCall(reqUrl, postPayload)

	return "... Pubsub message acknowledged"


def nextAction(globalId):
	reqUrl = utility_service_url + "/msgPublish"
	payloadObj = { 
		"msgAction": "index",
		"topicName": "indexQueue",
		"gId": globalId
	}
	responseObj = requests.get(
		reqUrl,
		params = payloadObj
	)
	respTxt = responseObj.text

	return respTxt


def main():
	#globalId = 2729
	#runWorkflow(globalId)

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
			successFlag = dispatchWorker(ackId, globalId)
			if successFlag == True:
				pass
				print nextAction(globalId)
			else:
				print ".. not initiating next action"
		except:
			pass
		time.sleep(1)


if __name__ == "__main__":
	main()
