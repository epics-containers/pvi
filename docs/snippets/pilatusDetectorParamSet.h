#ifndef PilatusDetectorParamSet_H
#define PilatusDetectorParamSet_H

#include "ADDriverParamSet.h"

#define PilatusResetPowerString "RESET_POWER"
#define PilatusThresholdApplyString "THRESHOLD_APPLY"
#define PilatusImageFileTmotString "IMAGE_FILE_TMOT"
#define PilatusWavelengthString "WAVELENGTH"
#define PilatusEnergyLowString "ENERGY_LOW"
#define PilatusEnergyHighString "ENERGY_HIGH"
#define PilatusDetDistString "DET_DIST"
#define PilatusDetVOffsetString "DET_VOFFSET"
#define PilatusBeamXString "BEAM_X"
#define PilatusBeamYString "BEAM_Y"
#define PilatusFluxString "FLUX"
#define PilatusFilterTransmString "FILTER_TRANSM"
#define PilatusStartAngleString "START_ANGLE"
#define PilatusAngleIncrString "ANGLE_INCR"
#define PilatusDet2thetaString "DET_2THETA"
#define PilatusPolarizationString "POLARIZATION"
#define PilatusAlphaString "ALPHA"
#define PilatusKappaString "KAPPA"
#define PilatusPhiString "PHI"
#define PilatusPhiIncrString "PHI_INCR"
#define PilatusChiString "CHI"
#define PilatusChiIncrString "CHI_INCR"
#define PilatusOmegaString "OMEGA"
#define PilatusOmegaIncrString "OMEGA_INCR"
#define PilatusOscillAxisString "OSCILL_AXIS"
#define PilatusNumOscillString "NUM_OSCILL"
#define PilatusBadPixelFileString "BAD_PIXEL_FILE"
#define PilatusFlatFieldFileString "FLAT_FIELD_FILE"
#define PilatusCbfTemplateFileString "CBFTEMPLATEFILE"
#define PilatusHeaderStringString "HEADERSTRING"
#define PilatusArmedString "ARMED"
#define PilatusNumBadPixelsString "NUM_BAD_PIXELS"
#define PilatusFlatFieldValidString "FLAT_FIELD_VALID"
#define PilatusPixelCutOffString "PIXEL_CUTOFF"
#define PilatusThTemp0String "TH_TEMP_0"
#define PilatusThTemp1String "TH_TEMP_1"
#define PilatusThTemp2String "TH_TEMP_2"
#define PilatusThHumid0String "TH_HUMID_0"
#define PilatusThHumid1String "TH_HUMID_1"
#define PilatusThHumid2String "TH_HUMID_2"
#define PilatusTvxVersionString "TVXVERSION"
#define PilatusResetPowerTimeString "RESET_POWER_TIME"
#define PilatusDelayTimeString "DELAY_TIME"
#define PilatusThresholdString "THRESHOLD"
#define PilatusThresholdAutoApplyString "THRESHOLD_AUTO_APPLY"
#define PilatusEnergyString "ENERGY"
#define PilatusMinFlatFieldString "MIN_FLAT_FIELD"
#define PilatusGapFillString "GAP_FILL"
#define ProgressBarTestString "PROGRESS"

