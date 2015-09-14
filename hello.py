#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
from flask import Flask

from application.apis import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)

@app.route('/')
def hello():
    return 'Hello World!'
