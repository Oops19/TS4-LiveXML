#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


import ast
import importlib
import inspect
import os
import time
from typing import Union, Tuple

from live_xml.modinfo import ModInfo
import sims4
import sims4.commands
from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.zone_spin.events.zone_late_load import S4CLZoneLateLoadEvent
from sims4communitylib.utils.common_io_utils import CommonIOUtils
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
from ts4lib.libraries.ts4folders import TS4Folders
from ts4lib.utils.basic_extras import BasicExtras
from ts4lib.utils.tuning_helper import TuningHelper

log: CommonLog = CommonLogRegistry.get().register_log(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)
log.enable()
log.debug(f"Starting {ModInfo.get_identity().name} v{ModInfo.get_identity().version}")
log.disable()


class O19Tuner:
    initialized = False
    config = {}
    script = dict()
    pc = 0
    lvl = 1
    items = dict()

    def __init__(self):
        ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
        mod_data = ts4f.data_folder
        os.makedirs(mod_data, exist_ok=True)

        io = CommonIOUtils()
        _config = {}
        for file in os.listdir(mod_data):
            if not file.endswith(".dict"):
                log.debug(f"Skipping '{file}'")
                continue
            log.debug(f"Reading '{file}'")
            try:
                __cfg = ast.literal_eval(io.load_from_file(os.path.join(mod_data, file)))
                _config = {**__cfg, **_config}
            except:
                log.warn(f"Error parsing file")
                continue
        log.debug(f"Final configuration: {_config}")
        O19Tuner.config = _config

    @staticmethod
    def convert_process_to_script(script: []):
        """
        Stores 'script' in 'O19Tuner.script' as dict({programCounter: "level command"})
        The 'programCounter' increases after each command and gets reset to the previous value if a loop/if is left.
        The 'level' defines how nested the loops and ifs are.
        The 'command' is the well-known script command.
        :param script: The script to be executed
        :return:
        """
        _script = dict()
        O19Tuner.pc = 0
        O19Tuner.lvl = 0
        _pc = 0
        for cmd in script:
            lvl_array = cmd.split(":", 1)[0].replace("    ", "\t").split('\t')
            lvl = len(lvl_array)  # all commands must end with ':' !! (var = cwo: needs change !!)
            if lvl > 9:
                log.error(f"ERROR: Max supported recursion reached for '{cmd}'.", throw=False)
                return
            if lvl_array[-1].startswith(' '):
                log.error(f"ERROR: Command '{cmd}' contains wrong number of leading SPACE characters (0, 4, 8, 12, ... required).", throw=False)
                return
            _script.update({_pc: f"{lvl:1d} {cmd.strip()}"})
            _pc += 1
        if not _script.get(0).startswith('1 '):
            log.error(f"ERROR: First command must not be intended.", throw=False)
            return
        O19Tuner.script = _script
        log.debug(f"Script: '{O19Tuner.script}'.")

    def tune(self, log_only: bool = False):
        """
        Function to process all '*.dict' files in 'The Sims 4/mod_data/{ModInfo.get_identity().name}/'
        :param log_only: Do not run any commands. - Currently not supported!
        :return:
        """
        config = O19Tuner.config
        try:
            for description, data in config.items():
                log.debug(f"Processing '{description}'")
                _manager_imp = data.get('manager_imp', 'INTERACTION')
                _tunings_imp = data.get('tunings_imp', None)
                tunings_imp_ids = tuple()
                tunings_imp_tunings = tuple()
                if _tunings_imp:
                    tunings_imp_dict = TuningHelper().get_tuning_dict(_manager_imp, _tunings_imp)
                    for tuning_id, elements in tunings_imp_dict.items():
                        tunings_imp_ids += (tuning_id,)
                        tuning = elements[0]
                        tunings_imp_tunings += (tuning,)

                _manager = data.get('manager', 'INTERACTION')
                _tunings = data.get('tunings')
                tuning_dict = TuningHelper().get_tuning_dict(_manager, _tunings)
                _process = data.get('process', None)
                if _process:
                    _items = data.get('items')
                    self.convert_process_to_script(_process)
                    log.debug(f"m={_manager}\ni={_items}\np={_process}\ns={self.script}")
                    self.process_tunings(tuning_dict, _items, tunings_imp_ids, tunings_imp_tunings)
                _command = data.get('command', None)
                if _command:
                    _command_parameters = data.get('command_parameters', '')
                    _command_timing = data.get('command_timing', 'at_end')
                    _command_offset_time = data.get('command_offset_time', None)
                    _command_xevt_id = data.get('command_xevt_id', None)
                    log.debug(f"c={_command}; p={_command_parameters}; t={_command_timing}; o={_command_offset_time}; x={_command_xevt_id}")
                    BasicExtras().add_do_command(_manager, _tunings, _command, _command_parameters,
                                               _command_timing, _command_offset_time, _command_xevt_id)

        except Exception as e:
            log.error(f"{e}")

    @staticmethod
    def get_items(tuning, _items: list) -> Union[None, dict]:
        items = {'tuning': tuning}
        skip_tuning = False

        _parent = tuning
        if _items:
            for _item in _items:
                _parent = tuning
                for i in _item.split('.'):
                    try:
                        _parent = getattr(_parent, i, None)
                        items.update({i: _parent})
                        if _parent is None:
                            log.warn(f'i: {type(_parent)} = {_parent}')
                        else:
                            log.debug(f'i: {type(_parent)} = {_parent}')
                    except:
                        skip_tuning = True
                        break
                if skip_tuning:
                    break
            if skip_tuning:
                log.warn(f"\tError processing tuning, skipping tuning.")
                return None
        log.debug(f"\tItems '{items}'")
        return items

    def process_tunings(self, tuning_dict: dict, _items: list, tunings_imp_ids: Tuple = tuple(), tunings_imp_tunings: Tuple = tuple()):
        for tuning_id, elements in tuning_dict.items():
            tuning = elements[0]
            # manager_name = elements[1]
            tuning_name = elements[2]

            log.debug(f"")
            log.debug(f"Processing tuning '{tuning_name}({tuning_id})' ...")

            items = self.get_items(tuning, _items)
            if items is None:
                log.error(f"Error within tuning_id '{tuning_id}', skipping it.", throw=False)
                continue

            if tunings_imp_ids:
                items.update({'tunings_imp_ids': tunings_imp_ids})
                items.update({'tunings_imp_tunings': tunings_imp_tunings})
                log.debug(f"tunings_imp_ids: tuple = {tunings_imp_ids}")
                log.debug(f"tunings_imp_tunings: tuple = {tunings_imp_tunings}")

            O19Tuner.items = items
            for pc, lvl_cmd in O19Tuner.script.items():
                lvl, cmd = lvl_cmd.split(' ', 1)
                lvl = int(lvl)
                if lvl == 1:
                    if not cmd.startswith("#"):
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = pc
                        self.process_command(cmd)
                    else:
                        log.debug(f"Skipping {lvl_cmd}")

    def process_command(self, cmd):
        log_prefix = f"\t" * O19Tuner.lvl
        log.debug(f"{log_prefix}{O19Tuner.lvl:01d} {O19Tuner.pc:02d} Processing command '{cmd}'")
        cmd = cmd.replace(" ", "").replace("\t", "")

        if cmd.startswith('assign:'):  # 'assign: var* = value'
            _var, _value = cmd.split(":", 1)[1].split('=', 1)
            _value = self.parse_value(_value)
            O19Tuner.items.update({_var: _value})
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(_value)} = {_value}")

        elif cmd.startswith('mul:') or cmd.startswith('div:') or cmd.startswith('add:') or cmd.startswith('addut:') or cmd.startswith('addul:') or cmd.startswith('sub:'):  # 'mul: var* = var*, var*'
            _cmd = cmd.split(":", 1)[0]
            _var, _vars = cmd.split(":", 1)[1].split('=', 1)
            _var1, _var2 = _vars.split(',', 1)
            v1 = O19Tuner.items.get(_var1)
            v2 = O19Tuner.items.get(_var2)
            _value = v1
            try:
                if cmd.startswith('add:'):
                    _value = v1 + v2
                elif cmd.startswith('addut:'):
                    _value = tuple(set(v1 + v2))
                elif cmd.startswith('addul:'):
                    _value = list(set(v1 + v2))
                elif cmd.startswith('sub:'):
                    _value = v1 - v2
                elif cmd.startswith('mul:'):
                    _value = v1 * v2
                else:
                    _value = v1 / v2
                if isinstance(v1, int) and isinstance(v2, int):
                    _value = int(_value)

                O19Tuner.items.update({_var: _value})
                log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(_value)} = {_value}")
            except Exception as e:
                log.error(f"{log_prefix}Error: '{cmd}' ({v1}+-*/{v2}): '{e}'")

        elif cmd.startswith('setattr:'):  # 'setattr: obj*, name, value*'
            _obj, _name, _value = cmd.split(':')[1].split(',', 2)
            if O19Tuner.items.get(_obj):
                setattr(O19Tuner.items.get(_obj), _name, O19Tuner.items.get(_value))
                log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) [{_obj}: {type(O19Tuner.items.get(_obj))} = {O19Tuner.items.get(_obj)}], [{_name}: {type(O19Tuner.items.get(_name))}].[{O19Tuner.items.get(_name)}] = [{_value}: {type(O19Tuner.items.get(_value))} = {O19Tuner.items.get(_value)}]")
            else:
                log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_name}: obj is None")

        elif cmd.startswith('getattr:'):  # 'getattr: var* = obj*, name'
            _var, _obj__name = cmd.split(":", 1)[1].split('=', 1)
            _obj, _name = _obj__name.split(',', 1)
            if O19Tuner.items.get(_obj):
                _rv = getattr(O19Tuner.items.get(_obj), _name, None)
            else:
                _rv = None
            O19Tuner.items.update({_var: _rv})
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(_rv)} = {_rv}")

        elif cmd.startswith('classstr:'):  # "classstr: var* = <class '...'>"  # use double quotes !
            # for classes which can not be zone_loaded (assign will also work)
            _var, _classstr = cmd.split(":", 1)[1].split('=', 1)
            _value = self.parse_value(_classstr)
            O19Tuner.items.update({_var: _classstr})
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(_classstr)} = {_classstr}")

        elif cmd.startswith('class:'):  # 'class: var* = a.b.c.CONFIGURATION_DATA'
            _item_class_name, _class_string = cmd.split(":")[1].split('=', 1)
            _module_name, _class_name = _class_string.rsplit('.', 1)
            _class = getattr(importlib.import_module(_module_name), _class_name)
            O19Tuner.items.update({_item_class_name: _class})
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_item_class_name}: {type(_class)} = {_class}")

        elif cmd.startswith('tuning:'):  # 'tuning: var* = name'
            _var, _tuning_name = cmd.split(":", 1)[1].split('=', 1)
            tuning_dict = TuningHelper().get_tuning_dict(None, [_tuning_name, ])
            tuning_id, elements = tuning_dict.popitem()
            tuning = elements[0]
            manager_name = elements[1]
            tuning_name = elements[2]
            O19Tuner.items.update({_var: tuning})
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(tuning)} = {tuning} [manager={manager_name}, tuning={tuning_name}({tuning_id}]")

        elif cmd.startswith('del:'):  # 'tuning: var* = name'
            _var, _obj = cmd.split(":", 1)[1].split(',', 1)
            _list = O19Tuner.items.get(_var)
            _element = O19Tuner.items.get(_obj)
            if _list and _element:
                try:
                    del _list[_element]
                except:
                    if isinstance(_list, set) and _element in _list:
                        _list.remove(_element)
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(_list)} = {_list}")

        elif cmd.startswith('print:'):  # 'print: var*'
            _var = cmd.split(":", 1)[1]
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) `{_var}´: `{type(O19Tuner.items.get(_var))}´ = `{O19Tuner.items.get(_var)}´")

        elif cmd.startswith('printmembers:'):  # 'printmembers: var*'
            _var = cmd.split(":", 1)[1]
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) `{_var}´: `{type(O19Tuner.items.get(_var))}´ = `{O19Tuner.items.get(_var)}´")
            found_something = False
            try:
                for k, v in inspect.getmembers(O19Tuner.items.get(_var)):
                    if not k.startswith('__'):
                        found_something = True
                        log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) `{k}´: `{type(k)}´ = `{v}´: `{type(v)}´")
            except Exception as e:
                log.error(f"Error: {e}", throw=True)
            if not found_something:
                log.debug(f"No members, logging objects:")
                try:
                    for e in O19Tuner.items.get(_var):
                        log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) `{e}´: `{type(e)}´")
                except Exception as e:
                    log.error(f"Error: {e}", throw=True)

        elif cmd.startswith('set:') or cmd.startswith('frozenset:') or cmd.startswith('tuple:'):  # 'set: var* = a, b, c, ...' or 'frozenset: ...' or 'tuple: ...'
            _var, __values = cmd.split(":", 1)[1].split('=', 1)

            if __values[:2] == '**' and __values[-2:] == '**':
                _value = O19Tuner.items.get(__values[2:-2])
                if cmd.startswith('frozenset:'):
                    _list = frozenset(_value)
                elif cmd.startswith('tuple:'):
                    _list = tuple()
                    _list = _list + (_value,)
                elif cmd.startswith('set:'):
                    _list = set()
                    _list.add(_value, )
                else:
                    _list = list()
                    _list.append(_value, )
            else:
                _list = list()
                if __values != '':
                    _values = __values.split(',')
                    for _value in _values:
                        _value = self.parse_value(_value)
                        _list.append(_value)
                if cmd.startswith('frozenset:'):
                    _list = frozenset(_list)
                elif cmd.startswith('tuple:'):
                    _list = tuple(_list)
                elif cmd.startswith('set:'):
                    _list = set(_list)

            O19Tuner.items.update({_var: _list})
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(_list)} = {_list}")

        elif cmd.startswith('cwo:'):  # 'cwo: var* = obj*, key, new-value*'
            _var, _obj__key__new_value = cmd.split(":", 1)[1].split('=', 1)
            _obj, _key, _new_value = _obj__key__new_value.split(',', 2)
            if O19Tuner.items.get(_obj):
                rv = O19Tuner.items.get(_obj).clone_with_overrides(**{_key: O19Tuner.items.get(_new_value)})
            else:
                rv = None
            O19Tuner.items.update({_var: rv})
            log.debug(f"{log_prefix}({cmd.split(':', 1)[0]}) {_var}: {type(rv)} = {rv}")

        elif cmd.startswith('if:') or cmd.startswith('ifnot:'):  # 'if: var*' or 'ifnot: var*'
            _var = cmd.split(":", 1)[1]
            if (cmd.startswith('if:') and O19Tuner.items.get(_var)) or (cmd.startswith('ifnot:') and not O19Tuner.items.get(_var)):
                this_lvl = O19Tuner.lvl
                this_pc = O19Tuner.pc
                next_lvl = this_lvl + 1
                next_pc = this_pc + 1
                for _pc in range(next_pc, len(O19Tuner.script)):
                    lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                    lvl = int(lvl)
                    if lvl == next_lvl:
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = _pc
                        self.process_command(cmd)
                    if lvl == this_lvl:
                        log.debug("End of if")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

        elif cmd.startswith('ifis:') or cmd.startswith('ifnotis:'):  # 'ifis: var*, var*' or 'ifnotis: var*, var*'
            _var, _var2 = cmd.split(":", 1)[1].split(',')
            if (cmd.startswith('ifis:') and O19Tuner.items.get(_var) == O19Tuner.items.get(_var2)) or (cmd.startswith('ifnotis:') and O19Tuner.items.get(_var) != O19Tuner.items.get(_var2)):
                this_lvl = O19Tuner.lvl
                this_pc = O19Tuner.pc
                next_lvl = this_lvl + 1
                next_pc = this_pc + 1
                for _pc in range(next_pc, len(O19Tuner.script)):
                    lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                    lvl = int(lvl)
                    if lvl == next_lvl:
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = _pc
                        self.process_command(cmd)
                    if lvl == this_lvl:
                        log.debug("End of if")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

        elif cmd.startswith('ifin:') or cmd.startswith('ifnotin:'):  # 'ifin: var*, var*' or 'ifnotin: var*, var*'
            _var, _list = cmd.split(":", 1)[1].split(',')
            if (cmd.startswith('ifin:') and O19Tuner.items.get(_var) in O19Tuner.items.get(_list)) or (cmd.startswith('ifnotin:') and O19Tuner.items.get(_var) not in O19Tuner.items.get(_list)):
                this_lvl = O19Tuner.lvl
                this_pc = O19Tuner.pc
                next_lvl = this_lvl + 1
                next_pc = this_pc + 1
                for _pc in range(next_pc, len(O19Tuner.script)):
                    lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                    lvl = int(lvl)
                    if lvl == next_lvl:
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = _pc
                        self.process_command(cmd)
                    if lvl == this_lvl:
                        log.debug("End of if")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

        elif cmd.startswith('isinstance:'):  # 'isinstance: var*, class*'
            _var, _class = cmd.split(":", 1)[1].split(',', 1)
            if isinstance(O19Tuner.items.get(_var), O19Tuner.items.get(_class)):
                this_lvl = O19Tuner.lvl
                this_pc = O19Tuner.pc
                next_lvl = this_lvl + 1
                next_pc = this_pc + 1
                for _pc in range(next_pc, len(O19Tuner.script)):
                    lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                    lvl = int(lvl)
                    if lvl == next_lvl:
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = _pc
                        self.process_command(cmd)
                    if lvl == this_lvl:
                        log.debug("End of if")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

        elif cmd.startswith('isinstancetypestr:'):  # 'isinstancetypestr: var*, class_type_str*'
            # for classes which can not be zone_loaded
            _var, class_type_str = cmd.split(":", 1)[1].split(',', 1)
            __var = O19Tuner.items.get(_var)
            __class_type_str = O19Tuner.items.get(class_type_str)
            if __var is None or __class_type_str is None:
                log.warn(f"var={__var} andd classstr={__class_type_str} - test fails!")
                return
            _type_var = type(__var)
            if f"{__var}: {_type_var}".replace(' ', '') == __class_type_str.replace(' ', ''):
                this_lvl = O19Tuner.lvl
                this_pc = O19Tuner.pc
                next_lvl = this_lvl + 1
                next_pc = this_pc + 1
                for _pc in range(next_pc, len(O19Tuner.script)):
                    lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                    lvl = int(lvl)
                    if lvl == next_lvl:
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = _pc
                        self.process_command(cmd)
                    if lvl == this_lvl:
                        log.debug("End of if")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

        elif cmd.startswith('isinstancestr:'):  # 'isinstancestr: var*, classstr*'
            # for classes which can not be zone_loaded
            _var, _classstr = cmd.split(":", 1)[1].split(',', 1)
            __var = O19Tuner.items.get(_var)
            _type_var = type(__var)
            __classstr = O19Tuner.items.get(_classstr)
            if _type_var is None or __classstr is None:
                log.warn(f"var={__var}: {_type_var} and classstr={__classstr} - test fails!")
                return
            if f"{_type_var}".replace(' ', '') == O19Tuner.items.get(_classstr).replace(' ', ''):
                this_lvl = O19Tuner.lvl
                this_pc = O19Tuner.pc
                next_lvl = this_lvl + 1
                next_pc = this_pc + 1
                for _pc in range(next_pc, len(O19Tuner.script)):
                    lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                    lvl = int(lvl)
                    if lvl == next_lvl:
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = _pc
                        self.process_command(cmd)
                    if lvl == this_lvl:
                        log.debug("End of if")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

        elif cmd.startswith('foreach:'):  # 'foreach: var*, _vars*'
            _var, _vars = cmd.split(":", 1)[1].split(',', 1)
            if O19Tuner.items.get(_vars):
                this_lvl = O19Tuner.lvl
                this_pc = O19Tuner.pc
                next_lvl = this_lvl + 1
                next_pc = this_pc + 1
                for __var in O19Tuner.items.get(_vars):
                    O19Tuner.items.update({_var: __var})
                    for _pc in range(next_pc, len(O19Tuner.script)):
                        lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                        lvl = int(lvl)
                        if lvl == next_lvl:
                            O19Tuner.lvl = lvl
                            O19Tuner.pc = _pc
                            self.process_command(cmd)
                        if lvl == this_lvl:
                            log.debug("End of loop, exiting")
                            O19Tuner.lvl = this_lvl
                            O19Tuner.pc = this_pc
                            break
            else:
                log.debug(f"'{cmd.split(':', 1)[0]} __var in _vars:' is None")
        else:
            log.warn(f"Unknown command: '{cmd}'")

    @staticmethod
    def parse_value(value) -> Union[None, bool, int, str, float]:
        """
        Simple method to set the type for the supplied string variable properly.
        :param value: A string value which will be converted to int/float/bool/None if possible
        :return: The converted type.
        """
        if isinstance(value, type(None)):
            var = None
        elif isinstance(value, bool):
            var = bool(value)
        else:
            # Not a binary 'True/False/None' assignment
            # Check for isdecimal() to convert it to int().
            #   '½'.isnumeric() == True, this is a str() and not an int() assignment
            #   '²'.isdigit() == True, this is a str() and not an int() assignment
            if value.isdecimal() or value.lstrip('-').isdecimal():
                var = int(value)
            else:
                try:
                    var = float(value)
                except ValueError:
                    if isinstance(value, str):
                        if value.capitalize() == 'None':
                            var = None
                        elif value.capitalize() == 'True':
                            var = True
                        elif value.capitalize() == 'False':
                            var = False
                        else:
                            var = str(value)
                    else:
                        var = str(value)  # String assignment as last resort
        return var


