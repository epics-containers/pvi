#ifndef pilatusDetector_H
#define pilatusDetector_H

#include <stddef.h>
#include <stdlib.h>
#include <stdarg.h>
#include <math.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <ctype.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <cbf_ad.h>
#include <tiffio.h>

#include <epicsTime.h>
#include <epicsThread.h>
#include <epicsEvent.h>
#include <epicsMutex.h>
#include <epicsString.h>
#include <epicsStdio.h>
#include <epicsMutex.h>
#include <cantProceed.h>
#include <iocsh.h>
#include <epicsExport.h>

#include <asynOctetSyncIO.h>

#include "ADDriver.h"

#define DRIVER_VERSION      2
#define DRIVER_REVISION     9
#define DRIVER_MODIFICATION 0

/** Messages to/from camserver */
#define MAX_MESSAGE_SIZE 256
#define MAX_FILENAME_LEN 256
#define MAX_HEADER_STRING_LEN 68
#define MAX_BAD_PIXELS 100
/** Time to poll when reading from camserver */
#define ASYN_POLL_TIME .01
#define CAMSERVER_DEFAULT_TIMEOUT 1.0
/** Additional time to wait for a camserver response after the acquire should be complete */
#define CAMSERVER_ACQUIRE_TIMEOUT 10.
#define CAMSERVER_RESET_POWER_TIMEOUT 30.
/** Time between checking to see if image file is complete */
#define FILE_READ_DELAY .01

/** Trigger modes */
typedef enum {
    TMInternal,
    TMExternalEnable,
    TMExternalTrigger,
    TMMultipleExternalTrigger,
    TMAlignment
} PilatusTriggerMode;

/** Bad pixel structure for Pilatus detector */
typedef struct {
    int badIndex;
    int replaceIndex;
} badPixel;


static const char *gainStrings[] = {"lowG", "midG", "highG", "uhighG"};

static const char *driverName = "pilatusDetector";

#define PilatusDelayTimeString      "DELAY_TIME"
#define PilatusThresholdString      "THRESHOLD"
#define PilatusThresholdApplyString "THRESHOLD_APPLY"
#define PilatusThresholdAutoApplyString "THRESHOLD_AUTO_APPLY"
#define PilatusEnergyString         "ENERGY"
#define PilatusArmedString          "ARMED"
#define PilatusResetPowerString     "RESET_POWER"
#define PilatusResetPowerTimeString "RESET_POWER_TIME"
#define PilatusImageFileTmotString  "IMAGE_FILE_TMOT"
#define PilatusBadPixelFileString   "BAD_PIXEL_FILE"
#define PilatusNumBadPixelsString   "NUM_BAD_PIXELS"
#define PilatusFlatFieldFileString  "FLAT_FIELD_FILE"
#define PilatusMinFlatFieldString   "MIN_FLAT_FIELD"
#define PilatusFlatFieldValidString "FLAT_FIELD_VALID"
#define PilatusGapFillString        "GAP_FILL"
#define PilatusWavelengthString     "WAVELENGTH"
#define PilatusEnergyLowString      "ENERGY_LOW"
#define PilatusEnergyHighString     "ENERGY_HIGH"
#define PilatusDetDistString        "DET_DIST"
#define PilatusDetVOffsetString     "DET_VOFFSET"
#define PilatusBeamXString          "BEAM_X"
#define PilatusBeamYString          "BEAM_Y"
#define PilatusFluxString           "FLUX"
#define PilatusFilterTransmString   "FILTER_TRANSM"
#define PilatusStartAngleString     "START_ANGLE"
#define PilatusAngleIncrString      "ANGLE_INCR"
#define PilatusDet2thetaString      "DET_2THETA"
#define PilatusPolarizationString   "POLARIZATION"
#define PilatusAlphaString          "ALPHA"
#define PilatusKappaString          "KAPPA"
#define PilatusPhiString            "PHI"
#define PilatusPhiIncrString        "PHI_INCR"
#define PilatusChiString            "CHI"
#define PilatusChiIncrString        "CHI_INCR"
#define PilatusOmegaString          "OMEGA"
#define PilatusOmegaIncrString      "OMEGA_INCR"
#define PilatusOscillAxisString     "OSCILL_AXIS"
#define PilatusNumOscillString      "NUM_OSCILL"
#define PilatusPixelCutOffString    "PIXEL_CUTOFF"
#define PilatusThTemp0String        "TH_TEMP_0"
#define PilatusThTemp1String        "TH_TEMP_1"
#define PilatusThTemp2String        "TH_TEMP_2"
#define PilatusThHumid0String       "TH_HUMID_0"
#define PilatusThHumid1String       "TH_HUMID_1"
#define PilatusThHumid2String       "TH_HUMID_2"
#define PilatusTvxVersionString     "TVXVERSION"
#define PilatusCbfTemplateFileString "CBFTEMPLATEFILE"
#define PilatusHeaderStringString   "HEADERSTRING"


