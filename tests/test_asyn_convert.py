import pytest

from pvi._convert._asyn_convert import (
    AsynFloat32Waveform,
    AsynFloat64Waveform,
    AsynInt32Waveform,
    AsynInt64Waveform,
    AsynWaveform,
    get_waveform_parameter,
)


@pytest.mark.parametrize(
    "dtyp,expected",
    [
        ("asynOctetRead", AsynWaveform),
        ("asynOctetWrite", AsynWaveform),
        ("asynInt32ArrayIn", AsynInt32Waveform),
        ("asynInt32ArrayOut", AsynInt32Waveform),
        ("asynInt64ArrayIn", AsynInt64Waveform),
        ("asynInt64ArrayOut", AsynInt64Waveform),
        ("asynFloat32ArrayIn", AsynFloat32Waveform),
        ("asynFloat32ArrayOut", AsynFloat32Waveform),
        ("asynFloat64ArrayIn", AsynFloat64Waveform),
        ("asynFloat64ArrayOut", AsynFloat64Waveform),
    ],
)
def test_get_waveform_parameter(dtyp, expected):
    assert get_waveform_parameter(dtyp) is expected


def test_get_waveform_parameter_unknown_raises():
    with pytest.raises(AssertionError, match="asynUnknown"):
        get_waveform_parameter("asynUnknown")
