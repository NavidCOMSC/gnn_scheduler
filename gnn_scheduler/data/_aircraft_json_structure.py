import csv
import json
import os
import glob


# Mpaping Resources(Technicians) to their IDs
STAFF_INDEX_MAP = {
    "B1 Technician": 1,
    "B2 Technician": 2,
    "B1 Engineer": 3,
    "B2 Engineer": 4,
}


def read_work_packages(work_packages_file):

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

        for row in reader:
            if not row:
                continue
            wp_name = row[0].strip()
            wp_dict[wp_name] = []
            for j in range(len(wo_columns)):
                col_index = 1 + j * 2
                if col_index >= len(row):
                    break
                dur_str = row[col_index].strip()
                if not dur_str:
                    continue
                # Convert duration to integer, handle potential errors
                try:
                    duration = int(dur_str)
                except ValueError:
                    print(
                        f"Invalid duration '{dur_str}' for work order '{wo_columns[j]}' in work package '{wp_name}'. Skipping."
                    )
                    continue
                staff_str = (
                    row[col_index + 1].strip()
                    if col_index + 1 < len(row)
                    else ""
                )
                staff_list = []
                if staff_str:
                    staff_list = [
                        s.strip().strip('"').strip()
                        for s in staff_str.split(",")
                        if s.strip()
                    ]

                staff_indices = [
                    STAFF_INDEX_MAP[s]
                    for s in staff_list
                    if s in STAFF_INDEX_MAP
                ]
                wo_name = wo_columns[j]
                wo_index = wo_index_map[wo_name]
                wp_dict[wp_name].append((wo_index, duration, staff_indices))

    return wp_dict, wo_columns


def parse_aircraft_file(aircrafts_file, wp_dict, wo_index_map):
    """
    Parse a single aircraft CSV file and create a JSON structure.
    Args:
        aircrafts_file: Path to the aircrafts CSV file.
        wp_dict: Dictionary mapping work packages to their work orders.
        wo_index_map: Mapping of work order names to their indices.
    """

    # Read aircrafts CSV file
    duration_matrix = []
    machine_matrix = []
    job_sequences = []
    landing_time_list = []
    departing_time_list = []
    instance_name = os.path.splitext(os.path.basename(aircrafts_file))[0]

    with open(aircrafts_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if not row:
                continue
            ac_serial = row[0].strip()
            landing_date = row[1].strip()
            landing_time = row[2].strip()
            departure_date = row[3].strip()
            departing_time = row[4].strip()
            wp_string = row[6].strip()

            landing_str = landing_date.replace("/", ":") + "-" + landing_time
            departing_str = (
                departure_date.replace("/", ":") + "-" + departing_time
            )

            wp_list = [wp.strip() for wp in wp_string.split(",")]

            durations = []
            machines = []
            sequences = []

            for wp in wp_list:
                if wp in wp_dict:
                    for wo_index, dur, staff_indices in wp_dict[wp]:
                        for staff_idx in staff_indices:
                            durations.append(dur)
                            machines.append(staff_idx)
                            sequences.append(wo_index)

            duration_matrix.append(durations)
            machine_matrix.append(machines)
            job_sequences.append(sequences)
            landing_time_list.append(landing_str)
            departing_time_list.append(departing_str)

    return {
        "instance": {
            "name": instance_name,
            "duration_matrix": duration_matrix,
            "machine_matrix": machine_matrix,
            "metadata": {},
        },
        "job_sequences": job_sequences,
        "landing_time": landing_time_list,
        "departing_time": departing_time_list,
        "metadata": {"status": "optimal", "makespan": None},
    }


def parse_aircraft_directory(work_packages_file, aircrafts_dir):
    """
    Parse all aircraft CSV files in a directory and create a JSON structure.
    Args:
        work_packages_file: Path to the work packages CSV file.
        aircrafts_dir: Directory containing aircrafts CSV files.
    """

    wp_dict, wo_index_map = read_work_packages(work_packages_file)
    aircraft_files = glob.glob(
        os.path.join(aircrafts_dir, "aircrafts_instance_*.csv")
    )
    aircraft_files.sort(
        key=lambda f: int(os.path.basename(f).split("_")[-1].split(".")[0])
    )

    all_instances = []
    for aircraft_file in aircraft_files:
        instance_data = parse_aircraft_file(
            aircraft_file, wp_dict, wo_index_map
        )
        all_instances.append(instance_data)

    return all_instances


# Example usage
if __name__ == "__main__":
    work_packages_file = "work_packages_work_orders.csv"
    aircrafts_dir = "path/to/aircrafts_directory"  # Update this path

    result = parse_aircraft_directory(work_packages_file, aircrafts_dir)
    with open("output.json", "w") as f:
        json.dump(result, f, indent=4)
