
from urllib.parse import urlparse, unquote

from OpenSSL import crypto
from flask import request, Blueprint, current_app as app, jsonify, send_from_directory

TakatVideo = Blueprint('clone_marti', __name__)

@TakatVideo.route('/Alive', methods=['POST'])
def Alive():
    return jsonify({'message': 'We are alive, ALIVE!'}), 200