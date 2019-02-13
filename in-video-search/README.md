## App Engine Flex Service for "In" Video Search 

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

This is a Google App Engine Flex app that provides a wrapper and proxy for requests
to and responses from an Elastic Search instance. This service handles searches for
materials in a particular meeting. Meetings are identified with a `urlId` parameter.


### Assumptions

* You have deployed an Elastic Search instance
* You have deployed the `app-engine-front-end` service (`ep-searchVideo.py`)


### Deploy this App

Deploy to App Engine
`gcloud app deploy app.yaml`