## Container to Create a List of Words from Speech API Responses

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
kicks off a workflow to retrieve all associated Google Speech API responses from Google
Cloud Storage, parse these responses, and then output a file with a master list of words
(one word per line) to Google Cloud Storage. This master list will be used in the
development of a word cloud.

In the `results_files_to_string` function there is workflow to replace words or phrases
from the Speech API response with a different entry.

### Assumptions

* You have created a Pubsub topic called `wordlistQueue`
* You have created a Pubsub subscription called `word-list-creation-subscription`
* You have deployed a utility service to handle database lookups and updates

### Build and Run this container

Build
`docker build -t create-word-list:latest .`

Run
`docker run -it create-word-list`