import csv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from matplotlib.patches import Patch

# === Load the floorplan image ===
img = mpimg.imread("floorplan.png")
height, width = img.shape[0], img.shape[1]

# === Load (x, y) coordinates ===
coords = []
with open("locations.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        coords.append((int(row["x"]), int(row["y"])))

# === Load calibrated RSSI values ===
calibrated_rssi = []
with open("rssi_log_calibrated.csv", "r", encoding="latin-1") as f:
    reader = csv.DictReader(f)
    for row in reader:
        calibrated_rssi.append(float(row["calibrated_rssi"]))

# === Verify data alignment ===
if len(coords) != len(calibrated_rssi):
    raise ValueError("Number of RSSI values doesn't match number of coordinates.")

# === Color zones & thresholds ===
def get_color(rssi):
    if rssi >= -65:
        return "#4CBB17"
    elif -75 < rssi < -65:
        return "#90EE90"
    elif -85 < rssi <= -75:
        return "#FFFF00"
    elif -95 < rssi <= -85:
        return "#FFB6C1"
    else:
        return "#FF0000"

# === Plot heatmap ===
fig, ax = plt.subplots()
ax.imshow(img)
plt.title("Smoothed RSSI Heatmap Overlay")

# Overlay Gaussian-style blobs
for (x, y), rssi in zip(coords, calibrated_rssi):
    color = get_color(rssi)
    ax.scatter(x, y, s=2000, color=color, alpha=0.4, edgecolors='none')

# === Add custom legend ===
legend_elements = [
    Patch(facecolor="#4CBB17", label="≥ -65 (Strong)", edgecolor='black'),
    Patch(facecolor="#90EE90", label="-75 to -65", edgecolor='black'),
    Patch(facecolor="#FFFF00", label="-85 to -75", edgecolor='black'),
    Patch(facecolor="#FFB6C1", label="-95 to -85", edgecolor='black'),
    Patch(facecolor="#FF0000", label="< -95 (Weak)", edgecolor='black')
]
ax.legend(handles=legend_elements, loc="lower right", title="RSSI Signal Strength")

plt.axis("off")
plt.tight_layout()
plt.show()