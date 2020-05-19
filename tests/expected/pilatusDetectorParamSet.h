#ifndef PilatusDetectorParamSet_H
#define PilatusDetectorParamSet_H

#include "ADDriverParamSet.h"

#define PilatusArmedString "Armed"
#define PilatusThresholdEnergyString "ThresholdEnergy"
#define PilatusMinFlatFieldString "MinFlatField"
#define PilatusGapFillString "GapFill"
#define PilatusTVXVersionString "TVXVersion"
#define PilatusPixelCutOffString "PixelCutOff"
#define PilatusHeaderStringString "HeaderString"

class pilatusDetectorParamSet : public virtual ADDriverParamSet {
public:
    pilatusDetectorParamSet() {
        this->add(PilatusArmedString, asynParamInt32, &Armed);
        this->add(PilatusThresholdEnergyString, asynParamFloat64, &ThresholdEnergy);
        this->add(PilatusMinFlatFieldString, asynParamInt32, &MinFlatField);
        this->add(PilatusGapFillString, asynParamInt32, &GapFill);
        this->add(PilatusTVXVersionString, asynParamOctet, &TVXVersion);
        this->add(PilatusPixelCutOffString, asynParamInt32, &PixelCutOff);
        this->add(PilatusHeaderStringString, asynParamOctet, &HeaderString);
    }

protected:
    int Armed;
    #define FIRST_PILATUS_PARAM_INDEX Armed
    int ThresholdEnergy;
    int MinFlatField;
    int GapFill;
    int TVXVersion;
    int PixelCutOff;
    int HeaderString;
};

#endif // PilatusDetectorParamSet_H
