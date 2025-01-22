from tkinter import LAST
import adsk.core
from ..lib import fusion_utils as futil
import traceback

CMD_NAME = 'NC Program Rename'
CMD_ID = f'{futil.ADDIN_NAME} {CMD_NAME}'
CMD_Description = 'Auto rename all NC programs'
ICON_FOLDER = futil.resource_path('', '')
local_handlers = []
ui = futil.Fusion().getUI()

WORKSPACE_PANEL_IDS = [
    (futil.DESIGN_WORKSPACE_ID, futil.DESIGN_TEMPLATE_PANEL_ID),
    (futil.CAM_WORKSPACE_ID, futil.CAM_TEMPLATE_PANEL_ID),
]
LAST_COMMAND = ''

def start():
    ui = None
    try:
        fusion = futil.Fusion()
        ui = fusion.getUI()
        
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER
        )
        for (WORKSPACE_ID, PANEL_ID) in WORKSPACE_PANEL_IDS:
            workspace = ui.workspaces.itemById(WORKSPACE_ID)
            panel = workspace.toolbarPanels.itemById(PANEL_ID)

            control = panel.controls.addCommand(cmd_def)
            control.isPromoted = False
        futil.add_handler(ui.commandStarting, command_starting, local_handlers=local_handlers)
        futil.add_handler(cmd_def.commandCreated, onCommandCreated, local_handlers=local_handlers)
    except:
        futil.log(traceback.format_exc())
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop():
    ui = None
    try:
        ui = futil.Fusion().getUI()
        cmdDef = ui.commandDefinitions.itemById(CMD_ID)
        if cmdDef:
            cmdDef.deleteMe()

        for (WORKSPACE_ID, PANEL_ID) in WORKSPACE_PANEL_IDS:
            workspace = ui.workspaces.itemById(WORKSPACE_ID)
            panel = workspace.toolbarPanels.itemById(PANEL_ID)
            command_control = panel.controls.itemById(CMD_ID)
            if command_control:
                command_control.deleteMe()
    except:
        futil.log(traceback.format_exc())
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def onCommandCreated(args):
    eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
    cmd = eventArgs.command
    inputs = cmd.commandInputs

def onCommandExecute(args):
    ui = futil.Fusion().getUI()
    # rename_nc_programs(


# simple way to detect the last command that was run.
#  TODO: Refine this in cases for posting or editing NC programs 
def command_starting(args: adsk.core.ApplicationCommandEventArgs):
    global LAST_COMMAND
    command_definition = args.commandDefinition
    
    if command_definition.id == "IronNcProgram":
        LAST_COMMAND = command_definition.id
        
        
    if command_definition.id == "SelectCommand" and LAST_COMMAND == "IronNcProgram":
        rename_nc_programs() 
     
def rename_nc_programs():
    fusion = futil.Fusion()
    cam = fusion.getCAM()
    
    nc_programs = cam.ncPrograms
    for i in range(nc_programs.count):
        program = nc_programs.item(i)
        filename = program.parameters.itemByName("nc_program_filename").value.value
        program.name = filename
        
        