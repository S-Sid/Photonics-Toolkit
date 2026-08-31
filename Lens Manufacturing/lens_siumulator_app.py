import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math

def biconcave(R1, R2, T, n, d, ax, f, F1_x, F2_x, FFL, BFL):
    theta_1 = np.linspace((np.pi/4), -1 * (np.pi/4), 100000)
    x_1 = np.abs(R1) * np.cos(theta_1)
    y_1 = np.abs(R1) * np.sin(theta_1)

    theta_2 = np.linspace(3*(np.pi/4),5*(np.pi/4), 100000)
    x_2 = np.abs(R2) * np.cos(theta_2)
    y_2 = np.abs(R2) * np.sin(theta_2)
    
    x1_p = [y + (R1 - (T/2)) for y in x_1]
    C1 = R1 - (T/2)  # Fixed C1
    x2_p = [x + (R2 + (T/2)) for x in x_2]
    C2 = R2 + (T/2)  # Fixed C2

    y_p =  d/2
    y_n = -d/2

    mask_1 = (y_1 >= y_n) & (y_1 <= y_p)
    mask_2 = (y_2 >= y_n) & (y_2 <= y_p)
    
    x1_p = np.array(x1_p)
    y_1 = np.array(y_1)
    x2_p = np.array(x2_p)
    y_2 = np.array(y_2)

    x_1_max = np.min(x1_p[mask_1])
    x_2_max = np.max(x2_p[mask_2])

    y_1_max = np.max(y_1[mask_1])
    y_1_min = np.min(y_1[mask_1])

    y_2_max = np.max(y_2[mask_2])
    y_2_min = np.min(y_2[mask_2])

    x_left = x1_p[mask_1]
    y_left = y_1[mask_1]
    x_right_rev = x2_p[mask_2][::-1]
    y_right_rev = y_2[mask_2][::-1]

    x_poly = np.concatenate([x_left, x_right_rev])
    y_poly = np.concatenate([y_left, y_right_rev])
    
    ax.axhline(0, color='black', linewidth=1)
    ax.plot(x1_p[mask_1], y_1[mask_1], label='R1', color='k')
    ax.plot(x2_p[mask_2], y_2[mask_2], label='R2', color='k')
    ax.plot([x_1_max, x_2_max], [y_1_max, y_2_max], color='k')
    ax.plot([x_1_max, x_2_max], [y_1_min, y_2_min], color='k')
    ax.fill(x_poly, y_poly, color='lightblue', alpha=0.5, label='Glass')
    
    if f != float('inf'):
        ax.scatter(F1_x, 0, color="red", label=f"F1 (FFL: {FFL:.1f}mm)", zorder=3)
        ax.scatter(F2_x, 0, color="blue", label=f"F2 (BFL: {BFL:.1f}mm)", zorder=3)
    ax.scatter(C1, 0, color="green", label="C1 (Center of R1)", zorder=3)
    ax.scatter(C2, 0, color="orange", label="C2 (Center of R2)", zorder=3)
    
    ax.set_title(f"Biconcave Lens Simulation: f={f:.2f}mm and Refractive index : {n}")

