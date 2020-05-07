#ifndef PILATUS_PARAMETERS_H
#define PILATUS_PARAMETERS_H

class PilatusParameters {
public:
    PilatusParameters(asynPortDriver *parent);
    /* Group: AncilliaryInformation */
    int ThresholdEnergy;  /* asynParamFloat64 Setting */
    int MinFlatField;  /* asynParamInt32 Setting */
    int GapFill;  /* asynParamInt32 Setting */
    int TVXVersion;  /* asynParamOctet Readback */
    int PixelCutOff;  /* asynParamInt32 Readback */
    int HeaderString;  /* asynParamOctet Action */
    int Armed;  /* asynParamInt32 Readback */
}

#endif //PILATUS_PARAMETERS_H
