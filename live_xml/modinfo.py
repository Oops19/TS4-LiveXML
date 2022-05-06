from sims4communitylib.mod_support.common_mod_info import CommonModInfo


class ModInfo(CommonModInfo):
    """ Mod info for the S4CL Sample Mod. """
    # To create a Mod Identity for this mod, simply do ModInfo.get_identity(). Please refrain from using the ModInfo of The Sims 4 Community Library in your own mod and instead use yours!
    _FILE_PATH: str = str(__file__)

    @property
    def _name(self) -> str:
        # This is the name that'll be used whenever a Messages.txt or Exceptions.txt file is created <_name>_Messages.txt and <_name>_Exceptions.txt.
        return 'LiveXML'

    @property
    def _author(self) -> str:
        # This is your name.
        return 'o19'

    @property
    def _base_namespace(self) -> str:
        # This is the name of the root package
        return 'live_xml'

    @property
    def _file_path(self) -> str:
        # This is simply a file path that you do not need to change.
        return ModInfo._FILE_PATH

    @property
    def _version(self) -> str:
        return '0.8.2'

"""
0.8.2 Identify the first line of the script properly
0.8.1 if attributes in `'items': [..., ],` are not in the tuning they will be set to None instead of skipping the tuning.
0.8.0 Hopefully all 0.7.x issues have been fixed

0.7.0 Adding 'inspect' to drill down into tunings
        New commands like 'if', 'ifnot' and 'isinstancestr' for classes which can not be loaded
        Mathematical functions 'add', 'sub', 'mul' and 'div'
        tuple: Defines a tuple()
        **var** allows to access *var for frozenset, set and tuple.

0.6.0 Rebranding as 'Live XML (Tuning Editor)', not compatible with 0.5.2

0.5.2 A few changes and new commands, not compatible with 0.5.1
        set: Defines a set()
        frozenset: Defines a frozenset()
        assign: Assigns a value to a variable
        
0.5.1 A few changes and new commands, not compatible with 0.5.0
        getattr: var = obj, key
        cwo: var = obj, key, new-value
        isinstance: obj, class
        foreach: var, list

0.5.0 Many changes to support more tunings
        In *.dict: 'tuning': 'foo' ==> 'tuning_names': ['foo', 'bar']
        Deprecated 'var = value', only 'var = cwo: value, value, value' should be used. Use 'set:' instead.
        New: 'set: var_name = value
        New: 'getattr: a, b, c' which is executed as 'c = getattr(a, b) as'
"""
