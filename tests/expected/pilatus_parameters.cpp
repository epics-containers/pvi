PilatusParameters::PilatusParameters(asynPortDriver *parent) {
    parent->createParam("ThresholdEnergy", asynParamFloat64, &ThresholdEnergy);
}