const std::string pilatusParamTree = \
"{\"parameters\":[{\"type\": \"Group\", \"name\": \"ComponentGroupOne\", \"label\": \"\", \"layout\": {\"type\": \"Grid\", \"labelled\": true}, \"children\": [{\"type\": \"SignalW\", \"name\": \"WaitForPlugins\", \"label\": \"\", \"pv\": \"WaitForPlugins\", \"widget\": {\"type\": \"CheckBox\"}}, {\"type\": \"SignalW\", \"name\": \"EmptyFreeList\", \"label\": \"\", \"pv\": \"EmptyFreeList\", \"widget\": {\"type\": \"CheckBox\"}}, {\"type\": \"SignalW\", \"name\": \"NDAttributesMacros\", \"label\": \"\", \"pv\": \"NDAttributesMacros\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"NDAttributesFile\", \"label\": \"\", \"pv\": \"NDAttributesFile\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"ADCoreVersion\", \"label\": \"\", \"pv\": \"ADCoreVersion_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"DriverVersion\", \"label\": \"\", \"pv\": \"DriverVersion_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"PortName\", \"label\": \"\", \"pv\": \"PortName_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Manufacturer\", \"label\": \"\", \"pv\": \"Manufacturer_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Model\", \"label\": \"\", \"pv\": \"Model_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"SerialNumber\", \"label\": \"\", \"pv\": \"SerialNumber_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"SDKVersion\", \"label\": \"\", \"pv\": \"SDKVersion_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"FirmwareVersion\", \"label\": \"\", \"pv\": \"FirmwareVersion_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"AcquireBusyCB\", \"label\": \"\", \"pv\": \"AcquireBusyCB\", \"widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"BayerPattern\", \"label\": \"\", \"pv\": \"BayerPattern_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"ArraySizeX\", \"label\": \"\", \"pv\": \"ArraySizeX_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"ArraySizeY\", \"label\": \"\", \"pv\": \"ArraySizeY_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"ArraySizeZ\", \"label\": \"\", \"pv\": \"ArraySizeZ_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"ArraySize\", \"label\": \"\", \"pv\": \"ArraySize_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Codec\", \"label\": \"\", \"pv\": \"Codec_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"CompressedSize\", \"label\": \"\", \"pv\": \"CompressedSize_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"UniqueId\", \"label\": \"\", \"pv\": \"UniqueId_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"TimeStamp\", \"label\": \"\", \"pv\": \"TimeStamp_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"EpicsTSSec\", \"label\": \"\", \"pv\": \"EpicsTSSec_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"EpicsTSNsec\", \"label\": \"\", \"pv\": \"EpicsTSNsec_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"NDAttributesStatus\", \"label\": \"\", \"pv\": \"NDAttributesStatus\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"PoolMaxMem\", \"label\": \"\", \"pv\": \"PoolMaxMem\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"PoolUsedMem\", \"label\": \"\", \"pv\": \"PoolUsedMem\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"PoolAllocBuffers\", \"label\": \"\", \"pv\": \"PoolAllocBuffers\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"PoolFreeBuffers\", \"label\": \"\", \"pv\": \"PoolFreeBuffers\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"NumQueuedArrays\", \"label\": \"\", \"pv\": \"NumQueuedArrays\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"Acquire\", \"label\": \"\", \"pv\": \"Acquire\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"\", \"read_widget\": null}, {\"type\": \"SignalRW\", \"name\": \"NDimensions\", \"label\": \"\", \"pv\": \"NDimensions\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"NDimensions_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"Dimensions\", \"label\": \"\", \"pv\": \"Dimensions\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"Dimensions_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"DataType\", \"label\": \"\", \"pv\": \"DataType\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"DataType_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ColorMode\", \"label\": \"\", \"pv\": \"ColorMode\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"ColorMode_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ArrayCounter\", \"label\": \"\", \"pv\": \"ArrayCounter\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"ArrayCounter_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ArrayCallbacks\", \"label\": \"\", \"pv\": \"ArrayCallbacks\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"ArrayCallbacks_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"FilePathExists\", \"label\": \"\", \"pv\": \"FilePathExists_RBV\", \"widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"FullFileName\", \"label\": \"\", \"pv\": \"FullFileName_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"NumCaptured\", \"label\": \"\", \"pv\": \"NumCaptured_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"WriteStatus\", \"label\": \"\", \"pv\": \"WriteStatus\", \"widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"WriteMessage\", \"label\": \"\", \"pv\": \"WriteMessage\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"FilePath\", \"label\": \"\", \"pv\": \"FilePath\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"FilePath_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"CreateDirectory\", \"label\": \"\", \"pv\": \"CreateDirectory\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"CreateDirectory_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"FileName\", \"label\": \"\", \"pv\": \"FileName\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"FileName_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"FileNumber\", \"label\": \"\", \"pv\": \"FileNumber\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"\", \"read_widget\": null}, {\"type\": \"SignalRW\", \"name\": \"AutoIncrement\", \"label\": \"\", \"pv\": \"AutoIncrement\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"AutoIncrement_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"FileTemplate\", \"label\": \"\", \"pv\": \"FileTemplate\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"FileTemplate_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"AutoSave\", \"label\": \"\", \"pv\": \"AutoSave\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"AutoSave_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"WriteFile\", \"label\": \"\", \"pv\": \"WriteFile\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"WriteFile_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"ReadFile\", \"label\": \"\", \"pv\": \"ReadFile\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"ReadFile_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"FileFormat\", \"label\": \"\", \"pv\": \"FileFormat\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"FileFormat_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"FileWriteMode\", \"label\": \"\", \"pv\": \"FileWriteMode\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"FileWriteMode_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"Capture\", \"label\": \"\", \"pv\": \"Capture\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"Capture_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"NumCapture\", \"label\": \"\", \"pv\": \"NumCapture\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"NumCapture_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"DeleteDriverFile\", \"label\": \"\", \"pv\": \"DeleteDriverFile\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"DeleteDriverFile_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"LazyOpen\", \"label\": \"\", \"pv\": \"LazyOpen\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"LazyOpen_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"TempSuffix\", \"label\": \"\", \"pv\": \"TempSuffix\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"TempSuffix_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"ReadStatus\", \"label\": \"\", \"pv\": \"ReadStatus\", \"widget\": {\"type\": \"CheckBox\"}}, {\"type\": \"SignalR\", \"name\": \"MaxSizeX\", \"label\": \"\", \"pv\": \"MaxSizeX_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"MaxSizeY\", \"label\": \"\", \"pv\": \"MaxSizeY_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"TimeRemaining\", \"label\": \"\", \"pv\": \"TimeRemaining_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"NumExposuresCounter\", \"label\": \"\", \"pv\": \"NumExposuresCounter_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"NumImagesCounter\", \"label\": \"\", \"pv\": \"NumImagesCounter_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"DetectorState\", \"label\": \"\", \"pv\": \"DetectorState_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"StatusMessage\", \"label\": \"\", \"pv\": \"StatusMessage_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"StringToServer\", \"label\": \"\", \"pv\": \"StringToServer_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"StringFromServer\", \"label\": \"\", \"pv\": \"StringFromServer_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"ShutterStatus\", \"label\": \"\", \"pv\": \"ShutterStatus_RBV\", \"widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"ShutterControlEPICS\", \"label\": \"\", \"pv\": \"ShutterControlEPICS\", \"widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"TemperatureActual\", \"label\": \"\", \"pv\": \"TemperatureActual\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"BinX\", \"label\": \"\", \"pv\": \"BinX\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"BinX_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"BinY\", \"label\": \"\", \"pv\": \"BinY\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"BinY_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"MinX\", \"label\": \"\", \"pv\": \"MinX\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"MinX_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"MinY\", \"label\": \"\", \"pv\": \"MinY\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"MinY_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"SizeX\", \"label\": \"\", \"pv\": \"SizeX\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"SizeX_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"SizeY\", \"label\": \"\", \"pv\": \"SizeY\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"SizeY_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ReverseX\", \"label\": \"\", \"pv\": \"ReverseX\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"ReverseX_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"ReverseY\", \"label\": \"\", \"pv\": \"ReverseY\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"ReverseY_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"AcquireTime\", \"label\": \"\", \"pv\": \"AcquireTime\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"AcquireTime_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"AcquirePeriod\", \"label\": \"\", \"pv\": \"AcquirePeriod\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"AcquirePeriod_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"Gain\", \"label\": \"\", \"pv\": \"Gain\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"Gain_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"FrameType\", \"label\": \"\", \"pv\": \"FrameType\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"FrameType_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ImageMode\", \"label\": \"\", \"pv\": \"ImageMode\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"ImageMode_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"TriggerMode\", \"label\": \"\", \"pv\": \"TriggerMode\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"TriggerMode_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"NumExposures\", \"label\": \"\", \"pv\": \"NumExposures\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"NumExposures_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"NumImages\", \"label\": \"\", \"pv\": \"NumImages\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"NumImages_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ShutterMode\", \"label\": \"\", \"pv\": \"ShutterMode\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"ShutterMode_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ShutterControl\", \"label\": \"\", \"pv\": \"ShutterControl\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"ShutterControl_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"ShutterOpenDelay\", \"label\": \"\", \"pv\": \"ShutterOpenDelay\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"ShutterOpenDelay_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ShutterCloseDelay\", \"label\": \"\", \"pv\": \"ShutterCloseDelay\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"ShutterCloseDelay_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"Temperature\", \"label\": \"\", \"pv\": \"Temperature\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"Temperature_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"ResetPower\", \"label\": \"\", \"pv\": \"ResetPower\", \"widget\": {\"type\": \"CheckBox\"}}, {\"type\": \"SignalW\", \"name\": \"ThresholdApply\", \"label\": \"\", \"pv\": \"ThresholdApply\", \"widget\": {\"type\": \"CheckBox\"}}, {\"type\": \"SignalW\", \"name\": \"ImageFileTmot\", \"label\": \"\", \"pv\": \"ImageFileTmot\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Wavelength\", \"label\": \"\", \"pv\": \"Wavelength\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"EnergyLow\", \"label\": \"\", \"pv\": \"EnergyLow\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"EnergyHigh\", \"label\": \"\", \"pv\": \"EnergyHigh\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"DetDist\", \"label\": \"\", \"pv\": \"DetDist\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"DetVOffset\", \"label\": \"\", \"pv\": \"DetVOffset\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"BeamX\", \"label\": \"\", \"pv\": \"BeamX\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"BeamY\", \"label\": \"\", \"pv\": \"BeamY\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Flux\", \"label\": \"\", \"pv\": \"Flux\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"FilterTransm\", \"label\": \"\", \"pv\": \"FilterTransm\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"StartAngle\", \"label\": \"\", \"pv\": \"StartAngle\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"AngleIncr\", \"label\": \"\", \"pv\": \"AngleIncr\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Det2theta\", \"label\": \"\", \"pv\": \"Det2theta\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Polarization\", \"label\": \"\", \"pv\": \"Polarization\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Alpha\", \"label\": \"\", \"pv\": \"Alpha\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Kappa\", \"label\": \"\", \"pv\": \"Kappa\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Phi\", \"label\": \"\", \"pv\": \"Phi\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"PhiIncr\", \"label\": \"\", \"pv\": \"PhiIncr\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Chi\", \"label\": \"\", \"pv\": \"Chi\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"ChiIncr\", \"label\": \"\", \"pv\": \"ChiIncr\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"Omega\", \"label\": \"\", \"pv\": \"Omega\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"OmegaIncr\", \"label\": \"\", \"pv\": \"OmegaIncr\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"OscillAxis\", \"label\": \"\", \"pv\": \"OscillAxis\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"NumOscill\", \"label\": \"\", \"pv\": \"NumOscill\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"BadPixelFile\", \"label\": \"\", \"pv\": \"BadPixelFile\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"FlatFieldFile\", \"label\": \"\", \"pv\": \"FlatFieldFile\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"CbfTemplateFile\", \"label\": \"\", \"pv\": \"CbfTemplateFile\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalW\", \"name\": \"HeaderString\", \"label\": \"\", \"pv\": \"HeaderString\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Armed\", \"label\": \"\", \"pv\": \"Armed\", \"widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"NumBadPixels\", \"label\": \"\", \"pv\": \"NumBadPixels\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"FlatFieldValid\", \"label\": \"\", \"pv\": \"FlatFieldValid\", \"widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalR\", \"name\": \"PixelCutOff\", \"label\": \"\", \"pv\": \"PixelCutOff_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Temp0\", \"label\": \"\", \"pv\": \"Temp0_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Temp1\", \"label\": \"\", \"pv\": \"Temp1_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Temp2\", \"label\": \"\", \"pv\": \"Temp2_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Humid0\", \"label\": \"\", \"pv\": \"Humid0_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Humid1\", \"label\": \"\", \"pv\": \"Humid1_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"Humid2\", \"label\": \"\", \"pv\": \"Humid2_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"TVXVersion\", \"label\": \"\", \"pv\": \"TVXVersion_RBV\", \"widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ResetPowerTime\", \"label\": \"\", \"pv\": \"ResetPowerTime\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"ResetPowerTime_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"DelayTime\", \"label\": \"\", \"pv\": \"DelayTime\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"DelayTime_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ThresholdEnergy\", \"label\": \"\", \"pv\": \"ThresholdEnergy\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"ThresholdEnergy_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"ThresholdAutoApply\", \"label\": \"\", \"pv\": \"ThresholdAutoApply\", \"widget\": {\"type\": \"CheckBox\"}, \"read_pv\": \"ThresholdAutoApply_RBV\", \"read_widget\": {\"type\": \"LED\"}}, {\"type\": \"SignalRW\", \"name\": \"Energy\", \"label\": \"\", \"pv\": \"Energy\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"Energy_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"MinFlatField\", \"label\": \"\", \"pv\": \"MinFlatField\", \"widget\": {\"type\": \"TextWrite\", \"lines\": 1}, \"read_pv\": \"MinFlatField_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalRW\", \"name\": \"GapFill\", \"label\": \"\", \"pv\": \"GapFill\", \"widget\": {\"type\": \"ComboBox\", \"choices\": []}, \"read_pv\": \"GapFill_RBV\", \"read_widget\": {\"type\": \"TextRead\", \"lines\": 1}}, {\"type\": \"SignalR\", \"name\": \"ProgressBarTest\", \"label\": \"\", \"pv\": \"ProgressBarTest_RBV\", \"widget\": {\"type\": \"ProgressBar\"}}]}]}";

