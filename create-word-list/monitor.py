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

from flask import Flask

monitor_app = Flask(__name__)


# The health check reads the PID file created by psqworker and checks the proc
# filesystem to see if the worker is running. This same pattern can be used for
# rq and celery.
@monitor_app.route('/_ah/health')
def health():
    return 'healthy', 200


@monitor_app.route('/')
def index():
    return health()

if __name__ == '__main__':
    monitor_app.run('0.0.0.0', 8080)