o19_tuner = O19Tuner()


@CommonEventRegistry.handle_events(ModInfo.get_identity().name)
def handle_event(event_data: S4CLZoneLateLoadEvent):
    if O19Tuner.initialized:
        log.enable()
        log.info("Already initialized ...")
        log.disable()
        return
    log.enable()
    log.info("Modifying tuning values ...")
    log.disable()
    global o19_tuner
    # log.enable()  # TODO comment for release
    if not o19_tuner:
        o19_tuner = O19Tuner()
    t = time.time()
    # log.enable()  # TODO comment for release
    o19_tuner.tune()
    dt = time.time() - t
    log.enable()
    log.debug(f"Duration: {dt:.3f}")
    log.disable()
    O19Tuner.initialized = True


@sims4.commands.Command('o19.live_xml.reload', command_type=sims4.commands.CommandType.Live)
def debug_o19_live_xml_reload(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        log.enable()
        output(f"Processing is logged to 'mod_logs'.")
        global o19_tuner
        o19_tuner = O19Tuner()  # Read again all modified files
        t = time.time()
        o19_tuner.tune()
        dt = time.time() - t
        output(f"Done, duration: {dt:.3f} (without logs: {dt / 2.5:.1f})")
        log.disable()
    except Exception as ex:
        output(f"Error: {ex}")


@sims4.commands.Command('o19.live_xml.log', command_type=sims4.commands.CommandType.Live)
def debug_o19_live_xml_log(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        log.enable()
        output(f"Tunings are logged to 'mod_logs'.")
        global o19_tuner
        if not o19_tuner:
            o19_tuner = O19Tuner()
        o19_tuner.tune(log_only=True)
        log.disable()
        output(f"Done")
    except Exception as ex:
        output(f"Error: {ex}")
