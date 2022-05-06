#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


import inspect
import os

from live_xml.modinfo import ModInfo
from live_xml.o19_tuning_helper import O19TuningHelper

from sims4.commands import CommandType, CheatOutput, Command
from sims4communitylib.utils.common_io_utils import CommonIOUtils

from sims4communitylib.utils.common_log_registry import CommonLogRegistry, CommonLog
from sims4communitylib.utils.common_log_utils import CommonLogUtils

log: CommonLog = CommonLogRegistry.get().register_log(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)



from sims4communitylib.services.commands.common_console_command import CommonConsoleCommand
from sims4communitylib.services.commands.common_console_command_output import CommonConsoleCommandOutput
@CommonConsoleCommand(
    ModInfo.get_identity(),
    'x19.inspect',
    "Log Usage: 'x19.inspect [-|manager] tuning [attribute[.attribute]*]", command_aliases=('x19.inspect.l', 'x19.inspect.log')
)
def xxx_cmd_o19_inspect_log(output: CommonConsoleCommandOutput, manager=None, tuning='', attributes=''):
    cmd_inspect_v2(manager, tuning, attributes, output)


@CommonConsoleCommand(
    ModInfo.get_identity(),
    'x19.inspect.c',
    'Console Usage: x19.inspect.c', command_aliases=('x19.inspect.console')
)
def xxx_cmd_o19_inspector_console(output: CommonConsoleCommandOutput, manager='-', tuning='', attributes=''):
    cmd_inspect_v2(manager, tuning, attributes, output, do_console=True)

def cmd_inspect_v2(manager, tuning, attributes, output, do_console: bool = False):
    output(f"cmd_inspect({manager}, {tuning}, {attributes}, {do_console})")
    try:
        log.enable()
        O19TuningInspector.o19_inspect(output, manager, tuning, attributes, do_console=do_console)
    except Exception as e:
        output(f"Error: '{e}'")
        log.error(f"Error: '{e}'")
    log.disable()



@Command('inspect', 'inspect.log', command_type=CommandType.Live)
def cmd_inspect_log(manager='', tuning='', attributes='', _connection=None):
    cmd_inspect(manager, tuning, attributes, _connection)


@Command('inspect.c', 'inspect.console', command_type=CommandType.Live)
def cmd_inspect_console(manager='', tuning='', attributes='', _connection=None):
    cmd_inspect(manager, tuning, attributes, _connection, do_console=True)


def cmd_inspect(manager, tuning, attributes, _connection, do_console: bool = False):
    output = CheatOutput(_connection)
    output(f"cmd_inspect({manager}, {tuning}, {attributes}, {do_console})")
    try:
        log.enable()
        O19TuningInspector.o19_inspect(output, manager, tuning, attributes, do_console=do_console)
    except Exception as e:
        output(f"Error: '{e}'")
        log.error(f"Error: '{e}'")
    log.disable()


