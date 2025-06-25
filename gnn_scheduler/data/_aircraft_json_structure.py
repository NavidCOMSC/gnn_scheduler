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
