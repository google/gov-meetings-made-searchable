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
import ujson
import webapp2
import utilities


class main(webapp2.RequestHandler):
	def get(self):
		self.response.headers["Content-Type"] = "application/json"
		self.response.headers.add_header(
			"Cache-Control",
			"no-cache, no-store, must-revalidate, max-age=0"
		)
		self.response.headers.add_header(
			"Expires",
			"0"
		)

		try:
			globalId = self.request.get("gId")
			sqlData = (globalId)
			sqlCmd = "select videoName, beenTranscribed, beenTranscoded, videoDownloaded, videoLink, orgIdentifier, prodTranscript, meetingDate, meetingDesc, beenIndexed, youtubeId, meetingId, prodTranscode, urlIdentifier from meetingRegistry where globalId = %s"
			resultList = utilities.dbExecution(sqlCmd, sqlData)
			videoName = resultList[2][0][0]
			beenTranscribed = resultList[2][0][1]
			beenTranscoded = resultList[2][0][2]
			videoDownloaded = resultList[2][0][3]
			videoLink = resultList[2][0][4]
			orgIdentifier = resultList[2][0][5]
			prodTranscript = resultList[2][0][6]
			meetingDate = resultList[2][0][7]
			meetingDesc = resultList[2][0][8]
			beenIndexed = resultList[2][0][9]
			youtubeId = resultList[2][0][10]
			meetingId = resultList[2][0][11]
			prodTranscode = resultList[2][0][12]
			urlIdentifier = resultList[2][0][13]
		except:
			videoName = None
			beenTranscribed = None
			beenTranscoded = None
			videoDownloaded = None
			videoLink = None
			orgIdentifier = None
			prodTranscript = None
			meetingDate = None
			meetingDesc = None
			beenIndexed = None
			youtubeId = None
			meetingId = None
			prodTranscode = None
			urlIdentifier= None

		resultObj = {}
		resultObj["videoName"] = videoName
		resultObj["beenTranscribed"] = beenTranscribed
		resultObj["beenTranscoded"] = beenTranscoded
		resultObj["videoDownloaded"] = videoDownloaded
		resultObj["videoLink"] = videoLink
		resultObj["orgIdentifier"] = orgIdentifier
		resultObj["prodTranscript"] = prodTranscript
		resultObj["meetingDate"] = meetingDate
		resultObj["meetingDesc"] = meetingDesc
		resultObj["beenIndexed"] = beenIndexed
		resultObj["youtubeId"] = youtubeId
		resultObj["meetingId"] = meetingId
		resultObj["prodTranscode"] = prodTranscode
		resultObj["urlIdentifier"] = urlIdentifier

		self.response.out.write(ujson.dumps(resultObj))


app = webapp2.WSGIApplication([
		("/meetingDetails", main)], debug = True
	)
