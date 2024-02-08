#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#


from sims4communitylib.mod_support.common_mod_info import CommonModInfo


class ModInfo(CommonModInfo):
    """ Mod info for the S4.CL Sample Mod. """
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
        return '1.0.6'


"""
v1.0.6
    Updated README for new TS4 version.
v1.0.5
    Updated README and compile.sh
v1.0.4
    Update README and compile.sh
v1.0.3
    Update README and compile.sh
v1.0.2
    Update README and compile.sh
v1.0.1
    Use TS4F to locate mod_data
v1.0.0
    This has been 0.9 for long enough.
    Removed the 'Tuning Inspector'
    Move some code to TS4Lib
0.9.8.3
    Fixed bogus dependency to GT Club Limits
0.9.8.2
    Fixed 'frozenset/set/tuple/list:' not being properly parsed
0.9.8.1
    Added 'del:' to remove elements from lists / dicts
0.9.8 Polished the code a little bit
    Tested implementation of https://modthesims.info/d/602945/set-filters-on-paintings-by-reference-v4.html
    Tested implementation of 'Neglect Toddlers and Children (No Whisk Away)'  
0.9.7.2 Added 'addut:' and 'addul:' to create tuples with unique values. 
0.9.7.1 Improved **var** support
        Added support for objects ('manager_imp': 'OBJECT', 'tunings_imp': ["object_...", ],)
        Fixed tunings_imp_ids and tunings_imp_tunings handling
0.9.7 Added init.py to utils :/
0.9.6 Fixing Typo and weak PEP warnings
0.9.5 Typo in README.md: 'tunings_imp_tunings' vs. 'tunings_imp_ids'
0.9.4 Config will only be read one time after startup, not on every zone load.
0.9.3 Added 'ifis: var1*, var2*', 'ifnotis: ..', 'ifin: ..' and 'ifnotin: ..' commands
0.9.2 Added manager_imp and tunings_imp to allow referencing buff/trait tunings 
0.9.1 Fixed a bug introduced last minute preventing do_command from working. :(
0.9.0 Code cleanup for 'do_command'
0.8.9 Removed old Tuning Helper
0.8.8 Added Tuning Helper and Basic Extras Utilities.
0.8.7 Support for reading do_command config
0.8.6 Support for empty frozneset() with 'frozenset: empty_frozenset = '
        Added 'print: *var' - if things don't work as expected this may help. Not meant for final scripts.
        Added 'printmembers: *var' - if things don't work as expected this may help. Not meant for final scripts.
        Improved the inspector to drill down into nested tuple and/or list elements. 
0.8.4 New 'isinstancetypestr:' command to check for 'value: type' as 'value' is not always enough.
0.8.3 Catch a fatal 'None' exception caused by errors in .dict files.
0.8.2 Identify the first line of the script properly
0.8.1 if attributes in `'items': [..., ],` are not in the tuning they will be set to None instead of skipping the tuning.
0.8.0 Hopefully all 0.7.x issues have been fixed

0.7.0 Adding 'inspect' to drill down into tunings
        New commands like 'if', 'ifnot' and 'isinstancestr' for classes which can not be zone_loaded
        Mathematical functions 'add', 'sub', 'mul' and 'div'
        tuple: Defines a tuple()
        **var** allows to access *var for frozenset, set and tuple.

0.6.0 Branding as 'Live XML (Tuning Editor)', not compatible with 0.5.2

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
