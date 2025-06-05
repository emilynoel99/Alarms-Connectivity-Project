import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Load your floorplan image
img = mpimg.imread('floorplan.png')  # Replace with your actual image path

# Display the image
fig, ax = plt.subplots()
ax.imshow(img)
plt.title("Click to select points. Close window when done.")

# Store clicked points
coords = []

def onclick(event):
    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        coords.append((x, y))
        print(f"Clicked: ({x}, {y})")
        ax.plot(x, y, 'ro')  # Mark the point
        plt.draw()

# Connect the click event
cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()

# Save to a file after clicking
with open("locations.csv", "w") as f:
    f.write("x,y\n")
    for x, y in coords:
        f.write(f"{x},{y}\n")