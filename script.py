
import csv

# Input/output CSV filenames
input_file = "rssi_log.csv"
output_file = "rssi_log_calibrated.csv"

calibrated_data = []

with open(input_file, "r") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        try:
            rssi = float(row["rssi"])
            timestamp = row["timestamp"]
            calibrated_rssi = 1.57 * rssi + 24.2
            calibrated_data.append((timestamp, rssi, calibrated_rssi))
        except ValueError:
            print(f"Skipping row with invalid RSSI: {row}")

# Save calibrated data
with open(output_file, "w", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["timestamp", "measured_rssi", "calibrated_rssi"])
    writer.writerows(calibrated_data)

print(f"Calibrated data written to {output_file}")