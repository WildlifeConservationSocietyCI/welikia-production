# welikia-production
Repository for scripts and tools for producing final Welikia assets, datasets, and texts

## flatten_place_sdrs 
This script parses the fields of its one required input `shapefile`. For any field names that have an underscore (`_`) followed by an integer, if the `score` value for that row/field is 1, 2, or 3, a tuple is created with a unique combination of `id_placename` and `id_sdr`. The tuples and their accompanying scores are then output to csv and can optionally be used to write directly to a Welikia database.

### requirements
This script is meant to be run within a Python environment installed by esri, i.e. one that contains `arcpy`, typically installed with a path like `
C:\Python27\ArcGIS10.5\`.

Additional required libraries may be installed with `/path/to/pip install -r requirements.txt`, ensuring that the correct `pip` in the correct environment is selected.

To run database updates, an `.env` file should be created in the root of the repository, with a redacted structure like:
```
DBHOST=  
DBPORT=  
DBNAME=  
DBUSER=  
DBPASS=  
```
In addition, to reach the production Welikia database, the IP of the machine running the script must be added to the relevant AWS whitelist. 

### using the script
Call the script with the correct Python interpreter normally, passing the required shapefile as the first argument. The shapefile *must* have a `Placename` field containing the integer `id_placename` for each feature.

A csv will be output in the same location with same base name as the shapefile, unless an optional `-c --csv` path argument is supplied.

If a `-d --database` argument is supplied, the placename/sdr/score data will be written to the `placename_location` table of the database. An `UPDATE` will be used if the placename/sdr combination already exists, and the score text will be appended; if the combination does not exist, an `INSERT` (with `canonical = TRUE`) will be used.

```
usage: flatten_place_sdrs.py [-h] [-f SDRFIELD] [-d] [-c CSV] shapefile

positional arguments:
  shapefile             Path to input placename features shapefile

optional arguments:
  -h, --help            show this help message and exit
  -f SDRFIELD, --sdrfield SDRFIELD
                        Name of single field containing SDR ids, to be written
                        with DEFAULT_SCORE. If not specified, all fields
                        ending in `_x` where `x` is an SDR integer id will be
                        used, and assumed to contain scores. (default: None)
  -d, --database        Write location records to database directly, in
                        addition to outputting csv. To use this option,
                        database credentials must be specified in a config
                        file as detailed in the README. (default: False)
  -c CSV, --csv CSV     Path to output csv. If not specified, shapefile
                        basename and location will be used. (default: None)
```

### other notes
- If multiple shapefile records with the same placename/SDR combination (but potentially different scores) exist, only the first will be used.
- This script should only be used once per shapefile to update the database; additional runs will cause updates to append multiple copies of the score text.
- Database inserts set `canonical = 1`; updates do nothing with `canonical` (since there is no way to know which should be canonical).

## place_synthesis
This script outputs a markdown file that aggregates Welikia place information stored in the welikia.net database (accessed via parameters stored in `.env` over ssh), a shapefile containing plate and grid assignments, and a directory of markdown files, one per place.

### requirements
- ssh connection to welikia.net database
- `.env` file in project root (parent of `src`) containing database credentials (see `flatten_place_sdrs` requirements). In addition, to reach the production Welikia database, the IP of the machine running the script must be added to the relevant AWS whitelist.
- placenames shapefile containing plate and grid data
- directory (may contain subdirectories) of markdown files, each named with the convention `<anytext>.<place id>.VERSION.md`. `VERSION` is a constant defined at the top of the script.

### using the script
```
usage: place_synthesis.py [-h] [-o OUTPUT] shapefile markdown-dir

positional arguments:
  shapefile             Path to input placename features shapefile
  markdown-dir          Path to directory of markdown files with place id in each filename

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to output markdown. If not specified, shapefile basename and location will be used. (default: None)
```

#### example invocation
`python place_synthesis.py ~/Documents/welikia/placenames/synthesis/Placenames_v7.shp ~/Documents/welikia/placenames/synthesis/markdown_seconddraft`

### other notes
See `TODO` items throughout the code; in particular, shapefile plate/grid data processing is still needed.

- Output formatting is limited. Whether it's worth considerable development time to improve via code depends on the downstream editing processes.
- Likewise with handling field data that is not consistent. For example, ordering references chronologically isn't well defined when the year may not be part of the name string. Aggregating reference page numbers is similarly vexed. 
