import arcpy
import argparse
import csv
from pathlib2 import Path

PLACENAME_FIELD = "Placename"
SCORES = {
    1: "[This feature is shown in this source but in a different place than the synthesized data.]",
    2: "[This feature is shown in the synthesized data similar to this source.]",
    3: "[This feature is shown in the synthesized data based on this source.]",
}


def extant_shp(string):
    if Path(string).is_file():
        return string
    else:
        raise


def get_sdr_id(field):
    field_parts = field.split("_")
    if len(field_parts) > 1:
        try:
            return int(field_parts[-1])
        except ValueError as e:
            pass  # not numeric
    return None


def sdr_fields(fields):
    return_fields = []
    for field in fields:
        sdr_id = get_sdr_id(field)
        if sdr_id:
            return_fields.append(field)
    return return_fields


def get_rowcount(cursor, query):
    cursor.execute(query)
    cursor.fetchall()
    return cursor.rowcount


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "shapefile", type=extant_shp, help="Path to input placename features shapefile"
)
parser.add_argument(
    "-d",
    "--database",
    action="store_true",
    default=False,
    help="Write location records to database directly, in addition to outputting csv. "
    "To use this option, database credentials must be specified in a config file as detailed in the README.",
)
parser.add_argument(
    "-c",
    "--csv",
    help="Path to output csv. If not specified, shapefile basename and location will be used.",
)
options = vars(parser.parse_args())
shapefile = options.get("shapefile")
csvfile = options.get("csv") or str(Path(shapefile).with_suffix(".csv"))

if options["database"]:
    import mysql.connector
    from dotenv import dotenv_values

    envfile = "{}/.env".format(Path(__file__).parents[1].as_posix())
    config = dotenv_values(dotenv_path=envfile, verbose=True)
    DBHOST = config.get("DBHOST")
    DBPORT = config.get("DBPORT")
    DBNAME = config.get("DBNAME")
    DBUSER = config.get("DBUSER")
    DBPASS = config.get("DBPASS")
    DBTABLE = config.get("DBTABLE")
    if (
        not DBHOST
        or not DBPORT
        or not DBNAME
        or not DBUSER
        or not DBPASS
        or not DBTABLE
    ):
        raise ImportError("Missing database configuration parameters")

    conn = mysql.connector.connect(
        host=DBHOST, port=DBPORT, database=DBNAME, user=DBUSER, password=DBPASS
    )
    mysql_cursor = conn.cursor()

fields = [PLACENAME_FIELD] + sdr_fields([f.name for f in arcpy.ListFields(shapefile)])
if len(fields) <= 1:
    exit("No SDR fields to process.")

placename_sdr_dict = {}
with open(csvfile, "w") as csvhandle:
    csvwriter = csv.writer(csvhandle, lineterminator="\n")
    csvwriter.writerow(["id_placename", "id_sdr", "location"])

    with arcpy.da.SearchCursor(shapefile, fields) as cursor:
        for row in cursor:
            id_placename = int(row[0])
            for position, field in enumerate(fields):
                id_sdr = get_sdr_id(field)
                score = row[position]
                # If the same place/sdr combination occurs twice with different scores,
                # e.g. (96,191,2) and (96,191,1), the entry with the highest score will be written
                if score in SCORES.keys() and (
                    (
                        (id_placename, id_sdr) in placename_sdr_dict
                        and score > placename_sdr_dict[(id_placename, id_sdr)]
                    )
                    or (id_placename, id_sdr) not in placename_sdr_dict
                ):
                    placename_sdr_dict[(id_placename, id_sdr)] = score

    placename_sdr_rows = [
        (id_placename, id_sdr, score)
        for (id_placename, id_sdr), score in placename_sdr_dict.items()
    ]
    csvwriter.writerows(placename_sdr_rows)

if options["database"]:
    missing_placenames = []
    missing_sdrs = []
    for locationrow in placename_sdr_rows:
        id_placename = locationrow[0]
        id_sdr = locationrow[1]

        placename_query = "SELECT id_placename FROM placename WHERE id_placename = {}".format(
            id_placename
        )
        pncount = get_rowcount(mysql_cursor, placename_query)
        if pncount < 1:
            missing_placenames.append(id_placename)

        sdr_query = "SELECT id FROM sdr WHERE id = {}".format(id_sdr)
        sdrcount = get_rowcount(mysql_cursor, sdr_query)
        if sdrcount < 1:
            missing_sdrs.append(id_sdr)

        if pncount > 0 and sdrcount > 0:
            location_query = "SELECT * FROM {} WHERE id_placename = {} AND id_sdr = {}".format(
                DBTABLE, id_placename, id_sdr
            )
            locationcount = get_rowcount(mysql_cursor, location_query)
            if locationcount > 0:
                query = (
                    "UPDATE {} SET location = CONCAT_WS(CHAR(13), location, '{}') WHERE "
                    "id_placename = {} AND id_sdr = {}".format(
                        DBTABLE, SCORES[locationrow[2]], id_placename, id_sdr
                    )
                )
            else:
                query = (
                    "INSERT INTO {} (id_placename, id_sdr, location, canonical) "
                    "VALUES ({}, {}, '{}', 1)".format(
                        DBTABLE, id_placename, id_sdr, SCORES[locationrow[2]]
                    )
                )
            print(query)
            mysql_cursor.execute(query)
            conn.commit()

    if len(missing_placenames) > 0:
        print("missing placename ids:")
        print("\n".join([str(p) for p in missing_placenames]))
    if len(missing_sdrs) > 0:
        print("missing SDR ids:")
        print("\n".join([str(s) for s in missing_sdrs]))
