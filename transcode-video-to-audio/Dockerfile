# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


FROM gcr.io/google_appengine/python
FROM gcr.io/google_appengine/python
RUN echo "deb http://www.deb-multimedia.org jessie main non-free" >> /etc/apt/sources.list
RUN echo "deb-src http://www.deb-multimedia.org jessie main non-free" >> /etc/apt/sources.list
RUN apt-get --allow-unauthenticated -y update
RUN apt-get --allow-unauthenticated -y install deb-multimedia-keyring
RUN apt-get --allow-unauthenticated -y update
RUN apt-get --allow-unauthenticated -y install libav-tools ffmpeg nmap vim 

RUN apt-get install curl

RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdir -p /usr/local/gcloud
RUN tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz
RUN /usr/local/gcloud/google-cloud-sdk/install.sh
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

ADD smaday-speech-api-bc2c81143be8.json /app/smaday-speech-api-bc2c81143be8.json
RUN gcloud auth activate-service-account --key-file=smaday-speech-api-bc2c81143be8.json
ENV GOOGLE_APPLICATION_CREDENTIALS /app/smaday-speech-api-bc2c81143be8.json

RUN virtualenv /env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD procfile /app/procfile
ADD . /app
CMD honcho start -f /app/procfile worker monitor
ENV https_proxy ""
ENV http_proxy ""
