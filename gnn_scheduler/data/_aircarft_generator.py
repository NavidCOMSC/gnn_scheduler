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
