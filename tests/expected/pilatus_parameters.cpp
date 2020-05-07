PilatusParameters::PilatusParameters(asynPortDriver *parent) {
    parent->createParam("ThresholdEnergy", asynParamFloat64, &ThresholdEnergy);
    parent->createParam("MinFlatField", asynParamInt32, &MinFlatField);
    parent->createParam("GapFill", asynParamInt32, &GapFill);
    parent->createParam("TVXVersion", asynParamOctet, &TVXVersion);
    parent->createParam("PixelCutOff", asynParamInt32, &PixelCutOff);
    parent->createParam("HeaderString", asynParamOctet, &HeaderString);
    parent->createParam("Armed", asynParamInt32, &Armed);
}
