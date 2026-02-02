from enum import Enum
from typing import Any, Dict, Optional, Union
from enum import Enum
from contextlib import contextmanager

from opentakserver.extensions import logger     #logger.debug

from blueprints.TakatPersistantVideo_api.models.MediaMTXPathConfig import MediaMTXPathConfig as MTXConfig
from blueprints.TakatPersistantVideo_api.MediaMTX_api import MediaMTX_api
from blueprints.TakatPersistantVideo_api.Tascomm_DB_api import Tasscom_DB_api as DBapi
from blueprints.TakatPersistantVideo_api.Takat_Logging import Takat_Logger
from blueprints.TakatPersistantVideo_api.Takat_Logging import Takat_Messages
from blueprints.TakatPersistantVideo_api.models.CameraObjectConfig import CameraObjectConfig as CamObjectConfig

class  CameraObject:
    
    def __init__(self,  debug: bool=False, log: bool=False, uid: Optional[str]= None):
        # below all selfs are from data model
        """
            camera_object_uid: str
            camera_object_jwt: str
            camera_object_user: str
                
            # the unique uid of the source and virtual camera as stored in the database
            source_cam_config_uid: str
            virtual_cam_config_uid: str
            
            # virtual cam settings for api access
            # this refers to where the mediamtx server that hosts this camera lives
            virtual_cam_fqdn: str
            virtual_cam_port: int
            virtual_cam_jwt: str
            virtual_cam_retries: int
            virtual_cam_verified_ssl: bool
                
            # source cam settings for api access
            # this refers to where the mediamtx server that hosts this camera lives
            source_cam_fqdn: str
            source_cam_port: int
            source_cam_jwt: str
            source_cam_retries: int
            source_cam_verified_ssl: bool
        """
        
        self._camera_object_uid = ""
        self._camera_object_jwt = ""
        self._camera_object_user = ""
        
        self._virtual_cam_config_uid = ""
        self._source_cam_config_uid = ""
        
        self._virtual_cam_fqdn = "127.0.0.1" 
        self._virtual_cam_port = 9997
        self._virtual_cam_jwt = "" 
        self._virtual_cam_retries = 3
        self._virtual_cam_verified_ssl = False
        
        self._source_cam_fqdn = "" 
        self._source_cam_port = 0
        self._source_cam_jwt = ""
        self._source_cam_retries = 0
        self._source_cam_verified_ssl = False
        
        # set basic camera object data and handelers
        self._caller = "CameraObject"     # name of the object needed for debug/logging
        self._logging = Takat_Logger()    # logger
        self._messages = Takat_Messages() # system to create standard messages.
        self._DB= DBapi(retries=3, log=log, debug=debug)
        
        # setup a connection to the mediamtx server
        self._MTX = MediaMTX_api(fqdn=self._virtual_cam_fqdn,
                                 port=self._virtual_cam_port,
                                 retries=self._virtual_cam_retries,
                                 verified_ssl=self._virtual_cam_verified_ssl,
                                 Jwt=self._virtual_cam_jwt)
        # logging flags
        self._debug = debug     # not from data model
        self._log = log         # not from data model
        
        # objects to eventually store all the settings in
        self._virtual_cam_config = MTXConfig() # create a defaulted config
        self._source_cam_config = MTXConfig()  # create a defaulted config
        
        
        # okay, if we recieved a uid we are going to attempt loading values from the database and setup the mediamtx servers..
        # note that this can go Catawompus!
            
        if uid is not None:
            try:
                # Step 1: Load from DB
                load_response = self.Load_From_DB(uid=uid)
                if load_response.get("status") != 200:
                    if self._log: self._logging.Error(caller=self._caller, 
                                                      message=f"CameraObject.__init__: failed to load from DB: {load_response}")
                    # fallback to safe defaults is already in place
                else:
                    if self._log:
                        self._logging.Info(caller=self._caller, log=self._log,
                                            message=f"CameraObject {uid} loaded from DB successfully.")
                    
                    # Step 2: Sync MediaMTX paths
                    sync_response = self.Sync_MediaMTX()
                    if sync_response.get("status") != 200:
                        if self._log:
                            self._logging.Error(caller=self._caller,
                                                message=f"CameraObject.__init__: failed to sync MediaMTX: {sync_response}")
                    
                    # fallback to safe defaults already in place
                    else:
                        if self._log:
                            self._logging.Info(
                                caller=self._caller,
                                log=self._log,
                                message=f"CameraObject {uid} synced with MediaMTX successfully.")

            except Exception as e:
                # catch any unexpected runtime errors
                if self._log:
                    self._logging.Error(caller=self._caller, 
                                        message=f"CameraObject.__init__: unexpected error during setup: {str(e)}")
                if self._debug:
                    self._logging.Debug(caller=self._caller,
                                        message=f"CameraObject.__init__: traceback for {uid}: {str(e)}")        
        
    # property Getters
    @property
    def camera_object_uid(self) -> str:
        return self._camera_object_uid
    
    @property
    def Stream(self):
        #return the full stream path for the virtual camera config "source" attribute
        return self._virtual_cam_config.source
    
    @property
    def VirtualCamUID(self) -> str:
        return self._virtual_cam_config_uid
    @property
    def SourceCamUID(self) -> str:
        return self._source_cam_config_uid
    @property
    def CameraObjectUID(self) -> str:
        return self._camera_object_uid
    
    @property
    def CameraObjectJWT(self, masked: bool=True) -> str:
        # return the jwt; by default we mask it as a security prevention
        if masked: return self._logging.Mask_For_Logging(token=self._camera_object_jwt)
        else: return self._camera_object_jwt
    
    # ─────────────────────────────────────────────────────────────────────────────
    # InternalFunctions
    # ─────────────────────────────────────────────────────────────────────────────
    def _unique_uid(self) -> bool:
        """
        Check if this camera object's UID is unique in the database.
        
        Returns:
            bool: True if unique, False if it exists or if an error occurs.
        """
        try:
            # call the database method
            exists = self._DB.DoesUIDExist(self.camera_object_uid)
            return not exists # if it exists, then it's NOT unique, so return the inverse 
        except Exception as e:
            # log the error, but fail safely
            if self._log:
                self._logging.Error(caller=self._caller,
                                    message=f"_AreWeUnique: Error checking UID {self.camera_object_uid}: {str(e)}")
            if self._debug:
                self._logging.Debug(caller=self._caller,
                                    message=f"_AreWeUnique: Debug info - UID {self.camera_object_uid}, exception: {str(e)}")
            return False  # safe default if an error occurs
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Main Functions
    # ─────────────────────────────────────────────────────────────────────────────

    def Load_From_DB(self, uid):
        try:
            #TODO add magic to retrieve object from database and set defaults
            data = CamObjectConfig()
            # get the data from the database.
            #TODO we grab the entire video object, the camera object is a part of it so we have to dig it out
            data = data.from_dict(self._DB.GetVideoObject(uid=uid))
            
            # grab the data from the returned output
            # and set self._  values for the data model
            #TODO
            """
            self._camera_object_uid = data.get("")
            self._camera_object_jwt = ""
            self._camera_object_user = ""
            
            self._virtual_cam_config_uid = ""
            self._source_cam_config_uid = ""
            
            self._virtual_cam_fqdn = "127.0.0.1" 
            self._virtual_cam_port = 9997
            self._virtual_cam_jwt = "" 
            self._virtual_cam_retries = 3
            self._virtual_cam_verified_ssl = False
            
            self._source_cam_fqdn = "" 
            self._source_cam_port = 0
            self._source_cam_jwt = ""
            self._source_cam_retries = 0
            self._source_cam_verified_ssl = False
            """
            
            # we set it up properly so... we are done!!
            return self._messages.SuccessMessage(caller=self._caller, status=200, endpoint="", 
                                                 msg=f"camera object {uid} succefully created", 
                                                 log=self._log, uid=uid)
        except Exception as e:
            return self._messages.ErrorMessage(status = 500, endpoint="", 
                                               event="Load_From_DB", error=str(e), log=self._log,uid=str(uid), 
                                               caller=self._caller)
    def Sync_MediaMTX(self):
        # try and force the media mtx settings for the source and the virtual camera to be the same as the ones in memory.
        
        try:          
            # Virtual Camera
            exists = self._MTX.PathExists(self._virtual_cam_config_uid)
            if exists:  # patch path
                # call patch path
                self._MTX.PatchPath(uid=self._virtual_cam_config_uid, updates=self._virtual_cam_config.to_mediamtx_dict())
                # make some logs
                if self._log: self._logging.Info(caller=self._caller, log=self._log, message=f"Patched Path {self._virtual_cam_config_uid} on server {self._virtual_cam_fqdn}")
                if self._debug: self._logging.Debug(caller=self._caller, log=self._log, message=f"Patched Path {self._virtual_cam_config_uid} on server {self._virtual_cam_fqdn}") 
            else: # doesn't exit, create path
                self._MTX.CreatePath(uid=self._virtual_cam_config_uid, config=self._virtual_cam_config.to_mediamtx_dict())
                # make some more logs
                if self._log: self._logging.Info(caller=self._caller, log=self._log, message=f"Created Path {self._virtual_cam_config_uid} on server {self._virtual_cam_fqdn}")
                if self._debug: self._logging.Debug(caller=self._caller, log=self._log, message=f"Created Path {self._virtual_cam_config_uid} on server {self._virtual_cam_fqdn}") 
                    
            # Source Camera
            # does the path exists on the mediamtx server?
            exists = self._MTX.PathExists(fqdn=self._source_cam_fqdn, port=self._source_cam_port,
                                            retries=self._source_cam_retries, verified_ssl=self._source_cam_verified_ssl,
                                            Jwt=self._source_cam_jwt, log=self._log, uid=self._source_cam_config_uid)
            if exists: # patch the source cam path
                self._MTX.PatchPath(uid=self._source_cam_config_uid, updates=self._source_cam_config.to_mediamtx_dict())
                if self._log: self._logging.Info(caller=self._caller, log=self._log, message=f"Patched Path {self._source_cam_config_uid} on server {self._source_cam_fqdn}")
                if self._debug: self._logging.Debug(caller=self._caller, log=self._log, message=f"Patched Path {self._source_cam_config_uid} on server {self._source_cam_fqdn}")
            else: # create the source cam path
                self._MTX.CreatePath(uid=self._source_cam_config_uid, config=self._source_cam_config.to_mediamtx_dict())
                if self._log: self._logging.Info(caller=self._caller, log=self._log, message=f"Created Path {self._source_cam_config_uid} on server {self._source_cam_fqdn}")
                if self._debug: self._logging.Debug(caller=self._caller, log=self._log, message=f"Created Path {self._source_cam_config_uid} on server {self._source_cam_fqdn}")
                                        
            # we have sybced the camera object!!
            return self._messages.SuccessMessage(caller=self._caller, status=200, endpoint="", 
                                                 msg=f"CameraObject.Sync_MediaMTX: {self._camera_object_uid} has been successfully synced", 
                                                 log=self._log, uid=self._camera_object_uid )

        except Exception as e:
            # okay, something went Katawompus :(
            if self._log:
                self._logging.Error(caller=self._caller, message=f"CameraObject.Sync_MediaMTX: whilest attepting to sync camera object {self._camera_object_uid}, an unexpected error occured: {str(e)}")          
            if self._debug:
                self._logging.Debug(caller=self._caller, message=f"CameraObject.Sync_MediaMTX: whilest attepting to sync camera object {self._camera_object_uid}, virtual camera {self._virtual_cam_config_uid}, source camera {self._source_cam_config_uid}, an unexpected error occured: {str(e)}")    
        
            return self._messages.ErrorMessage(status = 500, endpoint="", 
                                               event="Sync_MediaMTX", error=str(e), log=self._log,uid=str(self._camera_object_uid), 
                                               caller=self._caller)