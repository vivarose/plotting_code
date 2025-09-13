"""
Viva R. Horowitz
vibe-coded with Google Gemini
2025-09-13

Simple GUI plotting software with linear fitting.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
try:
    # Scipy is needed for detailed linear regression stats
    from scipy.stats import linregress
except ImportError:
    linregress = None # Set to None if not available

class DataPlotterApp(tk.Tk):
    """
    A GUI application for plotting data with uncertainties.
    Users can paste data from spreadsheets, select X and Y axes,
    assign uncertainty columns, and generate a plot.
    """
    def __init__(self):
        super().__init__()
        self.title("Hamilton Plotter")
        self.geometry("1200x800")

        # 1. Maximize window on startup
        try:
            self.state('zoomed')
        except tk.TclError:
            # Fallback for some Linux environments that prefer this
            self.attributes('-zoomed', True)

        # --- Data Storage ---
        self.df = None
        self.x_axis_var = tk.StringVar()
        self.x_error_var = tk.StringVar()
        self.y_axis_vars = {}
        self.y_error_vars = {}
        
        # --- Sample Data Sets ---
        self.sample_data_sets = {
            "Linear Motion": (
                "# Data for an object with constant acceleration.\n"
                "# Plot Position, Velocity, and/or Acceleration vs. Time.\n"
                "Time (s)\tTime Uncertainty (s)\tPosition (m)\tPos Uncertainty (m)\tVelocity (m/s)\tVel Uncertainty (m/s)\tAcceleration (m/s^2)\tAccel Uncertainty (m/s^2)\n"
                "0.0\t0.02\t0.0\t0.2\t0.0\t0.5\t9.8\t0.4\n"
                "1.0\t0.02\t4.9\t0.2\t9.8\t0.5\t9.8\t0.4\n"
                "2.0\t0.02\t19.5\t0.3\t19.6\t0.6\t9.8\t0.4\n"
                "3.0\t0.02\t44.0\t0.3\t29.4\t0.6\t9.8\t0.4\n"
                "4.0\t0.02\t78.5\t0.4\t39.2\t0.7\t9.8\t0.4\n"
            ),
            "Biology (Plant Growth)": (
                "# Height of a plant over time under constant light.\n"
                "Day\tDay Uncertainty\tHeight (cm)\tHeight Uncertainty (cm)\n"
                "1\t0.5\t2.1\t0.2\n"
                "3\t0.5\t4.3\t0.2\n"
                "5\t0.5\t6.0\t0.3\n"
                "7\t0.5\t8.2\t0.3\n"
                "9\t0.5\t9.8\t0.3\n"
            ),
            "Psychology (Hick's Law)": (
                "# Reaction time increases with the number of choices (Hick's Law).\n"
                "# 'Bits' is calculated as log2(number_of_choices).\n"
                "Bits of Information\tBits Uncertainty\tReaction Time (ms)\tRT Uncertainty (ms)\n"
                "1\t0\t320\t15\n"
                "2\t0\t460\t20\n"
                "3\t0\t590\t22\n"
                "4\t0\t710\t25\n"
                "5\t0\t880\t30\n"
            ),
            "Neuroscience (Firing Rate)": (
                "# Firing rate of a neuron in response to stimulus intensity.\n"
                "Stimulus Intensity (nA)\tIntensity Uncertainty (nA)\tFiring Rate (Hz)\tRate Uncertainty (Hz)\n"
                "10\t1.0\t5\t2\n"
                "20\t1.0\t12\t3\n"
                "30\t1.0\t19\t3\n"
                "40\t1.0\t26\t4\n"
                "50\t1.0\t34\t4\n"
            ),
            "Simple Pendulum": (
                "# Data for a simple pendulum's swing.\n"
                "# Plot Angle vs. Time for sinusoidal motion.\n"
                "Time (s)\tAngle (rad)\tAngle Uncertainty (rad)\n"
                "0.00\t0.52\t0.01\n"
                "0.25\t0.37\t0.01\n"
                "0.50\t0.00\t0.01\n"
                "0.75\t-0.37\t0.01\n"
                "1.00\t-0.52\t0.01\n"
                "1.25\t-0.37\t0.01\n"
                "1.50\t0.00\t0.01\n"
            ),
            "Ohm's Law": (
                "# Data for a simple circuit to verify Ohm's Law (V=IR).\n"
                "# Plot Voltage vs. Current to find resistance.\n"
                "Current (A)\tCurrent Uncertainty (A)\tVoltage (V)\tVoltage Uncertainty (V)\n"
                "0.1\t0.01\t1.05\t0.05\n"
                "0.2\t0.01\t1.98\t0.05\n"
                "0.3\t0.01\t3.01\t0.05\n"
                "0.4\t0.01\t4.05\t0.05\n"
                "0.5\t0.01\t4.95\t0.05\n"
            )
        }

        # --- UI Styling ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', padding=6, relief="flat", background="#cceeff", font=('Helvetica', 10))
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 11))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('TRadiobutton', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TCheckbutton', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('Vertical.TScrollbar', background='#e0e0e0', troughcolor='#f0f0f0')


        # --- Main Layout ---
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create two main panes: one for controls, one for the plot
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # --- Control Panel (Left Side) with Scrollbar ---
        control_container = ttk.Frame(paned_window, padding="10", width=420)
        control_container.pack_propagate(False)
        paned_window.add(control_container, weight=1)

        # Create a canvas and a vertical scrollbar
        canvas = tk.Canvas(control_container, background='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=canvas.yview, style='Vertical.TScrollbar')
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # This frame will contain all the widgets and be scrolled by the canvas
        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_configure)
        
        # Add mouse wheel scrolling
        def on_mousewheel(event):
            # Platform-independent scrolling
            if event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")

        self.bind_all("<MouseWheel>", on_mousewheel) # Windows/macOS
        self.bind_all("<Button-4>", on_mousewheel)   # Linux scroll up
        self.bind_all("<Button-5>", on_mousewheel)   # Linux scroll down


        self._create_data_input_widgets(scrollable_frame)
        self._create_axis_selection_widgets(scrollable_frame)
        self._create_plot_options_widgets(scrollable_frame)
        self._create_action_buttons(scrollable_frame)

        # --- Plot Area (Right Side) ---
        plot_frame = ttk.Frame(paned_window, padding="10")
        paned_window.add(plot_frame, weight=3)
        self._create_plot_widgets(plot_frame)
        
        # Bind Enter key to generate plot
        self.bind('<Return>', lambda event=None: self.plot_button.invoke())

    def _create_data_input_widgets(self, parent):
        """Creates the text box for data input."""
        ttk.Label(parent, text="1. Paste or Edit Data Below", style='Header.TLabel').pack(anchor='w', pady=(0, 5), fill=tk.X)
        
        # --- Sample Data Dropdown ---
        sample_frame = ttk.Frame(parent)
        sample_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(sample_frame, text="Choose Sample Data:").pack(side='left', padx=(0,5))
        
        self.sample_data_var = tk.StringVar()
        sample_combo = ttk.Combobox(sample_frame, textvariable=self.sample_data_var, state='readonly')
        sample_combo['values'] = list(self.sample_data_sets.keys())
        sample_combo.pack(fill=tk.X, expand=True)
        sample_combo.set(list(self.sample_data_sets.keys())[0]) # Set default
        sample_combo.bind('<<ComboboxSelected>>', self.on_sample_data_selected)
        
        # --- Data Text Box ---
        self.text_data_input = tk.Text(parent, height=15, width=50, undo=True, font=('Courier New', 10))
        self.text_data_input.pack(fill=tk.X, expand=True)
        self.on_sample_data_selected() # Load the default sample data
        
        ttk.Button(parent, text="Load Data from Text Box", command=self.load_data).pack(pady=10, fill=tk.X)
        
    def on_sample_data_selected(self, event=None):
        """Loads the selected sample data into the text box."""
        selection = self.sample_data_var.get()
        data_string = self.sample_data_sets.get(selection, "")
        self.text_data_input.delete('1.0', tk.END)
        self.text_data_input.insert('1.0', data_string)

    def _create_axis_selection_widgets(self, parent):
        """Creates frames and widgets for selecting X and Y axes."""
        ttk.Label(parent, text="2. Select Axes", style='Header.TLabel').pack(anchor='w', pady=(10, 5), fill=tk.X)
        
        self.x_axis_frame = ttk.LabelFrame(parent, text="X-Axis (Choose One)", padding="10")
        self.x_axis_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.x_axis_frame, text="No data loaded.").pack()

        self.y_axis_frame = ttk.LabelFrame(parent, text="Y-Axes (Choose One or More)", padding="10")
        self.y_axis_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.y_axis_frame, text="No data loaded.").pack()

    def _create_plot_options_widgets(self, parent):
        """Creates widgets for plot titles and labels."""
        ttk.Label(parent, text="3. Plot Options (Optional)", style='Header.TLabel').pack(anchor='w', pady=(10, 5), fill=tk.X)
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=tk.X)

        self.plot_title_var = tk.StringVar(value="My Plot Title")
        self.x_label_var = tk.StringVar()
        self.y_label_var = tk.StringVar()

        ttk.Label(options_frame, text="Plot Title:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(options_frame, textvariable=self.plot_title_var).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(options_frame, text="X-Axis Label:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(options_frame, textvariable=self.x_label_var).grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(options_frame, text="Y-Axis Label:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(options_frame, textvariable=self.y_label_var).grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        options_frame.columnconfigure(1, weight=1)

    def _create_action_buttons(self, parent):
        """Creates the main plot and fit buttons."""
        ttk.Label(parent, text="4. Actions", style='Header.TLabel').pack(anchor='w', pady=(20, 5), fill=tk.X)
        self.plot_button = ttk.Button(parent, text="Generate Plot", command=self.plot_data, style='TButton')
        self.plot_button.pack(pady=(0,5), fill=tk.X, ipady=10)
        
        self.fit_button = ttk.Button(parent, text="Perform Linear Fit", command=self.perform_linear_fit)
        self.fit_button.pack(pady=5, fill=tk.X, ipady=10)


    def _create_plot_widgets(self, parent):
        """Creates the Matplotlib figure and canvas."""
        self.fig, self.ax = plt.subplots(facecolor='#f0f0f0')
        self.ax.set_title("Plot will appear here")
        self.ax.grid(True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.fig.tight_layout()

    def load_data(self):
        """
        Parses the data from the text input using Pandas and updates the UI
        with column choices for axis selection.
        """
        data_string = self.text_data_input.get("1.0", tk.END)
        if not data_string.strip():
            messagebox.showerror("Error", "Input data is empty.")
            return
            
        data_string_no_comments = "\n".join([line for line in data_string.split('\n') if not line.strip().startswith('#')])

        try:
            data_io = io.StringIO(data_string_no_comments)
            separator = ',' if ',' in data_string_no_comments else '\t'
            self.df = pd.read_csv(data_io, sep=separator)
            self.df = self.df.dropna(how='all')
            
            if self.df.empty:
                raise ValueError("Parsed data is empty.")
                
            self.update_axis_selection_ui()
        except Exception as e:
            messagebox.showerror("Data Loading Error", f"Could not parse data.\nPlease ensure it is in a valid CSV or tab-separated format with a header row.\n\nError: {e}")
            self.df = None

    def update_axis_selection_ui(self):
        """Clears and repopulates the axis selection widgets based on loaded data."""
        for widget in self.x_axis_frame.winfo_children():
            widget.destroy()
        for widget in self.y_axis_frame.winfo_children():
            widget.destroy()

        if self.df is None:
            ttk.Label(self.x_axis_frame, text="No data loaded.").pack()
            ttk.Label(self.y_axis_frame, text="No data loaded.").pack()
            return
            
        columns = self.df.columns.tolist()
        self.y_axis_vars = {}
        self.y_error_vars = {}

        # --- Populate X-Axis Frame ---
        self.x_axis_var.set(columns[0])
        self.x_label_var.set(columns[0])
        for col in columns:
            rb = ttk.Radiobutton(self.x_axis_frame, text=col, variable=self.x_axis_var, value=col, command=lambda c=col: self.x_label_var.set(c))
            rb.pack(anchor='w')
            
        # Add X Uncertainty Selection
        ttk.Separator(self.x_axis_frame, orient='horizontal').pack(fill='x', pady=10)
        x_err_frame = ttk.Frame(self.x_axis_frame)
        x_err_frame.pack(fill='x', expand=True)
        ttk.Label(x_err_frame, text="Uncertainty Column (Optional):").pack(side='left', padx=(0, 5))
        
        self.x_error_var.set("None")
        error_options = ["None"] + columns
        x_error_menu = ttk.OptionMenu(x_err_frame, self.x_error_var, *error_options)
        x_error_menu.pack(side='left', fill='x', expand=True)

        # --- Populate Y-Axis Frame ---
        y_grid_frame = ttk.Frame(self.y_axis_frame)
        y_grid_frame.pack(fill=tk.X)
        ttk.Label(y_grid_frame, text="Plot").grid(row=0, column=0, padx=5)
        ttk.Label(y_grid_frame, text="Y-Axis Column").grid(row=0, column=1, padx=5, sticky='w')
        ttk.Label(y_grid_frame, text="Uncertainty Column (Optional)").grid(row=0, column=2, padx=5, sticky='w')
        
        for i, col in enumerate(columns):
            self.y_axis_vars[col] = tk.BooleanVar()
            
            def create_toggle_handler(var):
                def handler(event=None):
                    var.set(not var.get())
                    self.update_y_label()
                return handler

            cb = ttk.Checkbutton(y_grid_frame, variable=self.y_axis_vars[col], command=self.update_y_label)
            cb.grid(row=i + 1, column=0, padx=5, sticky='w')
            
            label = ttk.Label(y_grid_frame, text=col)
            label.grid(row=i + 1, column=1, sticky='w')
            label.bind("<Button-1>", create_toggle_handler(self.y_axis_vars[col]))

            self.y_error_vars[col] = tk.StringVar(value="None")
            error_options = ["None"] + columns
            error_menu = ttk.OptionMenu(y_grid_frame, self.y_error_vars[col], *error_options)
            error_menu.grid(row=i + 1, column=2, padx=5, sticky='ew')
        y_grid_frame.columnconfigure(2, weight=1)

    def update_y_label(self):
        """Automatically updates the Y-axis label based on selected columns."""
        selected_y = [col for col, var in self.y_axis_vars.items() if var.get()]
        self.y_label_var.set(", ".join(selected_y))

    def plot_data(self):
        """
        Retrieves user selections for axes and uncertainties,
        and generates a plot on the Matplotlib canvas.
        """
        if self.df is None:
            messagebox.showwarning("Warning", "Please load data first.")
            return

        x_col = self.x_axis_var.get()
        selected_y_cols = [col for col, var in self.y_axis_vars.items() if var.get()]

        if not x_col or not selected_y_cols:
            messagebox.showwarning("Warning", "Please select at least one X and one Y axis.")
            return

        self.ax.clear()

        try:
            x_data = pd.to_numeric(self.df[x_col], errors='coerce')

            # Get X error data series once
            x_err_col = self.x_error_var.get()
            x_err_series = None
            if x_err_col != "None":
                x_err_series = pd.to_numeric(self.df[x_err_col], errors='coerce')

            for y_col in selected_y_cols:
                y_data = pd.to_numeric(self.df[y_col], errors='coerce')
                
                valid_indices = x_data.notna() & y_data.notna()
                x_plot = x_data[valid_indices]
                y_plot = y_data[valid_indices]

                # Process Y error
                y_err_col = self.y_error_vars[y_col].get()
                y_err_data = None
                if y_err_col != "None":
                    y_err_data_series = pd.to_numeric(self.df[y_err_col], errors='coerce')
                    y_err_data = y_err_data_series[valid_indices]
                
                # Process X error
                x_err_data = None
                if x_err_series is not None:
                    x_err_data = x_err_series[valid_indices]
                
                self.ax.errorbar(x_plot, y_plot, yerr=y_err_data, xerr=x_err_data, fmt='o', 
                                 capsize=4, label=y_col, alpha=0.8)

        except Exception as e:
            messagebox.showerror("Plotting Error", f"An error occurred while preparing the data for plotting.\nCheck that columns are numeric.\n\nError: {e}")
            return

        # --- Final Plot Formatting ---
        self.ax.set_title(self.plot_title_var.get(), fontsize=20)
        self.ax.set_xlabel(self.x_label_var.get(), fontsize=20)
        self.ax.set_ylabel(self.y_label_var.get(), fontsize=20)
        
        self.ax.tick_params(axis='both', which='major', labelsize=20)
        
        self.ax.legend()
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        self.fig.tight_layout()
        self.canvas.draw()

    def _get_y_col_for_fit(self, y_cols):
        """Handles the logic of selecting a Y column for fitting, using a popup if necessary."""
        if not y_cols:
            return None
        if len(y_cols) == 1:
            return y_cols[0]

        # Create a popup window to ask the user
        popup = tk.Toplevel(self)
        popup.title("Select Y-Axis for Fit")
        popup.geometry("300x200")
        ttk.Label(popup, text="Multiple Y-axes are plotted.\nPlease select one to fit:").pack(pady=10)

        selected_y = tk.StringVar()
        selected_y.set(y_cols[0])

        for col in y_cols:
            ttk.Radiobutton(popup, text=col, variable=selected_y, value=col).pack(anchor='w', padx=20)
        
        # This function will be called when the user clicks OK
        def on_ok():
            popup.result = selected_y.get()
            popup.destroy()
        
        # This function will be called if the user closes the window
        def on_cancel():
            popup.result = None
            popup.destroy()

        ok_button = ttk.Button(popup, text="OK", command=on_ok)
        ok_button.pack(pady=10)
        popup.protocol("WM_DELETE_WINDOW", on_cancel)

        # Wait for the popup to close
        popup.grab_set()
        self.wait_window(popup)

        return getattr(popup, 'result', None)
    
    def _format_fit_parameter(self, value, uncertainty):
        """
        Formats a value and its uncertainty according to scientific best practices.
        - The uncertainty is rounded to two significant figures.
        - The value is rounded to the same decimal place as the uncertainty.
        - Switches to scientific notation for very large or small numbers.
        """
        if uncertainty is None or uncertainty <= 0 or not np.isfinite(uncertainty):
            return f"{value:.4g} ± {uncertainty:.2g}"

        # Determine the number of decimal places from the uncertainty
        exponent = np.floor(np.log10(np.abs(uncertainty)))
        decimal_places = int(-exponent + 1) # For 2 significant figures in uncertainty

        # Use scientific notation if the value is very large or small
        value_exponent = np.floor(np.log10(np.abs(value))) if value != 0 else 0
        if value_exponent < -3 or value_exponent > 4:
            # Format in scientific notation
            norm_value = value / (10**value_exponent)
            norm_uncertainty = uncertainty / (10**value_exponent)
            
            norm_exponent = np.floor(np.log10(np.abs(norm_uncertainty)))
            norm_decimal_places = int(-norm_exponent + 1)
            
            val_str = f"{norm_value:.{norm_decimal_places}f}"
            err_str = f"{norm_uncertainty:.{norm_decimal_places}f}"
            
            return f"({val_str} ± {err_str})e{int(value_exponent)}"

        # Use fixed-point notation for "normal" sized numbers
        if decimal_places >= 0:
            return f"{value:.{decimal_places}f} ± {uncertainty:.{decimal_places}f}"
        else: # Handle rounding for numbers > 10 (decimal_places is negative)
            rounded_value = round(value, decimal_places)
            rounded_uncertainty = round(uncertainty, decimal_places)
            return f"{rounded_value:.0f} ± {rounded_uncertainty:.0f}"


    def perform_linear_fit(self):
        """Performs a linear regression on the plotted data and displays it."""
        if linregress is None:
            messagebox.showerror("Dependency Missing", "The 'scipy' library is required for detailed linear fitting.\nPlease install it by running:\n\npip install scipy")
            return

        if self.df is None:
            messagebox.showwarning("Warning", "Please load and plot data first.")
            return

        if not self.ax.lines and not self.ax.collections:
            messagebox.showwarning("Warning", "Please generate a plot before fitting.")
            return
            
        x_col = self.x_axis_var.get()
        selected_y_cols = [col for col, var in self.y_axis_vars.items() if var.get()]
        
        y_col_to_fit = self._get_y_col_for_fit(selected_y_cols)

        if not y_col_to_fit:
            # User cancelled the popup or there were no y-cols
            if len(selected_y_cols) > 1:
                messagebox.showinfo("Fit Cancelled", "Linear fit was cancelled.")
            elif not selected_y_cols:
                 messagebox.showwarning("Warning", "No Y-axis selected to fit.")
            return

        try:
            x_data = pd.to_numeric(self.df[x_col], errors='coerce')
            y_data = pd.to_numeric(self.df[y_col_to_fit], errors='coerce')

            valid_indices = x_data.notna() & y_data.notna()
            x_clean = x_data[valid_indices]
            y_clean = y_data[valid_indices]

            if len(x_clean) < 2:
                messagebox.showerror("Fit Error", "Need at least two data points to perform a linear fit.")
                return

            # Perform linear regression using scipy to get detailed stats
            res = linregress(x_clean, y_clean)
            slope = res.slope
            intercept = res.intercept
            r_squared = res.rvalue**2
            slope_stderr = res.stderr
            intercept_stderr = res.intercept_stderr

            x_fit = np.linspace(x_clean.min(), x_clean.max(), 100)
            y_fit = slope * x_fit + intercept
            
            # Format the parameters using the new method
            slope_str = self._format_fit_parameter(slope, slope_stderr)
            intercept_str = self._format_fit_parameter(intercept, intercept_stderr)

            # Create the detailed label for the legend
            fit_label = (
                f"Fit for '{y_col_to_fit}'\n"
                f"y = ({slope_str})x + ({intercept_str})\n"
                f"$R^2$ = {r_squared:.4f}"
            )
            
            # Plot the fit line with the new detailed label
            self.ax.plot(x_fit, y_fit, color='red', label=fit_label)
            
            # Update legend and redraw canvas
            self.ax.legend()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Fit Error", f"An error occurred during the linear fit.\n\nError: {e}")

if __name__ == "__main__":
    app = DataPlotterApp()
    app.mainloop()

