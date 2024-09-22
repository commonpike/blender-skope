# Blender - Skope

## Install

Copy .env-dist to .env

If you have Blender, don't bother running install.sh;
just edit `.env` to match your Blender path. Ymmv.

Otherwise, run `install.sh` to install a version of Blender 
in the `./vendor` dir.

Run `skope.sh test`. This should open the default
project-dir. 

## Run
Dont open the .blend file. Instead, run \
`skope.sh [command] --project-dir render/foobar` 

This starts `src/skope.blend` with `src/skope-init.py`,
sometimes just in the background to generate
stills or clips.

The `--project-dir` argument expects to use the following folders:
- `[project-dir]/input` : images to use for the skope
- `[project-dir]/output` : where to write output files
- `[project-dir]/import` : where to look for json import files to regenerate

There are several `command`s available:
 - `edit` (edit the blend file)
 - `ui` (edit the blend file with frame change handlers enabled)
 - `render` (generate images or clips from scratch) 
 - `regenerate` (regenerate images or clips from saved json files) 

There are also some other command line options:

```
skope.sh [command] --project-dir render/foobar
--type (stills|clip)
--amount (number of stills)
--length (number of frames in clip)
--scale (percentage)
--format (JPG|PNG - stills only)
--input-dir (path to source images - default $projectdir/input)
--output-dir (path to output dir - default $projectdir/output)
--import-dir (path to dir with json files - default $projectdir/import)
```