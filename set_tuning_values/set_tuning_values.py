#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#
import ast
import os

import services
import sims4
import sims4.commands

from set_tuning_values.modinfo import ModInfo
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
    def tune(log_only: bool = False):
        # TODO Move 'config' to 'The Sims 4/mod_data/{ModInfo.get_identity().name}/config.dict'
        ' The format should be obvious, also the order how things get processed'
        config = O19Tuner.config
        try:
            for description, data in config.items():
                log.debug(f"Processing '{description}'")
                _manager = data.get('manager')
                _tuning = data.get('tuning')
                _items = data.get('items')
                _process = data.get('process')

                instance_manager = services.get_instance_manager(sims4.resources.Types[_manager])
                tuning_ids = set()
                log.debug(f"{_tuning}")
                if _tuning.startswith('*'):
                    if _tuning.endswith('*'):
                        _tuning = _tuning[1:-1]
                        for (key, tuning_file) in instance_manager.types.items():
                            if f"{tuning_file.__name__}" in _tuning:
                                tuning_ids.add(key.instance)
                    else:
                        _tuning = _tuning[1:]
                        for (key, tuning_file) in instance_manager.types.items():
                            if f"{tuning_file.__name__}".endswith(_tuning):
                                tuning_ids.add(key.instance)
                elif _tuning.endswith('*'):
                    _tuning = _tuning[:-1]
                    for (key, tuning_file) in instance_manager.types.items():
                        if f"{tuning_file.__name__}".startswith(_tuning):
                            tuning_ids.add(key.instance)
                else:
                    for (key, tuning_file) in instance_manager.types.items():
                        if f"{tuning_file.__name__}" == _tuning:
                            tuning_ids.add(key.instance)
                log.debug(f"Tunings: '{tuning_ids}'")

                for tuning_id in tuning_ids:
                    log.debug(f"")
                    log.debug(f"Processing tuning '{tuning_id}' ...")
                    skip_tuning = False
                    i = None
                    tuning = instance_manager.get(tuning_id)
                    items = {'tuning': tuning}
                    _parent = tuning
                    for _item in _items:
                        _parent = tuning
                        for i in _item.split('.'):
                            try:
                                _parent = getattr(_parent, i)
                                items.update({i: _parent})
                            except:
                                skip_tuning = True
                                break
                        if skip_tuning:
                            break
                    if skip_tuning:
                        log.warn(f"\tItem '{i}' not found, skipping tuning '{tuning_id}'.")
                        break
                    log.debug(f"\tItems '{items}'")
                    if log_only:
                        continue

                    for p in _process:
                        log.debug(f"\tProcessing command '{p}' ...")
                        # {'tuning': <class 'sims4.tuning.instances.buff_Object_MassageChair_WornOutNails'>,
                        # '_temporary_commodity_info': ImmutableSlots({'categories': frozenset(), 'max_duration': 1440, 'persists': True}),
                        #  'max_duration': 1440}
                        #     'var': ImmutableSlots({'categories': frozenset(), 'max_duration': 4320, 'persists': True})}

                        p = p.replace(" ", "")
                        if p.startswith('setattr:'):
                            _obj, _name, _value = p.split(':')[1].split(',')
                            setattr(items.get(_obj), _name, items.get(_value))
                            log.debug(f"setattr: {_obj}: {type(items.get(_obj))} = {items.get(_obj)}; {_name}: {type(items.get(_name))} = {items.get(_name)}; {_value}: {type(items.get(_value))} = {items.get(_value)}")
                            # setattr: tuning: <class 'sims4.tuning.class.instances.HashedTunedInstanceMetaclass'> = <class 'sims4.tuning.instances.buff_Object_MassageChair_WornOutNails'>
                            # _temporary_commodity_info: <class 'sims4.collections.make_immutable_slots_class.<locals>.ImmutableSlots'> = ImmutableSlots({'categories': frozenset(), 'max_duration': 1440, 'persists': True})
                            # var: <class 'sims4.collections.make_immutable_slots_class.<locals>.ImmutableSlots'> = ImmutableSlots({'categories': frozenset(), 'max_duration': 4320, 'persists': True})
                            # setattr: <class 'sims4.tuning.instances.buff_Object_MassageChair_WornOutNails'> <class 'sims4.tuning.class.instances.HashedTunedInstanceMetaclass'>  ImmutableSlots({'categories': frozenset(), 'max_duration': 1440, 'persists': True}) <class 'sims4.collections.make_immutable_slots_class.<locals>.ImmutableSlots'>  ImmutableSlots({'categories': frozenset(), 'max_duration': 1440, 'persists': True}) <class 'sims4.collections.make_immutable_slots_class.<locals>.ImmutableSlots'>

                        elif p.startswith('var'):
                            p = p.split("=")[1]
                            if p.startswith('cwo:'):
                                _obj, _key, _value = p.split(":")[1].split(',')
                                var = items.get(_obj).clone_with_overrides(**{_key: items.get(_value)})
                                log.debug(f"\tcwo: {_obj}: {type(items.get(_obj))} = {items.get(_obj)}; {_key}: {type(items.get(_key))} = {items.get(_key)}; {_value}: {type(items.get(_value))} = {items.get(_value)}")
                                # cwo: ImmutableSlots({'categories': frozenset(), 'max_duration': 1440, 'persists': True}) <class 'sims4.collections.make_immutable_slots_class.<locals>.ImmutableSlots'>
                                # 1440 <class 'int'>
                                # 4320 <class 'str'>
                                # var = ImmutableSlots({'categories': frozenset(), 'max_duration': 4320, 'persists': True}) ?

                            else:
                                # simple assignment
                                if p.isdecimal():
                                    var = int(p)
                                else:
                                    if p.capitalize() == 'True':
                                        var = True
                                    elif p.capitalize() == 'False':
                                        var = False
                                    else:
                                        try:
                                            var = float(p)
                                        except ValueError:
                                            var = str(p)  # String assignment
                            items.update({'var': var})
                            log.debug(f"\tvar: {type(var)} = {var}")
                        else:
                            log.warn(f"\tError processing: '{p}' in tuning '{tuning_id}'")
                            break
        except Exception as e:
            log.warn(f"Error '{e}'")


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
        if not o19_tuner:
            o19_tuner = O19Tuner()
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
