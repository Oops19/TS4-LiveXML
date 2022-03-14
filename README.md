#  Set Tuning Values
This mod is for everyone who wants to modify tuning values without editing XML files. It is a superior alternative to overrides.

## Installation
The ZIP file should be extracted into the `The Sims 4` folder to make sure that the folder structure is set up correctly.
* All settings are read from `The Sims 4/mod_data/set_tuning_values/`.
* The mod documentation (everything in `mod_documentation`) should also not be stores in `Mods`.
* The mod `set_tuning_values.ts4cript` itself should be stored in `Mods` or in a sub folder. I highly recommend to store it in `_o19_` so you know who created it.

Unless not yet installed: Install [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest) as this mod is required.
* I highly recommend to install the S4CL files into `_cn_` so you know who contributed this mod.

This mod has been tested with 1.84.171 (2022-02-15) and S4CL v1.75 (2021-09-28).
It is expected to work with many older and upcoming releases of TS4 and S4CL.

## Warning - Game mechanics changed
The `mod_data/*.dict` files modify tunings to change the game mechanics and checks in various ways.
* Please review the files in `mod_data` and remove files which you do not want to use.
* Filtering of broadcasts affects multiple sims.
* Modified age/race/gender checks may allow sims to execute tasks which were never planned to be available for them.
* Modified range checks may lower or increase the privacy need of sims. 

The included files should not affect the game-play too much but it's hard to test everything.

## Merging
Most people do not merge script mods. This mod may be merged with a ZIP program with other mods. The file name may be renamed, it is not used to reference anything.

## Future
It is possible to exploit the `Snippet Tuning` XML format to add there JSON data (or within XML tags) so a mod creator can still deliver a .package file instead of a file to be stored in `mod_data`.

Then it would be more like the XML Injector.

## Creating custom settings
The   [inspector](https://modthesims.info/showthread.php?t=575118) by [scumbumbo](https://modthesims.info/m/7401825) is probably the best tool ever written for TS4 to avoid that mods break with every update.
Many mod creators know about it but only a few use it. So they create bogus mods on purpose which break with every update even though they could avoid it.
 
To modify a tuning it may be best to inspect it with the inspector and to take note about the needed parameter names and values.
Locating them may require some work and one will get used to it.
 
This mod allows to replace values with `setattr()` to assing values and `clone_with_overrides()` to modify a `frozenset()`. This is likely not sufficient for all desired replacements but a good start.

Some documented examples can be found in 'mod_data'.

### File structure
Everything which should be replaced has been put into round brackets `(...)`. The brackets and everything in between must be replaced.

Sample configuration:
`{
	'(custom unique name)': {
		'manager': '(needed manager, ususally in upper case)',  # core/sims4/resources.py or in tuning i="..."
		'tunings': ['(a tuning name, leading and ending wildcards * are supported)', '(another tuning name)'],  # you may add the tuning IDs as comment here
		'items': ['(to fetch a few properties of the tuning define them here)'],
		'process': [
		    '(first command)',
		    '(second command)',  # and so on.
		    '(loop or if command)',
		    '    (inner loop command)', # use 4 spaces or TAB for the commands within the loop.
		]
	}
}`


### Commands
All strings which end with `*` are added to a local data store. So `var*` is not the same as `var` but it can be easily confused.

* `'manager': '...',` and
* `'tunings': ['...', '...', ]` - 'tuning*' = get_tuning(tuning-names, manager-name)
If tunings match more than one tuning then all tunings will be processed one after the other in a loop.

Within `process` the business logic is added.
* `'items': ['...', '...', ]` - All these items will be added to global variables.
* The item 'foo' will be added to the global variable 'foo*' with the value of 'tuning.foo'.
* The item 'foo.bar' wil add 'foo*' as above and 'bar*' with the value of 'tuning.foo.bar'.
* The `getattr:` command could also be used.

* `assign: var* = value` - Value 'value' may be 'None', 'True', 'False', an integer or a float number or a string. It will be assigned to 'var*'. 'value' is a string and does not reference to a variable.
* `getattr: var* = obj*, prop` - The 'prop' property of 'obj*' will be assigned to 'var*'. 'prop' is a string and does not reference to a variable.
* `setattr: obj*, prop, value*` - Sets the property 'prop' of the 'obj*' to 'value*'. 'prop' is a string while 'value*' references a variable which has been assigned before.
* `class: var* = string` - Assign the class 'string' to 'var*'. This is not a string assignment, the class must exist.
* `set: var* = value, value2, value3` - Create a set() with 1-n elements. See 'assign:' for possible values.
* `frozenset: var* = value, value2` - Create a frozenset() with 1-n elements. See 'assign:' for possible values.
* `cwo: var* = obj*, key, value*` - Clone object 'obj*' with 'ImmutableSlots' 'key' to new 'value*' and store it in 'var*'
* `foreach: var*, vars*` - Loop over all elements in 'vars*' and assign them to 'var*'
All following command have to be intended with 1 TAB or 4 SPACE characters.
Loops and checks can be nested, the next level has to be intended with another TAB or 4 SPACE characters.
There is no 'break' or 'continue' available, as soon as the intend is removed the loop ends.
* `isinstance: var*, class*` - Checks whether 'var*' is an instance of 'class*'.
All following command have to be intended with 1 TAB or 4 SPACE characters.
Checks and loops can be nested, the next level has to be intended with another TAB or 4 SPACE characters.
There is no else available, as soon as the intend is removed the 'if' ends.