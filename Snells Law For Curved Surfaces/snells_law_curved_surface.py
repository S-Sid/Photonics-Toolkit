import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class OpticsSimApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Concave & Convex Surface Optics Simulator")
        self.root.geometry("900x650")
        
        self.create_sidebar()
        self.create_canvas()
        
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, width=250, bg="#0E0D0D", padx=10, pady=10)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Surface Type
        tk.Label(sidebar, text="Surface Type:", bg="#0E0D0D", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        self.surface_var = tk.StringVar(value="Concave")
        surface_combo = ttk.Combobox(sidebar, textvariable=self.surface_var, values=["Concave", "Convex"], state="readonly")
        surface_combo.pack(fill=tk.X, pady=5)
        surface_combo.bind("<<ComboboxSelected>>", self.on_surface_change)
        
        # Radius (r)
        tk.Label(sidebar, text="Radius (r):", bg="#0E0D0D").pack(anchor=tk.W, pady=(10, 0))
        self.r_var = tk.DoubleVar(value=5.0)
        tk.Entry(sidebar, textvariable=self.r_var).pack(fill=tk.X)
        
        # Object Position (x_o) relative to principal point (0,0)
        tk.Label(sidebar, text="Object Position (x_o):", bg="#0E0D0D").pack(anchor=tk.W, pady=(10, 0))
        self.xo_var = tk.DoubleVar(value=-3.0)
        tk.Entry(sidebar, textvariable=self.xo_var).pack(fill=tk.X)
        
        # Refractive Index 1 (n1)
        tk.Label(sidebar, text="Refractive Index 1 (n1):", bg="#0E0D0D").pack(anchor=tk.W, pady=(10, 0))
        self.n1_var = tk.DoubleVar(value=1.33)
        tk.Entry(sidebar, textvariable=self.n1_var).pack(fill=tk.X)
        
        # Refractive Index 2 (n2)
        tk.Label(sidebar, text="Refractive Index 2 (n2):", bg="#0E0D0D").pack(anchor=tk.W, pady=(10, 0))
        self.n2_var = tk.DoubleVar(value=1.0)
        tk.Entry(sidebar, textvariable=self.n2_var).pack(fill=tk.X)
        
        # Incident Angle (a_i)
        tk.Label(sidebar, text="Incident Angle (a_i in °):", bg="#0E0D0D").pack(anchor=tk.W, pady=(10, 0))
        self.ai_var = tk.DoubleVar(value=25.0)
        tk.Entry(sidebar, textvariable=self.ai_var).pack(fill=tk.X)
        
        # Plot Button
        ttk.Button(sidebar, text="Calculate & Plot", command=self.plot_rays).pack(fill=tk.X, pady=20)
        
    def create_canvas(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.plot_rays() # Initial plot

    def on_surface_change(self, event):
        # Update defaults based on surface selection
        if self.surface_var.get() == "Concave":
            self.r_var.set(5.0)
            self.xo_var.set(-3.0) 
        else:
            self.r_var.set(9.0)
            self.xo_var.set(-4.0) 

    def plot_rays(self):
        self.ax.clear()
        
        try:
            r = self.r_var.get()
            x_o_input = self.xo_var.get() # Object relative to Principal Point (0,0)
            n1 = self.n1_var.get()
            n2 = self.n2_var.get()
            a_i = self.ai_var.get()
            surface = self.surface_var.get()
        except tk.TclError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
            return

        m_i = np.tan(np.deg2rad(a_i))
        
        if surface == "Convex":
            # Map into math space where Center is (0,0)
            x_o = x_o_input - r 
            c = -1 * m_i * x_o
            
            # 135 to 225 degree arc
            theta = np.linspace(3*(np.pi/4), 5*(np.pi/4), 100)
            x_arc = r * np.cos(theta)
            y_arc = r * np.sin(theta)
            
            x1 = r * np.cos(np.pi)
            x_i_arr = np.linspace(x_o, x1 + 5, num=50000)
            y_i_arr = m_i * x_i_arr + c
            
            mask = x_i_arr**2 + y_i_arr**2 >= r**2
            x_i = x_i_arr[mask]
            y_i = y_i_arr[mask]
            
            if len(x_i) == 0:
                messagebox.showwarning("Warning", "Ray does not intersect the surface!")
                return
                
            x_hit, y_hit = x_i[-1], y_i[-1]
            
            m_c = (0 - y_hit) / (0 - x_hit) if x_hit != 0 else 0
            x_c = np.linspace(0, x_hit - 1, 1000)
            y_c = m_c * x_c
            
            angle_i = np.deg2rad(np.abs(np.rad2deg(np.arctan(m_i))) + np.abs(np.rad2deg(np.arctan(m_c))))
            
            try:
                angle_r = np.arcsin((n1/n2) * np.sin(angle_i))
            except RuntimeWarning:
                messagebox.showerror("Error", "Total Internal Reflection occurred!")
                return
                
            m_r_angle = np.rad2deg(angle_r) + np.rad2deg(np.arctan(m_c))
            m_r = np.tan(np.deg2rad(m_r_angle))
            
            x_r = np.linspace(x_hit, x_hit + 2, 1000)
            y_r = m_r * (x_r - x_hit) + y_hit
            
            # Shift coordinates for plotting so Principal Point is at 0
            x_arc_plot = x_arc + r
            x_i_plot = x_i + r
            x_c_plot = x_c + r
            x_r_plot = x_r + r
            x_hit_plot = x_hit + r
            cx, cy = r, 0
            
            self.ax.plot(x_arc_plot, y_arc, color='k')
            self.ax.plot(x_i_plot, y_i, color='r', linewidth=2, label="Incident Ray")
            self.ax.plot(x_c_plot, y_c, color='k', linewidth=2, label="Normal", linestyle='--')
            self.ax.plot(x_r_plot, y_r, color='b', label="Refracted Ray")
            
            self.ax.text(x_o_input, 1.8, f"n1 = {n1}", fontsize=12, fontweight='bold')
            self.ax.text(r, -1.8, f"n2 = {n2}", fontsize=12, fontweight='bold')
            
            self.ax.annotate(rf'$\theta_i = {np.rad2deg(angle_i):.1f}^\circ$',
                             (x_hit_plot, y_hit), textcoords="offset points", xytext=(-70, -25))
            
        else: # Convex
            # Map into math space where Center is (0,0)
            x_o = x_o_input + r 
            c = -1 * m_i * x_o
            
            # -60 to 60 degree arc
            theta = np.linspace(-np.pi/3, np.pi/3, 100)
            x_arc = r * np.cos(theta)
            y_arc = r * np.sin(theta)
            
            x1 = r * np.cos(0)
            x_i_arr = np.linspace(x_o, x1, num=50000)
            y_i_arr = m_i * x_i_arr + c
            
            mask = x_i_arr**2 + y_i_arr**2 <= r**2
            x_i = x_i_arr[mask]
            y_i = y_i_arr[mask]
            
            if len(x_i) == 0:
                messagebox.showwarning("Warning", "Ray does not intersect the surface!")
                return
                
            x_hit, y_hit = x_i[-1], y_i[-1]
            
            m_c = (y_hit - 0) / (x_hit - 0) if x_hit != 0 else 0
            x_c = np.linspace(0, x_hit + 3, 1000)
            y_c = m_c * x_c
            
            angle_i = np.arctan(m_i) - np.arctan(m_c)
            
            try:
                angle_r = np.arcsin((n1/n2) * np.sin(angle_i))
            except RuntimeWarning:
                messagebox.showerror("Error", "Total Internal Reflection occurred!")
                return
                
            m_r_angle = np.rad2deg(angle_r) + np.rad2deg(np.arctan(m_c))
            m_r = np.tan(np.deg2rad(m_r_angle))
            
            x_r = np.linspace(x_hit, x_hit + 5, 1000)
            y_r = m_r * (x_r - x_hit) + y_hit
            
            # Shift coordinates for plotting so Principal Point is at 0
            x_arc_plot = x_arc - r
            x_i_plot = x_i - r
            x_c_plot = x_c - r
            x_r_plot = x_r - r
            x_hit_plot = x_hit - r
            cx, cy = -r, 0
            
            self.ax.plot(x_arc_plot, y_arc, color='k')
            self.ax.plot(x_i_plot, y_i, color='y', linewidth=2, label="Incident Ray")
            self.ax.plot(x_c_plot, y_c, color='k', linewidth=2, label="Normal", linestyle='--')
            self.ax.plot(x_r_plot, y_r, color='b', label="Refracted Ray")
            
            self.ax.text(x_o_input, 1.8, f"n1 = {n1}", fontsize=12, fontweight='bold')
            self.ax.text(3, -1.8, f"n2 = {n2}", fontsize=12, fontweight='bold')
            
            self.ax.annotate(rf'$\theta_i = {np.rad2deg(angle_i):.1f}^\circ$',
                             (x_hit_plot, y_hit), textcoords="offset points", xytext=(-70, -25))
            self.ax.annotate(rf'$\theta_r = {np.rad2deg(angle_r):.1f}^\circ$',
                             (x_hit_plot, y_hit), textcoords="offset points", xytext=(25, 20))

        # Common Plot Settings
        self.ax.axhline(0, color='black', linewidth=1)
        
        # Center of Curvature (C)
        self.ax.scatter(cx, cy, color='k', linewidth=3)
        self.ax.annotate('C', (cx, cy), textcoords="offset points", xytext=(0, -15), ha='center')
        
        # Object (O)
        self.ax.scatter(x_o_input, 0, color='r', linewidth=3)
        self.ax.annotate('O', (x_o_input, 0), textcoords="offset points", xytext=(0, -15), ha='center')

        # Principal Point / Vertex (V) at Origin (0,0)
        # self.ax.scatter(0, 0, color='green', linewidth=3, zorder=5)
        # # self.ax.annotate('V(0,0)', (0, 0), textcoords="offset points", xytext=(0, 10), ha='center', color='green', fontweight='bold')
        
        self.ax.set_aspect('equal', adjustable='datalim')
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.ax.legend(loc="lower left")
        
        # Dynamic Limits based on Radius and Object position
        min_x = min(x_o_input, cx) - 2
        max_x = max(x_o_input, cx) + 5
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(-r - 1, r + 1)
            
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("error", category=RuntimeWarning) # Catch numpy arcsin domain errors
    
    root = tk.Tk()
    app = OpticsSimApp(root)
    root.mainloop()