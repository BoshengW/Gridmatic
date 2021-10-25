from flask import Blueprint

BP_fetch = Blueprint('BP_fetch', __name__)

from . import fetching