class O19TuningInspector:
    _do_console = False
    _output = None
    log_file = None

    @staticmethod
    def set_log_file():
        O19TuningInspector.log_file = os.path.join(CommonLogUtils.get_sims_documents_location_path(), 'mod_logs', 'inspector.log')

    @staticmethod
    def inspector_log(message, do_console=False):
        with open(O19TuningInspector.log_file, "a") as fp:
            fp.write('{}\n'.format(message))

        if O19TuningInspector._output:
            log_to_console = do_console | O19TuningInspector._do_console
            if log_to_console:
                O19TuningInspector._output(message)

    @staticmethod
    def o19_inspect(output, manager=None, tuning='', attributes='', do_console: bool = False):
        O19TuningInspector._output = output
        O19TuningInspector._do_console = do_console
        if O19TuningInspector.log_file is None:
            O19TuningInspector.set_log_file()
        if os.path.isfile(O19TuningInspector.log_file):
            CommonIOUtils.delete_file(O19TuningInspector.log_file, ignore_errors=True)

        if tuning == '':
            O19TuningInspector.inspector_log('A tuning ID is required.', True)
            return
        try:
            tuning = f"{tuning}"
            manager = f"{manager}".upper()
            if manager == "-":
                manager = None
            else:
                try:
                    import sims4
                    import services
                    from sims4.resources import Types
                    services.get_instance_manager(sims4.resources.Types[manager.upper()])
                except:
                    O19TuningInspector.inspector_log(f"Unknown manager '{manager}'", True)
                    return

            attributes = f"{attributes}"
            tuning_dict = O19TuningHelper.get_tuning_dict(manager, [tuning, ])
            if not tuning_dict:
                O19TuningInspector.inspector_log('Tuning not found.', True)
                return
            tuning_id, elements = tuning_dict.popitem()  # process only the first item, in interactive mode this should be fine
            tuning = elements[0]
            manager_name = elements[1]
            tuning_name = elements[2]

            if not tuning:
                O19TuningInspector.inspector_log(f'ERROR: tuning ({tuning_id}) is None', True)
                return
            if not manager:
                manager = manager_name
            O19TuningInspector.inspector_log('-' * 160, True)
            O19TuningInspector.inspector_log(f"** o19.inspect {manager} {tuning_name} {attributes} **", True)
            O19TuningInspector.inspector_log(f'** <I n="{tuning_name}" s="{tuning_id}" ... > **')

            if attributes == '':
                O19TuningInspector.o19_inspect_object(tuning)
            else:
                O19TuningInspector.o19_resolve_attrs(tuning, attributes)
        except Exception as e:
            log.error(f"{e}")

    @staticmethod
    def o19_resolve_attrs(tuning, attributes):
        eof = "EOF"
        cur_attr = tuning
        attribute_name, remaining_attributes = f"{attributes}.{eof}".split('.', 1)
        if attribute_name == eof:
            return

        O19TuningInspector.inspector_log(f"** {attribute_name} **")
        attribute = O19TuningInspector.o19_getattr(tuning, attribute_name)
        if attribute:
            O19TuningInspector.inspector_log(f"        {attribute_name}: {type(attribute)} = {attribute}")
            O19TuningInspector.o19_inspect_object(attribute)
            O19TuningInspector.o19_resolve_attrs(attribute, remaining_attributes)
        else:
            O19TuningInspector.inspector_log(f"Attribute '{attribute_name}' not found.")

    @staticmethod
    def o19_getattr(obj, attribute_name):
        attribute = getattr(obj, attribute_name, None)
        if attribute:
            O19TuningInspector.inspector_log(f"    # attribute_name = getattr(obj, '{attribute_name}', None)")
            return attribute

        # # Code would work if the console input would preserve the case. As lower case it usually fails (except for str, int, float).
        # if attribute_name[:11] == 'isinstance(' and attribute_name[-1:] == ')':
        #      _class_string = attribute_name[11:-1]
        #     _module_name, _class_name = _class_string.rsplit('.', 1)
        #     _class = getattr(importlib.import_module(_module_name), _class_name)
        # else:
        #     _class = None

        if isinstance(obj, tuple) or isinstance(obj, list):
            O19TuningInspector.inspector_log(f"{type(obj)}")
            for elem in obj:
                # if _class:
                #     if isinstance(elem, _class):
                #         O19TuningInspector.inspector_log(f"    # for elem in obj: isinstance(elem, {type(attribute)}")
                #         return elem
                attribute = getattr(elem, attribute_name, None)
                if attribute:
                    O19TuningInspector.inspector_log(f"    # for t in obj: attribute_name = getattr(t, 'attribute_name', None)")
                    return attribute
            # not found, workaround for isinstance
            for elem in obj:
                elem_str = f"{elem}"
                elem_str_lower = elem_str.lower()
                if elem_str_lower.startswith(attribute_name):
                    attribute = elem
                    O19TuningInspector.inspector_log(f"    # for t in obj: isinstance(t, {type(attribute)}")
                    return attribute
            O19TuningInspector.inspector_log(f"ERROR Could not get attribute '{attribute_name}' for object '{obj}: {type(obj)} - (tuple/list)'", True)

        elif isinstance(obj, dict):
            for _attribute_name, _attribute_value in obj.items():
                if f'{_attribute_name}' == f'attribute_name':
                    O19TuningInspector.inspector_log(f"    # attribute_name = obj['attribute_name']")
                    return _attribute_value
            O19TuningInspector.inspector_log(f"ERROR Could not get attribute '{attribute_name}' for object '{obj}: {type(obj)} - (dict)'", True)

        else:
            O19TuningInspector.inspector_log(f"ERROR Could not get attribute '{attribute_name}' for object '{obj}: {type(obj)} - (other)'", True)

        return None

    @staticmethod
    def o19_inspect_object(obj):
        found_something = False
        O19TuningInspector.inspector_log(f"    ** members **")
        try:
            for k, v in inspect.getmembers(obj):
                if not k.startswith('__'):
                    found_something = True
                    O19TuningInspector.inspector_log(f'        {k}: {type(k)} = {v}: {type(v)}')
        except Exception as e:
            O19TuningInspector.inspector_log(f"Error: {e}", True)
        if not found_something:
            O19TuningInspector.inspector_log(f"    ** objects **")
            try:
                for e in obj:
                    O19TuningInspector.inspector_log(f'        {e}: {type(e)}')
            except Exception as e:
                O19TuningInspector.inspector_log(f"Error: {e}", True)
