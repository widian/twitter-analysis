#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
from flask import Flask

from application.apis import api_bp
from application.page import page_bp

app = Flask(__name__, static_url_path='/')
app.register_blueprint(api_bp)
app.register_blueprint(page_bp)
