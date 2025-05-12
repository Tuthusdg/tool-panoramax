import subprocess
import piexif
import os
from datetime import datetime

def get_timestamp_from_insv(insv_file):
    # Using piexif to extract the timestamp from the INSV file metadata
    exif_dict = piexif.load(insv_file)
    
    # The DateTimeOriginal is stored under the '0th' IFD in EXIF metadata
    datetime_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode("utf-8")
    
    # Convert to datetime object
    timestamp = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
    return timestamp

def add_timestamp_to_video(mp4_file, timestamp):
    # Format the timestamp to use in the filename or as text
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    # Command to add timestamp as metadata to mp4 file (using ffmpeg)
    output_file = f"output_{os.path.basename(mp4_file)}"
    command = [
        'ffmpeg',
        '-i', mp4_file,
        '-metadata', f'creation_time={timestamp_str}',
        '-codec', 'copy',
        output_file
    ]

    # Run the ffmpeg command
    subprocess.run(command, check=True)
    print(f"Timestamp added to video. Output saved as: {output_file}")
    return output_file

def main():
    # Input files
    insv_file = 'vids/vid03.insv'  # Replace with your .insv file path
    mp4_file = 'vids/vid03.mp4'    # Replace with your .mp4 file path

    # Extract timestamp from INSV file
    timestamp = get_timestamp_from_insv(insv_file)
    print(f"Timestamp from INSV file: {timestamp}")

    # Add timestamp to MP4 video file
    add_timestamp_to_video(mp4_file, timestamp)

if __name__ == '__main__':
    main()


"modif"