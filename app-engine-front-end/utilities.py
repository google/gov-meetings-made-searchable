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
import MySQLdb

MySQLdb.escape_string("'")


def dbExecution(sqlCmd, sqlData):

	sqlInstance = "__Cloud_SQL_Instance_Connection_Name__"

	if os.getenv("SERVER_SOFTWARE", "").startswith("Google App Engine/"):
		connection = MySQLdb.connect(	unix_socket = "/cloudsql/" + sqlInstance,
										user = "__Cloud_SQL_Username__",
										passwd = "__Cloud_SQL_User_Password__",
										db = "prodDb")
	else:
		connection = MySQLdb.connect(	host = "__Cloud_SQL_Public_IP_Address__",
										user = "__Cloud_SQL_Username__",
										passwd = "__Cloud_SQL_User_Password__",
										db = "prodDb")
	cursor = connection.cursor()

	if len(sqlData) > 0:
		try:
			cmdExecution = cursor.execute(sqlCmd, *[sqlData])
		except:
			cmdExecution = cursor.execute(sqlCmd, [sqlData])
	else:
		cmdExecution = cursor.execute(sqlCmd)

	connection.commit()
	numResults = cursor.rowcount
	resultRows = cursor.fetchall()
	cursor.close()
	connection.close()
	resultList = [cmdExecution, numResults, resultRows]

	return resultList


def main():
	print "Content-type: text/plain; charset=UTF-8\n\n"
	print "Nothing To See Here"


if __name__ == "__main__":
	main()
