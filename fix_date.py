import os
import re
import time
from datetime import datetime

VIDEO_DIR = "vids"
filename_pattern = re.compile(r"VID_(\d{8})_(\d{6})")

for filename in os.listdir(VIDEO_DIR):
    if filename.endswith(".mp4"):
        match = filename_pattern.match(filename)
        if match:
            date_str, time_str = match.groups()
            datetime_str = f"{date_str}{time_str}"
            dt = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")

            timestamp = dt.timestamp()
            filepath = os.path.join(VIDEO_DIR, filename)

            # Modification du mtime et atime du fichier
            os.utime(filepath, (timestamp, timestamp))

            print(f"[OK] {filename} → mtime/atime mis à {dt.isoformat()}")
        else:
            print(f"[SKIP] Format de nom incorrect : {filename}")
