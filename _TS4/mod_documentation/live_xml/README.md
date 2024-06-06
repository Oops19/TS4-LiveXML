# Live XML

### Tuning Editor
This mod is for everyone who wants to modify tuning values without editing XML files. It is the superior alternative to overrides.

We often see xml tuning override mods which are 3 months old and when compared to the current XML it becomes obvious that EA added many new things to the XML files (fixes, buffs, traits, commodities, ...) which are missing in the mod.
They often break when EA releases a new TS4 version.

As a normal user you want to install this mod if another mod requires it.
The mod itself does not modify the game play at all.
Of course, you can install it and benefit (or suffer) from the game changes caused by the included sample configuration files if you fail to remove them.

This mod requires S4CL which can be downloaded from https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest

A command to help creating config files is now included.

## Real world example
How would we implement the simple requirement to disable autonomy for one interaction?

### Copy XML Tuning
**Don't do this!** There are many mods which have been created like this, unfortunately.

The simple way is to copy the tuning (eg 'stereo_Dance_LocalCultureSkill') and add a line `<T n="allow_autonomous">False</T>` to it.
Then add the XML to a new .package and it's done.
To do this for 10 similar tunings we copy all 10 files, edit them and add them to the .package.
And then we pray to EA that they never ever modify these tunings, even though we know that we did it wrong.

If you created your tunings mods like this you may consider to use this mod.
In the image we see only three missing lines, totally 200 lines are missing in the modded tuning.


### 'Live edit' the XML
We need to gather the tunings, for this mod we need the name.
Wildcards are supported, so it is easy to match similar tunings (eg 'stereo_Dance_*').
To set the 'allow_autonomous' to 'False' technically the property of the loaded tuning has to be modified.
With this mod we define a variable as 'False' and change the tuning.
It looks a little bit like a basic language which it actually is:
```text
assign: value = False
setattr: tuning, allow_autonomous, value
```
This code is executed as soon as a lot has been loaded and will then modify the loaded tunings on the fly.


## Other real world examples
There may be a long list with copied XML files which are now missing a lot of values.

There are tests which you just want to disable and make them fail each time.
For example to disable broadcasters setting 'allow_sims' to 'False' in the tuning often helps:
```text
assign: value = False
setattr: tuning, allow_sims, value
```
			
There are 'max_value_tuning', 'max_duration', ... parameters with a high value to avoid a fast repeated execution of an interaction.
Or they may have a low value to avoid that an effect lasts as long as it should, or vice versa.
It's quite easy to fix it:
```text
assign: value = 3660
cwo: var = _temporary_commodity_info, max_duration, value  # optionally if we need to modify a frozenset
setattr: tuning, max_value_tuning, value
```

These were all simple examples and the mod may not yet support all the options to edit a tuning. Especially more complex tests may be hard to implement with this mod.

So far location tests, radius size changes, creating sets and frozensets are supported. Also simple checks and loops are possible.
Code may look like this:
```text
frozenset: foo = 1, 2, 3
foreach: tuple, bar	
    foreach: elem, tuple
        setattr: elem, property, foo
```


## Security
This mod reads and parses configuration files with `literal_eval()`  into  Python dict() elements.
The elements are hopefully processed properly as variables and should never be executed.
Please let me know if you can identify security issues, no one wants to run a mod with code injection or shell vulnerabilities.
For now I recommend that you review the files before you save them to `mod_data/live_xml/`.

I consider this mod to be safe, otherwise I would not publish it.


## Mild Warning - Game mechanics changed
The `mod_data/*.dict` files modify tunings. They change the game mechanics and checks in various ways (like a .package with an XML does).
* Please review the files in `mod_data` and remove files which you do not want to use.
* Filtering of broadcasts affects multiple sims.
* Modified age/race/gender checks may allow sims to execute tasks which were never planned to be available for them.
* Modified range checks may lower or increase the privacy need of sims. 

The included files should not affect the game-play too much but it's hard to test everything.


## Cheat commands
To create a new config file it makes sense to clean up the 'mod_data/live_xml' directory to work only with the new file.

To reload the file `o19.live_xml.reload` can be used, it will log everything to `mod_logs/LiveXML_Messages.log`.
Logging is verbose, so you may see more messages than expected.

## Mod collision
This mod uses the cheat command 'inspect' and collides with similar mods like 'inspector.py' by scumbumbo.

## Merging
Most people do not merge script mods. This mod may be merged with a ZIP program with other mods. The file name may be renamed, it is not used to reference anything.


## Future
It is possible to exploit the `Snippet Tuning` XML format to add there JSON data (or within XML tags) so a mod creator can still deliver a .package file instead of a file to be stored in `mod_data`.

For simple and common properties a pie menu interaction may be added to all objects. It would be easy to implement but I'm not sure whether we really need this.


## Creating custom settings
Please use the 'Tuning Inspector' which is now a standalone mod. Both 'Live XML' and 'Patch XML' may need the inspector so it makes sense to have it as a unique mod.