/** Driver for Dectris Pilatus pixel array detectors using their camserver server over TCP/IP socket */
class pilatusDetector : public ADDriver {
public:
    pilatusDetector(const char *portName, const char *camserverPort,
                    int maxSizeX, int maxSizeY,
                    int maxBuffers, size_t maxMemory,
                    int priority, int stackSize);

    /* These are the methods that we override from ADDriver */
    virtual asynStatus writeInt32(asynUser *pasynUser, epicsInt32 value);
    virtual asynStatus writeFloat64(asynUser *pasynUser, epicsFloat64 value);
    virtual asynStatus writeOctet(asynUser *pasynUser, const char *value,
                                    size_t nChars, size_t *nActual);
    void report(FILE *fp, int details);
    /* These should be private but are called from C so must be public */
    void pilatusTask();

protected:
    int PilatusDelayTime;
    #define FIRST_PILATUS_PARAM PilatusDelayTime
    int PilatusThreshold;
    int PilatusThresholdApply;
    int PilatusThresholdAutoApply;
    int PilatusEnergy;
    int PilatusArmed;
    int PilatusResetPower;
    int PilatusResetPowerTime;
    int PilatusImageFileTmot;
    int PilatusBadPixelFile;
    int PilatusNumBadPixels;
    int PilatusFlatFieldFile;
    int PilatusMinFlatField;
    int PilatusFlatFieldValid;
    int PilatusGapFill;
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
    int PilatusPixelCutOff;
    int PilatusThTemp0;
    int PilatusThTemp1;
    int PilatusThTemp2;
    int PilatusThHumid0;
    int PilatusThHumid1;
    int PilatusThHumid2;
    int PilatusTvxVersion;
    int PilatusCbfTemplateFile;
    int PilatusHeaderString;

 private:
    /* These are the methods that are new to this class */
    void abortAcquisition();
    void makeMultipleFileFormat(const char *baseFileName);
    asynStatus waitForFileToExist(const char *fileName, epicsTimeStamp *pStartTime, double timeout, NDArray *pImage);
    void correctBadPixels(NDArray *pImage);
    int stringEndsWith(const char *aString, const char *aSubstring, int shouldIgnoreCase);
    asynStatus readImageFile(const char *fileName, epicsTimeStamp *pStartTime, double timeout, NDArray *pImage);
    asynStatus readCbf(const char *fileName, epicsTimeStamp *pStartTime, double timeout, NDArray *pImage);
    asynStatus readTiff(const char *fileName, epicsTimeStamp *pStartTime, double timeout, NDArray *pImage);
    asynStatus writeCamserver(double timeout);
    asynStatus readCamserver(double timeout);
    asynStatus writeReadCamserver(double timeout);
    asynStatus setAcquireParams();
    asynStatus setThreshold();
    asynStatus resetModulePower();
    asynStatus pilatusStatus();
    void readBadPixelFile(const char *badPixelFile);
    void readFlatFieldFile(const char *flatFieldFile);

    /* Our data */
    int imagesRemaining;
    epicsEventId startEventId;
    epicsEventId stopEventId;
    char toCamserver[MAX_MESSAGE_SIZE];
    char fromCamserver[MAX_MESSAGE_SIZE];
    NDArray *pFlatField;
    char multipleFileFormat[MAX_FILENAME_LEN];
    int multipleFileNumber;
    asynUser *pasynUserCamserver;
    badPixel badPixelMap[MAX_BAD_PIXELS];
    double averageFlatField;
    double demandedThreshold;
    double demandedEnergy;
    int firstStatusCall;
    double camserverVersion;
};

#endif
