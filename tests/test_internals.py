import pytest
from pydantic import ValidationError

from pvi import Group


def test_camel():
    g = Group(name="CamelThing", children=[])
    assert g.name == "CamelThing"
    with pytest.raises(ValidationError):
        Group(name="CamelThing_not", children=[])
