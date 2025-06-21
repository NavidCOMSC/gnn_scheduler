import os
import random
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import numpy as np

# Just get a module logger—do NOT call basicConfig here
logger = logging.getLogger(__name__)


class AircraftGenerator:
    """Generates CSV files for aircraft data with random attributes.

    This class generates dataframes for aircraft, including their serial numbers,
    associated work packages, work orders, and technicians. It creates a
    DataFrame for each entity and saves them as CSV files in a file path
    specified by the user.
    """

    def __init__(
        self,
        work_packages_file: str,
        instance_dir: str,
        turnaround_scaling_factor: float = 1.2,
        num_instances: int = 10,
        num_aircrafts: int = 20,
        num_technicians: int = 36,
        shift_duration: int = 8,
        min_total_man_hours_percentage: float = 0.7,
        max_total_man_hours_percentage: float = 0.9,
        max_turnaround_minutes: int = 1440,  # 28 hrs in minutes
        max_attempts: int = 1000,
        seed: Optional[int] = None,
        start_year: Optional[int] = None,
    ):
        self.work_packages_file = work_packages_file
        self.instance_dir = instance_dir
        self.turnaround_scaling_factor = turnaround_scaling_factor
        self.num_instances = num_instances
        self.num_aircrafts = num_aircrafts
        self.num_technicians = num_technicians
        self.shift_duration = shift_duration
        self.min_total_man_hours_percentage = min_total_man_hours_percentage
        self.max_total_man_hours_percentage = max_total_man_hours_percentage
        self.max_turnaround_minutes = max_turnaround_minutes
        self.max_attempts = max_attempts
        self.seed = seed
        self.start_year = start_year

        # set up the random seed for reproducibility
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)

        # check for missing the datetime input
        if self.start_year is None:
            self.start_year = datetime.now().year

    def generate_aircraft_instances(
        self,
        work_packages_file: str,
        instance_dir: str,
        turnaround_scaling_factor: float,
        num_instances: int,
        num_aircrafts: int,
        num_technicians: int,
        shift_duration: int,
        min_total_man_hours_percentage: float,
        max_total_man_hours_percentage: float,
        max_turnaround_minutes: int,
        max_attempts: int,
        seed: Optional[int] = None,
        start_year: Optional[int] = None,
    ) -> None:

        # loading and reading the work packages file
        df = pd.read_csv(work_packages_file)
        df["WP number"] = df["WP number"].astype(str)
        df["Minutes"] = df["Minutes"].fillna(0)
        df["Man_Hours"] = df["Man_Hours"].fillna(0)

        wps = df.to_dict("records")
        wp_map = {wp["WP number"]: wp for wp in wps}
        all_wp_numbers = [wp["WP number"] for wp in wps]

        # Compute man-hour window
        capacity = num_technicians * shift_duration  # 288 h
        raw_min_man = min_total_man_hours_percentage * capacity  # 201.6 h
        raw_max_man = max_total_man_hours_percentage * capacity  # 259.2 h

        total_unique_hours = sum(wp["Man_Hours"] for wp in wps)
        if total_unique_hours < raw_min_man:
            logger.warning(
                f"Total unique WP man-hours ({total_unique_hours:.1f}h) below "
                f"requested minimum ({raw_min_man:.1f}h); allowing repetition to fill."
            )
        if total_unique_hours > raw_max_man:
            logger.warning(
                f"Total unique WP man-hours ({total_unique_hours:.1f}h) above "
                f"requested maximum ({raw_max_man:.1f}h); allowing repetition to dilute."
            )

        os.makedirs(instance_dir, exist_ok=True)

        def generate_single_instance(instance_id: int):
            coverage_fails = manhour_fails = turnaround_fails = 0

            for _ in range(1, max_attempts + 1):
                used_wps = set()
                total_man_used = 0.0
                aircraft_data = []

                base_day = datetime(
                    start_year, random.randint(1, 12), random.randint(1, 28)
                )

                remaining = all_wp_numbers.copy()
                random.shuffle(remaining)

                for ac_idx in range(1, num_aircrafts + 1):
                    landing = base_day + timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )

                    sel_wps = []
                    minutes_sum = 0
                    hours_sum = 0.0

                    # guarantee one distinct WP until exhausted
                    if remaining:
                        wpn = remaining.pop()
                        sel_wps.append(wpn)
                        m = wp_map[wpn]["Minutes"]
                        h = wp_map[wpn]["Man_Hours"]
                        minutes_sum += m
                        hours_sum += h

                    # top up with repeats allowed
                    tries = 0
                    while True:
                        if minutes_sum > 20 and random.random() > 0.5:
                            break
                        tries += 1
                        if tries >= 50:
                            break
                        pick = random.choice(wps)
                        # allow picking any WP again
                        sel_wps.append(pick["WP number"])
                        minutes_sum += pick["Minutes"]
                        hours_sum += pick["Man_Hours"]

                    est_turn = round(minutes_sum * turnaround_scaling_factor)
                    if est_turn > max_turnaround_minutes:
                        turnaround_fails += 1
                        break

                    depart = landing + timedelta(minutes=est_turn)
                    ta_str = f"{est_turn//60:02d}:{est_turn%60:02d}"
                    ac_id = 100 + ac_idx

                    used_wps.update(sel_wps)
                    total_man_used += hours_sum

                    aircraft_data.append(
                        {
                            "Aircraft (A/C) Serial Number": ac_id,
                            "A/C Landing Date": landing.strftime("%d/%m/%Y"),
                            "A/C Landing Time": landing.strftime("%H:%M"),
                            "A/C departure Date": depart.strftime("%d/%m/%Y"),
                            "A/C departure Time": depart.strftime("%H:%M"),
                            "Turn Around Time": ta_str,
                            "Work that needs to be carried out": ", ".join(
                                sel_wps
                            ),
                        }
                    )

                if len(aircraft_data) != num_aircrafts:
                    continue

                if not set(all_wp_numbers).issubset(used_wps):
                    coverage_fails += 1
                    continue

                if (
                    total_man_used < raw_min_man
                    or total_man_used > raw_max_man
                ):
                    manhour_fails += 1
                    continue

                out_df = pd.DataFrame(aircraft_data)
                out_df["Work that needs to be carried out"] = (
                    out_df["Work that needs to be carried out"]
                    .fillna("")
                    .astype(str)
                    .apply(lambda s: s.replace("nan", "").strip(" ,"))
                )
                fn = os.path.join(
                    instance_dir, f"aircrafts_instance_{instance_id}.csv"
                )
                out_df.to_csv(fn, index=False)
                return

            logger.error(
                f"Instance {instance_id} failed after {max_attempts} attempts: "
                f"coverage_fails={coverage_fails}, "
                f"manhour_fails={manhour_fails}, "
                f"turnaround_fails={turnaround_fails}"
            )
            raise RuntimeError(f"Could not generate instance {instance_id}")

        for i in range(1, num_instances + 1):
            generate_single_instance(i)
