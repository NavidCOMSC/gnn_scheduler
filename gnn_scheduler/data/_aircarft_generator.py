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
        output_dir: str,
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
        self.output_dir = output_dir
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
