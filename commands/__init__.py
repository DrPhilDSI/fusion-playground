# Commands added to the add-in. Import, start and stop them here.

from ..lib import fusion_utils as futil

# Fusion will automatically call the start() and stop() functions for each of these commands

commands = []
config = futil.load_config()

if config["enable_command_hello_world"]:
    from . import command_hello_world
    commands.append(command_hello_world)

def create_ui_panels():
    ui = futil.Fusion().getUI()
    designWS = ui.workspaces.itemById(futil.DESIGN_WORKSPACE_ID)
    toolbar_tab = designWS.toolbarTabs.add(futil.DESIGN_TEMPLATE_TAB_ID, futil.TEMPLATE_PANEL_NAME)
    toolbar_tab.toolbarPanels.add(futil.DESIGN_TEMPLATE_PANEL_ID, futil.TEMPLATE_PANEL_NAME)

    manufWS = ui.workspaces.itemById(futil.CAM_WORKSPACE_ID)
    toolbar_tab = manufWS.toolbarTabs.add(futil.CAM_TEMPLATE_TAB_ID, futil.TEMPLATE_PANEL_NAME)
    toolbar_tab.toolbarPanels.add(futil.CAM_TEMPLATE_PANEL_ID, futil.TEMPLATE_PANEL_NAME)


def delete_ui_panels():
    ui = futil.Fusion().getUI()
    designWS = ui.workspaces.itemById(futil.DESIGN_WORKSPACE_ID)
    panel = designWS.toolbarPanels.itemById(futil.DESIGN_TEMPLATE_PANEL_ID)
    if panel != None:
        panel.deleteMe()

    manufWS = ui.workspaces.itemById(futil.CAM_WORKSPACE_ID)
    panel = manufWS.toolbarPanels.itemById(futil.CAM_TEMPLATE_PANEL_ID)
    if panel != None:
        panel.deleteMe()


# Each module MUST define a "start" function.
# The start function will be run when the add-in is started.
def start():
    create_ui_panels()    
    for command in commands:
        command.start()


# Each module MUST define a "stop" function.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
    delete_ui_panels()
  


