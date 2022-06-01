import argparse
from datetime import datetime
from dotenv import dotenv_values
from operator import attrgetter
from pathlib2 import Path
from includes.database import Database
from includes.place import Place, Reference
from includes.utils import (
    extant_dir,
    extant_file,
    get_markdown_files,
    get_place,
    truthy,
    update_places,
)


# 1. SETUP

VERSION = 2  # markdown file draft
ID_LENAPE = 3
# ("1"=>"extant", "2"=>"disappeared", "3"=>"created", "4"=>"post-1609 natural")
STATUS_LABELS = {1: "", 2: "†", 3: "‡", 4: "≈"}
STUDY_AREAS = [
    ("sa_bronx", "Bronx"),
    ("sa_brooklyn", "Brooklyn"),
    ("sa_harbor_lower", "Lower harbor"),
    ("sa_harbor_upper", "Upper harbor"),
    ("sa_lis", "Long Island Sound"),
    ("sa_manhattan", "Manhattan"),
    ("sa_nassau", "Nassau"),
    ("sa_newjersey", "New Jersey"),
    ("sa_queens", "Queens"),
    ("sa_statenisland", "Staten Island"),
    ("sa_westchester", "Westchester"),
]

envfile = "{}/.env".format(Path(__file__).parents[1].as_posix())
config = dotenv_values(dotenv_path=envfile, verbose=True)

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "shapefile", type=extant_file, help="Path to input placename features shapefile"
)
parser.add_argument(
    "markdown-dir",
    type=extant_dir,
    help="Path to directory of markdown files with place id in each filename",
)
parser.add_argument(
    "-o",
    "--output",
    help="Path to output markdown. If not specified, shapefile basename and location will be used.",
)
options = vars(parser.parse_args())

shapefile = Path(options.get("shapefile")).expanduser()
markdown_dir = Path(options.get("markdown-dir")).expanduser()
timestr = datetime.now().date().isoformat()
outputfile = Path(
    options.get("output") or f"{markdown_dir.parent}/gazetteer-entries_{timestr}.md"
)


def get_study_areas(areas):
    return [a[1][1] for a in zip(areas, sorted(STUDY_AREAS)) if truthy(a[0])]


# 2. INITIAL POPULATION FROM DATABASE

places = []
with Database(config) as db:
    references = [Reference(*row) for row in db.query(Reference.sql)]
    maps = [r for r in references if r.type == "map"]
    texts = [r for r in references if r.type == "text"]

    place_results = db.query(Place.sql)
    for placerow in place_results:
        place = Place(
            id=placerow[0],
            name=placerow[1].strip(),
            name_invented=truthy(placerow[2]),
            name_indigenous=(placerow[3] == ID_LENAPE),
            status=STATUS_LABELS.get(placerow[4], ""),
            description=placerow[5] or "",  # db (not markdown) description
            study_areas=get_study_areas(placerow[-11:]),
            maps=[m for m in maps if m.id_placename == placerow[0]],
            texts=[t for t in texts if t.id_placename == placerow[0]],
        )

        places.append(place)

# p = get_place(places, "id", 6)
# print(p.references_output)


# 3. POPULATE PLACE TEXTS FROM MARKDOWN FILES

mdfiles = get_markdown_files(markdown_dir, VERSION)
for mdfile in mdfiles:
    with open(mdfile[1], "r") as f:
        main_text = f.read().strip()
    places = update_places(places, mdfile[0], "main_text", main_text)


# 4. POPULATE PLATE AND GRID FROM SHAPEFILE

# TODO: Iterate over shapefile and populate plate and grid, matching on place.id
# places = update_places(places, <placeid>, "plate", <plate number>)
# places = update_places(places, <placeid>, "grid", <grid string>)


# 5. OUTPUT

# sort by id
# places.sort(key=attrgetter("id"))
# sort by name
places.sort(key=attrgetter("name"))
# filter by borough
# brooklyn_places = [p for p in places if "Brooklyn" in p.study_areas]
places = [p for p in places if p.main_text != ""]   # removes all places without markdown text entry
# print(brooklyn_places[0])

# TODO:
#  - Can't right-align plate/grid in markdown
#  - Move to pypandoc and write to docx and do as much formatting as possible?
#    Or more useful to output text simply here, for further automated processing externally?
with outputfile.open("w", encoding='utf-8') as f:
    for place in places:
        entry = f"""
**{place.output_name}{place.status}** ({", ".join(place.study_areas)})

Plate {place.plate} ({place.grid})

{place.main_text}{place.references_output}
"""

        f.write(entry)
