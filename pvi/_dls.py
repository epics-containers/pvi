from ._types import AsynParameter, AsynParameterTree, Formatter, Group
from ._util import walk


class DLSFormatter(Formatter):
    def format_h_file(self, parameters: AsynParameterTree, basename: str) -> str:
        parameter_members = ""
        for parameter in walk(parameters):
            if isinstance(parameter, Group):
                parameter_members += f"/* Group: {parameter.name} */\n"
            elif isinstance(parameter, AsynParameter):
                parameter_members += (
                    f"    int {parameter.name};  "
                    f"/* {parameter.type} {parameter.description} */\n"
                )
        h_txt = f"""\
#ifndef {basename.upper()}_PARAMETERS_H
#define {basename.upper()}_PARAMETERS_H

class {basename.title()}Parameters {{
public:
    {basename.title()}Parameters(asynPortDriver *parent);
    {parameter_members.rstrip()}
}}

#endif //{basename.upper()}_PARAMETERS_H
"""
        return h_txt

    def format_cpp_file(self, parameters: AsynParameterTree, basename: str) -> str:
        create_params = ""
        for parameter in walk(parameters):
            if isinstance(parameter, AsynParameter):
                create_params += (
                    f'    parent->createParam("{parameter.name}", '
                    f"{parameter.type}, &{parameter.name});"
                )
        cpp_txt = f"""\
{basename.title()}Parameters::{basename.title()}Parameters(asynPortDriver *parent) {{
{create_params.rstrip()}
}}
"""
        return cpp_txt