### Configuration file structure
Everything which must be replaced has been put into round brackets `(...)`. The brackets and everything in between must be replaced.

##### Structure:
```python
{
	'(custom unique name)': {
		'manager_imp': '(ususally in upper case)',  # optional parameter
		'tunings_imp': ['(a tuning name, leading and ending wildcards * are supported)', '(another tuning name)'],  # optional parameter        
		'manager': '(needed manager, ususally in upper case)',  # core/sims4/resources.py or in tuning i="..."
		'tunings': ['(a tuning name, leading and ending wildcards * are supported)', '(another tuning name)'],  # you may add the tuning IDs as comment here
		'items': ['(to fetch a few properties of the tuning define them here)'],
		'process': [
		    '(first command)',
		    '(second command)',  # and so on.
		    '(loop OR if command)',
		    '    (inner loop command OR process if==True)', # use 4 spaces or TAB for the commands within the loop.
		],
        'command': '(debug command)',  # To run a command
        'command_parameters': '(debug command argument)',  # To run a command
	}
}
```

### Referencing Tunings
To access the IDs or tunings of buffs or traits to add them to a block or allow list one may start the configuration with:
* `'manager_imp': '...',` and
* `'tunings_imp': ['...', '...', ]` - This will add to variables:
* `*tunings_imp_tunings = tuple(<class ...>, )`
* `*tunings_imp_ids = tuple(123, )`

They can later be accessed as a normal variable and add a class list of tunings to an EA allow list:
* `add: new_whitelist_traits = whitelist_traits, tunings_imp_tunings',`

### Commands
All strings which end with `*` are added to/read from a local data store. So `var*` is not the same as `var`. Don't get confused.

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
* `classstr: var* = string` - Assign the 'string' to 'var*'. This is a string assignment and should only be used if the class can't be loaded (eg for Wrapper classes).
* `frozenset: var* = ` - Create an empty frozenset.
* `frozenset: var* = value, value2, ...` - Create a frozenset() with 1-n elements. See 'assign:' for possible values.
* `set: var* = value, value2, ...` - Create a set() with 1-n elements. See 'assign:' for possible values.
* `tuple: var* = value, value2, ...` - Create a tuple() with 1-n elements. See 'assign:' for possible values.
* `list: var* = value, value2, ...` - Create a list() with 1-n elements. See 'assign:' for possible values.
* For `frozenset, set, tuple, list` `'**var**'` may be specified instead of `value, value2, ...`. In this case the value of 'var*' will be assigned. Very useful to assign a class/tuning to a tuple.
* `cwo: var* = obj*, key, value*` - Clone object 'obj*' with 'ImmutableSlots' 'key' to new 'value*' and store it in 'var*'
* `print: var*` - Print the value of a variable for debug purposes.
* `printmembers: var*` - Print the value of a variable and all its members for debug purposes.

Simple mathematical functions. Hopefully `sin/cos/tan/sqrt/pow()` are not needed.
* `mul: var* = var1*, var2*` - Assign 'var1*' * 'var2*' to 'var*'.
* `div: var* = var1*, var2*` - Assign 'var1*' / 'var2*' to 'var*'.
* `add: var* = var1*, var2*` - Assign 'var1*' + 'var2*' to 'var*'.
* `sub: var* = var1*, var2*` - Assign 'var1*' - 'var2*' to 'var*'.
* `addut: var* = var1*, var2*` - Assign 'var1*' + 'var2*' to 'var*'. Convert var* to a Tuple with Unique values. - `tuple(set(var*))`
* `addul: var* = var1*, var2*` - Assign 'var1*' + 'var2*' to 'var*'. Convert var* to a List with Unique values. - `list(set(var*))`
Both `addu?:` commands shuffle the order of the elements. This should be no issue.

TODO
Replacement functions
* `--add: var*, value, value2, ...` - Append 'value', 'value2', ... to '*var'. 
* `--del: var*, value, value2, ...` - Remove 'value', 'value2', ... from '*var'.
* `--sub: var*, value1, value2` - Substitute 'value1' with 'value2' in '*var'.
For all three commands `'**var**'` may be specified. In this case the value of 'var*' will be used.

Loops, Ifs, etc. allow creating more complex configurations. 
* `if: var*` - Checks whether 'var*' is set.
* `ifnot: var*` - Checks whether 'var*' is not set.
* `ifis: var1*, var2*` - Checks whether 'var1*' == 'var2*'.
* `ifnotis: var1*, var2*` - Checks whether 'var1*' != 'var2*'.
* `ifin: var1*, var2*` - Checks whether 'var1*' in 'var2*'. 'var2*' should be a set/list/tuple
* `ifnotin: var1*, var2*` - Checks whether ''var1*' not in 'var2*'.
* `isinstance: var*, class*` - Checks whether 'var*' is an instance of 'class*'.
* `isinstancestr: var*, classstr*` - Checks whether 'type(var*)' is the same as 'classstr*'.
* `isinstancetypestr: var*, class*` - Checks whether 'var*: type(var*)' is the same as 'classstr*'.
* `foreach: var*, vars*` - Loop over all elements in 'vars*' and assign them to 'var*'