class pilatusDetectorParamSet : public virtual ADDriverParamSet {
public:
    pilatusDetectorParamSet() {
        this->add(PilatusResetPowerString, asynParamInt32, &PilatusResetPower);
        this->add(PilatusThresholdApplyString, asynParamInt32, &PilatusThresholdApply);
        this->add(PilatusImageFileTmotString, asynParamFloat64, &PilatusImageFileTmot);
        this->add(PilatusWavelengthString, asynParamFloat64, &PilatusWavelength);
        this->add(PilatusEnergyLowString, asynParamFloat64, &PilatusEnergyLow);
        this->add(PilatusEnergyHighString, asynParamFloat64, &PilatusEnergyHigh);
        this->add(PilatusDetDistString, asynParamFloat64, &PilatusDetDist);
        this->add(PilatusDetVOffsetString, asynParamFloat64, &PilatusDetVOffset);
        this->add(PilatusBeamXString, asynParamFloat64, &PilatusBeamX);
        this->add(PilatusBeamYString, asynParamFloat64, &PilatusBeamY);
        this->add(PilatusFluxString, asynParamFloat64, &PilatusFlux);
        this->add(PilatusFilterTransmString, asynParamFloat64, &PilatusFilterTransm);
        this->add(PilatusStartAngleString, asynParamFloat64, &PilatusStartAngle);
        this->add(PilatusAngleIncrString, asynParamFloat64, &PilatusAngleIncr);
        this->add(PilatusDet2thetaString, asynParamFloat64, &PilatusDet2theta);
        this->add(PilatusPolarizationString, asynParamFloat64, &PilatusPolarization);
        this->add(PilatusAlphaString, asynParamFloat64, &PilatusAlpha);
        this->add(PilatusKappaString, asynParamFloat64, &PilatusKappa);
        this->add(PilatusPhiString, asynParamFloat64, &PilatusPhi);
        this->add(PilatusPhiIncrString, asynParamFloat64, &PilatusPhiIncr);
        this->add(PilatusChiString, asynParamFloat64, &PilatusChi);
        this->add(PilatusChiIncrString, asynParamFloat64, &PilatusChiIncr);
        this->add(PilatusOmegaString, asynParamFloat64, &PilatusOmega);
        this->add(PilatusOmegaIncrString, asynParamFloat64, &PilatusOmegaIncr);
        this->add(PilatusOscillAxisString, asynParamOctet, &PilatusOscillAxis);
        this->add(PilatusNumOscillString, asynParamInt32, &PilatusNumOscill);
        this->add(PilatusBadPixelFileString, asynParamOctet, &PilatusBadPixelFile);
        this->add(PilatusFlatFieldFileString, asynParamOctet, &PilatusFlatFieldFile);
        this->add(PilatusCbfTemplateFileString, asynParamOctet, &PilatusCbfTemplateFile);
        this->add(PilatusHeaderStringString, asynParamOctet, &PilatusHeaderString);
        this->add(PilatusArmedString, asynParamInt32, &PilatusArmed);
        this->add(PilatusNumBadPixelsString, asynParamInt32, &PilatusNumBadPixels);
        this->add(PilatusFlatFieldValidString, asynParamInt32, &PilatusFlatFieldValid);
        this->add(PilatusPixelCutOffString, asynParamInt32, &PilatusPixelCutOff);
        this->add(PilatusThTemp0String, asynParamFloat64, &PilatusThTemp0);
        this->add(PilatusThTemp1String, asynParamFloat64, &PilatusThTemp1);
        this->add(PilatusThTemp2String, asynParamFloat64, &PilatusThTemp2);
        this->add(PilatusThHumid0String, asynParamFloat64, &PilatusThHumid0);
        this->add(PilatusThHumid1String, asynParamFloat64, &PilatusThHumid1);
        this->add(PilatusThHumid2String, asynParamFloat64, &PilatusThHumid2);
        this->add(PilatusTvxVersionString, asynParamOctet, &PilatusTvxVersion);
        this->add(PilatusResetPowerTimeString, asynParamInt32, &PilatusResetPowerTime);
        this->add(PilatusDelayTimeString, asynParamFloat64, &PilatusDelayTime);
        this->add(PilatusThresholdString, asynParamFloat64, &PilatusThreshold);
        this->add(PilatusThresholdAutoApplyString, asynParamInt32, &PilatusThresholdAutoApply);
        this->add(PilatusEnergyString, asynParamFloat64, &PilatusEnergy);
        this->add(PilatusMinFlatFieldString, asynParamInt32, &PilatusMinFlatField);
        this->add(PilatusGapFillString, asynParamInt32, &PilatusGapFill);
        this->add(ProgressBarTestString, asynParamFloat64, &ProgressBarTest);

        this->paramTree = pilatusParamTree;
    }

