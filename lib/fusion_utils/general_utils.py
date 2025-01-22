#  Copyright 2022 by Autodesk, Inc.
#  Permission to use, copy, modify, and distribute this software in object code form
#  for any purpose and without fee is hereby granted, provided that the above copyright
#  notice appears in all copies and that both that copyright notice and the limited
#  warranty and restricted rights notice below appear in all supporting documentation.
#
#  AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY
#  DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.
#  AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
#  UNINTERRUPTED OR ERROR FREE.

import os
from re import TEMPLATE
import traceback
import os
import adsk.cam
import adsk.fusion
import adsk.core
import json


app = adsk.core.Application.get()
ui = app.userInterface

ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = 'Phil Squared'

# Workspace IDs
CAM_WORKSPACE_ID = 'CAMEnvironment'
DESIGN_WORKSPACE_ID = 'FusionSolidEnvironment'

# Panel IDs
DESIGN_TEMPLATE_PANEL_ID = f'Design_{ADDIN_NAME}_panel'
CAM_TEMPLATE_PANEL_ID = f'CAM_{ADDIN_NAME}_panel'

# Tab IDs
DESIGN_TEMPLATE_TAB_ID = f'Design_{ADDIN_NAME}_tab'
CAM_TEMPLATE_TAB_ID = f'CAM_{ADDIN_NAME}_tab'

# Panel Names
TEMPLATE_PANEL_NAME = ADDIN_NAME

# Directory paths
def ancestor_dir(path, n):
    for i in range(n):
        path = os.path.dirname(path)
    return path

def addin_root_rpath(*rpath) -> str:
    root = ancestor_dir(__file__, 3)
    return os.path.join(root, *rpath)

def resource_path(*rpath) -> str:
    return addin_root_rpath("resources", *rpath)

def load_json(path: str):
    if not os.path.exists(path):
        raise Exception(f"File not found: {path}")
    with open(path) as file:
        return json.load(file)

def save_json(path : str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        json.dump(data, file, indent=2)

def load_config() -> dict:
    path = addin_root_rpath("config.json")
    if os.path.exists(path):
        config = load_json(path)
    return config

CURRENT_CONFIG = load_config()

# Fusion specific utilities
class Fusion:
    def __init__(self, doc = None):
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface

        # doc is not available during fusion startup
        # so we initialize it lazy
        self._doc = doc
        self._cam = None
        self._design = None


    def getCAM(self) -> adsk.cam.CAM:
        if self._doc is None:
            self._doc = self.app.activeDocument
        products = self._doc.products
        if self._cam is None:
            if not self.is_CAM_available():
                self.activateCAM()
            self._cam : adsk.cam.CAM = adsk.cam.CAM.cast(
                products.itemByProductType("CAMProductType")
            )
        return self._cam
    
    def activateCAM(self):
        ui = self.getUI()
        camWS = ui.workspaces.itemById('CAMEnvironment') 
        camWS.activate()

    def is_CAM_available(self):
        if self._doc is None:
            self._doc = self.app.activeDocument
        products = self._doc.products
        prod = products.itemByProductType("CAMProductType")
        return prod is not None


    def getDesign(self) -> adsk.fusion.Design:
        if self._doc is None:
            self._doc = self.app.activeDocument
        products = self._doc.products
        if self._design is None:
            self._design = adsk.fusion.Design.cast(
                products.itemByProductType("DesignProductType")
            )
        return self._design
    
    def getUI(self) -> adsk.core.UserInterface:
        return self.ui

    def getApplication(self) -> adsk.core.Application:
        return self.app
    
# Parameter utilities
    
def get_parameter(obj, name : str):
    assert isinstance(name, str)
    p = obj.parameters.itemByName(name)
    if p is None:
        names = [p.name for p in obj.parameters]
        names.sort()
        msg = f"""
        Parameter not found.
        name = {name}
        available parameters:
        {names}
        """
        raise Exception(msg)
    assert isinstance(p, adsk.cam.CAMParameter)
    return p

def set_parameter(obj, key, value):
    p = None
    try:
        p = get_parameter(obj, key)
    except Exception as e:
        raise Exception(f"Could not get parameter {key}: {e}")
    if isinstance(value, dict):
        subtypekey = value["subtypekey"]
        if subtypekey == "Expression":
            expression = value["expression"]
            try:
                p.expression = expression
            except Exception as error:
                msg = f"""
                Could not set parameter expression:
                {key =}
                {expression = }
                {error = }
                """
                raise Exception(msg)
        else:
            raise Exception(f"Unexpected subtypekey: {subtypekey}")
    else:
        try:
            p.value.value = value
        except Exception as error:
            msg = f"""
            Could not set parameter value:
            {key =}
            {value = }
            {error = }
            """
            raise Exception(msg)
    return p


DEBUG = True

def log(message: str, level: adsk.core.LogLevels = adsk.core.LogLevels.InfoLogLevel, force_console: bool = False):
    """Utility function to easily handle logging in your app.

    Arguments:
    message -- The message to log.
    level -- The logging severity level.
    force_console -- Forces the message to be written to the Text Command window. 
    """    
    # Always print to console, only seen through IDE.
    print(message)  

    # Log all errors to Fusion log file.
    if level == adsk.core.LogLevels.ErrorLogLevel:
        log_type = adsk.core.LogTypes.FileLogType
        app.log(message, level, log_type)

    # If config.DEBUG is True write all log messages to the console.
    if DEBUG or force_console:
        log_type = adsk.core.LogTypes.ConsoleLogType
        app.log(message, level, log_type)


def handle_error(name: str, show_message_box: bool = False):
    """Utility function to simplify error handling.

    Arguments:
    name -- A name used to label the error.
    show_message_box -- Indicates if the error should be shown in the message box.
                        If False, it will only be shown in the Text Command window
                        and logged to the log file.                        
    """    

    log('===== Error =====', adsk.core.LogLevels.ErrorLogLevel)
    log(f'{name}\n{traceback.format_exc()}', adsk.core.LogLevels.ErrorLogLevel)

    # If desired you could show an error as a message box.
    if show_message_box:
        ui.messageBox(f'{name}\n{traceback.format_exc()}')
