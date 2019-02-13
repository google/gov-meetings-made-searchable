## App Engine Utility Service

This is not an officially supported Google product, though support will be provided on a best-effort basis.

Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


### Introduction

This is a Google App Engine app that facilitates interaction with the Google Cloud SQL
database, and provides common utilities for back end services.


### Assumptions

* You have created a Google Cloud SQL database called `prodDb`
* You have created a table in the `prodDb` database called `meetingRegistry`
* You have installed the third-party Python libraries in the `lib` directory `pip install -t lib -r requirements.txt`


### Test and Deploy this App

Test Locally
`dev_appserver.py app.yaml`

Deploy to App Engine
`gcloud app deploy --promote`


### Note on Security
As implemented, these services and API end points are not secure. Anyone with the right
URL and paths code read and write to the system. Before deploying this app into
production, you will want to implement a custom security schema or standard authentication
protocol (Basic API Authentication w/ TLS, OAuth2, etc).s