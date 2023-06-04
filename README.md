# Kaleidogen

dont open the .blend file.
instead, run `runner.sh`

there are several modes of running the project:
 - 'edit' (edit the blend file)
 - 'edit-stills' (edit the blend file, but each frame is a random state)
 - 'generate-thumbs' (generate random thumbs) 
 - 'render-stills' (render selected jsons)

## generate-thumbs
when 'generating', while exporting thumbs from
the blend file to the 'thumbs' dir', json files are
written next to the thumbs describing each
thumb

## select
after 'generating', manually select the best ones 
and copy the json files into the 'selected' dir

## render-stills
when 'rendering', for each json file in the 
selecteddir, a larger version is rendered in the 'lrage' dir', 
and json files are written next to each file
    
this way you can generate 1000s of thumbs,
select only the best ones, and render large 
versions in a second run.