"""
===============================================================================
Knife-Edge THz Beam Diameter Measurement (FWHM) - KT Version
===============================================================================
Author      : Sidharth Raj
Description :
    This script measures the diameter of a Terahertz (THz) beam using the
    "knife-edge" technique.

    Physics in one line:
        A sharp edge (knife) is moved across the beam in fixed steps. As it
        moves, it gradually blocks more of the beam, so the detected power
        traces an S-shaped curve (an error function). The DERIVATIVE of that
        S-curve is the beam's intensity profile, which is a Gaussian. The
        FWHM (Full Width at Half Maximum) of that Gaussian is the beam
        diameter.

    Pipeline:
        1. Read the raw knife-edge data (power vs stepper position).
        2. Crop to the region of interest (where the edge actually moves
           through the beam).
        3. (Optional) smooth the curve with a Savitzky-Golay filter.
        4. Differentiate the edge curve -> Gaussian beam profile.
        5. Fit a Gaussian to the derivative and report its FWHM in mm.

Each plt.show() below corresponds to one stage; titles have been added so the
figures are self-describing.
===============================================================================
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

plt.rcParams.update({'font.size': 14})

# Total distance travelled by the stepper motor during the scan, in mm.
# UPDATE THIS to match your scan range.
d_x = 70


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def gaussian(x, A, mu, sigma):
    """Standard Gaussian: A = height, mu = centre, sigma = width."""
    y = A * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    return y


def find_fwhm(x, y):
    """
    Find the Full Width at Half Maximum of a peak.
    Locates where the curve crosses half of its peak height on the left and
    right of the peak, and returns the distance between those crossings.
    """
    peak_index = np.argmax(y)                 # position of the peak
    peak_value = y[peak_index]                # peak height
    half_max_value = peak_value / 2           # the half-maximum level
    # Last point on the LEFT that is still below half-max:
    left_index = np.where(y[:peak_index] <= half_max_value)[0][-1]
    # First point on the RIGHT that drops back below half-max:
    right_index = np.where(y[peak_index:] <= half_max_value)[0][0] + peak_index
    fwhm = x[right_index] - x[left_index]     # width between the two crossings
    return fwhm, right_index, left_index


# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD THE RAW KNIFE-EDGE DATA
# ─────────────────────────────────────────────────────────────────────────────
file_name_h = r"C:\Sidharth\Start Python\KT Codes\System\p1+15_70mm.csv"   # UPDATE the sweep path
df = pd.read_csv(file_name_h)

# Column index 3 holds the detected signal. Change it if the signal sits in a
# different column of your TDS file.
y1 = df.iloc[:, 3]

# Index offset that marks where the region of interest begins.
#   len(y1)//70  = number of data points per mm (70 mm scan)
#   x 30         = the index that corresponds to the 30 mm mark
# Change the "30" to move where the analysed region starts, and "70" if the
# scan length changes.
dl = 40 * int((len(y1) // 70))
print(dl)

y = y1
print(len(y))

# Build the distance (x) axis from 0 to d_x mm, one entry per data point.
x1 = np.linspace(0, d_x, num=len(y1))
x = x1
print(x1[dl], "from this point the signal will start")   # prints ~30 mm here


# ─────────────────────────────────────────────────────────────────────────────
# 2. CROP TO THE REGION OF INTEREST
# ─────────────────────────────────────────────────────────────────────────────
# Keep only the part of the scan that contains the edge transition.
# Default: take the SECOND half (from dl onward).
# To analyse the FIRST half instead, swap to the two commented lines below.
# y = y1[:dl]; x = x1[:dl]      # first half
x = x1[dl:]   # second half (x)
y = y1[dl:]   # second half (y)

# --- Plot 1: raw knife-edge over the full scan ---
plt.plot(x1, y1)
plt.title("Raw knife-edge vs distance covered")
plt.xlabel('Step(mm)')
plt.ylabel('THz Amplitude(V)')
plt.show()

print(len(y))

# --- Plot 2: cropped region of interest ---
plt.plot(x, y)
plt.title("Cropped X-axis to region of interest")
plt.xlabel('Step(mm)')
plt.ylabel('THz Amplitude(V)')
plt.show()

# If the edge runs the other way, the curve may need flipping. Uncomment:
# y = np.flip(y)

plt.plot(x, y)
plt.title("Cropped signal (orientation check)")
plt.xlabel('Step(mm)')
plt.ylabel('THz Amplitude(V)')
plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# 3. OPTIONAL SMOOTHING (Savitzky-Golay)
# ─────────────────────────────────────────────────────────────────────────────
# Smooths noise while preserving the shape of the edge.
# Keep the window as small as possible so real features are not flattened.
window_size = 25      # must be odd; larger = smoother
poly_order = 2        # polynomial order fitted inside each window

print(f"the length of y is{len(y)}")
y_smooth = y
y_smooth = savgol_filter(y, window_size, poly_order)

# --- Plot 3: smoothed knife-edge ---
plt.plot(x, y_smooth, linewidth=2)
plt.title("Smoothed knife-edge (if required)")
plt.xlabel('Step(mm)')
plt.ylabel('THz Amplitude(V)')
plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# 4. DIFFERENTIATE -> BEAM PROFILE
# ─────────────────────────────────────────────────────────────────────────────
# The derivative of the edge response is the beam intensity profile (Gaussian).
dx = x[2] - x[1]                      # spacing between samples in mm
dy_dx = np.gradient(y, dx)            # derivative of the RAW signal
# dy_dx = np.gradient(y_smooth, dx)   # use this instead if smoothing is applied

# Sanity checks on the derivative.
print("Any NaNs?", np.isnan(dy_dx).any())
print("Any Infs?", np.isinf(dy_dx).any())
print("Indices with issues:", np.where(~np.isfinite(dy_dx)))

# --- Plot 4: edge curve (blue) and its derivative (green) ---
plt.plot(x, dy_dx, color='g', linewidth=2)
plt.plot(x, y_smooth, linewidth=2)
plt.title("Knife-edge and its derivative (dy/dx)")
plt.xlabel('Step(mm)')
plt.ylabel('THz Amplitude(V)')
plt.show()


# ─────────────────────────────────────────────────────────────────────────────
# 5. GAUSSIAN FIT AND FWHM  (do not change anything after this)
# ─────────────────────────────────────────────────────────────────────────────
# First guess for the fit: height, centre, width.
initial_guess = [max(dy_dx), np.mean(x), np.std(x)]
popt, pcov = curve_fit(gaussian, x[1:], dy_dx[1:], p0=initial_guess)
amplitude, mean, std_dev = popt

# Build a smooth fitted curve for display and FWHM measurement.
x_fit = np.linspace(min(x), max(x), len(x) * 2)
y_fit = gaussian(x_fit, max(dy_dx), mean, std_dev)
y_fit_max = max(abs(y_fit))

plt.plot(x_fit, y_fit, linewidth=2, color='b')

# Measure the FWHM of the fitted Gaussian = the THz beam diameter.
fwhm_h, r_i_h, l_i_h = find_fwhm(x_fit, y_fit)
print("FWHM Horizontal:", fwhm_h, l_i_h, r_i_h)

# Draw the half-maximum line and its end markers on the plot.
half_max = max(y_fit) / 2
plt.plot([x_fit[l_i_h], x_fit[r_i_h]], [half_max, half_max], color='red', linewidth=2)
plt.scatter([x_fit[l_i_h], x_fit[r_i_h]], [half_max, half_max], color='red')

# --- Plot 5: fitted Gaussian with FWHM annotation ---
plt.xlabel('Step(mm)')
plt.ylabel('THz Amplitude(V)')
plt.title(f"FWHM Analysis FWHM: {np.round(fwhm_h, 2)} mm")
plt.show()