def biconvex(R1, R2, T, n, d, ax, f, F1_x, F2_x, FFL, BFL):
    theta_1 = np.linspace((np.pi/4), -1 * (np.pi/4), 100000)
    x_1 = np.abs(R1) * np.cos(theta_1)
    y_1 = np.abs(R1) * np.sin(theta_1)

    theta_2 = np.linspace(3*(np.pi/4), 5*(np.pi/4), 100000)
    x_2 = np.abs(R2) * np.cos(theta_2)
    y_2 = np.abs(R2) * np.sin(theta_2)

    # Fixed shift math to prevent mirroring
    x1_p = [-y + (R1 - (T/2)) for y in x_1] 
    x2_p = [-x + (R2 + (T/2)) for x in x_2]

    C1 = R1 - (T/2)  # Fixed C1
    C2 = R2 + (T/2)  # Fixed C2

    x1_p = np.array(x1_p)
    x2_p = np.array(x2_p)

    # Replaced complex masking with your standard d/2 bounds
    mask_1 = (y_1 >= -d/2) & (y_1 <= d/2)
    mask_2 = (y_2 >= -d/2) & (y_2 <= d/2)
    
    x1_1, y1_1 = x1_p[mask_1], y_1[mask_1]
    x2_1, y2_1 = x2_p[mask_2], y_2[mask_2]

    x_left = x1_1
    y_left = y1_1
    x_right_rev = x2_1[::-1]
    y_right_rev = y2_1[::-1]

    x_poly = np.concatenate([x_left, x_right_rev])
    y_poly = np.concatenate([y_left, y_right_rev])

    ax.axhline(0, color='black', linewidth=1)
    ax.fill(x_poly, y_poly, color='lightblue', alpha=0.5, label='Glass')
    
    if f != float('inf'):
        ax.scatter(F1_x, 0, color="red", label=f"F1 (FFL: {FFL:.1f}mm)", zorder=3)
        ax.scatter(F2_x, 0, color="blue", label=f"F2 (BFL: {BFL:.1f}mm)", zorder=3)
    ax.scatter(C1, 0, color="green", label="C1 (Center of R1)", zorder=3)
    ax.scatter(C2, 0, color="orange", label="C2 (Center of R2)", zorder=3)

    # Flat edges
    y_top = np.max(y1_1)
    y_bot = np.min(y1_1)
    x_top_1 = x1_1[np.argmax(y1_1)]
    x_top_2 = x2_1[np.argmax(y2_1)]
    x_bot_1 = x1_1[np.argmin(y1_1)]
    x_bot_2 = x2_1[np.argmin(y2_1)]

    ax.plot([x_top_1, x_top_2], [y_top, y_top], color="k")
    ax.plot([x_bot_1, x_bot_2], [y_bot, y_bot], color="k")
    ax.plot(x1_1, y1_1, color="k")
    ax.plot(x2_1, y2_1, color="k")

    ax.set_title(f"Biconvex Lens Simulation: f={f:.2f}mm Refractive index {n}")

def planoconcave(R1, R2, T, n, d, ax, f, F1_x, F2_x, FFL, BFL):
    if R1 != 0:
        theta_1 = np.linspace((np.pi/4), -1 * (np.pi/4), 100000)
        # The coordinates for building the arc 
        x_1 = np.abs(R1) * np.cos(theta_1)
        y_1 = np.abs(R1) * np.sin(theta_1)
    
        x1_p = [y + (R1 - (T/2)) for y in x_1]
        C1 = R1 + (T/2)
    
        y2_p = np.linspace(-d/2, d/2, 100)
        x2_p = np.full_like(y2_p, T/2)
    
        x1_p = np.array(x1_p)
        y_1 = np.array(y_1)
    
        mask_1 = (y_1 >= -d/2) & (y_1 <= d/2)
    
        x_1_max = np.min(x1_p[mask_1])
        y_1_max = np.max(y_1[mask_1])
        y_1_min = np.min(y_1[mask_1])
    
        # 1. Prepare data for the fill. We need to create a closed loop.
        # Left side of the lens (Surface 1)
        x_left = x1_p[mask_1]
        y_left = y_1[mask_1]
    
        # Concatenate them to form a single polygon
        x_poly = np.concatenate([x_left, [T/2, T/2]])
        y_poly = np.concatenate([y_left, [-d/2, d/2]])

        ax.axhline(0, color='black', linewidth=1)
        ax.plot(x1_p[mask_1], y_1[mask_1], label='R1', color='k')
        ax.plot(x2_p, y2_p, label='R2',color = 'k')
        ax.plot([x_1_max, T/2], [y_1_max, d/2], color='k')
        ax.plot([x_1_max, T/2], [y_1_min, -d/2], color='k')
        ax.fill(x_poly, y_poly, color='lightblue', alpha=0.5, label='Glass')
        
        if f != float('inf'):
            ax.scatter(F1_x, 0, color="red", label=f"F1 (FFL: {FFL:.1f}mm)", zorder=3)
            ax.scatter(F2_x, 0, color="blue", label=f"F2 (BFL: {BFL:.1f}mm)", zorder=3)
        ax.scatter(C1, 0, color="green", label="C1 (Center of R1)", zorder=3)
        ax.set_title(f"Planoconcave Lens Simulation: f={f:.2f}mm and Refractive Index: {n}")

    elif R2 != 0:
        theta_2 = np.linspace(3*(np.pi/4), 5*(np.pi/4), 100000)
        # The coordinates for building the arc 
        x_2 = np.abs(R2) * np.cos(theta_2)
        y_2 = np.abs(R2) * np.sin(theta_2)
    
        # Fix 1: Convert the list comprehension directly into a NumPy array
        x2_p = np.array([x + (R2 + (T/2)) for x in x_2])
        C2 = R2 - (T/2)
    
        y1_p = np.linspace(-d/2, d/2, 100)
        x1_p = np.full_like(y1_p, -T/2)
    
        # I REMOVED the two lines here that were overwriting x1_p and y_1!
        # They were causing your max/min calculations below to grab the wrong data.
    
        mask_2 = (y_2 >= -d/2) & (y_2 <= d/2)
    
        # Fix 2: Updated these to pull from the correct arrays (x2_p and y_2)
        x_2_max = np.max(x2_p[mask_2]) 
        y_2_max = np.max(y_2[mask_2])
        y_2_min = np.min(y_2[mask_2])
    
        # Prepare data for the fill
        x_right = x2_p[mask_2]
        y_right = y_2[mask_2]
    
        # Concatenate them to form a single polygon
        x_poly = np.concatenate([x_right, [-T/2, -T/2]])
        y_poly = np.concatenate([y_right, [-d/2, d/2]])

        ax.axhline(0, color='black', linewidth=1)
        ax.plot(x2_p[mask_2], y_2[mask_2], label='R2', color='k')
        ax.plot(x1_p, y1_p, label='R1', color="k")
        ax.plot([x_2_max, -T/2], [y_2_max, d/2], color='k')
        ax.plot([x_2_max, -T/2], [y_2_min, -d/2], color='k')
        ax.fill(x_poly, y_poly, color='lightblue', alpha=0.5, label='Glass (N-BK7)')
        
        if f != float('inf'):
            ax.scatter(F1_x, 0, color="red", label=f"F1 (FFL: {FFL:.1f}mm)", zorder=3)
            ax.scatter(F2_x, 0, color="blue", label=f"F2 (BFL: {BFL:.1f}mm)", zorder=3)
        ax.scatter(C2, 0, color="green", label="C2 (Center of R2)", zorder=3)
        ax.set_title(f"Planoconcave Lens Simulation: f={f:.2f}mm and Refractive Index: {n}")

