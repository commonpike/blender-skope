# Blender - Skope

dont open the .blend file.
instead, run `skope.sh [command]`. This starts
`src/skope.blend` with `src/skope-init.py`,
sometimes just in the background to generate
stills or clips.

There are several `command`s available:
 - 'edit' (edit the blend file)
 - 'test' (edit the blend file with frame change handlers enabled)
 - 'render' (generate images or clips from scratch) 
 - 'regenerate' (regenerate images or clips from saved state files) 

There are also some command line options:

```
--type (stills|clip)
--amount (number of stills)
--length (number of frames in clip)
--scale (percentage)
--format (JPG|PNG - stills only)
--input-dir (path to source images)
--output-dir (path to output dir)
--import-dir (path to dir with prerendered state files - regenerate only)
```