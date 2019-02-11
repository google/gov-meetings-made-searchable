FROM gcr.io/google_appengine/python

RUN apt-get --allow-unauthenticated -y update

RUN apt-get install curl

RUN apt-get -y install python-tk

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

RUN python -m nltk.downloader stopwords

ADD procfile /app/procfile
ADD . /app
CMD honcho start -f /app/procfile worker monitor
ENV https_proxy ""
ENV http_proxy ""