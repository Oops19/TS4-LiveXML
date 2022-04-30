#  Live XML
### Tuning Editor
This mod is for everyone who wants to modify tuning values without editing XML files. It is the superior alternative to overrides.

We often see xml tuning override mods which are 3 months old and when compared to the current XML it becomes obvious that EA added many new things to the XML files (fixes, buffs, traits, commodities, ...) which are missing in the mod.
They often break when EA releases a new TS4 version.

As a normal user you want to install this mod if another mod requires it.
The mod itself does not modify the game play at all.
Of course, you can install it and benefit (or suffer) from the game changes caused by the included sample configuration files if you fail to remove them.

This mod requires S4CL which can be downloaded from https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest

A command to help creating config files is now included.
~~The mod for modders to create config files for this mod can be found below in `Creating custom settings`.~~

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
```
assign: value = False
setattr: tuning, allow_autonomous, value
```
This code is executed as soon as a lot has been loaded and will then modify the loaded tunings on the fly.


## Other real world examples
There may be a long list with copied XML files which are now missing a lot of values.

There are tests which you just want to disable and make them fail each time.
For example to disable broadcasters setting 'allow_sims' to 'False' in the tuning often helps:
```
assign: value = False
setattr: tuning, allow_sims, value
```
			
There are 'max_value_tuning', 'max_duration', ... parameters with a high value to avoid a fast repeated execution of an interaction.
Or they may have a low value to avoid that an effect lasts as long as it should, or vice versa.
It's quite easy to fix it:
```
assign: value = 3660
cwo: var = _temporary_commodity_info, max_duration, value  # optionally if we need to modify a frozenset
setattr: tuning, max_value_tuning, value
```

These were all simple examples and the mod may not yet support all the options to edit a tuning. Especially more complex tests may be hard to implement with this mod.

