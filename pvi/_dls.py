from ._types import AsynParameter, Channel, Formatter, Group, Record, Tree
from ._util import walk

FIELD_TXT = '    field({0:5s} "{1}")\n'
INFO_TXT = '    info({0} "{1})\n'


class DLSFormatter(Formatter):
    def format_edl(self, records: Tree[Channel], basename: str) -> str:
        raise NotImplementedError(self)

    def format_template(self, records: Tree[Record], basename: str) -> str:
        txt = ""
        for record in walk(records):
            if isinstance(record, Group):
                txt += f"# Group: {record.name}\n\n"
            elif isinstance(record, Record):
                fields = ""
                for k, v in record.fields_.items():
                    fields += FIELD_TXT.format(k + ",", v)
                for k, v in record.infos.items():
                    fields += INFO_TXT.format(k + ",", v)
                txt += f"""\
record({record.type}, "{record.name}") {{
{fields.rstrip()}
}}

"""
        return txt

    def format_h(self, parameters: Tree[AsynParameter], basename: str) -> str:
        parameter_members = ""
        for parameter in walk(parameters):
            if isinstance(parameter, Group):
                parameter_members += f"/* Group: {parameter.name} */\n"
            else:
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

    def format_cpp(self, parameters: Tree[AsynParameter], basename: str) -> str:
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
