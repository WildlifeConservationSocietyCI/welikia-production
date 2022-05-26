from pathlib2 import Path


def extant_dir(string):
    resolved_path = Path(string).expanduser()
    if resolved_path.is_dir():
        return string
    else:
        raise ValueError(f"{string} is not a directory")


def extant_file(string):
    resolved_path = Path(string).expanduser()
    if resolved_path.is_file():
        return string
    else:
        raise ValueError(f"{string} is not a file")


def truthy(val):
    return val in ("t", "T", "true", "True", True, 1, "1")


def get_markdown_files(mddir, version):
    file_list = [f for f in mddir.glob("**/*.md") if f.is_file()]
    md_files = []
    for f in file_list:
        try:
            # file has to have an id and a draft number
            (placeid, fileversion) = f.stem.split(".")[-2:]
            if int(fileversion) == version:
                md_files.append((int(placeid), f))
        except ValueError:
            pass

    return md_files


def get_place(places, prop, value):
    for p in places:
        if getattr(p, prop, None) == value:
            return p
    return None


def update_places(places, placeid, prop, value):
    for idx, place in enumerate(places):
        if place.id == placeid:
            setattr(place, prop, value)
            places[idx] = place
            break
    return places


def format_references(labelstem, references):
    # TODO: order chronologically? String may not have embedded year
    if len(references) > 0:
        ref_label = labelstem
        refs = []
        for r in references:
            refstring = f"{r.name_shorter}"
            if r.pagenumbers:
                refstring = f"{r.name_shorter}: {r.pagenumbers}"
            refs.append(refstring)
        if len(refs) > 1:
            ref_label = f"{labelstem}s"
        return f"\n\n{ref_label}: {'; '.join(refs)}"
    return ""
