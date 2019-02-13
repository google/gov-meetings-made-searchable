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


def cleanInput(inputVal, inputLen):
	inputVal = str(inputVal)
	if len(inputVal) > inputLen:
		inputVal = inputVal[:inputLen]
	inputVal = inputVal.replace("/", "")
	inputVal = inputVal.replace("\\", "")
	inputVal = inputVal.replace(";", "")

	return inputVal


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
			globalId = cleanInput(globalId, 5)
			prodTranscode = self.request.get("transcode")
			prodTranscode = cleanInput(prodTranscode, 22)
			if globalId != "":
				if prodTranscode != "":
					sqlCmd = "update meetingRegistry set prodTranscode = %s where globalId = %s"
					sqlData = (prodTranscode, globalId)
					resultList = utilities.dbExecution(sqlCmd, sqlData)
			outputStr = str(resultList)
		except:
			outputStr = None

		resultObj = {}
		resultObj["response"] = outputStr

		self.response.out.write(ujson.dumps(resultObj))


app = webapp2.WSGIApplication([
		("/idTranscode", main)], debug = True
	)
