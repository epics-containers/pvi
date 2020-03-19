from typing import List, Union

from pydantic import BaseModel, Field

from ._types import WithType

GroupOrParameter = Union["Group", Float64AsynParameter, StringAsynParameter, Float64StreamParameter]


class Group(WithType):
    """Group that can contain multiple parameters or other Groups"""

    name: str = Field(..., description="Name of the Group that will form its label")
    children: List[GroupOrParameter] = Field(
        ..., description="Child Parameters or Groups"
    )
    device: bool = Field(True, "Create a child Device instead of grouping in the GUI")


class Schema(BaseModel):
    base: str = Field(None, description="YAML file to use as base class for this")
    local: str = Field(None, description="YAML file that overrides this for local changes")
    arguments: List[Union[StringArgument, FloatArgument]] = Field([], description="Arguments needed to make an isntance of this")
    producer: Union[AsynProducer, DLSAsynProducer] = Field(..., description="The Producer class to make templates, screens, etc.")
    components: List[GroupOrParameter]
    
    pv_prefix: str = Field(..., description="The PV Prefix for records created by the template file")
    template_file: str = Field(..., description="Path to the template file that will be created")
    includes: List[Union[DBInclude, YAMLInclude]]
    startup_script: str    