    int PilatusResetPower;
    #define FIRST_PILATUSDETECTORPARAMSET_PARAM PilatusResetPower
    int PilatusThresholdApply;
    int PilatusImageFileTmot;
    int PilatusWavelength;
    int PilatusEnergyLow;
    int PilatusEnergyHigh;
    int PilatusDetDist;
    int PilatusDetVOffset;
    int PilatusBeamX;
    int PilatusBeamY;
    int PilatusFlux;
    int PilatusFilterTransm;
    int PilatusStartAngle;
    int PilatusAngleIncr;
    int PilatusDet2theta;
    int PilatusPolarization;
    int PilatusAlpha;
    int PilatusKappa;
    int PilatusPhi;
    int PilatusPhiIncr;
    int PilatusChi;
    int PilatusChiIncr;
    int PilatusOmega;
    int PilatusOmegaIncr;
    int PilatusOscillAxis;
    int PilatusNumOscill;
    int PilatusBadPixelFile;
    int PilatusFlatFieldFile;
    int PilatusCbfTemplateFile;
    int PilatusHeaderString;
    int PilatusArmed;
    int PilatusNumBadPixels;
    int PilatusFlatFieldValid;
    int PilatusPixelCutOff;
    int PilatusThTemp0;
    int PilatusThTemp1;
    int PilatusThTemp2;
    int PilatusThHumid0;
    int PilatusThHumid1;
    int PilatusThHumid2;
    int PilatusTvxVersion;
    int PilatusResetPowerTime;
    int PilatusDelayTime;
    int PilatusThreshold;
    int PilatusThresholdAutoApply;
    int PilatusEnergy;
    int PilatusMinFlatField;
    int PilatusGapFill;
    int ProgressBarTest;
};

#endif // PilatusDetectorParamSet_H
