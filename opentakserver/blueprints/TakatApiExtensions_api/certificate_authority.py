import io
import os
import random
import re
import subprocess
import traceback
import uuid
import zipfile
from pathlib import Path
from shutil import copyfile, rmtree
from urllib.parse import urlparse

from flask import request
from jinja2 import Template
from opentakserver.certificate_authority import CertificateAuthority as BaseCertificateAuthority


class CertificateAuthority(BaseCertificateAuthority):
    """Extended Certificate Authority with custom generate_zip method for TakatApiExtensions"""
    
    def generate_zip(self, common_name):
        truststore = os.path.join(self.app.config.get("OTS_CA_FOLDER"), 'truststore-root.p12')
        user_p12 = os.path.join(self.app.config.get("OTS_CA_FOLDER"), "certs", common_name,
                                "{}.p12".format(common_name))
        user_file_path = os.path.join(self.app.config.get("OTS_CA_FOLDER"), "certs", common_name)
        random_id = uuid.uuid4()
        new_uid = uuid.uuid4()
        parent_folder = "80b828699e074a239066d454a76284eb"
        folder = "5c2bfcae3d98c9f4d262172df99ebac5"

        pref_file_template = Template("""<?xml version='1.0' standalone='yes'?>
                <preferences>
                    <preference version="1" name="cot_streams">
                        <entry key="count" class="class java.lang.Integer">1</entry>
                        <entry key="description0" class="class java.lang.String">OpenTAKServer_{{ server }}</entry>
                        <entry key="enabled0" class="class java.lang.Boolean">true</entry>
                        <entry key="connectString0" class="class java.lang.String">{{ server }}:{{ ssl_port }}:ssl</entry>
                    </preference>
                    <preference version="1" name="com.atakmap.app_preferences">
                        <entry key="deviceProfileEnableOnConnect" class="class java.lang.Boolean">true</entry>
                        <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
                        <entry key="caLocation" class="class java.lang.String">/storage/emulated/0/atak/cert/{{ server_filename }}</entry>
                        <entry key="caPassword" class="class java.lang.String">{{ cert_password }}</entry>
                        <entry key="clientPassword" class="class java.lang.String">{{ cert_password }}</entry>
                        <entry key="certificateLocation" class="class java.lang.String">/storage/emulated/0/atak/cert/{{ user_filename }}</entry>
                        <entry key="appMgmtEnableUpdateServer" class="class java.lang.Boolean">true</entry>
                        <entry key="atakUpdateServerUrl" class="class java.lang.String">https://{{ server }}:{{ marti_port }}/api/packages</entry>
                        <entry key="repoStartupSync" class="class java.lang.Boolean">true</entry>
                        <entry key="updateServerCaLocation" class="class java.lang.String">/storage/emulated/0/atak/cert/{{ server_filename }}</entry>
                        <entry key="updateServerCaPassword" class="class java.lang.String">{{ cert_password }}</entry>
                    </preference>
                </preferences>
                """)

        manifest_file_template = Template("""<MissionPackageManifest version="2">
                   <Configuration>
                      <Parameter name="uid" value="{{ uid }}"/>
                      <Parameter name="name" value="OpenTAKServer_{{ server }}"/>
                      <Parameter name="onReceiveDelete" value="true"/>
                   </Configuration>
                   <Contents>
                      <Content ignore="false" zipEntry="{{ folder }}/preference.pref"/>
                      <Content ignore="false" zipEntry="{{ folder }}/{{ server_filename }}"/>
                      <Content ignore="false" zipEntry="{{ folder }}/{{ user_filename }}"/>	  
                   </Contents>
                </MissionPackageManifest>
                """)

        manifest_file_parent_template = Template("""<MissionPackageManifest version="2">
                       <Configuration>
                          <Parameter name="uid" value="{{ uid }}"/>
                          <Parameter name="name" value="OpenTAKServer_{{ server }}_CONFIG"/>
                       </Configuration>
                       <Contents>
                          <Content ignore="false" zipEntry="{{ folder }}/{{ internal_dp_name }}.zip"/>
                       </Contents>
                    </MissionPackageManifest>
                    """)

        pref = pref_file_template.render(server=self.app.config.get("OTS_FQDN"),
                                         marti_port=self.app.config.get('OTS_MARTI_HTTPS_PORT'),
                                         server_filename="truststore-root.p12",
                                         user_filename=f"{common_name}.p12",
                                         cert_password=self.app.config.get("OTS_CA_PASSWORD"),
                                         ssl_port=self.app.config.get("OTS_SSL_STREAMING_PORT"))
        man = manifest_file_template.render(uid=random_id, server=self.app.config.get("OTS_FQDN"),
                                            server_filename="truststore-root.p12",
                                            user_filename=f"{common_name}.p12", folder=folder)
        man_parent = manifest_file_parent_template.render(uid=new_uid, server=self.app.config.get("OTS_FQDN"),
                                                          folder=parent_folder,
                                                          internal_dp_name=common_name)

        if not os.path.exists(os.path.join(user_file_path, folder)):
            os.makedirs(os.path.join(user_file_path, folder))

        if not os.path.exists(os.path.join(user_file_path, 'MANIFEST')):
            os.makedirs(os.path.join(user_file_path, 'MANIFEST'))

        with open(os.path.join(user_file_path, folder, 'preference.pref'), 'w') as pref_file:
            pref_file.write(pref)

        with open(os.path.join(user_file_path, 'MANIFEST', 'manifest.xml'), 'w') as manifest_file:
            manifest_file.write(man)

        self.logger.debug("Generating inner Data Package: {}.zip".format(common_name))

        copyfile(truststore, os.path.join(user_file_path, folder, "truststore-root.p12"))
        self.logger.debug("Copying {} to {}".format(truststore, os.path.join(user_file_path, folder,
                                                                             "truststore-root.p12")))
        copyfile(user_p12, os.path.join(user_file_path, folder, "{}.p12".format(common_name)))
        zipf = zipfile.ZipFile(os.path.join(user_file_path, "{}.zip".format(common_name)), 'w', zipfile.ZIP_DEFLATED)

        os.chdir(os.path.join(user_file_path))

        for root, dirs, files in os.walk(folder):
            for file in files:
                zipf.write(os.path.join(root, file))
        for root, dirs, files in os.walk('MANIFEST'):
            for file in files:
                self.logger.debug("adding {} to zip".format(os.path.join(root, file)))
                zipf.write(os.path.join(root, file))
        zipf.close()

        rmtree(os.path.join(user_file_path, "MANIFEST"))
        rmtree(os.path.join(user_file_path, folder))

        # Create outer DP...because WinTAK
        if not os.path.exists(os.path.join(user_file_path, parent_folder)):
            os.makedirs(os.path.join(user_file_path, parent_folder))
        if not os.path.exists(os.path.join(user_file_path, "MANIFEST")):
            os.makedirs(os.path.join(user_file_path, "MANIFEST"))
        with open(os.path.join(user_file_path, "MANIFEST", 'manifest.xml'), 'w') as manifest_parent:
            manifest_parent.write(man_parent)

        self.logger.info("Generating Main Data Package: {}_CONFIG.zip".format(common_name))
        copyfile(os.path.join(user_file_path, "{}.zip".format(common_name)), os.path.join(user_file_path, parent_folder,
                                                                                          "{}.zip".format(common_name)))
        zipp = zipfile.ZipFile(os.path.join(user_file_path, "{}_CONFIG.zip".format(common_name)), 'w',
                               zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(parent_folder):
            for file in files:
                zipp.write(os.path.join(root, file))
        for root, dirs, files in os.walk('MANIFEST'):
            for file in files:
                zipp.write(os.path.join(root, file))
        zipp.close()

        # Generate iTAK zip
        itak_preferences = Template("""<?xml version='1.0' standalone='yes'?>
<preferences>
  <preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">OpenTAKServer_{{ server }}</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">{{ server }}:{{ ssl_port }}:ssl</entry>
  </preference>
  <preference version="1" name="com.atakmap.app_preferences">
    <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
    <entry key="caLocation" class="class java.lang.String">cert/truststore-root.p12</entry>
    <entry key="caPassword" class="class java.lang.String">{{ cert_password }}</entry>
    <entry key="clientPassword" class="class java.lang.String">{{ cert_password }}</entry>
    <entry key="certificateLocation" class="class java.lang.String">cert/{{ common_name }}.p12</entry>
  </preference>
</preferences>

""")

        f = open(os.path.join(user_file_path, "config.pref"), 'w')
        f.write(itak_preferences.render(server=self.app.config.get("OTS_FQDN"),
                                        ssl_port=self.app.config.get("OTS_SSL_STREAMING_PORT"),
                                        cert_password=self.app.config.get("OTS_CA_PASSWORD"),
                                        common_name=common_name))
        f.close()

        self.logger.info("Generating {}_CONFIG_iTAK.zip...".format(common_name))
        itak_zip = zipfile.ZipFile(os.path.join(user_file_path, "{}_CONFIG_iTAK.zip".format(common_name)), 'w',
                                   zipfile.ZIP_DEFLATED)
        itak_zip.write(os.path.join(user_file_path, "config.pref"), "config.pref")
        itak_zip.write(os.path.join(user_file_path, common_name + ".p12"), common_name + ".p12")
        itak_zip.write(os.path.join(self.app.config.get("OTS_CA_FOLDER"), "truststore-root.p12"), "truststore-root.p12")
        itak_zip.close()

        rmtree(os.path.join(user_file_path, "MANIFEST"))
        rmtree(os.path.join(user_file_path, parent_folder))
        os.remove(os.path.join(user_file_path, "{}.zip".format(common_name)))
        os.remove(os.path.join(user_file_path, "config.pref".format(common_name)))

        return ["{}_CONFIG.zip".format(common_name), "{}_CONFIG_iTAK.zip".format(common_name)]
