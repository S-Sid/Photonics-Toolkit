import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import math

def snell_try(theta_i, n1, n2):
    theta_i = math.radians(theta_i)
    sin_theta_r = (math.sin(theta_i) * n1) / n2 

    # 1. Critical Angle (using math.isclose for safety)
    # abs_tol=0.001 gives a safe 0.1% margin of error
    if math.isclose(sin_theta_r, 1.0, abs_tol=0.001) or math.isclose(sin_theta_r, -1.0, abs_tol=0.001):
        theta_r = 90.0
        return "Critical Angle", theta_r
    
    # 2. Total Internal Reflection (TIR)
    if sin_theta_r > 1.0 or sin_theta_r < -1.0:
        # Law of reflection: reflection angle = incident angle
        theta_r = math.degrees(theta_i) 
        return "TIR (Reflection)", theta_r
    
    # 3. Normal Refraction
    theta_r = math.asin(sin_theta_r)
    theta_r = math.degrees(theta_r)

    return "Refraction", theta_r

# --- Test Variables ---
current_i = 50.0
current_n1 = 1.33
current_n2 = 1.0

# --- 3. Figure Setup ---
fig, ax = plt.subplots(figsize=(8, 8))
# Shrink the bottom of the plot to make room for our UI widgets
plt.subplots_adjust(bottom=0.25) 

# --- 4. The Drawing Function ---
def draw_plot():
    ax.clear() # Clear the old plot completely
    
    # Calculate physics
    status, r_deg = snell_try(current_i, current_n1, current_n2)
    
    angle_i = math.radians(current_i)
    angle_r = math.radians(r_deg)

    # Incident Ray: Starts at Top-Left, ends at (0,0)
    x_i = [-2 * math.sin(angle_i),0]
    y_i = [2 * math.cos(angle_i),0]

    # Outgoing Ray: Starts at (0,0), ends outward
    if status == "TIR (Reflection)":
        x_r = [2 * math.sin(angle_r),0]
        y_r = [2 * math.cos(angle_r),0] # Positive Y for reflection
    else: 
        x_r = [2 * math.sin(angle_r),0]
        y_r = [-2 * math.cos(angle_r),0] # Negative Y for refraction

    # Draw elements
    ax.axhline(0, color='black', linewidth=2)
    ax.axvline(0, color='gray', linestyle='--')
    
    ax.plot(x_i, y_i, color='blue', linewidth=2, label=f"Incident ({current_i:.1f}°)")
    ax.plot(x_r, y_r, color='red', linewidth=2, label=f"{status} ({r_deg:.1f}°)")

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    
    # Labels
    ax.text(-1.9, 1.8, f"n1 = {current_n1}", fontsize=14, fontweight='bold')
    ax.text(-1.9, -1.8, f"n2 = {current_n2}", fontsize=14, fontweight='bold')
    
    ax.legend(loc='upper right')
    plt.draw() # Force Matplotlib to update the window

# --- 5. UI Widget Setup ---
# Define where the boxes go: [left, bottom, width, height]
ax_n1 = plt.axes([0.25, 0.15, 0.2, 0.05])
ax_n2 = plt.axes([0.65, 0.15, 0.2, 0.05])
ax_i  = plt.axes([0.45, 0.05, 0.2, 0.05])

# Create the text boxes
text_n1 = TextBox(ax_n1, 'n1: ', initial=str(current_n1))
text_n2 = TextBox(ax_n2, 'n2: ', initial=str(current_n2))
text_i  = TextBox(ax_i, 'Angle (i): ', initial=str(current_i))

# --- 6. Update Logic ---
def submit(text):
    global current_n1, current_n2, current_i
    try:
        # Read the text boxes and convert them to floats
        current_n1 = float(text_n1.text)
        current_n2 = float(text_n2.text)
        current_i = float(text_i.text)
        draw_plot() # Redraw with the new numbers
    except ValueError:
        print("Please enter valid numbers!")

# Link the text boxes to the submit function so it triggers when you press Enter
text_n1.on_submit(submit)
text_n2.on_submit(submit)
text_i.on_submit(submit)

# Draw the initial plot
draw_plot()
plt.show()