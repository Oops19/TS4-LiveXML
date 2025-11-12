# 🧬 Live XML

## 🛠️ Tuning Editor

This mod is for anyone who wants to modify tuning values **without editing XML files directly**.  
It’s a superior alternative to traditional XML overrides.

Many override mods are outdated — often 3+ months old — and miss new additions EA makes to tuning files (e.g., fixes, buffs, traits, commodities).  
These mods frequently break when EA releases a new TS4 version.

As a regular user, install this mod only if another mod requires it.  
The mod itself does **not** change gameplay.  
However, if you leave the included sample configuration files untouched, you may experience gameplay changes — for better or worse.

A command-line tool to help create config files is now included.

## 🧪 Real-World Example
**Goal:** Disable autonomy for a specific interaction.

### ❌ Copy XML Tuning (Not Recommended)
Many mods do this — but it’s fragile and error-prone.

Example:  
You copy `stereo_Dance_LocalCultureSkill` and add:

```xml
<T n="allow_autonomous">False</T>
```
Then you package it.
To do this for 10 similar tunings, you copy and edit all 10 files.
And then you hope EA never updates them — even though you know this approach is flawed.

If you’ve created mods this way, consider switching to Live XML.
In the image we see only three missing lines, totally 200 lines are missing in the modded tuning.

### ✅ Live Edit the XML
Instead of copying files, you gather the tuning names.
Wildcards are supported — e.g., stereo_Dance_* to match similar tunings.

To disable autonomy, you modify the property directly.
Define a variable and apply it like this:
```text
assign: value = False
setattr: tuning, allow_autonomous, value
```
This code runs when a lot is loaded and modifies the tuning on the fly.

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

---

# 📝 Addendum

## 🔄 Game compatibility
This mod has been tested with `The Sims 4` 1.119.109, S4CL 3.17, TS4Lib 0.3.42.
It is expected to remain compatible with future releases of TS4, S4CL, and TS4Lib.

