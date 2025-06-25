import csv
import json


def parse_files(work_packages_file, aircrafts_file):

    # Mpaping Resources(Technicians) to their IDs
    staff_index_map = {
        "B1 Technician": 1,
        "B2 Technician": 2,
        "B1 Engineer": 3,
        "B2 Engineer": 4,
    }

    # Read work packages from CSV
    wp_dict = {}
    wo_columns = []

    with open(work_packages_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        wo_columns = [
            col
            for i, col in enumerate(header)
            if col.startswith("WO") and not col.endswith("staff")
        ]
        wo_index_map = {wo: idx + 1 for idx, wo in enumerate(wo_columns)}
