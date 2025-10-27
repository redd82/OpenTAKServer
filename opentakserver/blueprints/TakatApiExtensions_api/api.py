import bleach
import os
import datetime
import hashlib
import traceback
import threading
import time
import subprocess
from shutil import copyfile
import sqlalchemy.exc
from sqlalchemy import select, delete

from flask import current_app as app, request, Blueprint, jsonify
from flask_security import roles_required
from flask_security.decorators import auth_required
from flask_login import current_user

from opentakserver.blueprints.ots_api.api import search, paginate
from opentakserver.extensions import logger, db
from opentakserver.models.EUD import EUD
from opentakserver.models.user import User
from opentakserver.models.DataPackage import DataPackage
from opentakserver.models.Certificate import Certificate
from opentakserver.blueprints.TakatApiExtensions_api.certificate_authority import CertificateAuthority

api_blueprint = Blueprint('takat_api_blueprint', __name__)

def _restart_service(name: str, delay: float = 1.0) -> None:
    def _runner():
        time.sleep(delay)
        try:
            subprocess.run(["sudo", "systemctl", "restart", name], check=True)
            logger.info("Queued restart for %s", name)
        except Exception:
            logger.exception("Restart failed for %s", name)
    threading.Thread(target=_runner, daemon=True).start()

def _restart_self(delay: float = 1.0) -> None:
    def _runner():
        time.sleep(delay)
        logger.info("Self-terminating for restart")
        os._exit(1)
    threading.Thread(target=_runner, daemon=True).start()
    
# TAKAT additional endpoints
@api_blueprint.route("/api/system/restartots", methods=["GET"])
@roles_required("administrator")
def restart_service_opentak():
    _restart_self()
    return {"success": True, "message": "Restart of ots queued"}, 202

@api_blueprint.route("/api/system/restartcot", methods=["GET"])
@roles_required("administrator")
def restart_service_cot():
    _restart_service("cot_parser.service")
    return {"success": True, "message": "Restart of cot service queued"}, 202

@api_blueprint.route("/api/system/restarteud", methods=["GET"])
@roles_required("administrator")
def restart_service_eud():
    _restart_service("eud_handler_ssl.service")
    _restart_service("eud_handler.service")
    return {"success": True, "message": "Restart eud services queued"}, 202

@api_blueprint.route('/api/usereuds', methods=['POST'])
@auth_required()
def get_usereuds():
    # Handle case where request.json might be None
    username = None
    if request.json and 'username' in request.json:
        username = bleach.clean(request.json.get('username'))
    
    query = db.session.query(EUD)

    if username:
        query = query.join(User, User.id == EUD.user_id)
        query = query.filter(User.username == username)
    
    query = search(query, EUD, 'callsign')
    query = search(query, EUD, 'uid')
    query = search(query, User, 'username')
    return paginate(query)

