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
import ujson
import urllib
import logging
from datetime import datetime
from collections import Counter
from google.appengine.ext import vendor
from google.appengine.api import urlfetch

archive_video_search_service_url = "__Archive_Video_Search_Service_URL__"


def mkDate(inputStr):
	datetimeObj = datetime.strptime(inputStr, "%Y%m%d")
	date_formatted_for_dateList = datetimeObj.strftime("%Y-%m-%d")
	dateDesc = datetimeObj.strftime("%b %-d, %Y")

	return [dateDesc, date_formatted_for_dateList]


def main():
	passedArgs = cgi.FieldStorage()
	queryString = passedArgs["q"].value
	orgIdentifier = passedArgs["orgId"].value

	logging.info("archive_search")

	payloadObj = {
		"orgId": orgIdentifier,
		"q": queryString
	}

	urlParams = urllib.urlencode(payloadObj, doseq=True)
	reqUrl = archive_video_search_service_url + "/?%s" % urlParams
	responseObj = urlfetch.fetch(reqUrl)
	responseStr = responseObj.content

	searchObj = ujson.loads(responseStr)

	dateList = []
	cntList = []
	descList = []
	tooltipList = []
	pieData = []

	meeting_total = 0
	result_total = 0

	resultCnt = 0
	resultObj = []
	for eachResp in searchObj["aggregations"]["group_by_meeting"]["buckets"]:
		meeting_total += 1
		dateIndex = eachResp["meeting_details"]["hits"]["hits"][0]["_source"]["meetingDate"]
		datetimeObj = datetime.strptime(dateIndex, "%Y%m%d")
		meetingDate = datetimeObj.strftime("%B %-d, %Y")

		tmpObj = {}
		tmpObj["urlIdentifier"] = eachResp["meeting_details"]["hits"]["hits"][0]["_source"]["urlIdentifier"]
		tmpObj["transcriptMatches"] = eachResp["doc_count"]
		tmpObj["meetingDate"] = meetingDate
		tmpObj["dateIndex"] = dateIndex
		tmpObj["meetingDesc"] = eachResp["meeting_details"]["hits"]["hits"][0]["_source"]["meetingDesc"]
		resultObj.append(tmpObj)
		resultCnt += 1

		meetingDate = eachResp["meeting_details"]["hits"]["hits"][0]["_source"]["meetingDate"]
		formatted_date_list  = mkDate(meetingDate);
		dateDesc = formatted_date_list[0];
		date_formatted_for_dateList = formatted_date_list[1];

		returnCnt = eachResp["doc_count"]
		cntList.append(returnCnt)

		result_total += returnCnt

		dateList.append(date_formatted_for_dateList)

		meetingDesc = eachResp["meeting_details"]["hits"]["hits"][0]["_source"]["meetingDesc"]
		descList.append(meetingDesc)

		tooltipStr = "%s - %s - %s results" % (meetingDesc, dateDesc, returnCnt)
		tooltipList.append(tooltipStr)

		entryObj = {}
		entryObj["meetingDesc"] = meetingDesc
		entryObj["returnCnt"] = returnCnt
		pieData.append(entryObj)

	infoObj = {}
	infoObj["meeting_total"] = resultCnt
	infoObj["result_total"] = result_total

	respObj = {}
	respObj["searchResults"] = resultObj
	
	chartObj = {}
	chartObj["countList"] = cntList
	chartObj["dateList"] = dateList
	chartObj["tooltipList"] = tooltipList


	masterList = []
   	for eachEntry in pieData:
   		for i in range(0, eachEntry["returnCnt"]):
   			masterList.append(eachEntry["meetingDesc"])
 	tallyDict = dict(Counter(masterList))
 	pie_data_list = []
 	for eachEntry in tallyDict.keys():
 		pie_data_list.append([eachEntry, tallyDict[eachEntry]])
	chartObj["pieData"] = pie_data_list

	respObj["chartData"] = chartObj
	respObj["resultsInfo"] = infoObj

	print "Expires: 0"
	print "Cache-Control: no-cache, no-store, must-revalidate, max-age=0"
	print "Content-Type: application/json\n"
	print ujson.dumps(respObj)


if __name__ == "__main__":
	main()
