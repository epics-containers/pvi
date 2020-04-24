from pydantic import BaseModel, Field

# TODO
# Correct the datatypes (currently using str for all)


class BaseRecordType(BaseModel):
    pass


class AnalogueCommon(BaseRecordType):
    ADEL: str = Field(None, description="ADEL")
    ALST: str = Field(None, description="ALST")
    AOFF: str = Field(None, description="AOFF")
    ASLO: str = Field(None, description="ASLO")
    EGU: str = Field(None, description="EGU")
    EGUF: str = Field(None, description="EGUF")
    EGUL: str = Field(None, description="EGUL")
    EOFF: str = Field(None, description="EOFF")
    ESLO: str = Field(None, description="ESLO")
    HHSV: str = Field(None, description="HHSV")
    HIGH: str = Field(None, description="HIGH")
    HIHI: str = Field(None, description="HIHI")
    HOPR: str = Field(None, description="HOPR")
    HSV: str = Field(None, description="HSV")
    HYST: str = Field(None, description="HYST")
    INIT: str = Field(None, description="INIT")
    LALM: str = Field(None, description="LALM")
    LBRK: str = Field(None, description="LBRK")
    LINR: str = Field(None, description="LINR")
    LLSV: str = Field(None, description="LLSV")
    LOLO: str = Field(None, description="LOLO")
    LOPR: str = Field(None, description="LOPR")
    LOW: str = Field(None, description="LOW")
    LSV: str = Field(None, description="LSV")
    MDEL: str = Field(None, description="MDEL")
    MLST: str = Field(None, description="MLST")
    ORAW: str = Field(None, description="ORAW")
    PBRK: str = Field(None, description="PBRK")
    PREC: int = Field(None, description="PREC")
    ROFF: str = Field(None, description="ROFF")
    RVAL: str = Field(None, description="RVAL")
    SIML: str = Field(None, description="SIML")
    SIMM: str = Field(None, description="SIMM")
    SIMS: str = Field(None, description="SIMS")
    SIOL: str = Field(None, description="SIOL")


class AnalogueIn(AnalogueCommon):
    SMOO: str = Field(None, description="SMOO")
    SVAL: str = Field(None, description="SVAL")


class AnalogueOut(AnalogueCommon):
    DOL: str = Field(None, description="DOL")
    DRVH: str = Field(None, description="DRVH")
    DRVL: str = Field(None, description="DRVL")
    IVOA: str = Field(None, description="IVOA")
    IVOV: str = Field(None, description="IVOV")
    OIF: str = Field(None, description="OIF")
    OMOD: str = Field(None, description="OMOD")
    OMSL: str = Field(None, description="OMSL")
    ORBV: str = Field(None, description="ORBV")
    OROC: str = Field(None, description="OROC")
    OVAL: str = Field(None, description="OVAL")
    PVAL: str = Field(None, description="PVAL")
    RBV: str = Field(None, description="RBV")


class BinaryCommon(BaseRecordType):
    COSV: str = Field(None, description="COSV")
    LALM: str = Field(None, description="LALM")
    MASK: str = Field(None, description="MASK")
    MLST: str = Field(None, description="MLST")
    ONAM: str = Field(None, description="ONAM")
    ORAW: str = Field(None, description="ORAW")
    OSV: str = Field(None, description="OSV")
    RVAL: str = Field(None, description="RVAL")
    SIML: str = Field(None, description="SIML")
    SIMM: str = Field(None, description="SIMM")
    SIMS: str = Field(None, description="SIMS")
    SIOL: str = Field(None, description="SIOL")
    ZNAM: str = Field(None, description="ZNAM")
    ZSV: str = Field(None, description="ZSV")


class BinaryIn(BinaryCommon):
    SVAL: str = Field(None, description="SVAL")


class BinaryOut(BinaryCommon):
    DOL: str = Field(None, description="DOL")
    HIGH: str = Field(None, description="HIGH")
    IVOA: str = Field(None, description="IVOA")
    IVOV: str = Field(None, description="IVOV")
    OMSL: str = Field(None, description="OMSL")
    ORBV: str = Field(None, description="ORBV")
    RBV: str = Field(None, description="RBV")
    RPVT: str = Field(None, description="RPVT")
    WDPT: str = Field(None, description="WDPT")


class LongCommon(BaseRecordType):
    ADEL: str = Field(None, description="ADEL")
    ALST: str = Field(None, description="ALST")
    EGU: str = Field(None, description="EGU")
    HHSV: str = Field(None, description="HHSV")
    HIGH: str = Field(None, description="HIGH")
    HIHI: str = Field(None, description="HIHI")
    HOPR: str = Field(None, description="HOPR")
    HSV: str = Field(None, description="HSV")
    HYST: str = Field(None, description="HYST")
    LALM: str = Field(None, description="LALM")
    LLSV: str = Field(None, description="LLSV")
    LOLO: str = Field(None, description="LOLO")
    LOPR: str = Field(None, description="LOPR")
    LOW: str = Field(None, description="LOW")
    LSV: str = Field(None, description="LSV")
    MDEL: str = Field(None, description="MDEL")
    MLST: str = Field(None, description="MLST")
    SIML: str = Field(None, description="SIML")
    SIMM: str = Field(None, description="SIMM")
    SIMS: str = Field(None, description="SIMS")
    SIOL: str = Field(None, description="SIOL")


class LongIn(LongCommon):
    SVAL: str = Field(None, description="SVAL")