# TAKAT API route overload for own implementation
@api_blueprint.route("/api/certificate", methods=['GET', 'POST'])
@auth_required()
def certificate():
    if request.method == 'POST' and 'username' in request.json.keys():
        try:
            username = bleach.clean(request.json.get('username'))
            truststore_filename = os.path.join(app.config.get("OTS_CA_FOLDER"), 'certs', "opentakserver",
                                               "truststore-root.p12")
            user_filename = os.path.join(app.config.get("OTS_CA_FOLDER"), 'certs', username,
                                         "{}.p12".format(username))

            user = app.security.datastore.find_user(username=username)

            if not user:
                return ({'success': False, 'error': 'Invalid username: {}'.format(username)}, 400,
                        {'Content-Type': 'application/json'})

            # Check if certificate directory already exists and clean it up
            cert_dir = os.path.join(app.config.get("OTS_CA_FOLDER"), 'certs', username)
            if os.path.exists(cert_dir):
                logger.warning(f"Certificate directory already exists for {username}: {cert_dir}")
                
                try:
                    # Clean up existing certificate directory
                    import shutil
                    shutil.rmtree(cert_dir)
                    logger.info(f"Removed existing certificate directory: {cert_dir}")
                    
                    # Also clean up any existing database records
                    existing_certs = db.session.execute(
                        select(Certificate).where(Certificate.username == username)
                    ).scalars().all()
                    
                    for cert in existing_certs:
                        if cert.data_package_id:
                            # Remove associated data package
                            data_pkg = db.session.get(DataPackage, cert.data_package_id)
                            if data_pkg:
                                db.session.delete(data_pkg)
                        db.session.delete(cert)
                    
                    db.session.commit()
                    logger.info(f"Cleaned up existing certificate records for {username}")
                    
                except Exception as e:
                    logger.error(f"Failed to clean up existing certificate for {username}: {e}")
                    db.session.rollback()
                    return ({'success': False, 'error': 'Failed to clean up existing certificate: {}'.format(str(e))}, 500,
                            {'Content-Type': 'application/json'})

            ca = CertificateAuthority(logger, app)
            filenames = ca.issue_certificate(username, False)
            file_hashes = []
            for filename in filenames:
                file_hash = hashlib.sha256(
                    open(os.path.join(app.config.get("OTS_CA_FOLDER"), 'certs', username, filename),
                         'rb').read()).hexdigest()

                # Check if DataPackage with this hash already exists
                existing_package = db.session.execute(
                    select(DataPackage).where(DataPackage.hash == file_hash)
                ).scalar_one_or_none()
                
                if existing_package:
                    logger.warning(f"DataPackage with hash {file_hash} already exists")
                    file_hashes.append(file_hash)
                    continue

                data_package = DataPackage()
                data_package.filename = filename
                data_package.keywords = "public"
                data_package.creator_uid = request.json.get('uid') if request.json and 'uid' in request.json else None
                data_package.submission_time = datetime.datetime.now(datetime.timezone.utc)
                data_package.mime_type = "application/x-zip-compressed"
                data_package.size = os.path.getsize(
                    os.path.join(app.config.get("OTS_CA_FOLDER"), 'certs', username, filename))
                data_package.hash = file_hash
                #data_package.submission_user = current_user.id
                data_package.submission_user = user.id

                try:
                    db.session.add(data_package)
                    db.session.commit()
                    logger.info(f"Successfully created DataPackage with hash: {file_hash}")
                except sqlalchemy.exc.IntegrityError as e:
                    db.session.rollback()
                    logger.error(f"IntegrityError creating DataPackage: {e}")
                    return ({'success': False, 'error': 'Certificate already exists for {}'.format(username)}, 400,
                            {'Content-Type': 'application/json'})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Unexpected error creating DataPackage: {e}")
                    logger.error(traceback.format_exc())
                    return ({'success': False, 'error': f'Database error: {str(e)}'}, 500,
                            {'Content-Type': 'application/json'})

                copyfile(os.path.join(app.config.get("OTS_CA_FOLDER"), 'certs', username, "{}".format(filename)),
                         os.path.join(app.config.get("UPLOAD_FOLDER"), "{}.zip".format(file_hash)))

                cert = Certificate()
                cert.common_name = username
                cert.username = username
                
                # Validate required configuration values with debugging
                ca_expiration_days = app.config.get("OTS_CA_EXPIRATION_TIME")
                logger.debug(f"OTS_CA_EXPIRATION_TIME raw value: {ca_expiration_days}")
                if ca_expiration_days is None:
                    logger.warning("OTS_CA_EXPIRATION_TIME not configured, using default 365 days")
                    ca_expiration_days = 365
                
                server_address = app.config.get("OTS_FQDN")
                logger.debug(f"OTS_FQDN raw value: '{server_address}' (type: {type(server_address)})")
                if not server_address or server_address.strip() == "":
                    logger.warning("OTS_FQDN not configured or empty, using localhost")
                    server_address = "localhost"
                
                server_port = app.config.get("OTS_SSL_STREAMING_PORT")
                logger.debug(f"OTS_SSL_STREAMING_PORT raw value: {server_port}")
                if server_port is None:
                    logger.warning("OTS_SSL_STREAMING_PORT not configured, using default 8089")
                    server_port = 8089
                
                cert_password = app.config.get("OTS_CA_PASSWORD")
                logger.debug(f"OTS_CA_PASSWORD raw value: '{cert_password}'")
                if not cert_password or cert_password.strip() == "":
                    logger.warning("OTS_CA_PASSWORD not configured or empty, using default")
                    cert_password = "atakatak"
                
                logger.info(f"Final values - server_address: '{server_address}', server_port: {server_port}, cert_password: '{cert_password}'")
                
                cert.expiration_date = datetime.datetime.today() + datetime.timedelta(days=ca_expiration_days)
                cert.server_address = str(server_address)  # Ensure it's a string
                cert.server_port = int(server_port)  # Ensure it's an integer  
                cert.truststore_filename = truststore_filename
                cert.user_cert_filename = user_filename
                cert.cert_password = str(cert_password)  # Ensure it's a string
                cert.data_package_id = data_package.id
                logger.info(f"Certificate object before save - server_address: '{cert.server_address}' (type: {type(cert.server_address)})")
                logger.info(f"Issuing certificate for user: {username}, user.id: {user.id}, serveraddress: {cert.server_address}")   # TAKAT ADAPTATION
                
                try:
                    db.session.add(cert)
                    db.session.commit()
                    logger.info(f"Successfully saved certificate for {username}")
                except sqlalchemy.exc.IntegrityError as e:
                    db.session.rollback()
                    logger.error(f"IntegrityError saving certificate: {e}")
                    logger.error(f"Certificate values at error: server_address='{cert.server_address}', server_port={cert.server_port}, cert_password='{cert.cert_password}'")
                    return ({'success': False, 'error': f'Database constraint error: {str(e)}'}, 500,
                            {'Content-Type': 'application/json'})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Unexpected error saving certificate: {e}")
                    logger.error(traceback.format_exc())
                    return ({'success': False, 'error': f'Failed to save certificate: {str(e)}'}, 500,
                            {'Content-Type': 'application/json'})
                file_hashes.append(file_hash)
                # TAKAT adaptation so its easier for TAKAT API to get hashes info
            return {'success': True, 'hash': file_hashes[0], 'hashItak': file_hashes[1]}, 200, {'Content-Type': 'application/json'}
        except BaseException as e:
            logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}, 500, {'Content-Type': 'application/json'}
    elif request.method == 'POST':
        return ({'success': False, 'error': "Please specify a callsign"}, 400,
                {'Content-Type': 'application/json'})
    elif request.method == 'GET':
        query = db.session.query(Certificate)
        query = search(query, Certificate, 'callsign')
        query = search(query, Certificate, 'username')

        return paginate(query)