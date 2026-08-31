"""
===============================================================================
THz-Pathology Image Correlation Pipeline (KT Version)
===============================================================================
Author: Sidharth / KT Team
Description: 
    This script calculates the Pearson correlation coefficient between user-defined 
    Regions of Interest (ROIs) in Terahertz and Pathology images. 

Folder Structure & Setup:
    For this script to run immediately "out of the box", ensure the reference 
    input images are kept in the exact same folder as this script:
    
    📁 Correlation Coefficient/
    ├── 📄 thz_patho_correlation_pipeline.py  (This script)
    ├──  Sample input file
         ├── 🖼️ B011A_Path_Image.png               (Reference Pathology image)
         └── 🖼️ B011A_THz_Image.tif                (Reference THz image)

Workflow:
    1. Alignment: Loads both images and resizes the larger one to match the smaller.
    2. ROI Marking (THz): User draws Tumor (Red) and Normal (Blue) regions.
    3. ROI Marking (Patho): User draws corresponding Tumor and Normal regions.
    4. Mask Merging: Combines the red and blue regions for each image type.
    5. Correlation: Flattens the combined masks and computes Pearson's r.

Controls:
    - Left-Click + Drag: Draw a freehand boundary around the tissue.
    - Enter Key: Finalize the drawing and move to the next step.
===============================================================================
"""

import cv2
import numpy as np
from scipy.stats import pearsonr

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# Because the reference files are bundled in the same folder as this script, 
# we use relative paths. This ensures the script works on any computer without 
# needing to edit absolute paths (like C:\Users\...).

PATHO_IMAGE_PATH = r"C:\Sidharth\Start Python\KT Codes\CW\Correlation Coefficient\Sample input file\Path_Image.png"
THZ_IMAGE_PATH   = r"C:\Sidharth\Start Python\KT Codes\CW\Correlation Coefficient\Sample input file\THz Image.tif"


# ─────────────────────────────────────────────────────────────────────────────
# 1. IMAGE ALIGNMENT FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def resize_to_match(img_reference, img_to_resize):
    """
    Resizes an image to match the height and width of a reference image.
    
    Why: OpenCV's cv2.resize expects dimensions in (width, height) format, 
    but numpy shapes output as (height, width). This function safely maps them.
    """
    h, w = img_reference.shape[:2] # Extract height and width, ignore color channels
    return cv2.resize(img_to_resize, (w, h))


def align_images(patho_path, thz_path):
    """
    Loads both images and ensures they are exactly the same size.
    Rule: The larger image is ALWAYS downsized to match the smaller image to 
    prevent interpolation artifacts (creating fake pixel data).
    """
    # cv2.imread loads images as NumPy arrays in BGR (Blue, Green, Red) format
    patho = cv2.imread(patho_path)
    thz   = cv2.imread(thz_path)

    # Basic error handling to ensure file paths are correct
    if patho is None:
        raise FileNotFoundError(f"Could not read pathology image: '{patho_path}'. Ensure it is in the same folder as the script.")
    if thz is None:
        raise FileNotFoundError(f"Could not read THz image: '{thz_path}'. Ensure it is in the same folder as the script.")

    # Get dimensions (h = height, w = width)
    h1, w1 = patho.shape[:2]
    h2, w2 = thz.shape[:2]

    # Check if dimensions differ
    if (h1, w1) != (h2, w2):
        print(f"[INFO] Dimension mismatch — Patho: {w1}x{h1}, THz: {w2}x{h2}")
        
        # Calculate total pixels to determine which image is "smaller"
        if h1 * w1 <= h2 * w2:          
            # Pathology is smaller; shrink THz
            thz = resize_to_match(patho, thz)
            print(f"[INFO] THz resized to {w1}x{h1}")
        else:                            
            # THz is smaller; shrink Pathology
            patho = resize_to_match(thz, patho)
            print(f"[INFO] Patho resized to {w2}x{h2}")
    else:
        print(f"[INFO] Images already match: {w1}x{h1}")

    return patho, thz


# ─────────────────────────────────────────────────────────────────────────────
# 2. INTERACTIVE DRAWING CLASS
# ─────────────────────────────────────────────────────────────────────────────

class ROIDrawer:
    """
    Handles the interactive UI for drawing regions of interest (ROIs) on images.
    We use a Class here so it can maintain its own "state" (keeping track of 
    mouse clicks and coordinate points) while the user is actively drawing.
    """

    def __init__(self, image, window_title, color, label="region"):
        # .copy() is crucial here so we don't permanently ruin the original image
        self.canvas       = image.copy() 
        
        # Create a completely black image of the exact same size to act as our mask
        self.mask         = np.zeros_like(image) 
        
        self.title        = window_title
        self.color        = color
        self.label        = label
        
        # self.points holds every (x,y) coordinate the mouse passes over while drawing
        self.points       = []
        self.drawing      = False # Acts as an on/off switch for the mouse tracker

    def _mouse_callback(self, event, x, y, flags, param):
        """
        Listens to the mouse. Triggered continuously by OpenCV while the window is open.
        """
        # Event 1: User clicks and holds the left mouse button
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.points.append((x, y))

        # Event 2: User is dragging the mouse while holding the button
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.points.append((x, y))
            # Draw a line connecting the last point to the current point so the 
            # user can actually see what they are drawing on the screen.
            if len(self.points) >= 2:
                cv2.line(self.canvas, self.points[-2], self.points[-1], self.color, 2)

        # Event 3: User releases the left mouse button
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False

    def run(self):
        """
        Opens the window, tracks the drawing, and returns the final mathematical mask.
        """
        print(f"\n[DRAW] Draw the {self.label} region on '{self.title}'.")
        print("       Left-click + drag to draw  |  Enter = confirm")

        cv2.namedWindow(self.title)
        # Bind our custom mouse listening function to this specific window
        cv2.setMouseCallback(self.title, self._mouse_callback)

        # Infinite loop to keep the window open until the user presses Enter
        while True:
            cv2.imshow(self.title, self.canvas)
            key = cv2.waitKey(1) & 0xFF

            # 13 is the ASCII/keycode for the 'Enter' key
            if key == 13:          
                break

        # Clean up by closing the drawing window
        cv2.destroyWindow(self.title)

        # If the user actually drew something (needs at least 3 points for a shape)
        if len(self.points) >= 3:
            # Convert list of coordinates into a NumPy array required by OpenCV
            pts = np.array(self.points, dtype=np.int32)
            
            # This is the magic step: it takes the black mask we created in __init__
            # and fills the inside of the drawn shape with the chosen color.
            cv2.fillPoly(self.mask, [pts], self.color)
            print(f"[OK]  {self.label.capitalize()} mask created ({len(self.points)} points).")
        else:
            print(f"[WARN] Too few points for {self.label} — mask will be empty.")

        return self.mask