def planoconvex(R1, R2, T, n, d, ax, f, F1_x, F2_x, FFL, BFL):
    if R1 != 0:
        theta_1 = np.linspace((np.pi/4), -1 * (np.pi/4), 100000)
        # The coordinates for building the arc 
        x_1 = np.abs(R1) * np.cos(theta_1)
        y_1 = np.abs(R1) * np.sin(theta_1)
    
        x1_p = [-y + (R1 - (T/2)) for y in x_1]
        C1 = R1 + (T/2)
    
        y2_p = np.linspace(-d/2, d/2, 100)
        x2_p = np.full_like(y2_p, T/2)
    
        x1_p = np.array(x1_p)
        y_1 = np.array(y_1)
    
        mask_1 = (y_1 >= -d/2) & (y_1 <= d/2)
    
        x_1_max = np.max((x1_p[mask_1]))
    
        y_1_max = np.max(y_1[mask_1])
        y_1_min = np.min(y_1[mask_1])
    
        # 1. Prepare data for the fill. We need to create a closed loop.
        # Left side of the lens (Surface 1)
        x_left = x1_p[mask_1]
        y_left = y_1[mask_1]
    
        # Concatenate them to form a single polygon
        x_poly = np.concatenate([x_left, [T/2, T/2]])
        y_poly = np.concatenate([y_left, [-d/2, d/2]])

        ax.axhline(0, color='black', linewidth=1)
        ax.plot(x1_p[mask_1], y_1[mask_1], label='R1', color='k')
        ax.plot(x2_p, y2_p, color='k')
        ax.fill(x_poly, y_poly, color='lightblue', alpha=0.5, label='Glass')
        
        if f != float('inf'):
            ax.scatter(F1_x, 0, color="red", label=f"F1 (FFL: {FFL:.1f}mm)", zorder=3)
            ax.scatter(F2_x, 0, color="blue", label=f"F2 (BFL: {BFL:.1f}mm)", zorder=3)
        ax.scatter(C1, 0, color="green", label="C1 (Center of R1)", zorder=3)

        ax.plot([x_1_max, T/2], [y_1_max, d/2], color="k")
        ax.plot([x_1_max, T/2], [y_1_min, -d/2], color="k")
        ax.set_title(f"Planoconvex Lens Simulation: f={f:.2f}mm")

    elif R2 != 0:
        theta_2 = np.linspace(3*(np.pi/4), 5*(np.pi/4), 100000)
        # The coordinates for building the arc 
        x_2 = np.abs(R2) * np.cos(theta_2)
        y_2 = np.abs(R2) * np.sin(theta_2)
    
        # Fix 1: Convert the list comprehension directly into a NumPy array
        x2_p = np.array([-x + (R2 + (T/2)) for x in x_2])
        C2 = R2 - (T/2)
    
        y1_p = np.linspace(-d/2, d/2, 100)
        x1_p = np.full_like(y1_p, -T/2)
    
        # I REMOVED the two lines here that were overwriting x1_p and y_1!
        # They were causing your max/min calculations below to grab the wrong data.
    
        mask_2 = (y_2 >= -d/2) & (y_2 <= d/2)
    
        # Fix 2: Updated these to pull from the correct arrays (x2_p and y_2)
        x_2_max = np.min(x2_p[mask_2]) 
    
        y_2_max = np.max(y_2[mask_2])
        y_2_min = np.min(y_2[mask_2])
    
        # Prepare data for the fill
        x_right = x2_p[mask_2]
        y_right = y_2[mask_2]
    
        # Concatenate them to form a single polygon
        x_poly = np.concatenate([x_right, [-T/2, -T/2]])
        y_poly = np.concatenate([y_right, [-d/2, d/2]])

        ax.axhline(0, color='black', linewidth=1)
        ax.plot(x2_p[mask_2], y_2[mask_2], label='R2', color='k')
        ax.plot(x1_p, y1_p, color='k')
        ax.fill(x_poly, y_poly, color='lightblue', alpha=0.5, label='Glass (N-BK7)')
        
        if f != float('inf'):
            ax.scatter(F1_x, 0, color="red", label=f"F1 (FFL: {FFL:.1f}mm)", zorder=3)
            ax.scatter(F2_x, 0, color="blue", label=f"F2 (BFL: {BFL:.1f}mm)", zorder=3)
        ax.scatter(C2, 0, color="green", label="C2 (Center of R2)", zorder=3)

        ax.plot([x_2_max, -T/2], [y_2_max, d/2], color="k")
        ax.plot([x_2_max, -T/2], [y_2_min, -d/2], color="k")
        ax.set_title(f"Planoconvex Lens Simulation: f={f:.2f}mm")


