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


import json
import logging
from flask import Flask
from flask import request
from flask import Response
from elasticsearch import Elasticsearch

app = Flask(__name__)


@app.route("/")
def main():
	q = request.args.get("q")
	urlId = request.args.get("urlId")
	orgId = request.args.get("orgId")
		

	searchClient = Elasticsearch(
		["__Elastic_Search_Instance_URL__"],
		http_auth = (
			"__Elastic_Search_Instance_Username__",
			"__Elastic_Search_Instance_Password__"
		)
	)

	queryBody = {
		"query": {
			"bool": {
				"should": {
					"match": {
						"transcriptStr": {
							"query": q,
							"operator": "and"
						}
					},
				},
				"must": [
					{ "match": { "urlIdentifier": urlId } }
				]
			}
		},
		"_source": ["mediaTimestamp", "meetingDate", "segmentLength"],
		"highlight": {
			"fields" : {
				"transcriptStr": {
					"type": "plain",
					"fragment_size": 38,
					"number_of_fragments": 5
				}
			}
		},
		"size": 100,
		"min_score": 1.1
	}

	try:
		searchObj = searchClient.search(
			index = orgId,
			body = queryBody
		)
		outputStr = json.dumps(searchObj)
	except:
		outputStr = json.dumps( { "None": "None" } )

	return Response(outputStr, mimetype="application/json")


@app.errorhandler(500)
def server_error(e):
    logging.exception("An error occurred during a request.")
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == "__main__":
    app.run(host = "127.0.0.1", port = 8080, debug = True)
