##Container to Transcode Video to Audio

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
kicks off a workflow to lookup the video associated with that identifier, download the
corresponding video from Google Cloud Storage, transcode that video to audio in a FLAC
format, then upload the audio segments to Google Cloud Storage.


### Assumptions

* You have created a Pubsub topic called `transcodeQueue`
* You have created a Pubsub subscription called `media-transcode-subscription`
* You have deployed a utility service to handle database lookups and updates

### Build and Run this container

Build
`docker build -t transcode-video-to-audio:latest .`

Run
`docker run -it transcode-video-to-audio`