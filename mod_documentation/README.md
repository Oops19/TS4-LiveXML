#  Set Tuning Values
This mod is for everyone who wants to modify tuning values without editing XML files. It is a superior alternative to overrides.

## Installation
The ZIP file should be extracted into the `The Sims 4` folder to make sure that the folder structure is set up correctly.
* All settings are read from `The Sims 4/mod_data/set_tuning_values/`.
* The mod documentation (everything in `mod_documentation`) should also not be stores in `Mods`.
* The mod `set_tuning_values.ts4cript` itself should be stored in `Mods` or in a sub folder. I highly recommend to store it in `_o19_` so you know who created it.

Unless not yet installed: Install [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest) as this mod is required.
* I highly recommend to install the S4CL files into `_cn_` so you know who created it.

This mod has been tested with 1.84.171 (2022-02-15) and S4CL v1.75 (2021-09-28).
It is expected to work with many older and upcoming releases of TS4 and S4CL.

## Merging
Most people do not merge script mods. This mod may be merged with a ZIP program with other mods. The file name may be renamed, it is not used to reference anything.

## Creating custom settings
The   [inspector](https://modthesims.info/showthread.php?t=575118) by [scumbumbo](https://modthesims.info/m/7401825) is probably the best tool ever written for TS4 to avoid that mods break with every update.
Many mod creators know about it but only a few use it. So they create bogus mods on purpose which break with every update even though they could avoid it.
 
To modify a tuning it may be best to inspect it with the inspector and to take note about the needed parameter names and values.
Locating them may require some work and one will get used to it.
 
This mod allows to replace values with `setattr()` to assing values and `clone_with_overrides()` to modify a `frozenset()`. This is likely not sufficient for all desired replacements but a good start.

Some documented examples can be found in 'mod_data'.

## Future
It is possible to exploit the `Snippet Tuning` XML format to add there JSON data (or within XML tags) so a mod creator can still deliver a .package file instead of a file to be stored in `mod_data`.

Then it would be more like the XML Injector.

