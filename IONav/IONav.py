import os
from __main__ import vtk, qt, ctk, slicer

from Guidelet import GuideletLoadable, GuideletLogic, GuideletTest, GuideletWidget
from Guidelet import Guidelet
import logging
import time
import math

class IONav(GuideletLoadable):

  def __init__(self, parent):
    GuideletLoadable.__init__(self, parent)
    self.parent.title = "IONav"
    self.parent.categories = ["Image Overlay"]
    self.parent.dependencies = []
    self.parent.contributors = ["Zachary Baum, Tamas Ungi, Andras Lasso, Gabor Fichtinger"]
    self.parent.helpText = """
    IONav Guidelet -- for use in image overlay navigation of patient volumes, calibration of the image overlay system, viewbox and tools, and patient registration.
    """
    self.parent.acknowledgementText = """
    """

class IONavWidget(GuideletWidget):

  def __init__(self, parent = None):
    GuideletWidget.__init__(self, parent)


  def setup(self):
    GuideletWidget.setup(self)
    slicer.modules.IONavWidget.launchGuideletButton.setEnabled(False)


  def addLauncherWidgets(self):
    GuideletWidget.addLauncherWidgets(self)
    self.launcherFormLayout.addWidget(qt.QLabel(""))
    self.addAddDataDialog()
    self.addTrackingSystemComboBox()
    self.addPatientVolumeNodeComboBox()
    self.addRASFiducialComboBox()


  def addAddDataDialog(self):
    self.openAddDataDialogButton = qt.QPushButton("Add Data")
    self.launcherFormLayout.addRow(self.openAddDataDialogButton)
    self.openAddDataDialogButton.connect('clicked()', self.onAddDataDialogClicked)
    self.openAddDataDialogButton.connect('clicked()', self.onSelect)


  def onAddDataDialogClicked(self):
    slicer.util.openAddDataDialog()


  def addTrackingSystemComboBox(self):
    self.trackerSelectComboBox = qt.QComboBox()
    self.trackerSelectComboBox.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed))
    self.trackerSelectComboBox.addItem("Micron Tracker")
    self.trackerSelectComboBox.addItem("Intel RealSense")

    self.trackerSelectHBox = qt.QHBoxLayout()
    self.trackerSelectLabel = qt.QLabel(" Tracking Device: ")
    self.trackerSelectLabel.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Maximum, qt.QSizePolicy.Fixed))
    self.trackerSelectHBox.addWidget(self.trackerSelectLabel)
    self.trackerSelectHBox.addWidget(self.trackerSelectComboBox)

    self.launcherFormLayout.addRow(self.trackerSelectHBox)


  def addPatientVolumeNodeComboBox(self):
    self.patientVolumeComboBox = slicer.qMRMLNodeComboBox()
    self.patientVolumeComboBox.nodeTypes = (("vtkMRMLScalarVolumeNode"), "")
    self.patientVolumeComboBox.selectNodeUponCreation = False
    self.patientVolumeComboBox.addEnabled = False
    self.patientVolumeComboBox.renameEnabled = False
    self.patientVolumeComboBox.removeEnabled = False
    self.patientVolumeComboBox.showHidden = False
    self.patientVolumeComboBox.showChildNodeTypes = False
    self.patientVolumeComboBox.setMRMLScene(slicer.mrmlScene)

    self.patientVolumeHBox = qt.QHBoxLayout()
    self.patientVolumeHBox.addWidget(qt.QLabel(" Patient Volume:  "))
    self.patientVolumeHBox.addWidget(self.patientVolumeComboBox)

    self.launcherFormLayout.addRow(self.patientVolumeHBox)

    self.patientVolumeComboBox.nodeActivated.connect(self.onSelect)


  def addRASFiducialComboBox(self):
    self.rasFiducialComboBox = slicer.qMRMLNodeComboBox()
    self.rasFiducialComboBox.nodeTypes = (("vtkMRMLMarkupsFiducialNode"), "")
    self.rasFiducialComboBox.selectNodeUponCreation = False
    self.rasFiducialComboBox.addEnabled = False
    self.rasFiducialComboBox.renameEnabled = False
    self.rasFiducialComboBox.removeEnabled = False
    self.rasFiducialComboBox.showHidden = False
    self.rasFiducialComboBox.showChildNodeTypes = False
    self.rasFiducialComboBox.setMRMLScene(slicer.mrmlScene)

    self.rasFiducialHBox = qt.QHBoxLayout()
    self.rasFiducialHBox.addWidget(qt.QLabel(" RAS Fiducials:    "))
    self.rasFiducialHBox.addWidget(self.rasFiducialComboBox)

    self.launcherFormLayout.addRow(self.rasFiducialHBox)

    self.rasFiducialComboBox.nodeActivated.connect(self.onSelect)


  def onSelect(self):
    canStart = self.rasFiducialComboBox.currentNode() != 0
    canStart = canStart and self.patientVolumeComboBox.currentNode() != 0
    canStart = canStart and self.rasFiducialComboBox.currentNode() != None
    canStart = canStart and self.patientVolumeComboBox.currentNode() != None
    slicer.modules.IONavWidget.launchGuideletButton.setEnabled(canStart)


  def onConfigurationChanged(self, selectedConfigurationName):
    GuideletWidget.onConfigurationChanged(self, selectedConfigurationName)
    settings = slicer.app.userSettings()


  def createGuideletInstance(self):
    return IONavGuidelet(None, self.guideletLogic, self.selectedConfigurationName, qt.Qt.TopDockWidgetArea)


  def createGuideletLogic(self):
    return IONavLogic()


class IONavLogic(GuideletLogic):

  def __init__(self, parent = None):
    GuideletLogic.__init__(self, parent)


  def addValuesToDefaultConfiguration(self):
    GuideletLogic.addValuesToDefaultConfiguration(self)
    moduleDirectoryPath = slicer.modules.ionav.path.replace('IONav.py', '')
    defaultSavePathOfIONav = os.path.join(moduleDirectoryPath, 'SavedScenes')
    settingList = {'StyleSheet' : moduleDirectoryPath + 'Resources/StyleSheets/ImageOverlayStyle.qss',
                   'MIOSScreenZoomYellowFactor' : '0.5',
                   'MIOSScreenZoomGreenFactor' : '0.1',
                   'ViewboxCalibrationMarkerVolumeSpacing' : '0.048',
                   'OverlayCalibrationMarkerVolumeSpacing' : '0.048',
                   'PlusServerHostNamePort' : '192.168.0.199:18944', # Either 192.168.0.199 for MicronTracker with gf-ultramac and ImageOverlay2 Network, or localhost for RealSense.
                   'PivotCalibrationErrorThresholdMm' : '0.9',
                   'PivotCalibrationDurationSec' : '7',
                   'SpinCalibrationErrorThresholdMm' : '0.1',
                   'SpinCalibrationDurationSec' : '7',
                   'PatientRegistrationFiducialAcquisitionDurationSec' : '3',
                   'NeedleModelToNeedleTip' : '0 1 0 0 0 0 1 0 1 0 0 0 0 0 0 1',
                   'NeedleBaseToNeedle' : '1 0 0 20.93 0 1 0 -6.00 0 0 1 -4.27 0 0 0 1',
                   'TestMode' : 'False',
                   'RecordingFilenamePrefix' : 'IONavRecording-',
                   'SavedScenesDirectory': defaultSavePathOfIONav
                   }
    self.updateSettings(settingList, 'Default')


class IONavTest(GuideletTest):

  def runTest(self):
    GuideletTest.runTest(self)