class LongOut(LongCommon):
    DOL: str = Field(None, description="DOL")
    DRVH: str = Field(None, description="DRVH")
    DRVL: str = Field(None, description="DRVL")
    IVOA: str = Field(None, description="IVOA")
    IVOV: str = Field(None, description="IVOV")
    OMSL: str = Field(None, description="OMSL")


class MultiBitBinaryCommon(BaseRecordType):
    COSV: str = Field(None, description="COSV")
    EIST: str = Field(None, description="EIST")
    EISV: str = Field(None, description="EISV")
    EIVL: str = Field(None, description="EIVL")
    ELST: str = Field(None, description="ELST")
    ELSV: str = Field(None, description="ELSV")
    ELVL: str = Field(None, description="ELVL")
    FFST: str = Field(None, description="FFST")
    FFSV: str = Field(None, description="FFSV")
    FFVL: str = Field(None, description="FFVL")
    FRST: str = Field(None, description="FRST")
    FRSV: str = Field(None, description="FRSV")
    FRVL: str = Field(None, description="FRVL")
    FTST: str = Field(None, description="FTST")
    FTSV: str = Field(None, description="FTSV")
    FTVL: str = Field(None, description="FTVL")
    FVST: str = Field(None, description="FVST")
    FVSV: str = Field(None, description="FVSV")
    FVVL: str = Field(None, description="FVVL")
    LALM: str = Field(None, description="LALM")
    MASK: str = Field(None, description="MASK")
    MLST: str = Field(None, description="MLST")
    NIST: str = Field(None, description="NIST")
    NISV: str = Field(None, description="NISV")
    NIVL: str = Field(None, description="NIVL")
    NOBT: str = Field(None, description="NOBT")
    ONST: str = Field(None, description="ONST")
    ONSV: str = Field(None, description="ONSV")
    ONVL: str = Field(None, description="ONVL")
    ORAW: str = Field(None, description="ORAW")
    RVAL: str = Field(None, description="RVAL")
    SDEF: str = Field(None, description="SDEF")
    SHFT: str = Field(None, description="SHFT")
    SIML: str = Field(None, description="SIML")
    SIMM: str = Field(None, description="SIMM")
    SIMS: str = Field(None, description="SIMS")
    SIOL: str = Field(None, description="SIOL")
    SVST: str = Field(None, description="SVST")
    SVSV: str = Field(None, description="SVSV")
    SVVL: str = Field(None, description="SVVL")
    SXST: str = Field(None, description="SXST")
    SXSV: str = Field(None, description="SXSV")
    SXVL: str = Field(None, description="SXVL")
    TEST: str = Field(None, description="TEST")
    TESV: str = Field(None, description="TESV")
    TEVL: str = Field(None, description="TEVL")
    THST: str = Field(None, description="THST")
    THSV: str = Field(None, description="THSV")
    THVL: str = Field(None, description="THVL")
    TTST: str = Field(None, description="TTST")
    TTSV: str = Field(None, description="TTSV")
    TTVL: str = Field(None, description="TTVL")
    TVST: str = Field(None, description="TVST")
    TVSV: str = Field(None, description="TVSV")
    TVVL: str = Field(None, description="TVVL")
    TWST: str = Field(None, description="TWST")
    TWSV: str = Field(None, description="TWSV")
    TWVL: str = Field(None, description="TWVL")
    UNSV: str = Field(None, description="UNSV")
    ZRST: str = Field(None, description="ZRST")
    ZRSV: str = Field(None, description="ZRSV")
    ZRVL: str = Field(None, description="ZRVL")


class MultiBitBinaryIn(MultiBitBinaryCommon):
    SVAL: str = Field(None, description="SVAL")


class MultiBitBinaryOut(MultiBitBinaryCommon):
    DOL: str = Field(None, description="DOL")
    IVOA: str = Field(None, description="IVOA")
    IVOV: str = Field(None, description="IVOV")
    OMSL: str = Field(None, description="OMSL")
    ORBV: str = Field(None, description="ORBV")
    RBV: str = Field(None, description="RBV")


class StringCommon(BaseRecordType):
    APST: str = Field(None, description="APST")
    MPST: str = Field(None, description="MPST")
    OVAL: str = Field(None, description="OVAL")
    SIML: str = Field(None, description="SIML")
    SIMM: str = Field(None, description="SIMM")
    SIMS: str = Field(None, description="SIMS")
    SIOL: str = Field(None, description="SIOL")


class StringIn(StringCommon):
    SVAL: str = Field(None, description="SVAL")


class StringOut(StringCommon):
    DOL: str = Field(None, description="DOL")
    IVOA: str = Field(None, description="IVOA")
    IVOV: str = Field(None, description="IVOV")
    OMSL: str = Field(None, description="OMSL")


class WaveformCommon(BaseRecordType):
    APST: str = Field(None, description="APST")
    BPTR: str = Field(None, description="BPTR")
    BUSY: str = Field(None, description="BUSY")
    EGU: str = Field(None, description="EGU")
    FTVL: str = Field(None, description="FTVL")
    HASH: str = Field(None, description="HASH")
    HOPR: str = Field(None, description="HOPR")
    LOPR: str = Field(None, description="LOPR")
    MPST: str = Field(None, description="MPST")
    NELM: str = Field(None, description="NELM")
    NORD: str = Field(None, description="NORD")
    PREC: int = Field(None, description="PREC")
    RARM: str = Field(None, description="RARM")
    SIML: str = Field(None, description="SIML")
    SIMM: str = Field(None, description="SIMM")
    SIMS: str = Field(None, description="SIMS")
    SIOL: str = Field(None, description="SIOL")


class WaveformIn(WaveformCommon):
    pass


class WaveformOut(WaveformCommon):
    pass
