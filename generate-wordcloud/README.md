## Container to Create a Word Cloud from a List of Words

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

This is a container that receives pubsub messages with `globalId` identifiers and then
kicks off a workflow to create a word cloud. The service pulls a word list from Google
Cloud Storage, removes stop words and generates a word cloud. The word cloud is saved to
Google Cloud Storage as a PNG image and the public URL for the image is written to the
`meetingRegistry` database.

### Assumptions

* You have created a Pubsub topic called `wordcloudQueue`
* You have created a Pubsub subscription called `wordcloud-creation-subscription`
* You have deployed a utility service to handle database lookups and updates

### Note

The file `stopwords-20180109-133115.json` contains a sample batch of stop words. You will
want to customize this file based on the frequency of common words and phrases used in
the meetings you are transcribing and analyzing.

### Build and Run this container

Build
`docker build -t generate-wordcloud:latest .`

Run
`docker run -it generate-wordcloud`