## 📦 Dependencies
Download the ZIP file - not the source code.
Required components:
* [This Mod](../../releases/latest)
* [TS4-Library](https://github.com/Oops19/TS4-Library/releases/latest)
* [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest)
* [The Sims 4](https://www.ea.com/games/the-sims/the-sims-4)

If not already installed, download and install TS4 and the listed mods. All are available for free.

## 📥 Installation
* Locate the localized `The Sims 4` folder (it contains the `Mods` folder).
* Extract the ZIP file directly into this folder.

This will create:
* `Mods/_o19_/$mod_name.ts4script`
* `Mods/_o19_/$mod_name.package`
* `mod_data/$mod_name/*`
* `mod_documentation/$mod_name/*` (optional)
* `mod_sources/$mod_name/*` (optional)

Additional notes:
* CAS and Build/Buy UGC without scripts will create `Mods/o19/$mod_name.package`.
* A log file `mod_logs/$mod_name.txt` will be created once data is logged.
* You may safely delete `mod_documentation/` and `mod_sources/` folders if not needed.

### 📂 Manual Installation
If you prefer not to extract directly into `The Sims 4`, you can extract to a temporary location and copy files manually:
* Copy `mod_data/` contents to `The Sims 4/mod_data/` (usually required).
* `mod_documentation/` is for reference only — not required.
* `mod_sources/` is not needed to run the mod.
* `.ts4script` files can be placed in a folder inside `Mods/`, but storing them in `_o19_` is recommended for clarity.
* `.package` files can be placed in a anywhere inside `Mods/`.

## 🛠️ Troubleshooting
If installed correctly, no troubleshooting should be necessary.
For manual installs, verify the following:
* Does your localized `The Sims 4` folder exist? (e.g. localized to Die Sims 4, Les Sims 4, Los Sims 4, The Sims 4, ...)
  * Does it contain a `Mods/` folder?
    * Does Mods/_o19_/ contain:
      * `ts4lib.ts4script` and `ts4lib.package`?
      * `{mod_name}.ts4script` and/or `{mod_name}.package`
* Does `mod_data/` contain `{mod_name}/` with files?
* Does `mod_logs/` contain:
  * `Sims4CommunityLib_*_Messages.txt`?
  * `TS4-Library_*_Messages.txt`?
  * `{mod_name}_*_Messages.txt`?
* Are there any `last_exception.txt` or `last_exception*.txt` files in `The Sims 4`?


* When installed properly this is not necessary at all.
For manual installations check these things and make sure each question can be answered with 'yes'.
* Does 'The Sims 4' (localized to Die Sims 4, Les Sims 4, Los Sims 4, The Sims 4, ...) exist?
  * Does `The Sims 4` contain the folder `Mods`?
    * Does `Mods` contain the folder `_o19_`? 
      * Does `_19_` contain `ts4lib.ts4script` and `ts4lib.package` files?
      * Does `_19_` contain `{mod_name}.ts4script` and/or `{mod_name}.package` files?
  * Does `The Sims 4` contain the folder `mod_data`?
    * Does `mod_data` contain the folder `{mod_name}`?
      * Does `{mod_name}` contain files or folders?
  * Does `The Sims 4` contain the `mod_logs` ?
    * Does `mod_logs` contain the file `Sims4CommunityLib_*_Messages.txt`?
    * Does `mod_logs` contain the file `TS4-Library_*_Messages.txt`?
      * Is this the most recent version or can it be updated?
    * Does `mod_logs` contain the file `{mod_name}_*_Messages.txt`?
      * Is this the most recent version or can it be updated?
  * Doesn't `The Sims 4` contain the file(s) `last_exception.txt`  and/or `last_exception*.txt` ?
* Share the `The Sims 4/mod_logs/Sims4CommunityLib_*_Messages.txt` and `The Sims 4/mod_logs/{mod_name}_*_Messages.txt`  file.

If issues persist, share:
`mod_logs/Sims4CommunityLib_*_Messages.txt`
`mod_logs/{mod_name}_*_Messages.txt`

## 🕵️ Usage Tracking / Privacy
This mod does not send any data to external servers.
The code is open source, unobfuscated, and fully reviewable.

Note: Some log entries (especially warnings or errors) may include your local username if file paths are involved.
Share such logs with care.

## 🔗 External Links
[Sources](https://github.com/Oops19/)
[Support](https://discord.gg/d8X9aQ3jbm)
[Donations](https://www.patreon.com/o19)

## ⚖️ Copyright and License
* © 2020-2025 [Oops19](https://github.com/Oops19)
* `.package` files: [Electronic Arts TOS for UGC](https://tos.ea.com/legalapp/WEBTERMS/US/en/PC/)  
* All other content (unless otherwise noted): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 

You may use and adapt this mod and its code — even without owning The Sims 4.
Have fun extending or integrating it into your own mods!

Oops19 / o19 is not affiliated with or endorsed by Electronic Arts or its licensors.
Game content and materials © Electronic Arts Inc. and its licensors.
All trademarks are the property of their respective owners.

## 🧾 Terms of Service
* Do not place this mod behind a paywall.
* Avoid creating mods that break with every TS4 update.
* For simple tuning mods, consider using:
  * [Patch-XML](https://github.com/Oops19/TS4-PatchXML) 
  * [LiveXML](https://github.com/Oops19/TS4-LiveXML).
* To verify custom tuning structures, use:
  * [VanillaLogs](https://github.com/Oops19/TS4-VanillaLogs).

## 🗑️ Removing the Mod
Installing this mod creates files in several directories. To fully remove it, delete:
* `The Sims 4/Mods/_o19_/$mod_name.*`
* `The Sims 4/mod_data/_o19_/$mod_name/`
* `The Sims 4/mod_documentation/_o19_/$mod_name/`
* `The Sims 4/mod_sources/_o19_/$mod_name/`

To remove all of my mods, delete the following folders:
* `The Sims 4/Mods/_o19_/`
* `The Sims 4/mod_data/_o19_/`
* `The Sims 4/mod_documentation/_o19_/`
* `The Sims 4/mod_sources/_o19_/`
