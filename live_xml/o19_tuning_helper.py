#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


import time
from typing import Union, Dict, Set

from live_xml.modinfo import ModInfo

import sims4
import sims4.commands
from server_commands.tuning_commands import get_managers
from sims4.resources import get_resource_key
import services

from sims4communitylib.utils.common_log_registry import CommonLogRegistry, CommonLog


log: CommonLog = CommonLogRegistry.get().register_log(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)


class O19TuningHelper:

    manager = None
    dt_sum = 0

    @staticmethod
    def get_tuning_ids(manager: Union[None, str], tuning_names: list) -> Set[int]:
        """
        :param manager: see @get_tuning_dict
        :param tuning_names: see @get_tuning_dict
        :return: A set with all matching tuning IDs.
        """
        tuning_dict = O19TuningHelper.get_tuning_dict(manager, tuning_names)
        return set(tuning_dict.keys())

    @staticmethod
    def get_tuning_dict(manager: Union[None, str], tuning_names: list) -> Dict[int, tuple]:
        """
        Interactive usage is fine, monitor times when using it in production and if it is called multiple times.
        This method is slow as it creates a dict and does not only return the tunings.
        :param manager: Identifier to select an instance_manager. Eg BUFF, TRAIT, ... 'None' will iterate over all manager and this will take some time!
        :param tuning_names: A list with tuning IDs as strings for this instance_manager.
        Supported formats: * '123' or '0xabc' to specify the tuning ID directly.
        * ' 123' or ' 0xabc' to specify a tuning name which looks like a number (in case this ever happens)
        * 'tuning_name' to specify a full name, eg: 'buff_sleep' or something like this
        * 'tuning_*' to specify all tuning_names which start with 'tuning_'
        * '*_name' to specify all tuning_names which end with '_name'
        * '*g_n*' to specify all tuning_names which contain 'g_n'
        * '*' to get all tuning_names for the specified instance_manager.
        :return: A dict with the tuning_id and the tuning_name. If wildcards have been used many tuning_ids and tuning_names may be returned.
        """
        t = time.time()
        O19TuningHelper.manager = manager
        log.debug(f"manager: {type(manager)} = {manager}")
        if manager is not None:
            rt_manager = manager.upper()
            instance_manager = services.get_instance_manager(sims4.resources.Types[rt_manager])
            tuning_dict = O19TuningHelper._get_tuning_dict(instance_manager, manager, tuning_names)
        else:
            tuning_dict: dict = {}
            managers = get_managers()
            for manager in managers:
                if manager == 'objects':
                    continue
                instance_manager = managers.get(manager, None)
                tuning_dict = {**tuning_dict, **O19TuningHelper._get_tuning_dict(instance_manager, manager, tuning_names)}
        dt = time.time() - t
        O19TuningHelper.dt_sum += dt
        log.debug(f"Duration: {dt:.3f}s (sum: {O19TuningHelper.dt_sum:.3f}s")
        return tuning_dict


    @staticmethod
    def _get_tuning_dict(instance_manager, manager, tuning_names: list) -> Dict[int, tuple]:
        """
        :param instance_manager: An instance_manager.
        :param manager: see @get_tuning_dict
        :param tuning_names: see @get_tuning_dict
        :return: see @get_tuning_dict
        """
        tuning_dict = dict()
        for tuning_name in tuning_names:
            if tuning_name.isdecimal():
                try:
                    _tuning_id = int(tuning_name)
                    key = get_resource_key(tuning_name, instance_manager.TYPE)
                    tuning_dict.update(O19TuningHelper._dict(instance_manager, manager, key, tuning_name))
                except:
                    log.error(f"Could not convert 'int({tuning_name})'", throw=True)
                continue

            if tuning_name.startswith('0x'):
                try:
                    _tuning_id = int(tuning_name, 16)
                    key = get_resource_key(tuning_name, instance_manager.TYPE)
                    tuning_dict.update(O19TuningHelper._dict(instance_manager, manager, key, tuning_name))
                except:
                    log.error(f"Could not convert 'int({tuning_name}, 16)'", throw=False)
                continue

            tuning_name = tuning_name.lower().strip()
            if tuning_name == '*':
                for (key, tuning_file) in instance_manager.types.items():
                    tuning_dict.update(O19TuningHelper._dict(instance_manager, manager, key, tuning_name))
            elif tuning_name.startswith('*'):
                if tuning_name.endswith('*'):
                    tuning_name = tuning_name[1:-1]
                    for (key, tuning_file) in instance_manager.types.items():
                        if f"{tuning_file.__name__.lower()}" in tuning_name:
                            tuning_dict.update(O19TuningHelper._dict(instance_manager, manager, key, tuning_name))
                else:
                    tuning_name = tuning_name[1:]
                    for (key, tuning_file) in instance_manager.types.items():
                        if f"{tuning_file.__name__.lower()}".endswith(tuning_name):
                            tuning_dict.update(O19TuningHelper._dict(instance_manager, manager, key, tuning_name))
            elif tuning_name.endswith('*'):
                tuning_name = tuning_name[:-1]
                for (key, tuning_file) in instance_manager.types.items():
                    if f"{tuning_file.__name__.lower()}".startswith(tuning_name):
                        tuning_dict.update(O19TuningHelper._dict(instance_manager, manager, key, tuning_name))
            else:
                for (key, tuning_file) in instance_manager.types.items():
                    if f"{tuning_file.__name__.lower()}" == tuning_name:
                        d = O19TuningHelper._dict(instance_manager, manager, key, tuning_name)
                        if d:
                            tuning_dict.update(d)
        if O19TuningHelper.manager or tuning_dict:
            log.debug(f"Tunings: '{tuning_dict}' for '{tuning_names}'")
        return tuning_dict

    @staticmethod
    def _dict(instance_manager, manager, key, tuning_name):
        try:
            tuning = instance_manager.get(key)

            # if O19TuningHelper.manager is not None and tuning is None:
            if tuning is None:
                if O19TuningHelper.manager:
                    log.debug(f"Skipping: {key.instance}: ({tuning}, {manager}, {tuning_name}")
                return {}
            return {key.instance: (tuning, f"{instance_manager.TYPE.name}", f"{tuning.__name__}")}
        except:
            log.error(f"Error: '_dict({instance_manager}, {manager}, {key}, {tuning_name})", throw=True)
            return {}