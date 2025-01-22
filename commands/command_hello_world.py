import adsk.core
from ..lib import fusion_utils as futil
import traceback

CMD_NAME = 'Hello World'
CMD_ID = f'{futil.ADDIN_NAME} {CMD_NAME}'
CMD_Description = 'Display a greeting for testing purposes.'
ICON_FOLDER = futil.resource_path('', '')
local_handlers = []

WORKSPACE_PANEL_IDS = [
    (futil.DESIGN_WORKSPACE_ID, futil.DESIGN_TEMPLATE_PANEL_ID),
    (futil.CAM_WORKSPACE_ID, futil.CAM_TEMPLATE_PANEL_ID),
]
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
    futil.add_handler(cmd.execute, onCommandExecute, local_handlers=local_handlers)

def onCommandExecute(args):
    ui = futil.Fusion().getUI()
    msg_box = ui.messageBox(
        f"""Hello World!""",
        "Hello",
        adsk.core.MessageBoxButtonTypes.OKButtonType,
    )