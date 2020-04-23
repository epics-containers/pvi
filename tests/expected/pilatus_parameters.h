#ifndef PILATUS_PARAMETERS_H
#define PILATUS_PARAMETERS_H

class PilatusParameters {
public:
    PilatusParameters(asynPortDriver *parent);
    /* Group: AncilliaryInformation */
    int ThresholdEnergy;  /* asynParamFloat64 Setting */
}

#endif //PILATUS_PARAMETERS_H
