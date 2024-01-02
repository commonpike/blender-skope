# Blender - Skope

dont open the .blend file.
instead, run `skope.sh`. This starts
`src/skope.blend` with `src/skope-init.py`

there are several modes of running the project:
 - 'edit' (edit the blend file)
 - 'edit-stills' (edit the blend file, but each frame is a random state)
 - 'generate-thumbs' (generate random thumbs) 
 - 'render-stills' (render selected jsons)

## edit
simply opens the blend file

## edit-still
opens the blend file, but on every frame,
the `state` is randomized

## generate-thumbs
for all frames, where each frame is randomized,
exports small thumbs and their adjacent json 
describing the `state` of each frame, 

## select (manually)
after 'generating thumbs', you can manually select 
the best ones and copy their json files into the 
'selected' dir

## render-stills
for each json file in the selecteddir, renders a large
version in the 'stills' dir, with adjacent json files
describing the `state` of each still
