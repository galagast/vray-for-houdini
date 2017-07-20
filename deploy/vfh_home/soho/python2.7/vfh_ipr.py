# Copyright (c) 2015-2017, Chaos Software Ltd.
#
# V-Ray For Houdini
#
# ACCESSIBLE SOURCE CODE WITHOUT DISTRIBUTION OF MODIFICATION LICENSE
#
# Full license text: https://github.com/ChaosGroup/vray-for-houdini/blob/master/LICENSE
#
# Main help resource:
#   http://www.sidefx.com/docs/hdk15.5/_h_d_k__s_o_h_o.html
#

import sys

import traceback

import hou

import soho
import sohoglue
import SOHOcommon

import _vfh_ipr

from soho import SohoParm

RENDER_RT_MODE_SOHO = 1


def main():
    def printDebug(fmt, *args):
        sys.stdout.write("V-Ray For Houdini IPR| ")
        sys.stdout.write(fmt % args)
        sys.stdout.write("\n")

    def dumpObjects(listName):
        printDebug("Checking \"%s\"" % listName)
        for obj in soho.objectList(listName):
            printDebug("   %s", obj.getName())

    def exportObjects(listName):
        for obj in soho.objectList(listName):
            _vfh_ipr.exportOpNode(opNode=obj.getName())

    def deleteObjects(listName):
        for obj in soho.objectList(listName):
            _vfh_ipr.deleteOpNode(opNode=obj.getName())

    def getViewParams(camera, sohoCam, t):
        camParms = {
            'space:world' : SohoParm('space:world', 'real',   [],              False),
            'focal'       : SohoParm('focal',       'real',   [0.050],         False),
            'aperture'    : SohoParm('aperture',    'real',   [0.0414214],     False),
            'orthowidth'  : SohoParm('orthowidth',  'real',   [2],             False),
            'near'        : SohoParm('near',        'real',   [0.001],         False),
            'far'         : SohoParm('far',         'real',   [1000],          False),
            'res'         : SohoParm('res',         'int',    [640,480],       False),
            'projection'  : SohoParm('projection',  'string', ["perspective"], False),
            'cropLeft'    : SohoParm('cropl',       'real',   [-1],            False),
            'cropRight'   : SohoParm('cropr',       'real',   [-1],            False),
            'cropBottom'  : SohoParm('cropb',       'real',   [-1],            False),
            'cropTop'     : SohoParm('cropt',       'real',   [-1],            False),
            'camera'      : SohoParm('camera',      'string', ['/obj/cam1'],   False)
        }

        camParmsEval = sohoCam.evaluate(camParms, t)
        if not camParmsEval:
            return {}

        viewParams = {
            'camera'    : camera,
            'transform' : camParmsEval['space:world'].Value,
            'ortho'     : 1 if camParmsEval['projection'].Value[0] in {'ortho'} else 0,
            'res'       : camParmsEval['res'].Value,
            'cropl'     : camParmsEval['cropl'].Value[0],
            'cropr'     : camParmsEval['cropr'].Value[0],
            'cropt'     : camParmsEval['cropt'].Value[0],
            'cropb'     : camParmsEval['cropb'].Value[0],
        }

        cropX = viewParams['res'][0] * viewParams['cropl']
        cropY = viewParams['res'][1] * (1.0 - viewParams['cropt'])
        cropW = viewParams['res'][0] * (viewParams['cropr'] - viewParams['cropl'])
        cropH = viewParams['res'][1] * (viewParams['cropt'] - viewParams['cropb'])

        printDebug("  Res: %s" % viewParams['res'])
        printDebug("  Crop: %i-%i %i x %i " % (cropX, cropY, cropW, cropH))

        return viewParams


    def exportView(rop, camera, sohoCam, t):
        printDebug("exportView()")

        _vfh_ipr.exportView(viewParams=getViewParams(camera, sohoCam, t))

    mode = soho.getDefaultedString('state:previewmode', ['default'])[0]

    # Evaluate an intrinsic parameter (see HDK_SOHO_API::evaluate())
    # The 'state:time' parameter evaluates the time from the ROP.
    now = soho.getDefaultedFloat('state:time', [0.0])[0]

    # Evaluate the 'camera' parameter as a string.
    # If the 'camera' parameter doesn't exist, use ['/obj/cam1'].
    # SOHO always returns lists of values.
    camera = soho.getDefaultedString('camera', ['/obj/cam1'])[0]

    # MPlay / Render View port.
    port = soho.getDefaultedInt("vm_image_mplay_socketport", [0])[0]

    # ROP node.
    ropPath = soho.getOutputDriver().getName()
    ropNode = hou.node(ropPath)

    # Use callbacks or SOHO
    render_rt_update_mode = hou.evalParm("render_rt_update_mode")

    printDebug("Initialize SOHO...")

    # Initialize SOHO with the camera.
    # XXX: This doesn't work for me, but it should according to the documentation...
    #   soho.initialize(now, camera)
    if not sohoglue.initialize(now, camera, None):
        soho.error("Unable to initialize rendering module with given camera")

    # Now, add objects to our scene
    soho.addObjects(now, "*", "*", "*", True)

    # Before we can evaluate the scene from SOHO, we need to lock the object lists.
    soho.lockObjects(now)

    for sohoCam in soho.objectList('objlist:camera'):
        break
    else:
        soho.error("Unable to find viewing camera for render")

    sohoOverride = soho.getDefaultedString('soho_overridefile', ['Unknown'])[0]

    printDebug("Processing Mode: \"%s\"" % mode)

    if mode in {"generate"}:
        # generate: Generation phase of IPR rendering 
        # In generate mode, SOHO will keep the pipe (soho_pipecmd)
        # command open between invocations of the soho_program.
        #   objlist:all
        #   objlist:camera
        #   objlist:light
        #   objlist:instance
        #   objlist:fog
        #   objlist:space
        #   objlist:mat
        #
        printDebug("IPR Port: %s" % port)
        printDebug("Driver: %s" % ropPath)
        printDebug("Camera: %s" % camera)
        printDebug("Now: %.3f" % now)

        _vfh_ipr.init(rop=ropPath, port=port, now=now, viewParams=getViewParams(camera, sohoCam, now))

    elif render_rt_update_mode == RENDER_RT_MODE_SOHO and mode in {"update"}:
        # update: Send updated changes from previous generation
        #
        # In this rendering mode, the special object list parameters:
        #   objlist:dirtyinstance
        #   objlist:dirtylight
        #   objlist:dirtyspace
        #   objlist:dirtyfog
        # will contain the list of all objects modified since the last render
        # (whether a generate or update).
        #
        # As well, the parameters:
        #   objlist:deletedinstance
        #   objlist:deletedlight
        #   objlist:deletedspace
        #   objlist:deletedfog
        # will list all objects which have been deleted from the scene.
        #

        # Update view.
        exportView(ropPath, camera, sohoCam, now)

        exportObjects("objlist:dirtyinstance")
        exportObjects("objlist:dirtylight")
        # exportObjects("objlist:dirtyspace")
        # exportObjects("objlist:dirtyfog")

        deleteObjects("objlist:deletedinstance")
        deleteObjects("objlist:deletedlight")
        # deleteObjects("objlist:deletedspace")
        # deleteObjects("objlist:deletedfog")

try:
    main()
except:
    traceback.print_exc()
