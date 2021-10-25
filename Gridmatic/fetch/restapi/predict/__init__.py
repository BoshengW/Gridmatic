from flask import Blueprint

BP_predict = Blueprint('BP_predict', __name__)

from . import predict