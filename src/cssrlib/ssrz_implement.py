
import pandas as pd
import re

# Define headers for tables
headers = {
    "Time Tag Message": "### SSRZ - 4090.7.9 Time Tag Message <ZM009>",
    "Low Rate Correction Message": "### SSRZ - 4090.7.2 Low Rate Correction Message <ZM002>",
    "High Rate Correction Message": "### SSRZ - 4090.7.1 High Rate Correction Message <ZM001>",
    "Gridded Ionosphere Correction Message": "### SSRZ - 4090.7.3 Gridded Ionosphere Correction Message <ZM003>",
    "Gridded Troposphere Correction Message": "### SSRZ - 4090.7.4 Gridded Troposphere Correction Message <ZM004>",
    "Satellite Dependent Regional Ionosphere Correction Message": "### SSRZ - 4090.7.5 Satellite Dependent Regional Ionosphere Correction Message <ZM005>",
    "Global VTEC Ionosphere Correction Message": "### SSRZ - 4090.7.6 Global VTEC Ionosphere Correction Message <ZM006>",
    "Regional Troposphere Correction Message": "### SSRZ - 4090.7.7 Regional Troposphere Correction Message <ZM007>"
}

# User-defined start time and duration
gps_week_start = 2337  # User-defined start GPS week
gps_time_start = 205265  # User-defined start GPS time of week (seconds)
max_duration = 1200  # Stop after 1200 seconds (20 minutes)

# Regular expression to extract GPS week and GPS time of the week
gps_week_pattern = re.compile(r"GPS week\s*:\s*(\d+)")
gps_time_pattern = re.compile(r"GPS time of the week \[s\]:\s*(\d+)")

# Dictionary to store data
seconds_data = {}

# Read the file
with open("HYPOS_SSRZ_NORD_11-12ssr,txt", "r") as file:
    lines = file.readlines()

current_gps_week = None  # Current detected GPS week
current_gps_time = None  # Current detected GPS time
current_header = None  # Tracks the current table being read
data = {}  # Temporary storage for tables
column_headers = {}  # Stores column names for each table

reading_data = False  # Track if we have reached the required start time
i = 0

while i < len(lines):
    line = lines[i].strip()

    # Detect Time Tag Message
    if line == headers["Time Tag Message"]:
        current_header = "Time Tag Message"
        i += 1
        continue

    # Extract GPS week
    if current_header == "Time Tag Message" and "GPS week" in line:
        match = gps_week_pattern.search(line)
        if match:
            current_gps_week = int(match.group(1))
        i += 1
        continue

    # Extract GPS time of the week
    if current_header == "Time Tag Message" and "GPS time of the week [s]:" in line:
        match = gps_time_pattern.search(line)
        if match:
            current_gps_time = int(match.group(1))  # Full GPS time in seconds

            # Skip data before the start time
            if current_gps_week < gps_week_start or current_gps_time < gps_time_start:
                i += 1
                continue

            # Start reading data
            reading_data = True

            # Stop if we exceed the required time range
            if current_gps_time >= gps_time_start + max_duration:
                break

            # Store previous second’s data
            if current_gps_time not in seconds_data and data:
                seconds_data[current_gps_time] = {
                    k: pd.DataFrame(v, columns=column_headers[k]) for k, v in data.items()
                }

            # Reset for new second
            data = {}
            column_headers = {}

        i += 1
        continue

    # Skip data until the start time is reached
    if not reading_data:
        i += 1
        continue

    # Detect start of a new table
    if line in headers.values():
        current_header = [key for key, val in headers.items() if val == line][0]

        # Extract column headers from the next line
        if i + 1 < len(lines):
            column_headers[current_header] = lines[i + 1].strip().split()
            data[current_header] = []  # Initialize storage for this table

        i += 2  # Skip to data lines after the header
        continue

    # Store data inside a table
    if current_header and current_header != "Time Tag Message":
        data[current_header].append(line.split())  # Assuming space-separated values

    i += 1  # Move to the next line

# Store the last second's data
if current_gps_time and data:
    seconds_data[current_gps_time] = {
        k: pd.DataFrame(v, columns=column_headers[k]) for k, v in data.items()
    }

# Example: Access tables for a specific second (e.g., full GPS time 205265)
example_time = 205265
if example_time in seconds_data:
    for table_name, df in seconds_data[example_time].items():
        print(f"Table: {table_name} at GPS time {example_time}")
        print(df.head())  # Show first few rows
        print()