# --- GUI Application Class ---
class LensSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lens Geometry Simulator")
        
        # Left Panel for Inputs
        control_frame = ttk.Frame(root, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(control_frame, text="Radius 1 (R1):").pack(anchor=tk.W, pady=2)
        self.r1_var = tk.StringVar(value="50")
        ttk.Entry(control_frame, textvariable=self.r1_var).pack(fill=tk.X, pady=2)
        
        ttk.Label(control_frame, text="Radius 2 (R2):").pack(anchor=tk.W, pady=2)
        self.r2_var = tk.StringVar(value="-50")
        ttk.Entry(control_frame, textvariable=self.r2_var).pack(fill=tk.X, pady=2)
        
        ttk.Label(control_frame, text="Thickness (T):").pack(anchor=tk.W, pady=2)
        self.t_var = tk.StringVar(value="10")
        ttk.Entry(control_frame, textvariable=self.t_var).pack(fill=tk.X, pady=2)
        
        ttk.Label(control_frame, text="Refractive Index (n):").pack(anchor=tk.W, pady=2)
        self.n_var = tk.StringVar(value="1.517")
        ttk.Entry(control_frame, textvariable=self.n_var).pack(fill=tk.X, pady=2)
        
        ttk.Label(control_frame, text="Diameter (d):").pack(anchor=tk.W, pady=2)
        self.d_var = tk.StringVar(value=str(1.5 * 25.4))
        ttk.Entry(control_frame, textvariable=self.d_var).pack(fill=tk.X, pady=2)
        
        ttk.Button(control_frame, text="Draw Lens", command=self.update_plot).pack(fill=tk.X, pady=20)
        
        # Right Panel for Matplotlib Plot
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Initial draw
        self.update_plot()

    def update_plot(self):
        try:
            R1 = float(self.r1_var.get())
            R2 = float(self.r2_var.get())
            T = float(self.t_var.get())
            n = float(self.n_var.get())
            d = float(self.d_var.get())
        except ValueError:
            return  # Ignore invalid string inputs
            
        self.ax.clear()
        
        # Original Logic Block
        lens = "meniscus"
        if R1 >= 0 and R2 <= 0:
            lens = "biconvex"
        elif R1 <= 0 and R2 >= 0:
            lens = "biconcave"

        if R1 == 0 or R2 == 0:
            if lens == "biconcave" or lens == "meniscus":
                lens = "planoconcave"
            elif lens == "biconvex":
                lens = "planoconvex"

        issue = "fine"

        if lens in ["biconcave", "biconvex"]:
            try:
                S_1 = np.abs(R1) - (R1**2 - (d/2)**2) ** (1/2)
                S_2 = np.abs(R2) - (R2**2 - (d/2)**2) ** (1/2)
                E_t = T - (S_1+S_2)
                if (E_t < 1.5):
                    issue = "Sag Error: Edge Thickness < 1.5mm"
                if d > 2*np.abs(R1) and d > 2*np.abs(R2):
                    issue = "Hemisphere Limit Exceeded"
            except RuntimeWarning:
                issue = "Math Error: d/2 > Radius"

        elif lens in ["planoconcave", "planoconvex"]:
            R = R1 if R1 != 0 else R2
            try:
                S = np.abs(R) - (R**2 - (d/2)**2) ** (1/2)
                E_t = T-S
                if (E_t < 0):
                    issue = "Sag Error: Invalid Edge Thickness"
                if d > 2*np.abs(R):
                    issue = "Hemisphere Limit Exceeded"
            except RuntimeWarning:
                issue = "Math Error: d/2 > Radius"

        # Calculate Focal Length and True Focal Points
        try:
            inv_R1 = 1 / R1 if R1 != 0 else 0
            inv_R2 = 1 / R2 if R2 != 0 else 0
            inv_f = (n - 1) * (inv_R1 - inv_R2 + ((n - 1) * T * inv_R1 * inv_R2) / n)
            f = 1 / inv_f if inv_f != 0 else float('inf')
        except ZeroDivisionError:
            f = float('inf')

        # Calculate Front and Back Focal Points based on Principal Planes
        if f != float('inf'):
            D1 = -(f * (n - 1) * T * inv_R2) / n if R2 != 0 else 0
            D2 = -(f * (n - 1) * T * inv_R1) / n if R1 != 0 else 0
            H1_x = -T/2 + D1
            H2_x = T/2 + D2
            F1_x = H1_x - f
            F2_x = H2_x + f
            FFL = abs(-T/2 - F1_x)
            BFL = abs(F2_x - T/2)
        else:
            F1_x = F2_x = FFL = BFL = 0

        # Draw logic wrapper
        try:
            if lens == "biconcave":
                biconcave(R1, R2, T, n, d, self.ax, f, F1_x, F2_x, FFL, BFL)
            elif lens == "biconvex":
                biconvex(R1, R2, T, n, d, self.ax, f, F1_x, F2_x, FFL, BFL)
            elif lens == "planoconcave":
                planoconcave(R1, R2, T, n, d, self.ax, f, F1_x, F2_x, FFL, BFL)
            elif lens == "planoconvex":
                planoconvex(R1, R2, T, n, d, self.ax, f, F1_x, F2_x, FFL, BFL)
        except Exception as e:
            pass 

        # Formatting
        self.ax.set_xlabel("Optical Axis (mm)")
        self.ax.set_ylabel("Radial Height (mm)")
        self.ax.legend(loc="upper right", fontsize='small')
        self.ax.grid(True, linestyle=':', alpha=0.6)
        
        # Display Issue on the plot if one exists
        if issue != "fine":
            self.ax.text(0.5, 0.5, f"WARNING: {issue}\nLens cannot be manufactured.", 
                         transform=self.ax.transAxes, color='red', fontsize=14, 
                         fontweight='bold', ha='center', va='center', 
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='red', boxstyle='round,pad=1'))

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = LensSimulatorApp(root)
    root.mainloop()