# coding: utf-8
from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import auth, admin_api, user_api, exam_api, questiion_api
