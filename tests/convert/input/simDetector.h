#include <epicsEvent.h>
#include "ADDriver.h"

#define DRIVER_VERSION      2
#define DRIVER_REVISION     9
#define DRIVER_MODIFICATION 0

/** Simulation detector driver; demonstrates most of the features that areaDetector drivers can support. */
class epicsShareClass simDetector : public ADDriver {
public:
    simDetector(const char *portName, int maxSizeX, int maxSizeY, NDDataType_t dataType,
                int maxBuffers, size_t maxMemory,
                int priority, int stackSize);

    /* These are the methods that we override from ADDriver */
    virtual asynStatus writeInt32(asynUser *pasynUser, epicsInt32 value);
    virtual asynStatus writeFloat64(asynUser *pasynUser, epicsFloat64 value);
    virtual void setShutter(int open);
    virtual void report(FILE *fp, int details);
    void simTask(); /**< Should be private, but gets called from C, so must be public */

protected:
    int SimGainX;
    #define FIRST_SIM_DETECTOR_PARAM SimGainX
    int SimGainY;
    int SimGainRed;
    int SimGainGreen;
    int SimGainBlue;
    int simOffset;
    int SimNoise;
    int SimResetImage;
    int SimMode;
    int SimPeakStartX;
    int SimPeakStartY;
    int SimPeakWidthX;
    int SimPeakWidthY;
    int SimPeakNumX;
    int SimPeakNumY;
    int SimPeakStepX;
    int SimPeakStepY;
    int SimPeakHeightVariation;
    int SimOffset;
    int SimXSineOperation;
    int SimXSine1Amplitude;
    int SimXSine1Frequency;
    int SimXSine1Phase;
    int SimXSine2Amplitude;
    int SimXSine2Frequency;
    int SimXSine2Phase;
    int SimYSineOperation;
    int SimYSine1Amplitude;
    int SimYSine1Frequency;
    int SimYSine1Phase;
    int SimYSine2Amplitude;
    int SimYSine2Frequency;
    int SimYSine2Phase;

private:
    /* These are the methods that are new to this class */
    template <typename epicsType> int computeArray(int sizeX, int sizeY);
    template <typename epicsType> int computeLinearRampArray(int sizeX, int sizeY);
    template <typename epicsType> int computePeaksArray(int sizeX, int sizeY);
    template <typename epicsType> int computeSineArray(int sizeX, int sizeY);
    int computeImage();

    /* Our data */
    epicsEventId startEventId_;
    epicsEventId stopEventId_;
    NDArray *pRaw_;
    NDArray *pBackground_;
    bool useBackground_;
    NDArray *pRamp_;
    NDArray *pPeak_;
    NDArrayInfo arrayInfo_;
    double *xSine1_;
    double *xSine2_;
    double *ySine1_;
    double *ySine2_;
    double xSineCounter_;
    double ySineCounter_;
};

typedef enum {
    SimModeLinearRamp,
    SimModePeaks,
    SimModeSine,
    SimModeOffsetNoise
} SimModes_t;

typedef enum {
    SimSineOperationAdd,
    SimSineOperationMultiply
} SimSineOperation_t;

#define SimGainXString                "SIM_GAIN_X"
#define SimGainYString                "SIM_GAIN_Y"
#define SimGainRedString              "SIM_GAIN_RED"
#define SimGainGreenString            "SIM_GAIN_GREEN"
#define SimGainBlueString             "SIM_GAIN_BLUE"
#define SimOffsetString               "SIM_OFFSET"
#define SimNoiseString                "SIM_NOISE"
#define SimResetImageString           "RESET_IMAGE"
#define SimModeString                 "SIM_MODE"
#define SimPeakStartXString           "SIM_PEAK_START_X"
#define SimPeakStartYString           "SIM_PEAK_START_Y"
#define SimPeakWidthXString           "SIM_PEAK_WIDTH_X"
#define SimPeakWidthYString           "SIM_PEAK_WIDTH_Y"
#define SimPeakNumXString             "SIM_PEAK_NUM_X"
#define SimPeakNumYString             "SIM_PEAK_NUM_Y"
#define SimPeakStepXString            "SIM_PEAK_STEP_X"
#define SimPeakStepYString            "SIM_PEAK_STEP_Y"
#define SimPeakHeightVariationString  "SIM_PEAK_HEIGHT_VARIATION"
#define SimXSineOperationString       "SIM_XSINE_OPERATION"
#define SimXSine1AmplitudeString      "SIM_XSINE1_AMPLITUDE"
#define SimXSine1FrequencyString      "SIM_XSINE1_FREQUENCY"
#define SimXSine1PhaseString          "SIM_XSINE1_PHASE"
#define SimXSine2AmplitudeString      "SIM_XSINE2_AMPLITUDE"
#define SimXSine2FrequencyString      "SIM_XSINE2_FREQUENCY"
#define SimXSine2PhaseString          "SIM_XSINE2_PHASE"
#define SimYSineOperationString       "SIM_YSINE_OPERATION"
#define SimYSine1AmplitudeString      "SIM_YSINE1_AMPLITUDE"
#define SimYSine1FrequencyString      "SIM_YSINE1_FREQUENCY"
#define SimYSine1PhaseString          "SIM_YSINE1_PHASE"
#define SimYSine2AmplitudeString      "SIM_YSINE2_AMPLITUDE"
#define SimYSine2FrequencyString      "SIM_YSINE2_FREQUENCY"
#define SimYSine2PhaseString          "SIM_YSINE2_PHASE"
