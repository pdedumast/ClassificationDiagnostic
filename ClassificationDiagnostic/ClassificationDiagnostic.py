import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging



# ********************************************** #
# **************** Useful class **************** #
# ********************************************** #

class ExternalModuleTab():
  def __init__(self):
    self.collapsibleButton = None
    self.layout = None
    self.choiceComboBox = None
    self.currentModule = None
    self.currentComboboxIndex = None

  def hideCurrentModule(self):
    if self.currentModule:
      if hasattr(self.currentModule, 'widget'):
        self.layout.removeWidget(self.currentModule.widget)
        self.currentModule.widget.hide()
      else:
        self.layout.removeWidget(self.currentModule.widgetRepresentation())
        self.currentModule.widgetRepresentation().hide()
      self.choiceComboBox.setCurrentIndex(0)

  def deleteCurrentModule(self):
    self.hideCurrentModule()
    self.currentModule = None
    self.currentComboboxIndex = 0

  def showCurrentModule(self):
    if self.currentModule:
      if hasattr(self.currentModule, 'widget'):
        self.layout.addWidget(self.currentModule.widget)
        self.currentModule.widget.show()
      else:
        self.layout.addWidget(self.currentModule.widgetRepresentation())
        self.currentModule.widgetRepresentation().show()
      if hasattr(self.currentModule, 'enter'):
        self.currentModule.enter()
      self.choiceComboBox.setCurrentIndex(self.currentComboboxIndex)

  def setCurrentModule(self, module, index):
    self.deleteCurrentModule()
    self.currentModule = module
    self.currentComboboxIndex = index
    self.showCurrentModule()



# *********************************************************



#
# ClassificationDiagnostic
#

class ClassificationDiagnostic(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ClassificationDiagnostic" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Quantification"]
    self.parent.dependencies = []
    self.parent.contributors = ["Priscille de Dumast (University of Michigan)"] 
    self.parent.helpText = """
    TODO
    """
    self.parent.acknowledgementText = """
    This work was supported by the National
            Institutes of Dental and Craniofacial Research
            and Biomedical Imaging and Bioengineering of
            the National Institutes of Health under Award
            Number R01DE024450.
""" # replace with organization, grant and thanks.

#
# ClassificationDiagnosticWidget
#

class ClassificationDiagnosticWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # ---- Widget Setup ----

    # Global Variables
    self.logic = ClassificationDiagnosticLogic(self)

    # Interface
    loader = qt.QUiLoader()
    self.moduleName = 'ClassificationDiagnostic'
    scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)

    widget = loader.load(qfile, self.parent)
    self.layout = self.parent.layout()
    self.widget = widget
    self.layout.addWidget(widget)

    # self.comboBox_moduleChoice = self.logic.get('comboBox_moduleChoice')
    # self.collapsibleButton_module = self.logic.get('collapsibleButton_module')


    self.ExtModuleTab = ExternalModuleTab()
    self.ExtModuleTab.layout = self.logic.get('layout_module')
    self.ExtModuleTab.choiceComboBox = self.logic.get('comboBox_moduleChoice')


    # ------------------------------------------------------------------------------ #
    # ---------------- Setup and initialisation of global variables ---------------- #
    # ------------------------------------------------------------------------------ #

    # ------ Initialisation of the other modules is Slicer, if that's not already done ----- #
    if not hasattr(slicer.modules, 'DiagnosticIndexWidget'):
      slicer.modules.diagnosticindex.createNewWidgetRepresentation()
    if not hasattr(slicer.modules, 'ClassificationWidget'):
      slicer.modules.classification.createNewWidgetRepresentation()


    # ------ Creation of a dictionary that will contain the pythons modules ----- #
    self.ExternalPythonModules = dict()
    self.ExternalPythonModules["Diagnostic Index"] = slicer.modules.DiagnosticIndexWidget
    self.ExternalPythonModules["Shape Classification"] = slicer.modules.ClassificationWidget


    # ------ Creation of a dictionary that will contain the CLI modules ----- #
    self.ExternalCLIModules = dict()
    # self.ExternalCLIModules["Model to Model Distance"] = slicer.modules.modeltomodeldistance
    self.ExternalCLIModules["Shape Population Viewer"] = slicer.modules.launcher  

    # ------ Creation of a dictionary that will contain all the modules ----- #
    self.ExternalModulesDict = dict(self.ExternalPythonModules, **self.ExternalCLIModules)

    # ------ Setup of the external CLI modules ------ #
    # Setting the size to the good value
    for key, value in self.ExternalCLIModules.iteritems():
        value.widgetRepresentation().setSizePolicy(1,1)
        value.widgetRepresentation().adjustSize()

    # --------------------------------------------- #
    # ---------------- Connections ---------------- #
    # --------------------------------------------- #

    # self.comboBox_moduleChoice.connect('currentIndexChanged(QString)', self.onModuleChoiceChanged)

    # ------ Eternal Modules Selections ----- #
    self.ExtModuleTab.choiceComboBox.connect('currentIndexChanged(QString)',
                                          lambda newModule, currentCombobox = self.ExtModuleTab.choiceComboBox:
                                          self.onExternalModuleChangement(newModule, currentCombobox))

    # ------ Closing of the scene -----#
    slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.onCloseScene)


  def cleanup(self):
    pass



  # ******************************************* #
  # ---------------- Algorithm ---------------- #
  # ******************************************* #

  def onReload(self):
    slicer.util.reloadScriptedModule(self.moduleName)
    for key, value in self.ExternalPythonModules.iteritems():
      slicer.util.reloadScriptedModule(value.moduleName)


  # function called each time that the scene is closed (if Shape Quantifier has been initialized)
  def onCloseScene(self, obj, event):
    print "---- Close Shape Quantifier ---- "
    print " TODO "
    # for ExtModTab in self.ExternalModuleTabDict.itervalues():
    #   ExtModTab.choiceComboBox.setCurrentIndex(0)

  # ---------- switching of Tab ----------- #
  # Only one tab can be display at the same time, so when one tab is opened
  # all the other tabs are closed by this function
  # def onSelectedCollapsibleButtonChanged(self, selectedCollapsibleButton):
  #   print "--- on Selected Collapsible Button Changed ---"
  #   if selectedCollapsibleButton.isChecked():
  #     self.SceneCollapsibleButton.setChecked(False)
  #     self.DataSelectionCollapsibleButton.setChecked(False)
  #     for ExtModTab in self.ExternalModuleTabDict.itervalues():
  #       ExtModTab.choiceComboBox.blockSignals(True)
  #       if ExtModTab.collapsibleButton is selectedCollapsibleButton:
  #         ExtModTab.showCurrentModule()
  #       else:
  #         ExtModTab.collapsibleButton.setChecked(False)
  #         ExtModTab.hideCurrentModule()
  #       ExtModTab.choiceComboBox.blockSignals(False)
  #     selectedCollapsibleButton.setChecked(True)
  #     self.propagationOfInputDataToExternalModules()

  # ---------- switching of External Module ----------- #
  # This function hide all the external widgets if they are displayed
  # And show the new external module given in argument
  def onExternalModuleChangement(self, newModule, currentCombobox):
    print "--- on External Module Changement ---"
    self.ExtModuleTab.choiceComboBox.blockSignals(True)
    if newModule != "None":
      self.ExtModuleTab.setCurrentModule(self.ExternalModulesDict[newModule], currentCombobox.currentIndex)
    else:
      self.ExtModuleTab.deleteCurrentModule()
    self.ExtModuleTab.choiceComboBox.blockSignals(False)
    

#
# ClassificationDiagnosticLogic
#

class ClassificationDiagnosticLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, interface):
    self.interface = interface

  # Functions to recovery the widget in the .ui file
  def get(self, objectName):
      return self.findWidget(self.interface.widget, objectName)

  def findWidget(self, widget, objectName):
    if widget.objectName == objectName:
        return widget
    else:
        for w in widget.children():
            resulting_widget = self.findWidget(w, objectName)
            if resulting_widget:
                return resulting_widget
        return None


  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('ClassificationDiagnosticTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class ClassificationDiagnosticTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ClassificationDiagnostic1()

  def test_ClassificationDiagnostic1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = ClassificationDiagnosticLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
