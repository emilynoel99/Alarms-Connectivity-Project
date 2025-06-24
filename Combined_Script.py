import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import csv
import numpy as np
from scipy.ndimage import gaussian_filter
import statistics
from matplotlib.patches import Patch

# === CONFIG ===
FLOORPLAN_IMG = "floorplan.png"
LOCATIONS_CSV = "locations.csv"
CALIBRATED_CSV = "rssi_log_calibrated.csv"

# === STEP 1: Coordinate Picker ===
print("Step 1: Click points on the floorplan. Close the window when finished.")
coords = []
img = mpimg.imread(FLOORPLAN_IMG)
fig, ax = plt.subplots()
ax.imshow(img)
plt.title("Click to select points. Close window when done.")

def onclick(event):
    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        coords.append((x, y))
        print(f"Clicked: ({x}, {y})")
        ax.plot(x, y, 'ro')
        plt.draw()

fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()

# Save coordinates
with open(LOCATIONS_CSV, "w") as f:
    f.write("x,y\n")
    for x, y in coords:
        f.write(f"{x},{y}\n")

print(f"\nSaved {len(coords)} points to {LOCATIONS_CSV}")

# === STEP 2: Load RSSI Data and Group by Button ===
print("Step 2: Processing RSSI log...")

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

averaged_rssi = [statistics.mean(g) for g in groups]

# === STEP 3: Load Coordinates ===
locations = []
with open(LOCATIONS_CSV, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        locations.append((int(row["x"]), int(row["y"])))

min_len = min(len(locations), len(averaged_rssi))
locations = locations[:min_len]
averaged_rssi = averaged_rssi[:min_len]

if len(locations) != len(averaged_rssi):
    raise ValueError("Mismatch between number of coordinates and RSSI values")

print(f"Loaded {len(locations)} points and RSSI values.")

# === STEP 4: Create Heatmap ===
img = mpimg.imread(FLOORPLAN_IMG)
heatmap = np.zeros((img.shape[0], img.shape[1]))

for (x, y), rssi in zip(locations, averaged_rssi):
    if 0 <= y < heatmap.shape[0] and 0 <= x < heatmap.shape[1]:
        heatmap[y, x] = rssi  # note: row = y, col = x

heatmap = gaussian_filter(heatmap, sigma=20)

# === STEP 5: Plotting ===
def rssi_to_color(rssi):
    if rssi > -65:
        return '#00A86B'  # Green
    elif -75 < rssi <= -65:
        return '#66CDAA'  # Aquamarine
    elif -85 < rssi <= -75:
        return '#FFD700'  # Gold
    elif -95 < rssi <= -85:
        return '#FF7F7F'  # Light Red
    else:
        return '#FF0000'  # Bright Red

fig, ax = plt.subplots()
ax.imshow(img)

# Overlay raw points
for (x, y), rssi in zip(locations, averaged_rssi):
    ax.scatter(x, y, color=rssi_to_color(rssi), edgecolors='black', s=100, alpha=0.8)

# Overlay smoothed heatmap
ax.imshow(heatmap, cmap='hot', alpha=0.5)

# Custom legend
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