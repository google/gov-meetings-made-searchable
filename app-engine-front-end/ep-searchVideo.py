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
import time
import ujson
import urllib
import logging
from google.appengine.api import search
from google.appengine.api import urlfetch

in_video_search_service_url = "__In_Video_Search_Service_URL__"


def main():
	passedArgs = cgi.FieldStorage()
	queryString = passedArgs["q"].value
	urlIdentifier = passedArgs["urlId"].value
	orgIdentifier = passedArgs["orgId"].value

	logging.info("search")

	payloadObj = {
		"urlId": urlIdentifier,
		"orgId": orgIdentifier,
		"q": queryString
	}

	urlParams = urllib.urlencode(payloadObj, doseq=True)
	reqUrl = in_video_search_service_url + "/?%s" % urlParams
	responseObj = urlfetch.fetch(reqUrl)
	responseStr = responseObj.content

	searchObj = ujson.loads(responseStr)
	outputObj = {}
	for eachEntry in searchObj["hits"]["hits"]:
		if "highlight" in eachEntry:
			resultObj = {}
			
			tsVal = eachEntry["_source"]["mediaTimestamp"]
			resultObj["length"] = int(eachEntry["_source"]["segmentLength"])
			resultObj["timestamp"] = time.strftime("%H:%M:%S", time.gmtime(eachEntry["_source"]["mediaTimestamp"]))
			snippetStr = eachEntry["highlight"]["transcriptStr"][0]
			snippetStr = snippetStr.replace(".", "")
			snippetStr = snippetStr.lower()
			snippetStr = snippetStr.lstrip()
			resultObj["result"] = "... " + snippetStr +"..."
			outputObj[str(int(tsVal)).zfill(6)] =  resultObj

	print "Expires: 0"
	print "Cache-Control: no-cache, no-store, must-revalidate, max-age=0"
	print "Content-Type: application/json\n"
	print ujson.dumps(outputObj)


if __name__ == "__main__":
	main()