class IONavGuidelet(Guidelet):

  def __init__(self, parent, logic, configurationName = 'Default', sliceletDockWidgetPosition = 'Default'):
    Guidelet.__init__(self, parent, logic, configurationName, sliceletDockWidgetPosition)
    logging.debug('IONavGuidelet.__init__')

    self.logic.addValuesToDefaultConfiguration()
    self.moduleDirectoryPath = slicer.modules.ionav.path.replace('IONav.py', '')
    self.sliceletDockWidget.setObjectName('IONav Panel')
    self.sliceletDockWidget.setWindowTitle('IONav')
    self.mainWindow.setWindowTitle('IONav')
    self.mainWindow.windowIcon = qt.QIcon(self.moduleDirectoryPath + '/Resources/Icons/IONav.png')

    self.pivotCalibrationLogic = slicer.modules.pivotcalibration.logic()
    self.spinCalibrationLogic = slicer.modules.pivotcalibration.logic()

    self.fiducialRegistrationWizardNode = slicer.vtkMRMLFiducialRegistrationWizardNode()
    slicer.mrmlScene.AddNode(self.fiducialRegistrationWizardNode)
    self.fiducialRegistrationLogic = slicer.modules.fiducialregistrationwizard.logic()

    self.markupsLogic = slicer.modules.markups.logic()

    self.layout = slicer.util.getNode('Layout')

    self.setupScene()


  def createFeaturePanels(self):
    self.toolbarSettingsPanel = ctk.ctkSettingsPanel()
    self.setupToolbarPanel()

    featurePanelList = Guidelet.createFeaturePanels(self)

    self.ultrasoundCollapsibleButton.setVisible(False)
    self.advancedCollapsibleButton.setVisible(False)

    self.ultrasoundCollapsibleButton.setProperty('collapsed', True)
    self.advancedCollapsibleButton.setProperty('collapsed', True)

    return featurePanelList


  def __del__(self):
    self.preCleanup()


  def preCleanup(self):
    Guidelet.preCleanup(self)
    logging.debug('preCleanup')


  def setupConnections(self):
    logging.debug('IONav.setupConnections()')
    Guidelet.setupConnections(self)

    self.startNavigationButton.connect('clicked()', self.onRealSenseNavigationStart)

    self.startLeftNavigationButton.connect('triggered()', self.onSystemLeftSideClicked)
    self.startRightNavigationButton.connect('triggered()', self.onSystemRightSideClicked)

    self.startSystemCalibrationButton.connect('clicked()', self.onStartSystemCalibrationClicked)
    self.toolbarCalibrationTimer.connect('timeout()', self.onSystemSamplingTimeout)

    self.startViewboxCalibrationButton.connect('clicked()', self.onStartViewboxCalibrationClicked)
    self.startOverlayCalibrationButton.connect('clicked()', self.onStartOverlayCalibrationClicked)

    self.viewboxCalibrationTimer.connect('timeout()', self.onViewboxSamplingTimeout)
    self.overlayCalibrationTimer.connect('timeout()', self.onOverlaySamplingTimeout)

    self.beginPivotCalibrationButton.connect('triggered()', self.onNeedlePivotClicked)
    self.beginSpinCalibrationButton.connect('triggered()', self.onNeedleSpinClicked)
    self.toolbarPivotTimer.connect('timeout()', self.onPivotSamplingTimeout)
    self.toolbarSpinTimer.connect('timeout()', self.onSpinSamplingTimeout)

    self.beginPatientRegistrationButton.connect('triggered()', self.onPatientRegistrationClicked)
    self.addReferenceFiducialButton.connect('triggered()', self.onAddReferenceFiducialClicked)
    self.deleteFiducialButton.connect('triggered()', self.onDeleteLastFiducialClicked)
    self.deleteAllFiducialButton.connect('triggered()', self.onDeleteAllFiducialsClicked)
    self.clearRef2RasButton.connect('triggered()', self.onClearRef2RasClicked)

    self.toolbarPatientRegistrationTimer.connect('timeout()', self.onPatientRegistrationSamplingTimeout)

    self.showSlicerInterfaceButton.connect('triggered()', self.onShowSlicerInterfaceClicked)
    self.showFullScreenButton.connect('triggered()', self.onShowFullscreenButton)
    self.saveButton.connect('triggered()', self.onSaveClicked)


  def disconnect(self):
    logging.debug('IONav.disconnect()')
    Guidelet.disconnect(self)

    self.startNavigationButton.disconnect('clicked()', self.onRealSenseNavigationStart)

    self.startLeftNavigationButton.disconnect('triggered()', self.onSystemLeftSideClicked)
    self.startRightNavigationButton.disconnect('triggered()', self.onSystemRightSideClicked)

    self.startSystemCalibrationButton.disconnect('clicked()', self.onStartSystemCalibrationClicked)
    self.toolbarCalibrationTimer.disconnect('timeout()', self.onSystemSamplingTimeout)

    self.startViewboxCalibrationButton.disconnect('clicked()', self.onStartViewboxCalibrationClicked)
    self.startOverlayCalibrationButton.disconnect('clicked()', self.onStartOverlayCalibrationClicked)

    self.viewboxCalibrationTimer.disconnect('timeout()', self.onViewboxSamplingTimeout)
    self.overlayCalibrationTimer.disconnect('timeout()', self.onOverlaySamplingTimeout)

    self.beginPivotCalibrationButton.disconnect('triggered()', self.onNeedlePivotClicked)
    self.beginSpinCalibrationButton.disconnect('triggered()', self.onNeedleSpinClicked)
    self.toolbarPivotTimer.disconnect('timeout()', self.onPivotSamplingTimeout)
    self.toolbarSpinTimer.disconnect('timeout()', self.onSpinSamplingTimeout)

    self.beginPatientRegistrationButton.disconnect('triggered()', self.onPatientRegistrationClicked)
    self.addReferenceFiducialButton.disconnect('triggered()', self.onAddReferenceFiducialClicked)
    self.deleteFiducialButton.disconnect('triggered()', self.onDeleteLastFiducialClicked)
    self.deleteAllFiducialButton.disconnect('triggered()', self.onDeleteAllFiducialsClicked)
    self.clearRef2RasButton.disconnect('triggered()', self.onClearRef2RasClicked)

    self.toolbarPatientRegistrationTimer.disconnect('timeout()', self.onPatientRegistrationSamplingTimeout)

    self.showSlicerInterfaceButton.disconnect('triggered()', self.onShowSlicerInterfaceClicked)
    self.showFullScreenButton.disconnect('triggered()', self.onShowFullscreenButton)
    self.saveButton.disconnect('triggered()', self.onSaveClicked)


  def setupScene(self):
    logging.debug('setupScene')

    self.referenceToRas = slicer.util.getNode('ReferenceToRas')
    if not self.referenceToRas:
      self.referenceToRas = slicer.vtkMRMLLinearTransformNode()
      self.referenceToRas.SetName("ReferenceToRas")
      m = self.logic.readTransformFromSettings('ReferenceToRas', self.configurationName)
      if m is None: # If none loaded by default, uses "SpineCT" and 3D Printed Spine Phantom as the default Ref2RAS setup.
        m = self.logic.createMatrixFromString('0.00999094 0.0337202 0.999381 -61.2239 -0.999796 -0.017215 0.0105759 -160.143 0.017561 -0.999283 0.0335414 -42.2018 0 0 0 1')
      self.referenceToRas.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.referenceToRas)

    Guidelet.setupScene(self)
    logging.debug('Create transforms')

    # Create transforms that are static when in use (not updated through OpenIGTLink).
    # Needle Tip to Needle.
    self.needleTipToNeedle = slicer.util.getNode('NeedleTipToNeedle')
    if not self.needleTipToNeedle:
      self.needleTipToNeedle = slicer.vtkMRMLLinearTransformNode()
      self.needleTipToNeedle.SetName("NeedleTipToNeedle")
      m = self.logic.readTransformFromSettings('NeedleTipToNeedle', self.configurationName)
      if m:
        self.needleTipToNeedle.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.needleTipToNeedle)

    # Needle Base to Needle.
    self.needleBaseToNeedle = slicer.util.getNode('NeedleBaseToNeedle')
    if not self.needleBaseToNeedle:
      self.needleBaseToNeedle = slicer.vtkMRMLLinearTransformNode()
      self.needleBaseToNeedle.SetName("NeedleBaseToNeedle")
      m = self.logic.readTransformFromSettings('NeedleBaseToNeedle', self.configurationName)
      if m:
        self.needleBaseToNeedle.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.needleBaseToNeedle)

    # Needle Model to Needle.
    self.needleModelToNeedleTip = slicer.util.getNode('NeedleModelToNeedleTip')
    if not self.needleModelToNeedleTip:
      self.needleModelToNeedleTip = slicer.vtkMRMLLinearTransformNode()
      self.needleModelToNeedleTip.SetName("NeedleModelToNeedleTip")
      m = self.logic.readTransformFromSettings('NeedleModelToNeedleTip', self.configurationName)
      if m:
        self.needleModelToNeedleTip.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.needleModelToNeedleTip)

    # MicronTracker Transforms Setup
    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Micron Tracker":

      # Calibration Marker to ViewLeft.
      self.calibrationMarkerToViewboxLeft = slicer.util.getNode('CMarkerToViewLeft')
      if not self.calibrationMarkerToViewboxLeft:
        self.calibrationMarkerToViewboxLeft = slicer.vtkMRMLLinearTransformNode()
        self.calibrationMarkerToViewboxLeft.SetName("CMarkerToViewLeft")
        m = self.logic.readTransformFromSettings('CMarkerToViewLeft', self.configurationName)
        if m is None:
          m = self.logic.createMatrixFromString('-0.002 -0.024 0.999 95.829 -0.003 -0.999 -0.024 122.434 0.999 -0.003 0.002 125.046 0 0 0 1')
        self.calibrationMarkerToViewboxLeft.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.calibrationMarkerToViewboxLeft)

      # Calibration Marker to ViewRight.
      self.calibrationMarkerToViewboxRight = slicer.util.getNode('CMarkerToViewRight')
      if not self.calibrationMarkerToViewboxRight:
        self.calibrationMarkerToViewboxRight = slicer.vtkMRMLLinearTransformNode()
        self.calibrationMarkerToViewboxRight.SetName("CMarkerToViewRight")
        m = self.logic.readTransformFromSettings('CMarkerToViewRight', self.configurationName)
        if m is None:
          m = self.logic.createMatrixFromString('-0.002 0.033 -0.999 -98.340 0.030 -0.999 -0.033 120.153 -0.999 -0.029 -0.002 127.959 0 0 0 1')
        self.calibrationMarkerToViewboxRight.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.calibrationMarkerToViewboxRight)

      # Virtual Calibration Marker to Calibration Marker.
      self.virtualCalibrationMarkerToCalibrationMarker = slicer.util.getNode('VCMarkerToCMarker')
      if not self.virtualCalibrationMarkerToCalibrationMarker:
        self.virtualCalibrationMarkerToCalibrationMarker = slicer.vtkMRMLLinearTransformNode()
        self.virtualCalibrationMarkerToCalibrationMarker.SetName("VCMarkerToCMarker")
        m = self.logic.readTransformFromSettings('VCMarkerToCMarker', self.configurationName)
        if m is None:
          m = self.logic.createMatrixFromString('-0.999 0.003 -0.004 -0.678 -0.003 -0.999 0.041 348.545 -0.003 0.041 0.999 -5.979 0 0 0 1')
        self.virtualCalibrationMarkerToCalibrationMarker.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.virtualCalibrationMarkerToCalibrationMarker)

      # Calibration Volume to Virtual Calibration Marker.
      self.calibrationVolumeToVirtualCalibrationMarker = slicer.util.getNode('CalibrationVolumeToVCMarker')
      if not self.calibrationVolumeToVirtualCalibrationMarker:
        self.calibrationVolumeToVirtualCalibrationMarker = slicer.vtkMRMLLinearTransformNode()
        self.calibrationVolumeToVirtualCalibrationMarker.SetName("CalibrationVolumeToVCMarker")
        m = self.logic.readTransformFromSettings('CalibrationVolumeToVCMarker', self.configurationName)
        if m is None:
          m = self.logic.createMatrixFromString('-1 0 0 0 0 -1 0 0 0 0 1 0 0 0 0 1')
        self.calibrationVolumeToVirtualCalibrationMarker.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.calibrationVolumeToVirtualCalibrationMarker)

      # ViewRight to Reference.
      self.viewRightToReference = slicer.util.getNode('ViewRightToReference')
      if not self.viewRightToReference:
        self.viewRightToReference = slicer.vtkMRMLLinearTransformNode()
        self.viewRightToReference.SetName("ViewRightToReference")
        slicer.mrmlScene.AddNode(self.viewRightToReference)

      # ViewLeft to Reference.
      self.viewLeftToReference = slicer.util.getNode('ViewLeftToReference')
      if not self.viewLeftToReference:
        self.viewLeftToReference = slicer.vtkMRMLLinearTransformNode()
        self.viewLeftToReference.SetName("ViewLeftToReference")
        slicer.mrmlScene.AddNode(self.viewLeftToReference)

    # RealSense Transforms Setup
    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Intel RealSense":

      # Temporary Marker to Tracker.
      self.temporaryMarkerToTracker = slicer.util.getNode('TMarkerToTracker')
      if not self.temporaryMarkerToTracker:
        self.temporaryMarkerToTracker = slicer.vtkMRMLLinearTransformNode()
        self.temporaryMarkerToTracker.SetName("TMarkerToTracker")
        m = self.logic.readTransformFromSettings('TMarkerToTracker', self.configurationName)
        if m is None:
          m = self.logic.createMatrixFromString('0.149067 0.00504202 0.988814 -169.974 -0.95135 0.273428 0.142025 -65.5181 -0.269653 -0.961879 0.0455559 -343.777 0 0 0 1')
        self.temporaryMarkerToTracker.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.temporaryMarkerToTracker)

      # Calibration Marker to Temporary Marker.
      self.calibrationMarkerToTemporaryMarker = slicer.util.getNode('CMarkerToTMarker')
      if not self.calibrationMarkerToTemporaryMarker:
        self.calibrationMarkerToTemporaryMarker = slicer.vtkMRMLLinearTransformNode()
        self.calibrationMarkerToTemporaryMarker.SetName("CMarkerToTMarker")
        m = self.logic.readTransformFromSettings('CMarkerToTMarker', self.configurationName)
        if m is None:
          m = self.logic.createMatrixFromString('0.251957 -0.903183 -0.347532 -99.2483 0.884389 0.360699 -0.296231 -570.145 0.392906 -0.232716 0.889645 64.6166 0 0 0 1')
        self.calibrationMarkerToTemporaryMarker.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.calibrationMarkerToTemporaryMarker)

      # Virtual Calibration Marker to Calibration Marker.
      self.virtualCalibrationMarkerToCalibrationMarker = slicer.util.getNode('VCMarkerToCMarker')
      if not self.virtualCalibrationMarkerToCalibrationMarker:
        self.virtualCalibrationMarkerToCalibrationMarker = slicer.vtkMRMLLinearTransformNode()
        self.virtualCalibrationMarkerToCalibrationMarker.SetName("VCMarkerToCMarker")
        m = self.logic.readTransformFromSettings('VCMarkerToCMarker', self.configurationName)
        if m is None:
          m = self.logic.createMatrixFromString('-0.999637 -0.0206521 0.0173021 -0.128203 0.020569 -0.999776 -0.00496755 366.664 0.0174009 -0.00460986 0.999838 -0.402251 0 0 0 1')
        self.virtualCalibrationMarkerToCalibrationMarker.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.virtualCalibrationMarkerToCalibrationMarker)

      # Calibration Volume to Virtual Calibration Marker.
      self.calibrationVolumeToVirtualCalibrationMarker = slicer.util.getNode('CalibrationVolumeToVCMarker')
      if not self.calibrationVolumeToVirtualCalibrationMarker:
        self.calibrationVolumeToVirtualCalibrationMarker = slicer.vtkMRMLLinearTransformNode()
        self.calibrationVolumeToVirtualCalibrationMarker.SetName("CalibrationVolumeToVCMarker")
        m = self.logic.readTransformFromSettings('CalibrationVolumeToVCMarker', self.configurationName)
        """
        TODO: This should need re-calibration with new system setup.
        if m is None:
          m = self.logic.createMatrixFromString('-0.248137 0.0304673 0 0 -0.0304673 -0.248137 0 0 0 0 0.25 0 0 0 0 1')
        """
        self.calibrationVolumeToVirtualCalibrationMarker.SetMatrixTransformToParent(m)
        slicer.mrmlScene.AddNode(self.calibrationVolumeToVirtualCalibrationMarker)

      # Tracker to Reference.
      self.trackerToReference = slicer.util.getNode('TrackerToReference')
      if not self.trackerToReference:
        self.trackerToReference = slicer.vtkMRMLLinearTransformNode()
        self.trackerToReference.SetName("TrackerToReference")
        slicer.mrmlScene.AddNode(self.trackerToReference)

    # Create transforms that will be updated through OpenIGTLink.
    # Needle to Reference.
    self.needleToReference = slicer.util.getNode('NeedleToReference')
    if not self.needleToReference:
      self.needleToReference = slicer.vtkMRMLLinearTransformNode()
      self.needleToReference.SetName("NeedleToReference")
      slicer.mrmlScene.AddNode(self.needleToReference)

    # Setup Models.
    logging.debug('Create models')

    self.needleModel_NeedleTip = slicer.util.getNode('NeedleModel')
    if not self.needleModel_NeedleTip:
      slicer.modules.createmodels.logic().CreateNeedle(80, 1.0, 2.5, 0)
      self.needleModel_NeedleTip = slicer.util.getNode(pattern = "NeedleModel")
      self.needleModel_NeedleTip.GetDisplayNode().SetColor(0.333333, 1.0, 1.0)
      self.needleModel_NeedleTip.SetName("NeedleModel")
      self.needleModel_NeedleTip.GetDisplayNode().SliceIntersectionVisibilityOn()

    # Setup patient volume.
    self.patientVolume = slicer.modules.IONavWidget.patientVolumeComboBox.currentNode()

    # Setup RAS fiducial node and change its color.
    self.rasPointsNode = slicer.modules.IONavWidget.rasFiducialComboBox.currentNode()
    self.rasPointsDisplayNode = self.rasPointsNode.GetMarkupsDisplayNode()
    self.rasPointsDisplayNode.SetSelectedColor(1, 0, 0)

    # Reset slices before drawing calibration volumes.
    slicer.app.layoutManager().resetSliceViews()

    # Setup calibration volumes.
    # Viewbox calibration marker.
    self.viewboxCalibrationMarkerVolume = slicer.util.getNode('ViewboxCalibrationMarker')
    if self.viewboxCalibrationMarkerVolume == None:
      self.viewboxCalibrationMarkerVolume = slicer.vtkMRMLScalarVolumeNode()
      self.viewboxCalibrationMarkerVolume.SetName("ViewboxCalibrationMarker")
      slicer.mrmlScene.AddNode(self.viewboxCalibrationMarkerVolume)
    self.drawRealSenseMarkerToScreen(self.viewboxCalibrationMarkerVolume, 18)
    self.zoomYellow(float(self.parameterNode.GetParameter('MIOSScreenZoomYellowFactor')))

    # Overlay calibration marker.
    self.overlayCalibrationMarkerVolume = slicer.util.getNode('OverlayCalibrationMarker')
    if self.overlayCalibrationMarkerVolume == None:
      self.overlayCalibrationMarkerVolume = slicer.vtkMRMLScalarVolumeNode()
      self.overlayCalibrationMarkerVolume.SetName("OverlayCalibrationMarker")
      slicer.mrmlScene.AddNode(self.overlayCalibrationMarkerVolume)
    self.drawMarkerToVolume(self.overlayCalibrationMarkerVolume)
    self.zoomGreen(float(self.parameterNode.GetParameter('MIOSScreenZoomGreenFactor')))

    # Build Needle hierarchy.
    logging.debug('Set up transform tree')

    self.needleToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.needleTipToNeedle.SetAndObserveTransformNodeID(self.needleToReference.GetID())
    self.needleBaseToNeedle.SetAndObserveTransformNodeID(self.needleToReference.GetID())
    self.needleModelToNeedleTip.SetAndObserveTransformNodeID(self.needleTipToNeedle.GetID())
    self.needleModel_NeedleTip.SetAndObserveTransformNodeID(self.needleModelToNeedleTip.GetID())

    # Build MicronTracker Viewbox hierarchy -- Starts on right viewer by default.
    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Micron Tracker":
      self.viewRightToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
      self.calibrationMarkerToViewboxRight.SetAndObserveTransformNodeID(self.viewRightToReference.GetID())
      self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID(self.calibrationMarkerToViewboxRight.GetID())
      self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID(self.virtualCalibrationMarkerToCalibrationMarker.GetID())

    # Build RealSense Viewbox hierarchy
    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Intel RealSense":
      self.trackerToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
      self.temporaryMarkerToTracker.SetAndObserveTransformNodeID(self.trackerToReference.GetID())
      self.calibrationMarkerToTemporaryMarker.SetAndObserveTransformNodeID(self.temporaryMarkerToTracker.GetID())
      self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID(self.calibrationMarkerToTemporaryMarker.GetID())
      self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID(self.virtualCalibrationMarkerToCalibrationMarker.GetID())

    slicer.util.getNode('vtkMRMLSliceNodeRed').SetSliceVisible(False)
    self.layout.SetViewArrangement(4)

    # Hide slice view annotations (patient name, scale, color bar, etc.) as they
    # decrease reslicing performance by 20%-100%.
    logging.debug('Hide slice view annotations')
    import DataProbe
    dataProbeUtil = DataProbe.DataProbeLib.DataProbeUtil()
    dataProbeParameterNode = dataProbeUtil.getParameterNode()
    dataProbeParameterNode.SetParameter('showSliceViewAnnotations', '0')


  """
  Toolbar setup (buttons, label and timers)
  """

  def setupToolbarPanel(self):
    logging.debug('setupToolbarPanel')
    self.moduleIconsDirectoryPath = slicer.modules.ionav.path.replace('IONav.py', '/Resources/Icons/')
    self.sliceletPanelLayout.addWidget(self.toolbarSettingsPanel)
    self.toolbarLayout = qt.QFormLayout(self.toolbarSettingsPanel)
    self.hbox = qt.QHBoxLayout()
    self.hbox.setAlignment(qt.Qt.AlignCenter)

    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Micron Tracker":
      self.hbox.setSpacing(75)

    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Intel RealSense":
      self.hbox.setSpacing(50)

    # RealSense
    self.startNavigationButton = qt.QPushButton()
    self.startNavigationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'IONav.png'))
    self.hbox.addWidget(self.startNavigationButton)

    self.startViewboxCalibrationButton = qt.QPushButton('Viewbox Calibration')
    self.hbox.addWidget(self.startViewboxCalibrationButton)

    self.startOverlayCalibrationButton = qt.QPushButton()
    self.startOverlayCalibrationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'SystemCalibration.png'))
    self.hbox.addWidget(self.startOverlayCalibrationButton)

    self.overlayCalibrationTimer = qt.QTimer()
    self.overlayCalibrationTimer.setInterval(50)
    self.overlayCalibrationTimer.setSingleShot(True)

    self.viewboxCalibrationTimer = qt.QTimer()
    self.viewboxCalibrationTimer.setInterval(50)
    self.viewboxCalibrationTimer.setSingleShot(True)

    # MicronTracker
    self.startLeftRightNavigationButton = qt.QPushButton()
    self.startLeftRightNavigationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'IONav.png'))
    self.startLeftRightMenu = qt.QMenu(self.startLeftRightNavigationButton)
    self.startLeftRightNavigationButton.setMenu(self.startLeftRightMenu)

    self.startLeftNavigationButton = qt.QAction("Left View", self.startLeftRightMenu)
    self.startLeftNavigationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'LeftButton.png'))

    self.startRightNavigationButton = qt.QAction("Right View", self.startLeftRightMenu)
    self.startRightNavigationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'RightButton.png'))

    self.startLeftRightMenu.addAction(self.startLeftNavigationButton)
    self.startLeftRightMenu.addAction(self.startRightNavigationButton)

    self.hbox.addWidget(self.startLeftRightNavigationButton)

    self.startSystemCalibrationButton = qt.QPushButton()
    self.startSystemCalibrationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'SystemCalibration.png'))
    self.hbox.addWidget(self.startSystemCalibrationButton)

    self.toolbarCalibrationTimer = qt.QTimer()
    self.toolbarCalibrationTimer.setInterval(50)
    self.toolbarCalibrationTimer.setSingleShot(True)

    # Required for all tracking.
    self.needleCalibrationButton = qt.QPushButton()
    self.needleCalibrationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'PivotCalibration.png'))
    self.needleCalibrationMenu = qt.QMenu(self.needleCalibrationButton)
    self.needleCalibrationButton.setMenu(self.needleCalibrationMenu)

    self.beginPivotCalibrationButton = qt.QAction("Pivot Calibration", self.needleCalibrationMenu)
    self.beginPivotCalibrationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'PivotCalibration.png'))

    self.beginSpinCalibrationButton = qt.QAction("Spin Calibration", self.needleCalibrationMenu)
    self.beginSpinCalibrationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'PivotCalibration.png'))

    self.needleCalibrationMenu.addAction(self.beginPivotCalibrationButton)
    self.needleCalibrationMenu.addAction(self.beginSpinCalibrationButton)

    self.hbox.addWidget(self.needleCalibrationButton)

    self.patientRegistrationButton = qt.QPushButton()
    self.patientRegistrationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'FiducialRegistration.png'))
    self.patientRegistrationMenu = qt.QMenu(self.patientRegistrationButton)
    self.patientRegistrationButton.setMenu(self.patientRegistrationMenu)

    self.beginPatientRegistrationButton = qt.QAction("Start Registration", self.patientRegistrationMenu)
    self.beginPatientRegistrationButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'FiducialRegistration.png'))

    self.addReferenceFiducialButton = qt.QAction("Place Fiducial", self.patientRegistrationMenu)
    self.addReferenceFiducialButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'PlaceFiducial.png'))

    self.deleteFiducialButton = qt.QAction("Delete Last Fiducial", self.patientRegistrationMenu)
    self.deleteFiducialButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'Delete.png'))

    self.deleteAllFiducialButton = qt.QAction("Delete All Fiducials", self.patientRegistrationMenu)
    self.deleteAllFiducialButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'Delete.png'))

    self.clearRef2RasButton = qt.QAction("Clear Registration", self.patientRegistrationMenu)
    self.clearRef2RasButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'Delete.png'))

    self.patientRegistrationMenu.addAction(self.beginPatientRegistrationButton)
    self.patientRegistrationMenu.addSeparator()
    self.patientRegistrationMenu.addAction(self.addReferenceFiducialButton)
    self.patientRegistrationMenu.addSeparator()
    self.patientRegistrationMenu.addAction(self.deleteFiducialButton)
    self.patientRegistrationMenu.addAction(self.deleteAllFiducialButton)
    self.patientRegistrationMenu.addSeparator()
    self.patientRegistrationMenu.addAction(self.clearRef2RasButton)

    self.hbox.addWidget(self.patientRegistrationButton)

    self.settingsMenuButton = qt.QPushButton()
    self.settingsMenuButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'Settings.png'))
    self.settingsMenu = qt.QMenu(self.settingsMenuButton)
    self.settingsMenuButton.setMenu(self.settingsMenu)

    self.showSlicerInterfaceButton = qt.QAction("Show 3D Slicer", self.settingsMenu)
    self.showSlicerInterfaceButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'ShowSlicer.png'))

    self.showFullScreenButton = qt.QAction("Enter Full Screen", self.settingsMenu)
    self.showFullScreenButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'FullScreen.png'))

    self.saveButton = qt.QAction("Save Scene", self.settingsMenu)
    self.saveButton.setIcon(qt.QIcon(self.moduleIconsDirectoryPath + 'SaveScene.png'))

    self.settingsMenu.addAction(self.showSlicerInterfaceButton)
    self.settingsMenu.addAction(self.showFullScreenButton)
    self.settingsMenu.addSeparator()
    self.settingsMenu.addAction(self.saveButton)

    self.hbox.addWidget(self.settingsMenuButton)

    self.toolbarLayout.addRow(self.hbox)

    self.toolbarLabel = qt.QLabel()
    self.toolbarLayout.addRow(self.toolbarLabel)

    self.toolbarPivotTimer = qt.QTimer()
    self.toolbarPivotTimer.setInterval(50)
    self.toolbarPivotTimer.setSingleShot(True)

    self.toolbarSpinTimer = qt.QTimer()
    self.toolbarSpinTimer.setInterval(50)
    self.toolbarSpinTimer.setSingleShot(True)

    self.toolbarPatientRegistrationTimer = qt.QTimer()
    self.toolbarPatientRegistrationTimer.setInterval(50)
    self.toolbarPatientRegistrationTimer.setSingleShot(True)

    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Micron Tracker":
      self.startNavigationButton.setVisible(False)
      self.startViewboxCalibrationButton.setVisible(False)
      self.startOverlayCalibrationButton.setVisible(False)

    if str(slicer.modules.IONavWidget.trackerSelectComboBox.currentText) == "Intel RealSense":
      self.startLeftRightNavigationButton.setVisible(False)
      self.startSystemCalibrationButton.setVisible(False)


  """
  Volume re-slicing Logic
  """

  def onSystemStart(self):
    self.onNewButtonClicked()
    self.startNavigationButton.setEnabled(False)
    logging.debug("Switching to navigation view for reslicing.")

    self.layout.SetViewArrangement(6)

    redWidget = slicer.app.layoutManager().sliceWidget('Red')
    redWidget.setSliceOrientation('Reformat')
    redWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(self.patientVolume.GetID())
    self.needleModel_NeedleTip.GetDisplayNode().SliceIntersectionVisibilityOn()
    slicer.app.layoutManager().resetSliceViews()

    resliceLogic = slicer.modules.volumereslicedriver.logic()
    if resliceLogic:
      redNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
      resliceLogic.SetDriverForSlice(slicer.util.getNode('CalibrationVolumeToVCMarker').GetID(), redNode)
      resliceLogic.SetModeForSlice(6, redNode)
      resliceLogic.SetFlipForSlice(False, redNode)
      resliceLogic.SetRotationForSlice(0, redNode)
    else:
      logging.debug("Reslice logic not found. SlicerIGT needs to be installed.")


  """
  RealSense navigation start
  """

  def onRealSenseNavigationStart(self):
    self.onNewButtonClicked()
    logging.debug("Center camera view enabled.")
    self.trackerToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.temporaryMarkerToTracker.SetAndObserveTransformNodeID(self.trackerToReference.GetID())
    self.calibrationMarkerToTemporaryMarker.SetAndObserveTransformNodeID(self.temporaryMarkerToTracker.GetID())
    self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID(self.calibrationMarkerToTemporaryMarker.GetID())
    self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID(self.virtualCalibrationMarkerToCalibrationMarker.GetID())
    self.onSystemStart()


  """
  Viewbox side switching logic
  """

  def onSystemLeftSideClicked(self):
    self.onNewButtonClicked()
    logging.debug("Switched to left view.")
    self.viewLeftToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.calibrationMarkerToViewboxLeft.SetAndObserveTransformNodeID(self.viewLeftToReference.GetID())
    self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID(self.calibrationMarkerToViewboxLeft.GetID())
    self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID(self.virtualCalibrationMarkerToCalibrationMarker.GetID())
    self.onSystemStart()


  def onSystemRightSideClicked(self):
    self.onNewButtonClicked()
    logging.debug("Switched to right view.")
    self.viewRightToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.calibrationMarkerToViewboxRight.SetAndObserveTransformNodeID(self.viewRightToReference.GetID())
    self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID(self.calibrationMarkerToViewboxRight.GetID())
    self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID(self.virtualCalibrationMarkerToCalibrationMarker.GetID())
    self.onSystemStart()


  """
  MicronTracker Calibration Logic
  """

  def onSystemCalibrationStart(self):
    self.layout.SetViewArrangement(8)
    self.needleModel_NeedleTip.GetDisplayNode().SliceIntersectionVisibilityOff()
    self.viewRightToReference.SetAndObserveTransformNodeID('')
    self.viewLeftToReference.SetAndObserveTransformNodeID('')
    self.calibrationMarkerToViewboxRight.SetAndObserveTransformNodeID('')
    self.calibrationMarkerToViewboxLeft.SetAndObserveTransformNodeID('')
    self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID('')
    self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID('')


  def onStartSystemCalibrationClicked(self):
    self.onNewButtonClicked()

    greenSliceWidget = slicer.app.layoutManager().sliceWidget('Green')
    greenSliceWidget.setSliceOrientation('Axial')
    greenSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(self.overlayCalibrationMarkerVolume.GetID())
    slicer.util.getNode('vtkMRMLSliceNodeGreen').SetSliceVisible(False)
    slicer.app.layoutManager().resetSliceViews()

    self.onSystemCalibrationStart()
    self.startSystemCalibrationButton.setEnabled(False)

    self.CM2VBRNode = slicer.util.getNode('CMarkerToViewRight')
    self.CM2VBRMTime = self.CM2VBRNode.GetTransformToWorldMTime()

    self.CM2VBLNode = slicer.util.getNode('CMarkerToViewLeft')
    self.CM2VBLMTime = self.CM2VBLNode.GetTransformToWorldMTime()

    self.VCM2CMNode = slicer.util.getNode('VCMarkerToCMarker')
    self.VCM2CMMTime = self.VCM2CMNode.GetTransformToWorldMTime()

    self.systemCalibrationStopTime = time.time() + 60.0
    self.systemCalibrationStartTime = vtk.vtkTimerLog().GetMTime()

    self.onSystemSamplingTimeout()


  def onSystemSamplingTimeout(self):
    self.labelText = "Capturing transforms for {0:.1f} more seconds... ".format(self.systemCalibrationStopTime - time.time())

    self.CM2VBRMTime = self.CM2VBRNode.GetTransformToWorldMTime()
    if self.CM2VBRMTime > self.systemCalibrationStartTime:
      self.labelText += "CMarkerToViewRight updated. "
    else:
      self.labelText += "CMarkerToViewRight not updated. "

    self.CM2VBLMTime = self.CM2VBLNode.GetTransformToWorldMTime()
    if self.CM2VBLMTime > self.systemCalibrationStartTime:
      self.labelText += "CMarkerToViewLeft updated. "
    else:
      self.labelText += "CMarkerToViewLeft not updated. "

    self.VCM2CMMTime = self.VCM2CMNode.GetTransformToWorldMTime()
    if self.VCM2CMMTime > self.systemCalibrationStartTime:
      self.labelText += "VCMarkerToCMarker updated. "
    else:
      self.labelText += "VCMarkerToCMarker not updated. "

    self.toolbarLabel.setText(self.labelText)

    if (time.time() > self.systemCalibrationStopTime) | (self.CM2VBRMTime > self.systemCalibrationStartTime) & (self.CM2VBLMTime > self.systemCalibrationStartTime) & (self.VCM2CMMTime > self.systemCalibrationStartTime):
      self.onStopSystemCalibration()
    else:
      self.toolbarCalibrationTimer.start()


  def onStopSystemCalibration(self):
    self.updatedTransforms = []
    if self.CM2VBRMTime > self.systemCalibrationStartTime:
      self.updatedTransforms.append("CMarkerToViewRight")

    if self.CM2VBLMTime > self.systemCalibrationStartTime:
      self.updatedTransforms.append("CMarkerToViewLeft")

    if self.VCM2CMMTime > self.systemCalibrationStartTime:
      self.updatedTransforms.append("VCMarkerToCMarker")

    self.labelText = "Capturing stopped. Updated transforms: "
    if not self.updatedTransforms:
      self.labelText += "None."
    else:
      self.labelText += (", ".join(self.updatedTransforms) + ".")

    self.toolbarLabel.setText(self.labelText)
    self.startSystemCalibrationButton.setEnabled(True)

  """
  RealSense Viewbox Calibration Logic
  """

  def zoomYellow(self, factor):
    sliceNode = slicer.util.getNode('vtkMRMLSliceNodeYellow')
    newFOVx = sliceNode.GetFieldOfView()[0] * factor
    newFOVy = sliceNode.GetFieldOfView()[1] * factor
    newFOVz = sliceNode.GetFieldOfView()[2]
    sliceNode.SetFieldOfView(newFOVx, newFOVy, newFOVz)
    sliceNode.UpdateMatrices()


  def drawRealSenseMarkerBackground(self, image, canvasSize_px):
    image.SetDrawColor(self.whiteColour)
    image.FillBox(0, canvasSize_px[0], 0, canvasSize_px[1])
    image.Update()

    return image


  def drawRealSenseBlackBox(self, image, canvasSize_px, rowNum, colNum):
    image.SetDrawColor(self.blackColour)
    image.FillBox((rowNum * canvasSize_px[0] / 8), ((rowNum + 1) * canvasSize_px[0] / 8), (colNum* canvasSize_px[1] / 8), ((colNum + 1) * canvasSize_px[1] / 8))
    image.Update()

    return image


  def drawRealSenseMarker(self, canvasSize_px, markerID):
    image = vtk.vtkImageCanvasSource2D()
    image.SetExtent(0, canvasSize_px[0], 0, canvasSize_px[1], 0, canvasSize_px[2])
    self.drawRealSenseMarkerBackground(image, canvasSize_px)
    self.drawRealSenseMarkerForeground(image, canvasSize_px, markerID)

    return image


  def drawRealSenseMarkerForeground(self, image, canvasSize_px, markerID):

    if markerID == 18:
        self.drawRealSenseBlackBox(image, canvasSize_px, 1, 4)
        self.drawRealSenseBlackBox(image, canvasSize_px, 1, 6)
        self.drawRealSenseBlackBox(image, canvasSize_px, 2, 4)
        self.drawRealSenseBlackBox(image, canvasSize_px, 2, 5)
        self.drawRealSenseBlackBox(image, canvasSize_px, 2, 6)
        self.drawRealSenseBlackBox(image, canvasSize_px, 4, 1)
        self.drawRealSenseBlackBox(image, canvasSize_px, 4, 3)
        self.drawRealSenseBlackBox(image, canvasSize_px, 5, 1)
        self.drawRealSenseBlackBox(image, canvasSize_px, 5, 2)
        self.drawRealSenseBlackBox(image, canvasSize_px, 5, 3)
        self.drawRealSenseBlackBox(image, canvasSize_px, 6, 3)
        self.drawRealSenseBlackBox(image, canvasSize_px, 6, 5)
        self.drawRealSenseBlackBox(image, canvasSize_px, 6, 6)
    else:
        logging.debug('Marker pattern not created yet.')

    return image


  def drawRealSenseMarkerToScreen(self, volumeNode, markerID):
    self.whiteColour = [255, 255, 255, 0]
    self.blackColour = [0, 0, 0, 0]
    self.canvasSize_px = [1601, 1601, 1]

    image = self.drawRealSenseMarker(self.canvasSize_px, markerID)

    imageClip = vtk.vtkImageClip()
    imageClip.ClipDataOn()
    imageClip.SetOutputWholeExtent(0, self.canvasSize_px[0] - 1, 0, self.canvasSize_px[1] - 1, 0, 0)
    imageClip.SetInputConnection(image.GetOutputPort())
    imageClip.Update()

    imageData = imageClip.GetOutput()
    volumeNode.SetAndObserveImageData(imageData)

    spacingFactor = [float(self.parameterNode.GetParameter('ViewboxCalibrationMarkerVolumeSpacing'))] * 3
    volumeNode.SetSpacing(spacingFactor)

    yellowSliceWidget = slicer.app.layoutManager().sliceWidget('Yellow')
    yellowSliceWidget.setSliceOrientation('Axial')
    yellowSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
    slicer.util.getNode('vtkMRMLSliceNodeYellow').SetSliceOrigin(-45, 85, 0)


  def onViewboxCalibrationStart(self):
    self.layout.SetViewArrangement(7)
    self.needleModel_NeedleTip.GetDisplayNode().SliceIntersectionVisibilityOff()
    self.trackerToReference.SetAndObserveTransformNodeID('')
    self.temporaryMarkerToTracker.SetAndObserveTransformNodeID('')
    self.calibrationMarkerToTemporaryMarker.SetAndObserveTransformNodeID('')
    self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID('')
    self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID('')


  def onStartViewboxCalibrationClicked(self):
    self.onNewButtonClicked()

    yellowSliceWidget = slicer.app.layoutManager().sliceWidget('Yellow')
    yellowSliceWidget.setSliceOrientation('Axial')
    yellowSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(self.viewboxCalibrationMarkerVolume.GetID())
    slicer.util.getNode('vtkMRMLSliceNodeYellow').SetSliceVisible(False)
    slicer.app.layoutManager().resetSliceViews()

    self.onViewboxCalibrationStart()

    self.startViewboxCalibrationButton.setEnabled(False)
    self.temporaryMarkerToTrackerNode = slicer.util.getNode('TMarkerToTracker')
    self.temporaryMarkerToTrackerModifiedTime = self.temporaryMarkerToTrackerNode.GetTransformToWorldMTime()

    self.calibrationMarkerToTemporaryMarkerNode = slicer.util.getNode('CMarkerToTMarker')
    self.calibrationMarkerToTemporaryMarkerModifiedTime = self.calibrationMarkerToTemporaryMarkerNode.GetTransformToWorldMTime()

    self.viewboxCalibrationStopTime = time.time() + 60.0
    self.viewboxCalibrationStartTime = vtk.vtkTimerLog().GetMTime()
    self.onViewboxSamplingTimeout()


  def onViewboxSamplingTimeout(self):
    self.labelText = "Capturing transforms for {0:.1f} more seconds... ".format(self.viewboxCalibrationStopTime - time.time())

    self.temporaryMarkerToTrackerModifiedTime = self.temporaryMarkerToTrackerNode.GetTransformToWorldMTime()
    if self.temporaryMarkerToTrackerModifiedTime > self.viewboxCalibrationStartTime:
      self.labelText += "TMarkerToTracker updated. "
    else:
      self.labelText += "TMarkerToTracker not updated. "

    self.calibrationMarkerToTemporaryMarkerModifiedTime = self.calibrationMarkerToTemporaryMarkerNode.GetTransformToWorldMTime()
    if self.calibrationMarkerToTemporaryMarkerModifiedTime > self.viewboxCalibrationStartTime:
      self.labelText += "CMarkerToTMarker updated. "
    else:
      self.labelText += "CMarkerToTMarker not updated. "

    self.toolbarLabel.setText(self.labelText)

    if (time.time() > self.viewboxCalibrationStopTime) | ((self.temporaryMarkerToTrackerModifiedTime > self.viewboxCalibrationStartTime) & (self.calibrationMarkerToTemporaryMarkerModifiedTime > self.viewboxCalibrationStartTime)):
      self.onStopViewboxCalibration()
    else:
      self.viewboxCalibrationTimer.start()


  def onStopViewboxCalibration(self):
    self.updatedTransforms = []
    if self.temporaryMarkerToTrackerModifiedTime > self.viewboxCalibrationStartTime:
      self.updatedTransforms.append("TMarkerToTracker")

    if self.calibrationMarkerToTemporaryMarkerModifiedTime > self.viewboxCalibrationStartTime:
      self.updatedTransforms.append("CMarkerToTMarker")

    self.labelText = "Capturing stopped. Updated transforms: "
    if not self.updatedTransforms:
      self.labelText += "None."
    else:
      self.labelText += (", ".join(self.updatedTransforms) + ".")

    self.toolbarLabel.setText(self.labelText)
    self.startViewboxCalibrationButton.setEnabled(True)


  """
  RealSense Overlay Calibration Logic
  """

  def zoomGreen(self, factor):
    sliceNode = slicer.util.getNode('vtkMRMLSliceNodeGreen')
    newFOVx = sliceNode.GetFieldOfView()[0] * factor
    newFOVy = sliceNode.GetFieldOfView()[1] * factor
    newFOVz = sliceNode.GetFieldOfView()[2]
    sliceNode.SetFieldOfView(newFOVx, newFOVy, newFOVz)
    sliceNode.UpdateMatrices()


  def drawMarker(self, canvasSize_px):
    circleRadius_px = max(canvasSize_px[0], canvasSize_px[1]) / 10
    leftMarkerX_px =  85 * canvasSize_px[0] / 100
    leftMarkerY_px =  50 * canvasSize_px[1] / 100
    rightMarkerX_px = 15 * canvasSize_px[0] / 100
    rightMarkerY_px = 50 * canvasSize_px[1] / 100
    upperMarkerX_px = 55 * canvasSize_px[0] / 100
    upperMarkerY_px = 85 * canvasSize_px[1] / 100
    lowerMarkerX_px = 55 * canvasSize_px[0] / 100
    lowerMarkerY_px = 15 * canvasSize_px[1] / 100
    self.whiteColour = [255, 255, 255, 0]
    self.blackColour = [0, 0, 0, 0]

    image = vtk.vtkImageCanvasSource2D()
    image.SetExtent(0, canvasSize_px[0], 0, canvasSize_px[1], 0, canvasSize_px[2])

    self.drawMarkerBackground(image, canvasSize_px, self.whiteColour)

    self.drawCircle(image, leftMarkerX_px, leftMarkerY_px, circleRadius_px, self.blackColour)
    self.drawInnerMarkerRightUpper(image, leftMarkerX_px, leftMarkerY_px, circleRadius_px, self.blackColour)

    self.drawCircle(image, upperMarkerX_px, upperMarkerY_px, circleRadius_px, self.blackColour)
    self.drawInnerMarkerRightUpper(image, upperMarkerX_px, upperMarkerY_px, circleRadius_px, self.blackColour)

    self.drawCircle(image, rightMarkerX_px, rightMarkerY_px, circleRadius_px, self.blackColour)
    self.drawInnerMarkerLeftUpper(image, rightMarkerX_px, rightMarkerY_px, circleRadius_px, self.blackColour)

    self.drawCircle(image, lowerMarkerX_px, lowerMarkerY_px, circleRadius_px, self.blackColour)
    self.drawInnerMarkerLeftUpper(image, lowerMarkerX_px, lowerMarkerY_px, circleRadius_px, self.blackColour)

    return image


  def drawMarkerBackground(self, image, canvasSize, colour):
    image.SetDrawColor(colour)
    image.FillBox(0, canvasSize[0] - 1, 0, canvasSize[1] - 1) # Keeps the background inside the extent.
    image.Update()

    return image


  def drawCircle(self, image, xCoordinate, yCoordinate, radius, colour):
    image.SetDrawColor(colour)
    image.DrawCircle(xCoordinate, yCoordinate, radius)
    image.Update()

    return image


  def drawBar(self, image, xStart, yStart, xStop, yStop, colour):
    image.SetDrawColor(colour)
    image.DrawSegment(xStart, yStart, xStop, yStop)
    image.Update()

    return image


  def drawTriangleFill(self, image, xCoordinate, yCoordinate, colour):
    image.SetDrawColor(colour)
    image.FillPixel(xCoordinate, yCoordinate)
    image.Update()

    return image


  def drawCrossRightUpper(self, image, xCoordinate, yCoordinate, radius, colour):
    self.drawBar(image, xCoordinate, yCoordinate - radius, xCoordinate, yCoordinate - 1, colour)
    self.drawBar(image, xCoordinate - 1, yCoordinate, xCoordinate - 1, yCoordinate + radius, colour)
    self.drawBar(image, xCoordinate - radius, yCoordinate, xCoordinate - 1, yCoordinate, colour)
    self.drawBar(image, xCoordinate, yCoordinate - 1, xCoordinate + radius, yCoordinate - 1, colour)

    return image


  def drawCrossLeftUpper(self, image, xCoordinate, yCoordinate, radius, colour):
    self.drawBar(image, xCoordinate, yCoordinate, xCoordinate, yCoordinate - radius + 1, colour)
    self.drawBar(image, xCoordinate + 1, yCoordinate + 1, xCoordinate + 1, yCoordinate + radius, colour)
    self.drawBar(image, xCoordinate, yCoordinate, xCoordinate - radius + 1, yCoordinate, colour)
    self.drawBar(image, xCoordinate + 1, yCoordinate + 1, xCoordinate + radius, yCoordinate + 1, colour)

    return image


  def drawInnerMarkerRightUpper(self, image, xCoordinate, yCoordinate, radius, colour):
    self.drawCrossRightUpper(image, xCoordinate, yCoordinate, radius, colour)
    self.drawTriangleFill(image, xCoordinate - 2, yCoordinate + 2, colour)
    self.drawTriangleFill(image, xCoordinate + 2, yCoordinate - 2, colour)

    return image


  def drawInnerMarkerLeftUpper(self, image, xCoordinate, yCoordinate, radius, colour):
    self.drawCrossLeftUpper(image, xCoordinate, yCoordinate, radius, colour)
    self.drawTriangleFill(image, xCoordinate + 2, yCoordinate + 2, colour)
    self.drawTriangleFill(image, xCoordinate - 2, yCoordinate - 2, colour)

    return image


  def drawMarkerToVolume(self, volumeNode):
    canvasSize = [1000, 800, 0]

    image = self.drawMarker(canvasSize)

    imageClip = vtk.vtkImageClip()
    imageClip.ClipDataOn()
    imageClip.SetOutputWholeExtent(0, canvasSize[0] - 1, 0, canvasSize[1] - 1, 0, 0)
    imageClip.SetInputConnection(image.GetOutputPort())
    imageClip.Update()

    imageData = imageClip.GetOutput()
    volumeNode.SetAndObserveImageData(imageData)

    spacingFactor = [float(self.parameterNode.GetParameter('OverlayCalibrationMarkerVolumeSpacing'))] * 3
    volumeNode.SetSpacing(spacingFactor)

    greenSliceWidget = slicer.app.layoutManager().sliceWidget('Green')
    greenSliceWidget.setSliceOrientation('Axial')
    greenSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())


  def onOverlayCalibrationStart(self):
    self.layout.SetViewArrangement(8)
    self.needleModel_NeedleTip.GetDisplayNode().SliceIntersectionVisibilityOff()
    self.trackerToReference.SetAndObserveTransformNodeID('')
    self.temporaryMarkerToTracker.SetAndObserveTransformNodeID('')
    self.calibrationMarkerToTemporaryMarker.SetAndObserveTransformNodeID('')
    self.virtualCalibrationMarkerToCalibrationMarker.SetAndObserveTransformNodeID('')
    self.calibrationVolumeToVirtualCalibrationMarker.SetAndObserveTransformNodeID('')


  def onStartOverlayCalibrationClicked(self):
    self.onNewButtonClicked()

    greenSliceWidget = slicer.app.layoutManager().sliceWidget('Green')
    greenSliceWidget.setSliceOrientation('Axial')
    greenSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(self.overlayCalibrationMarkerVolume.GetID())
    slicer.util.getNode('vtkMRMLSliceNodeGreen').SetSliceVisible(False)
    slicer.app.layoutManager().resetSliceViews()

    self.onOverlayCalibrationStart()
    self.startOverlayCalibrationButton.setEnabled(False)

    self.virtualCalibrationMarkerToCalibrationMarkerNode = slicer.util.getNode('VCMarkerToCMarker')
    self.virtualCalibrationMarkerToCalibrationMarkerModifiedTime = self.virtualCalibrationMarkerToCalibrationMarkerNode.GetTransformToWorldMTime()

    self.overlayCalibrationStopTime = time.time() + 60.0
    self.overlayCalibrationStartTime = vtk.vtkTimerLog().GetMTime()

    self.onOverlaySamplingTimeout()


  def onOverlaySamplingTimeout(self):
    self.labelText = "Capturing transforms for {0:.1f} more seconds... ".format(self.overlayCalibrationStopTime - time.time())

    if self.virtualCalibrationMarkerToCalibrationMarkerModifiedTime > self.overlayCalibrationStartTime:
      self.labelText += "VCMarkerToCMarker updated. "
    else:
      self.labelText += "VCMarkerToCMarker not updated. "

    self.toolbarLabel.setText(self.labelText)

    if (time.time() > self.overlayCalibrationStopTime) | (self.virtualCalibrationMarkerToCalibrationMarkerModifiedTime > self.overlayCalibrationStartTime):
      self.onStopOverlayCalibration()
    else:
      self.overlayCalibrationTimer.start()


  def onStopOverlayCalibration(self):
    self.updatedTransforms = []

    if self.virtualCalibrationMarkerToCalibrationMarkerModifiedTime > self.overlayCalibrationStartTime:
      self.updatedTransforms.append("VCMarkerToCMarker")

    self.labelText = "Capturing stopped. Updated transforms: "
    if not self.updatedTransforms:
      self.labelText += "None."
    else:
      self.labelText += (", ".join(self.updatedTransforms) + ".")

    self.toolbarLabel.setText(self.labelText)
    self.startOverlayCalibrationButton.setEnabled(True)


  """
  Pivot and Spin Calibration Logic
  """

  def onNeedlePivotClicked(self):
    logging.debug('onNeedlePivotClicked')
    self.onNewButtonClicked()
    self.layout.SetViewArrangement(4)
    self.needleCalibrationButton.setEnabled(False)
    self.startPivotCalibration('NeedleTipToNeedle', self.needleToReference, self.needleTipToNeedle)


  def onPivotSamplingTimeout(self):
    self.toolbarLabel.setText("Pivot calibrating for {0:.1f} more seconds".format(self.pivotCalibrationStopTime-time.time()))
    if (time.time() < self.pivotCalibrationStopTime):
      self.toolbarPivotTimer.start()
    else:
      self.onStopPivotCalibration()


  def startPivotCalibration(self, toolToReferenceTransformName, toolToReferenceTransformNode, toolTipToToolTransformNode):
    self.pivotCalibrationResultTargetNode = toolTipToToolTransformNode
    self.pivotCalibrationResultTargetName = toolToReferenceTransformName
    self.pivotCalibrationLogic.SetAndObserveTransformNode(toolToReferenceTransformNode);
    self.pivotCalibrationStopTime = time.time() + float(self.parameterNode.GetParameter('PivotCalibrationDurationSec'))
    self.pivotCalibrationLogic.SetRecordingState(True)
    self.onPivotSamplingTimeout()


  def onStopPivotCalibration(self):
    self.pivotCalibrationLogic.SetRecordingState(False)
    self.needleCalibrationButton.setEnabled(True)
    calibrationSuccess = self.pivotCalibrationLogic.ComputePivotCalibration()

    if not calibrationSuccess:
      self.toolbarLabel.setText("Calibration failed: " + self.pivotCalibrationLogic.GetErrorText())
      self.pivotCalibrationLogic.ClearToolToReferenceMatrices()
      return

    if (self.pivotCalibrationLogic.GetPivotRMSE() >= float(self.parameterNode.GetParameter('PivotCalibrationErrorThresholdMm'))):
      self.toolbarLabel.setText("Calibration failed, error = {0:.2f} mm, please calibrate again.".format(self.pivotCalibrationLogic.GetPivotRMSE()))
      self.pivotCalibrationLogic.ClearToolToReferenceMatrices()
      return

    tooltipToToolMatrix = vtk.vtkMatrix4x4()
    self.pivotCalibrationLogic.GetToolTipToToolMatrix(tooltipToToolMatrix)
    self.pivotCalibrationLogic.ClearToolToReferenceMatrices()
    self.pivotCalibrationResultTargetNode.SetMatrixTransformToParent(tooltipToToolMatrix)
    self.logic.writeTransformToSettings(self.pivotCalibrationResultTargetName, tooltipToToolMatrix, self.configurationName)
    self.toolbarLabel.setText("Calibration completed, error = {0:.2f} mm.".format(self.pivotCalibrationLogic.GetPivotRMSE()))
    logging.debug("Pivot calibration completed. Tool: {0}. RMSE = {1:.2f} mm.".format(self.pivotCalibrationResultTargetNode.GetName(), self.pivotCalibrationLogic.GetPivotRMSE()))


  def onNeedleSpinClicked(self):
    logging.debug('onNeedleSpinClicked')
    self.onNewButtonClicked()
    self.layout.SetViewArrangement(4)
    self.needleCalibrationButton.setEnabled(False)
    self.startSpinCalibration('NeedleTipToNeedle', self.needleToReference, self.needleTipToNeedle)


  def onSpinSamplingTimeout(self):
    self.toolbarLabel.setText("Spin calibrating for {0:.1f} more seconds".format(self.spinCalibrationStopTime-time.time()))
    if (time.time() < self.spinCalibrationStopTime):
      self.toolbarSpinTimer.start()
    else:
      self.onStopSpinCalibration()


  def startSpinCalibration(self, toolToReferenceTransformName, toolToReferenceTransformNode, toolTipToToolTransformNode):
    self.spinCalibrationResultTargetNode = toolTipToToolTransformNode
    self.spinCalibrationResultTargetName = toolToReferenceTransformName
    self.spinCalibrationLogic.SetAndObserveTransformNode(toolToReferenceTransformNode);
    self.spinCalibrationStopTime = time.time() + float(self.parameterNode.GetParameter('SpinCalibrationDurationSec'))
    self.spinCalibrationLogic.SetRecordingState(True)
    self.onSpinSamplingTimeout()


  def onStopSpinCalibration(self):
    self.spinCalibrationLogic.SetRecordingState(False)
    self.needleCalibrationButton.setEnabled(True)
    calibrationSuccess = self.spinCalibrationLogic.ComputeSpinCalibration()

    if not calibrationSuccess:
      self.toolbarLabel.setText("Calibration failed: " + self.spinCalibrationLogic.GetErrorText())
      self.spinCalibrationLogic.ClearToolToReferenceMatrices()
      return

    if (self.spinCalibrationLogic.GetSpinRMSE() >= float(self.parameterNode.GetParameter('SpinCalibrationErrorThresholdMm'))):
      self.toolbarLabel.setText("Calibration failed, error = {0:.3f} mm, please calibrate again.".format(self.spinCalibrationLogic.GetSpinRMSE()))
      self.spinCalibrationLogic.ClearToolToReferenceMatrices()
      return

    needleTipToNeedleMatrix = vtk.vtkMatrix4x4()
    needleTipToNeedleRotationMatrix = vtk.vtkMatrix4x4()
    self.needleTipToNeedle.GetMatrixTransformToParent(needleTipToNeedleMatrix)
    needleTipToNeedleMatrixTranslation = vtk.vtkMatrix4x4()
    needleTipToNeedleMatrixTranslation.SetElement(0, 3, needleTipToNeedleMatrix.GetElement(0, 3))
    needleTipToNeedleMatrixTranslation.SetElement(1, 3, needleTipToNeedleMatrix.GetElement(1, 3))
    needleTipToNeedleMatrixTranslation.SetElement(2, 3, needleTipToNeedleMatrix.GetElement(2, 3))
    self.spinCalibrationLogic.GetToolTipToToolRotation(needleTipToNeedleRotationMatrix)
    vtk.vtkMatrix4x4().Multiply4x4(needleTipToNeedleMatrixTranslation, needleTipToNeedleRotationMatrix, needleTipToNeedleMatrix)
    self.needleTipToNeedle.SetMatrixTransformToParent(needleTipToNeedleMatrix)
    self.spinCalibrationLogic.ClearToolToReferenceMatrices()
    self.logic.writeTransformToSettings(self.spinCalibrationResultTargetName, needleTipToNeedleMatrix, self.configurationName)
    self.toolbarLabel.setText("Calibration completed, error = {0:.3f} mm.".format(self.spinCalibrationLogic.GetPivotRMSE()))
    logging.debug("Spin calibration completed. Tool: {0}. RMSE = {1:.3f} mm.".format(self.spinCalibrationResultTargetNode.GetName(), self.spinCalibrationLogic.GetSpinRMSE()))


  """
  Patient Registration Logic
  """

  def onPatientRegistrationClicked(self):
    self.onNewButtonClicked()
    self.layout.SetViewArrangement(1)

    redSliceWidget = slicer.app.layoutManager().sliceWidget('Red')
    redSliceWidget.setSliceOrientation('Axial')
    redSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(self.patientVolume.GetID())
    slicer.util.getNode('vtkMRMLSliceNodeRed').SetSliceVisible(True)
    yellowSliceWidget = slicer.app.layoutManager().sliceWidget('Yellow')
    yellowSliceWidget.setSliceOrientation('Sagittal')
    yellowSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(self.patientVolume.GetID())
    slicer.util.getNode('vtkMRMLSliceNodeYellow').SetSliceVisible(True)
    greenSliceWidget = slicer.app.layoutManager().sliceWidget('Green')
    greenSliceWidget.setSliceOrientation('Coronal')
    greenSliceWidget.sliceLogic().GetSliceCompositeNode().SetBackgroundVolumeID(self.patientVolume.GetID())
    slicer.util.getNode('vtkMRMLSliceNodeGreen').SetSliceVisible(True)

    slicer.app.layoutManager().resetSliceViews()

    self.referencePointsNode = slicer.util.getNode('ReferencePoints')
    if not self.referencePointsNode:
      self.markupsLogic.AddNewFiducialNode('ReferencePoints')
      self.referencePointsNode = slicer.util.getNode('ReferencePoints')
      referencePointsDisplayNode = self.referencePointsNode.GetMarkupsDisplayNode()
      referencePointsDisplayNode.SetSelectedColor(0, 0, 1)

    self.fiducialsToCollect = self.rasPointsNode.GetNumberOfFiducials()
    self.fiducialsCollected = self.referencePointsNode.GetNumberOfFiducials()

    self.fiducialRegistrationWizardNode.SetRegistrationModeToRigid()
    self.fiducialRegistrationWizardNode.SetAndObserveFromFiducialListNodeId(self.referencePointsNode.GetID())
    self.fiducialRegistrationWizardNode.SetAndObserveToFiducialListNodeId(self.rasPointsNode.GetID())
    self.fiducialRegistrationWizardNode.SetOutputTransformNodeId(self.referenceToRas.GetID())


  def onAddReferenceFiducialClicked(self):
    self.onPatientRegistrationClicked()
    self.onNewButtonClicked()
    self.patientRegistrationButton.setEnabled(False)
    logging.debug("Adding reference fiducial.")
    if self.fiducialsCollected < self.fiducialsToCollect:
      self.startPatientRegistration()
    else:
      self.toolbarLabel.setText("All reference points collected!")


  def startPatientRegistration(self):
    self.patientRegistrationPointStopTime = time.time() + float(self.parameterNode.GetParameter('PatientRegistrationFiducialAcquisitionDurationSec'))
    self.onPatientRegistrationSamplingTimeout()


  def onPatientRegistrationSamplingTimeout(self):
    self.toolbarLabel.setText("Waiting to capture Reference Point for {0:.1f} more seconds.".format(self.patientRegistrationPointStopTime-time.time()))
    if (time.time() < self.patientRegistrationPointStopTime):
      self.toolbarPatientRegistrationTimer.start()
    else:
      self.onStopPatientRegistration()


  def onStopPatientRegistration(self):
    self.fiducialRegistrationLogic.AddFiducial(self.needleTipToNeedle, self.referencePointsNode)
    self.fiducialsCollected = self.referencePointsNode.GetNumberOfFiducials()
    self.patientRegistrationButton.setEnabled(True)
    if self.fiducialsCollected < self.fiducialsToCollect:
      self.toolbarLabel.setText("Reference Point captured. Please capture remaining {0} point(s).".format(self.fiducialsToCollect-self.fiducialsCollected))
    elif self.fiducialsCollected == self.fiducialsToCollect:
      self.fiducialRegistrationLogic.UpdateCalibration(self.fiducialRegistrationWizardNode)
      self.toolbarLabel.setText(self.fiducialRegistrationLogic.GetOutputMessage(self.fiducialRegistrationWizardNode.GetID()))
      self.logic.writeTransformToSettings('ReferenceToRas', self.referenceToRas.GetMatrixTransformToParent(), self.configurationName)


  def onDeleteLastFiducialClicked(self):
    self.onPatientRegistrationClicked()
    self.onNewButtonClicked()
    logging.debug("Deleting last reference fiducial...")
    if self.fiducialsCollected == 0:
      logging.debug("No reference fiducial to delete.")
    else:
      self.referencePointsNode.RemoveMarkup(self.fiducialsCollected - 1)


  def onDeleteAllFiducialsClicked(self):
    self.onPatientRegistrationClicked()
    self.onNewButtonClicked()
    logging.debug("Deleting all reference fiducials...")
    if self.fiducialsCollected == 0:
      logging.debug("No reference fiducials to delete.")
    else:
      self.referencePointsNode.RemoveAllMarkups()


  def onClearRef2RasClicked(self):
    self.onPatientRegistrationClicked()
    self.onNewButtonClicked()
    logging.debug("Clearing Reference to RAS transform")
    m = self.logic.createMatrixFromString('1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
    self.referenceToRas.SetMatrixTransformToParent(m)


  """
  Show Slicer interface and Save buttons
  """

  def onShowSlicerInterfaceClicked(self):
    self.onNewButtonClicked()
    self.showToolbars(True)
    self.showModulePanel(True)
    self.showMenuBar(True)
    slicer.util.mainWindow().showMaximized()
    settings = qt.QSettings()
    settings.setValue('MainWindow/RestoreGeometry', 'true')
    self.viewArrangementOnExit = self.layout.GetViewArrangement()
    self.layout.SetViewArrangement(1)


  def onShowFullscreenButton(self):
    self.showFullScreen()
    if self.viewArrangementOnExit:
      self.layout.SetViewArrangement(self.viewArrangementOnExit)


  def onSaveClicked(self):
    self.onNewButtonClicked()
    node = self.logic.getParameterNode()
    sceneSaveDirectory = node.GetParameter('SavedScenesDirectory')
    sceneSaveDirectory = sceneSaveDirectory + "/" + self.logic.moduleName + "-" + time.strftime("%Y%m%d-%H%M%S")
    logging.info("Saving scene to: {0}".format(sceneSaveDirectory))
    if not os.access(sceneSaveDirectory, os.F_OK):
      os.makedirs(sceneSaveDirectory)
    applicationLogic = slicer.app.applicationLogic()
    if applicationLogic.SaveSceneToSlicerDataBundleDirectory(sceneSaveDirectory, None):
      logging.info("Scene saved to: {0}".format(sceneSaveDirectory))
    else:
      logging.error("Scene saving failed")


  """
  Resetter for all buttons, timers and toolbar label.
  """

  def onNewButtonClicked(self):
    self.startLeftNavigationButton.setEnabled(True)
    self.startRightNavigationButton.setEnabled(True)
    self.startSystemCalibrationButton.setEnabled(True)
    self.startNavigationButton.setEnabled(True)

    self.startOverlayCalibrationButton.setEnabled(True)
    self.startViewboxCalibrationButton.setEnabled(True)

    self.needleCalibrationButton.setEnabled(True)

    self.patientRegistrationButton.setEnabled(True)

    self.showSlicerInterfaceButton.setEnabled(True)
    self.saveButton.setEnabled(True)

    self.toolbarPivotTimer.stop()
    self.toolbarSpinTimer.stop()
    self.toolbarPatientRegistrationTimer.stop()
    self.overlayCalibrationTimer.stop()
    self.viewboxCalibrationTimer.stop()
    self.toolbarCalibrationTimer.stop()

    self.toolbarLabel.setText('')