All following command have to be intended with 1 TAB or 4 SPACE characters.
Checks and loops can be nested, the next level has to be intended with another TAB or 4 SPACE characters.
There is no else available, as soon as the intent is removed the 'if' part ends.

### 'Do Command'
Interactions allow specifying `<L n="basic_extras"><V t="do_command">` to call a Python command when an interaction is executed.
As with the process commands a manager is needed (INTERACTION highly suggested, the default) and tunings are needed to be modified.
Instead of `process` the following parameters are used:
* `'manager': INTERACTION,` - Defaults to `INTERACTION` if not specified.
* `'tunings': ['...', '...', ]` - Required. See above
* `'command': '...'` - Required. The command to be executed. Call it from the debug console (Shift+Ctrl+C) to test it.
* `'command_parameters: '...'` - Required if you want to specify arguments. The mod will prepend the tuning name or id to the `command_parameters` with '+' as a separator. One may join multiple arguments with '+' and specify them all as one string. Like 'buff_add_123+trait_add_123'.
* `'command_timing': '...'` - Optional. May be either `at_end` (default) or `at_beginning`.
* `'command_offset_time': '...'` - Optional. `command_timing` must be `at_beginning` and the command will be called with some delay. This is not required as it requires 'a lot' CPU resources.
* `'command_xevt_id': '...'` - Optional. The `xevt_id` which has been specified in a clip head ot the animation may be specified to run the command at the proper time within the animation.

LiveXML itself does not include a command to be called.
It supports mod creators who need more complex actions to write them with Python and call them from within the interaction.

LiveXML may implement in the future:
* Add/remove buffs and traits
* Change the outfit
* Dress/undress hat, gloves, socks and shoes
* Add/remove body hair
* Age up/down sim
* Change fit/fat/body sliders

Also within `<V n="outcome" t="single"><U n="single"><U n="actions"><L n="basic_extras">` `do_command` may be added - this is not yet supported by this mod.


# Addendum

## Game compatibility
This mod has been tested with `The Sims 4` 1.107.112, S4CL 3.4, TS4Lib 0.3.20 (2024-05).
It is expected to be compatible with many upcoming releases of TS4, S4CL and TS4Lib.

## Dependencies
Download the ZIP file, not the sources.
* [This Mod](../../releases/latest)
* [TS4-Library](https://github.com/Oops19/TS4-Library/releases/latest)
* [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest)
* [The Sims 4](https://www.ea.com/games/the-sims/the-sims-4)

If not installed download and install TS4 and these mods.
All are available for free.

## Installation
* Locate the localized `The Sims 4` folder which contains the `Mods` folder.
* Extract the ZIP file into this `The Sims 4` folder.
* It will create the directories/files `Mods/_o19_/$mod_name.ts4script`, `Mods/_o19_/$mod_name.package`, `mod_data/$mod_name/*` and/or `mod_documentation/$mod_name/*`
* `mod_logs/$mod_name.txt` will be created as soon as data is logged.

### Manual Installation
If you don't want to extract the ZIP file into `The Sims 4` folder you might want to read this. 
* The files in `ZIP-File/mod_data` are usually required and should be extracted to `The Sims 4/mod_data`.
* The files in `ZIP-File/mod_documentation` are for you to read it. They are not needed to use this mod.
* The `Mods/_o19_/*.ts4script` files can be stored in a random folder within `Mods` or directly in `Mods`. I highly recommend to store it in `_o19_` so you know who created it.

## Usage Tracking / Privacy
This mod does not send any data to tracking servers. The code is open source, not obfuscated, and can be reviewed.

Some log entries in the log file ('mod_logs' folder) may contain the local username, especially if files are not found (WARN, ERROR).

## External Links
[Sources](https://github.com/Oops19/)
[Support](https://discord.gg/d8X9aQ3jbm)
[Donations](https://www.patreon.com/o19)

## Copyright and License
* © 2024 [Oops19](https://github.com/Oops19)
* License for '.package' files: [Electronic Arts TOS for UGC](https://tos.ea.com/legalapp/WEBTERMS/US/en/PC/)  
* License for other media unless specified differently: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) unless the Electronic Arts TOS for UGC overrides it.
This allows you to use this mod and re-use the code even if you don't own The Sims 4.
Have fun extending this mod and/or integrating it with your mods.

Oops19 / o19 is not endorsed by or affiliated with Electronic Arts or its licensors.
Game content and materials copyright Electronic Arts Inc. and its licensors. 
Trademarks are the property of their respective owners.

### TOS
* Please don't put it behind a paywall.
* Please don't create mods which break with every TS4 update.
* For simple tuning modifications use [Patch-XML](https://github.com/Oops19/TS4-PatchXML) 
* or [LiveXML](https://github.com/Oops19/TS4-LiveXML).
* To check the XML structure of custom tunings use [VanillaLogs](https://github.com/Oops19/TS4-VanillaLogs).