def draw_roi(image, window_title, color, label):
    """Helper function to cleanly instantiate and run the ROIDrawer class."""
    drawer = ROIDrawer(image, window_title, color, label)
    return drawer.run()


# ─────────────────────────────────────────────────────────────────────────────
# 3. MASK MERGING & STATISTICS
# ─────────────────────────────────────────────────────────────────────────────

def merge_masks(red_mask, blue_mask):
    """
    Takes the Tumor (red) mask and Normal (blue) mask and overlays them.
    cv2.addWeighted adds arrays together. The '1' means 100% opacity for both.
    """
    return cv2.addWeighted(red_mask, 1, blue_mask, 1, 0)


def compute_correlation(merged_thz, merged_patho):
    """
    Calculates the statistical correlation between the THz and Patho masks.
    """
    # .flatten() is required because pearsonr only works on 1-Dimensional arrays (lists).
    # It takes our 2D image matrix (e.g., 500x500) and turns it into a 1D array (250,000 items).
    arr1 = np.array(merged_thz,   dtype=np.float32).flatten()
    arr2 = np.array(merged_patho, dtype=np.float32).flatten()

    # Safety check: If arrays aren't the same length, correlation will crash.
    if len(arr1) != len(arr2):
        raise ValueError(
            f"Array length mismatch: THz has {len(arr1)}, Patho has {len(arr2)}. "
            "Alignment step failed."
        )

    # Calculate Pearson's r. 
    # r = correlation coefficient (-1 to 1)
    # p_value = probability that this correlation happened by chance (lower is better)
    r, p_value = pearsonr(arr1, arr2)
    return r, p_value


# ─────────────────────────────────────────────────────────────────────────────
# 4. MAIN EXECUTION PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(" THz–Pathology Correlation Pipeline")
    print("=" * 60)

    # ── Step 1: Align
    print("\n[STEP 1] Loading and aligning images …")
    patho_img, thz_img = align_images(PATHO_IMAGE_PATH, THZ_IMAGE_PATH)

    # ── Step 2 & 3: THz Processing
    print("\n[STEP 2] THz image — mark TUMOUR region (red)")
    # OpenCV uses BGR, so Red is (0, 0, 255)
    red_mask_thz = draw_roi(thz_img, "THz | Tumour Region (Red)", (0, 0, 255), "tumour (THz)")

    print("\n[STEP 3] THz image — mark NORMAL tissue region (blue)")
    # OpenCV uses BGR, so Blue is (255, 0, 0)
    blue_mask_thz = draw_roi(thz_img, "THz | Normal Region (Blue)", (255, 0, 0), "normal tissue (THz)")

    merged_thz = merge_masks(red_mask_thz, blue_mask_thz)

    # ── Step 4 & 5: Pathology Processing
    print("\n[STEP 4] Pathology image — mark TUMOUR region (red)")
    red_mask_patho = draw_roi(patho_img, "Patho | Tumour Region (Red)", (0, 0, 255), "tumour (Patho)")

    print("\n[STEP 5] Pathology image — mark NORMAL tissue region (blue)")
    blue_mask_patho = draw_roi(patho_img, "Patho | Normal Region (Blue)", (255, 0, 0), "normal tissue (Patho)")

    merged_patho = merge_masks(red_mask_patho, blue_mask_patho)

    # ── Step 6: Compute Final Statistics
    print("\n[STEP 6] Computing Pearson correlation …")
    r, p = compute_correlation(merged_thz, merged_patho)

    # ── Display Results
    print("\n" + "=" * 60)
    print(f"  Pearson r   = {r:.4f}")
    print(f"  p-value     = {p:.4e}")
    
    # Simple logic to convert the math into a human-readable interpretation
    if abs(r) >= 0.7:
        strength = "strong"
    elif abs(r) >= 0.4:
        strength = "moderate"
    else:
        strength = "weak"
    
    direction = "positive" if r >= 0 else "negative"
    print(f"  Interpretation: {strength} {direction} correlation")
    print("=" * 60)

    # ── Optional Visual Confirmation
    # hstack places the two final masks side-by-side for a quick visual sanity check
    preview = np.hstack([merged_thz, merged_patho])
    cv2.imshow("Merged THz  (left)  vs  Merged Patho  (right)", preview)
    print("\nPress any key to close preview and exit.")
    
    cv2.waitKey(0)             # Wait infinitely for any key press
    cv2.destroyAllWindows()    # Cleanly close all remaining OpenCV windows
    print("[DONE]")


# Standard Python paradigm to ensure main() only runs if the script is executed directly
if __name__ == "__main__":
    main()