#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#

from set_tuning_values.modinfo import ModInfo

import ast
import importlib
import os
from typing import Union

import services
import sims4
import sims4.commands
from sims4.resources import get_resource_key

from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.zone_spin.events.zone_late_load import S4CLZoneLateLoadEvent
from sims4communitylib.utils.common_io_utils import CommonIOUtils
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
from sims4communitylib.utils.common_log_utils import CommonLogUtils

log: CommonLog = CommonLogRegistry.get().register_log(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)
log.enable()
log.debug(f"Starting {ModInfo.get_identity().name} v{ModInfo.get_identity().version} ")

class O19Tuner:
    config = {}
    script = dict()
    pc = 0
    lvl = 1
    items = dict()
    def __init__(self):
        mods_folder = None
        if os.name != 'nt':
            # Mac
            mods_folder = os.path.join(os.environ['HOME'], 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods')
        else:
            # Windows
            mods_folder = os.path.join(os.environ['USERPROFILE'], 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods')
        if not mods_folder:
            mods_folder = CommonLogUtils.get_sims_documents_location_path()
        if not mods_folder:
            log.warn("Could not locate 'Mods' folder")
            return
        mod_data = os.path.join(os.path.dirname(mods_folder), 'mod_data', ModInfo.get_identity().base_namespace)
        if log.enabled:
            if os.name != 'nt':
                _mod_data = mod_data.replace(os.environ['HOME'], '...')
            else:
                _mod_data = mod_data.replace(os.environ['USERPROFILE'], '...')
            log.debug(f"'Mod Data' folder: '{_mod_data}'")
        if not os.path.isdir(mod_data):
            log.warn(f"'{mod_data}' does not exist")
            return

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
        '''
        Stores 'script' in 'O19Tuner.script' as dict({programCounter: "level command"})
        The 'programCounter' increases after each command and gets reset to the previous value if a loop/if is left.
        The 'level' defines how nested the loops and ifs are.
        The 'command' is the well-known script command.
        :param script: The script to be executed
        :return:
        '''
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
            O19Tuner.script.update({_pc: f"{lvl:1d} {cmd.strip()}"})
            _pc += 1
        if not O19Tuner.script.get(1).startswith('1 '):
            log.error(f"ERROR: First command must not be intended.", throw=False)
            return
        log.debug(f"Script: '{O19Tuner.script}'.")

    @staticmethod
    def get_tuning_ids(_manager, _tunings) -> set:
        instance_manager = services.get_instance_manager(sims4.resources.Types[_manager])
        tuning_ids = set()
        tuning_names = dict()
        log.debug(f"{_tunings}")
        for _tuning in _tunings:
            if _tuning.startswith('*'):
                if _tuning.endswith('*'):
                    _tuning = _tuning[1:-1]
                    for (key, tuning_file) in instance_manager.types.items():
                        if f"{tuning_file.__name__}" in _tuning:
                            tuning_ids.add(key.instance)
                            tuning_names.update({key.instance: f"{tuning_file.__name__}"})
                else:
                    _tuning = _tuning[1:]
                    for (key, tuning_file) in instance_manager.types.items():
                        if f"{tuning_file.__name__}".endswith(_tuning):
                            tuning_ids.add(key.instance)
                            tuning_names.update({key.instance: f"{tuning_file.__name__}"})
            elif _tuning.endswith('*'):
                _tuning = _tuning[:-1]
                for (key, tuning_file) in instance_manager.types.items():
                    if f"{tuning_file.__name__}".startswith(_tuning):
                        tuning_ids.add(key.instance)
                        tuning_names.update({key.instance: f"{tuning_file.__name__}"})
            else:
                for (key, tuning_file) in instance_manager.types.items():
                    if f"{tuning_file.__name__}" == _tuning:
                        tuning_ids.add(key.instance)
                        tuning_names.update({key.instance: f"{tuning_file.__name__}"})
        log.debug(f"Tunings: '{tuning_names}'")
        tuning_names = None
        return tuning_ids


    def tune(self, log_only: bool = False):
        '''
        Function to process all '*.dict' files in 'The Sims 4/mod_data/{ModInfo.get_identity().name}/'
        :param log_only: Do not run any commands.
        :return:
        '''
        config = O19Tuner.config
        try:
            for description, data in config.items():
                log.debug(f"Processing '{description}'")
                _manager = data.get('manager')
                _tunings = data.get('tunings')
                tuning_ids = self.get_tuning_ids(_manager, _tunings)
                _items = data.get('items')
                _process = data.get('process')
                self.convert_process_to_script(_process)
                self.process_tunings(_manager, tuning_ids, _items)
        except Exception as e:
            log.warn(f"Error '{e}'")

    @staticmethod
    def get_items(tuning, _items: list) -> Union[None, dict]:
        items = {'tuning': tuning}
        skip_tuning = False
        i = None

        _parent = tuning
        for _item in _items:
            _parent = tuning
            for i in _item.split('.'):
                try:
                    _parent = getattr(_parent, i)
                    items.update({i: _parent})
                    log.debug(f'i: {type(_parent)} = {_parent}')
                except:
                    skip_tuning = True
                    break
            if skip_tuning:
                break
        if skip_tuning:
            log.warn(f"\tItem '{i}' not found, skipping tuning.")
            return None
        log.debug(f"\tItems '{items}'")
        return items

    def process_tunings(self, _manager: str, tuning_ids: set, _items: list):
        for tuning_id in tuning_ids:
            log.debug(f"")
            log.debug(f"Processing tuning '{tuning_id}' ...")

            instance_manager = services.get_instance_manager(sims4.resources.Types[_manager])
            tuning = instance_manager.get(tuning_id)
            items = self.get_items(tuning, _items)
            if items is None:
                log.error(f"Error within tuning_id '{tuning_id}', skipping it.", throw=False)
                continue

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
                        print(f"Skipping {lvl_cmd}")

    def process_command(self, cmd):
        log_prefix = f"\t" * O19Tuner.lvl
        log.debug(f"{log_prefix}{O19Tuner.lvl:01d} {O19Tuner.pc:02d} Processing command '{cmd}'")
        cmd = cmd.replace(" ", "").replace("\t", "")

        if cmd.startswith('setattr:'):  # 'setattr: obj*, name, value*'
            _obj, _name, _value = cmd.split(':')[1].split(',', 2)
            setattr(O19Tuner.items.get(_obj), _name, O19Tuner.items.get(_value))
            log.debug(f"{log_prefix}(setattr) [{_obj}: {type(O19Tuner.items.get(_obj))} = {O19Tuner.items.get(_obj)}], [{_name}: {type(O19Tuner.items.get(_name))}].[{O19Tuner.items.get(_name)}] = [{_value}: {type(O19Tuner.items.get(_value))} = {O19Tuner.items.get(_value)}]")

        elif cmd.startswith('getattr:'):  # 'getattr: var* = obj*, name'
            _var, _obj__name = cmd.split(":", 1)[1].split('=', 1)
            _obj, _name = _obj__name.split(',', 1)
            _rv = getattr(O19Tuner.items.get(_obj), _name)
            O19Tuner.items.update({_var: _rv})
            log.debug(f"{log_prefix}(getattr) {_var}: {type(_rv)} = {_rv}")

        elif cmd.startswith('set:'):  # 'set: var* = value'
            _var, _value = cmd.split(":", 1)[1].split('=', 1)
            _value = self.parse_value(_value)
            O19Tuner.items.update({_var: _value})
            log.debug(f"{log_prefix}(set) {_var}: {type(_value)} = {_value}")

        elif cmd.startswith('class:'):  # 'class: var* = a.b.c.D'
            _item_class_name, _class_string = cmd.split(":")[1].split('=', 1)
            _module_name, _class_name = _class_string.rsplit('.', 1)
            _class = getattr(importlib.import_module(_module_name), _class_name)
            O19Tuner.items.update({_item_class_name: _class})
            log.debug(f"{log_prefix}(class) {_item_class_name}: {type(_class)} = {_class}")

        elif cmd.startswith('cwo:'):  # 'cwo: var* = obj*, key, new-value*'
            _var, _obj__key__new_value = cmd.split(":", 1)[1].split('=', 1)
            _obj, _key, _new_value = _obj__key__new_value.split(',', 2)
            rv = O19Tuner.items.get(_obj).clone_with_overrides(**{_key: O19Tuner.items.get(_new_value)})
            O19Tuner.items.update({_var: rv})
            log.debug(f"{log_prefix}(cwo) {_var}: {type(rv)} = {rv}")

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
                        print("End of if")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

                pass
                # go one level deeper and process it

        elif cmd.startswith('foreach:'):  # 'foreach: var*, _vars*'
            _var, _vars = cmd.split(":", 1)[1].split(',', 1)
            this_lvl = O19Tuner.lvl
            this_pc = O19Tuner.pc
            next_lvl = this_lvl + 1
            next_pc = this_pc + 1
            log.debug(f" ---- {O19Tuner.items.get(_vars)}")
            for __var in O19Tuner.items.get(_vars):
                log.debug(f" ---- ---- {__var}")
                O19Tuner.items.update({_var: __var})
                log.debug(f" ---- ---- {next_pc} ---- {len(O19Tuner.script)}")
                for _pc in range(next_pc, len(O19Tuner.script)):
                    lvl, cmd = O19Tuner.script.get(_pc).split(' ', 1)
                    lvl = int(lvl)
                    if lvl == next_lvl:
                        O19Tuner.lvl = lvl
                        O19Tuner.pc = _pc
                        self.process_command(cmd)
                    if lvl == this_lvl:
                        print("End of loop, exiting")
                        O19Tuner.lvl = this_lvl
                        O19Tuner.pc = this_pc
                        break

    @staticmethod
    def parse_value(value) -> Union[None, bool, int, str, float]:
        '''
        Simple method to set the type for the supplied string variable properly.
        :param value: A string value which will be converted to int/float/bool/None if possible
        :return: The converted type.
        '''
        if value.capitalize() == 'None':
            var = None
        elif value.capitalize() == 'True':
            var = True
        elif value.capitalize() == 'False':
            var = False
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
                    var = str(value)  # String assignment as last resort
        return var

o19_tuner = O19Tuner()


@CommonEventRegistry.handle_events(ModInfo.get_identity().name)
def handle_event(event_data: S4CLZoneLateLoadEvent):
    log.enable()
    log.info("Modifying tuning values ...")
    global o19_tuner
    if not o19_tuner:
        o19_tuner = O19Tuner()
    o19_tuner.tune(log_only=True)
    log.disable()  # Use 'o19.set_tuning_values.reload' to get a log or enable logging with ??
    o19_tuner.tune()


@sims4.commands.Command('o19.set_tuning_values.reload', command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_dump_all(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        log.enable()
        output(f"Processing is logged to 'mod_logs'.")
        global o19_tuner
        o19_tuner = O19Tuner()  # Read again all modified files
        o19_tuner.tune()
        log.disable()
        output(f"Done")
    except Exception as ex:
        output(f"Error: {ex}")


@sims4.commands.Command('o19.set_tuning_values.log', command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_dump_all(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        log.enable()
        output(f"Tunigs are logged to 'mod_logs'.")
        global o19_tuner
        if not o19_tuner:
            o19_tuner = O19Tuner()
        o19_tuner.tune(log_only=True)
        log.disable()
        output(f"Done")
    except Exception as ex:
        output(f"Error: {ex}")