So far location tests, radius size changes, creating sets and frozensets are supported. Also simple checks and loops are possible.
Code may look like this:
```
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


## Installation
The ZIP file should be extracted into the `The Sims 4` folder to make sure that the folder structure is set up correctly.
* All settings are read from `The Sims 4/mod_data/set_tuning_values/`.
* The mod documentation (everything in `mod_documentation`) should also not be stores in `Mods`.
* The mod `set_tuning_values.ts4cript` itself should be stored in `Mods` or in a sub folder. I highly recommend to store it in `_o19_` so you know who created it.

Unless not yet installed: Install [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest) as this mod is required.
* I highly recommend to install the S4CL files into `_cn_` so you know who contributed this mod.

This mod has been tested with  1.86.157 (2022-03-31) and S4CL v1.76 (2022-02-14).
It is expected to work with many older and upcoming releases of TS4 and S4CL.

## Mod collision
This mod uses the cheat command 'inspect' and collides with similar mods like 'inspector.py' by scumbumbo.

## Merging
Most people do not merge script mods. This mod may be merged with a ZIP program with other mods. The file name may be renamed, it is not used to reference anything.


## Future
It is possible to exploit the `Snippet Tuning` XML format to add there JSON data (or within XML tags) so a mod creator can still deliver a .package file instead of a file to be stored in `mod_data`.

For simple and common properties a pie menu interaction may be added to all objects. It would be easy to implement but I'm not sure whether we really need this.


## Creating custom settings
The  [inspector](https://modthesims.info/showthread.php?t=575118) by [scumbumbo](https://modthesims.info/m/7401825) is probably the 2nd best tool ever written for TS4 to avoid that mods break with every update.
Many mod creators know about it but only a few use it. They create bogus mods on purpose which break with every update even though they could avoid it.

The best tool is very likely the embeeded inspector which will also be called with 'inspect'. If you have scumbumbo's inspector installed remove it.

To modify a tuning it may be best to inspect it with the inspector and to take note about the needed parameter names and values.
Locating them may require some work and one will get used to it. One may also need to modify the inspector.py file to dig deeper into the structures.

Some documented examples can be found in 'mod_data'.

### Configuration file structure
Everything which must be replaced has been put into round brackets `(...)`. The brackets and everything in between must be replaced.

##### Structure:
`{
	'(custom unique name)': {
		'manager': '(needed manager, ususally in upper case)',  # core/sims4/resources.py or in tuning i="..."
		'tunings': ['(a tuning name, leading and ending wildcards * are supported)', '(another tuning name)'],  # you may add the tuning IDs as comment here
		'items': ['(to fetch a few properties of the tuning define them here)'],
		'process': [
		    '(first command)',
		    '(second command)',  # and so on.
		    '(loop OR if command)',
		    '    (inner loop command OR process if==True)', # use 4 spaces or TAB for the commands within the loop.
		]
	}
}`


### Commands
All strings which end with `*` are added to a local data store. So `var*` is not the same as `var`. Don't get confused.

* `'manager': '...',` and
* `'tunings': ['...', '...', ]` - 'tuning*' = get_tuning(tuning-names, manager-name)
If tunings match more than one tuning then all tunings will be processed one after the other in a loop.

Within `process` the business logic is added.
* `'items': ['...', '...', ]` - All these items will be added to global variables.
* The item 'foo' will be added to the global variable 'foo*' with the value of 'tuning.foo'.
* The item 'foo.bar' wil add 'foo*' as above and 'bar*' with the value of 'tuning.foo.bar'.
* The `getattr:` command could also be used.

* `assign: var* = value` - Value 'value' may be 'None', 'True', 'False', an integer or a float number or a string. It will be assigned to 'var*'. 'value' is a string and does not reference to a variable.
* For `frozenset, set, tuple` `'**var**'` may be specified. In this case the value of 'var*' will be assigned. Very useful to assign a class/tuning to a tuple.
* `getattr: var* = obj*, prop` - The 'prop' property of 'obj*' will be assigned to 'var*'. 'prop' is a string and does not reference to a variable.
* `setattr: obj*, prop, value*` - Sets the property 'prop' of the 'obj*' to 'value*'. 'prop' is a string while 'value*' references a variable which has been assigned before.
* `class: var* = string` - Assign the class 'string' to 'var*'. This is not a string assignment, the class must exist.
* `classstr: var* = string` - Assign the 'string' to 'var*'. This is a string assignment and should only be used if the class can't be loaded (eg for Wrapper classes).
* `frozenset: var* = value, value2, ...` - Create a frozenset() with 1-n elements. See 'assign:' for possible values.
* `set: var* = value, value2, ...` - Create a set() with 1-n elements. See 'assign:' for possible values.
* `tuple: var* = value, value2, ...` - Create a tuple() with 1-n elements. See 'assign:' for possible values.
* `cwo: var* = obj*, key, value*` - Clone object 'obj*' with 'ImmutableSlots' 'key' to new 'value*' and store it in 'var*'

Simple mathematical functions. Hopefully `sin/cos/tan/sqrt/pow()` are not needed.
* `mul: var* = var1*, var2*` - Assign 'var1*' * 'var2*' to 'var*'. 
* `div: var* = var1*, var2*` - Assign 'var1*' / 'var2*' to 'var*'.
* `add: var* = var1*, var2*` - Assign 'var1*' + 'var2*' to 'var*'.
* `sub: var* = var1*, var2*` - Assign 'var1*' - 'var2*' to 'var*'.

Loops, Ifs, etc. allow creating more complex configurations. 
* `if: var*` - Checks whether 'var*' is set.
* `ifnot: var*` - Checks whether 'var*' is not set.
* `isinstance: var*, class*` - Checks whether 'var*' is an instance of 'class*'.
* `isinstancestr: var*, class*` - Checks whether 'type(var*)' is an instance of 'class*'.
* `foreach: var*, vars*` - Loop over all elements in 'vars*' and assign them to 'var*'

All following command have to be intended with 1 TAB or 4 SPACE characters.
Checks and loops can be nested, the next level has to be intended with another TAB or 4 SPACE characters.
There is no else available, as soon as the intent is removed the 'if' part ends.