## App Engine Front End Service

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

This is a Google App Engine app that provides a front end to the project. It uses the
Material Design for Bootstrap component library and surfaces backend data via several
endpoint (ep) API services.


### Assumptions

* You have created a Google Cloud SQL database called `prodDb`
* You have created a table in the `prodDb` database called `meetingRegistry`


### Test and Deploy this App

Test Locally
`dev_appserver.py app.yaml`

Deploy to App Engine
`gcloud app deploy --promote`