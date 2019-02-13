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

import cgi
import utilities

projectId = "__GCP_Project_ID__"


def main():
	passedArgs = cgi.FieldStorage()

	print "Content-type: text/plain; charset=UTF-8\n\n"

	if 1==1:
		gId = passedArgs["gId"].value
		gId = utilities.cleanInput(gId, 5)

		msgAction = passedArgs["msgAction"].value
		msgAction = utilities.cleanInput(msgAction, 22)

		topicName = passedArgs["topicName"].value
		topicName = utilities.cleanInput(topicName, 30)

		messageObj = utilities.publishMsg(projectId, gId, topicName, msgAction)
		print messageObj.get("messageIds")[0]


if __name__ == '__main__':
	main()