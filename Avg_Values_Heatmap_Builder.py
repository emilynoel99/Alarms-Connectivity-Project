import csv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from scipy.ndimage import gaussian_filter
from collections import defaultdict
import statistics


# --- CONFIGURABLES ---
CALIBRATED_CSV = "rssi_log_calibrated.csv"
COORDINATES_CSV = "locations.csv"
FLOORPLAN_IMG = "floorplan.png"


# --- STEP 1: Load and group RSSI data ---
groups = []
current_group = []
last_button = None


with open(CALIBRATED_CSV, "r") as f:
   reader = csv.DictReader(f)
   for row in reader:
       try:
           rssi = float(row["calibrated_rssi"].strip())
           button = row["button"].strip()
           if button != last_button:
               if current_group:
                   groups.append(current_group)
               current_group = [rssi]
               last_button = button
           else:
               current_group.append(rssi)
       except (ValueError, KeyError):
           continue
   if current_group:
       groups.append(current_group)


print("Loaded RSSI groups:")
for i, g in enumerate(groups):
   print(f"Group {i+1} ({len(g)} points): {g}")


# --- STEP 2: Average values without outlier filtering ---
averaged_rssi = [statistics.mean(group) for group in groups]


# --- STEP 3: Load coordinates ---
locations = []
with open(COORDINATES_CSV, "r") as f:
   reader = csv.DictReader(f)
   for row in reader:
       locations.append((int(row["x"]), int(row["y"])))


print("Loaded coordinates:")
#print number of coordinates
for x, y in locations:
   print(f"({x}, {y})")


#Match lengths
min_len = min(len(locations), len(averaged_rssi))
locations = locations[:min_len]
averaged_rssi = averaged_rssi[:min_len]


print(f"Number of coordinates: {len(locations)}")
print(f"Number of RSSI averages: {len(averaged_rssi)}")


# Check match
if len(locations) != len(averaged_rssi):
   raise ValueError("Mismatch between number of coordinates and RSSI values")


# --- STEP 4: Load image and create heatmap layer ---
img = mpimg.imread(FLOORPLAN_IMG)
heatmap = np.zeros((img.shape[0], img.shape[1]))


# Draw Gaussian blobs
for (x, y), rssi in zip(locations, averaged_rssi):
   x, y = int(x), int(y)
   if 0 <= y < heatmap.shape[0] and 0 <= x < heatmap.shape[1]:
       heatmap[y, x] = rssi  # Note y before x (row, col)


# Apply smoothing
heatmap = gaussian_filter(heatmap, sigma=20)


# --- STEP 5: Plot with custom color mapping ---
def rssi_to_color(rssi):
   if rssi > -65:
       return '#00A86B'  # Kelly Green
   elif -75 < rssi <= -65:
       return '#66CDAA'  # Medium Aquamarine
   elif -85 < rssi <= -75:
       return '#FFD700'  # Gold
   elif -95 < rssi <= -85:
       return '#FF7F7F'  # Light Red
   else:
       return '#FF0000'  # Bright Red


fig, ax = plt.subplots()
ax.imshow(img)


# Overlay the raw points with color
for (x, y), rssi in zip(locations, averaged_rssi):
   ax.scatter(x, y, color=rssi_to_color(rssi), edgecolors='black', s=100, alpha=0.8)


# Overlay smoothed heatmap
ax.imshow(heatmap, cmap='hot', alpha=0.5)


# Create legend manually
from matplotlib.patches import Patch
legend_elements = [
   Patch(facecolor='#00A86B', edgecolor='black', label='> -65 dBm'),
   Patch(facecolor='#66CDAA', edgecolor='black', label='-75 to -65 dBm'),
   Patch(facecolor='#FFD700', edgecolor='black', label='-85 to -75 dBm'),
   Patch(facecolor='#FF7F7F', edgecolor='black', label='-95 to -85 dBm'),
   Patch(facecolor='#FF0000', edgecolor='black', label='< -95 dBm'),
]
ax.legend(handles=legend_elements, loc='upper right')


plt.title("RSSI Heatmap Over Floorplan")
plt.axis('off')
plt.tight_layout()
plt.show()
