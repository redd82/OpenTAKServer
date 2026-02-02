from flask import Blueprint, jsonify
from opentakserver.extensions import db
from opentakserver.models.DataPackage import DataPackage

data_package_marti_api = Blueprint('takat_data_package_marti_api', __name__)

# TAKAT API route overload for own implementation
@data_package_marti_api.route('/Marti/sync/search', methods=['GET'])
def data_package_search():
    data_packages = db.session.execute(db.select(DataPackage)).scalars()
    res = {'resultCount': 0, 'results': []}
    for dp in data_packages:
        # TAKAT Added filtering so no CONFIG datapackages are sent
        if dp.filename.endswith('_CONFIG.zip') or dp.filename.endswith('_CONFIG_iTAK.zip'):
            continue
        
        submission_user = "anonymous"
        if dp.user:
            submission_user = dp.user.username
        res['results'].append(
            {'UID': dp.hash, 'Name': dp.filename, 'Hash': dp.hash, 'CreatorUid': dp.creator_uid,
             "SubmissionDateTime": dp.submission_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'), "EXPIRATION": "-1",
             "Keywords": ["missionpackage"],
             "MIMEType": dp.mime_type, "Size": "{}".format(dp.size), "SubmissionUser": submission_user,
             "PrimaryKey": "{}".format(dp.id),
             "Tool": dp.tool if dp.tool else "public"
             })
        res['resultCount'] += 1

    return jsonify(res)