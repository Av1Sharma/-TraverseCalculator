import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, Menu
import math
import json
import os
from datetime import datetime

# Auto-update module
try:
    import updater
    UPDATER_AVAILABLE = True
except ImportError:
    UPDATER_AVAILABLE = False


class PolygonTraverseCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Traverse Calculator")
        self.root.geometry("1300x900")
        
        # Variables
        self.num_sides = tk.IntVar(value=4)
        self.angle_entries = []
        self.bearing_entries = []
        self.distance_entries = []
        
        # Project info variables
        self.project_name = tk.StringVar()
        self.user_name = tk.StringVar()
        self.project_address = tk.StringVar()
        self.traverse_id = tk.StringVar()
        
        # Settings variables
        self.traverse_type = tk.StringVar(value="closed")
        self.units = tk.StringVar(value="metric")
        
        # File tracking
        self.current_file = None
        self.is_modified = False
        
        # Store last calculation results for export
        self.last_results = ""
        
        # Create icon
        self.create_icon()
        
        # Setup UI
        self.setup_menu()
        self.setup_ui()
        self.setup_statusbar()
        
        # Update clock
        self.update_clock()
        
        # Check for updates on startup (after 3 seconds to let UI load)
        if UPDATER_AVAILABLE:
            updater.check_for_updates_on_startup(self.root, delay_ms=3000)
        
    def create_icon(self):
        """Create a colorful polygon icon"""
        # Create a small toplevel window temporarily to generate icon
        icon_size = 32
        icon_canvas = tk.Canvas(self.root, width=icon_size, height=icon_size, 
                                bg='white', highlightthickness=0)
        
        # Draw a colorful pentagon
        center_x, center_y = icon_size // 2, icon_size // 2
        radius = 12
        points = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i in range(5):
            angle = math.radians(90 + i * 72)
            x = center_x + radius * math.cos(angle)
            y = center_y - radius * math.sin(angle)
            points.extend([x, y])
        
        icon_canvas.create_polygon(points, fill='#4ECDC4', outline='#2C3E50', width=2)
        
        # We can't easily set a custom icon in tkinter without external files
        # The icon will be displayed in the header instead
        icon_canvas.destroy()
        
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_command(label="Import Input File...", command=self.import_file)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=self.print_output)
        file_menu.add_command(label="Export to PDF...", command=self.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self.close_project)
        file_menu.add_command(label="Exit", command=self.exit_app)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_file())
        
        # Options/Settings menu
        options_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)
        
        # Traverse Type submenu
        traverse_menu = Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Traverse Type", menu=traverse_menu)
        traverse_menu.add_radiobutton(label="Closed Traverse", variable=self.traverse_type, 
                                       value="closed", command=self.on_traverse_type_change)
        traverse_menu.add_radiobutton(label="Open Traverse (Coming Soon)", variable=self.traverse_type,
                                       value="open", state="disabled")
        
        options_menu.add_separator()
        
        # Units submenu
        units_menu = Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Units", menu=units_menu)
        units_menu.add_radiobutton(label="English (feet)", variable=self.units, 
                                    value="english", command=self.on_units_change)
        units_menu.add_radiobutton(label="Metric (meters)", variable=self.units, 
                                    value="metric", command=self.on_units_change)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Check for Updates...", command=self.check_for_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help Contents (Coming Soon)", state="disabled")
        
    def setup_statusbar(self):
        """Setup the status bar at the bottom"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # File label
        self.file_label = ttk.Label(self.statusbar, text="File: <new file>", 
                                     relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Date/time label
        self.datetime_label = ttk.Label(self.statusbar, text="", 
                                         relief=tk.SUNKEN, anchor=tk.E, padding=(5, 2))
        self.datetime_label.pack(side=tk.RIGHT)
        
    def update_clock(self):
        """Update the clock in the status bar"""
        now = datetime.now()
        self.datetime_label.config(text=now.strftime("%m/%d/%Y    %I:%M %p"))
        self.root.after(1000, self.update_clock)
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with program name and icon
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create colorful polygon icon
        icon_canvas = tk.Canvas(header_frame, width=40, height=40, 
                                bg=self.root.cget('bg'), highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Draw pentagon icon
        center_x, center_y = 20, 20
        radius = 15
        points = []
        for i in range(5):
            angle = math.radians(90 + i * 72)
            x = center_x + radius * math.cos(angle)
            y = center_y - radius * math.sin(angle)
            points.extend([x, y])
        icon_canvas.create_polygon(points, fill='#4ECDC4', outline='#2C3E50', width=2)
        
        # Draw inner details
        inner_radius = 8
        inner_points = []
        for i in range(5):
            angle = math.radians(90 + i * 72)
            x = center_x + inner_radius * math.cos(angle)
            y = center_y - inner_radius * math.sin(angle)
            inner_points.extend([x, y])
        icon_canvas.create_polygon(inner_points, fill='#96CEB4', outline='#2C3E50', width=1)
        
        # Program title
        title_label = ttk.Label(header_frame, text="Traverse Calculator", 
                                 font=("Arial", 18, "bold"), foreground="#2C3E50")
        title_label.pack(side=tk.LEFT)
        
        # Project Identification Data frame
        project_frame = ttk.LabelFrame(main_frame, text="Project Identification Data", padding="10")
        project_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: Project Name and Traverse ID
        ttk.Label(project_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=3)
        project_name_entry = ttk.Entry(project_frame, textvariable=self.project_name, width=40)
        project_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(project_frame, text="Traverse ID:").grid(row=0, column=2, sticky=tk.E, padx=(20, 5), pady=3)
        traverse_id_entry = ttk.Entry(project_frame, textvariable=self.traverse_id, width=25)
        traverse_id_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=3)
        
        # Row 2: User Name
        ttk.Label(project_frame, text="User Name:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=3)
        user_name_entry = ttk.Entry(project_frame, textvariable=self.user_name, width=40)
        user_name_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        # Row 3: Project Address (spans multiple columns)
        ttk.Label(project_frame, text="Project Address:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=3)
        project_address_entry = ttk.Entry(project_frame, textvariable=self.project_address, width=80)
        project_address_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=3)
        
        # Number of sides input
        input_header_frame = ttk.Frame(main_frame)
        input_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(input_header_frame, text="Number of Sides:").pack(side=tk.LEFT, padx=(0, 5))
        sides_entry = ttk.Entry(input_header_frame, textvariable=self.num_sides, width=10)
        sides_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(input_header_frame, text="Generate Input Fields", 
                   command=self.generate_fields).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(input_header_frame, text="Calculate", 
                   command=self.calculate).pack(side=tk.LEFT, padx=10)
        
        # Input frame (scrollable)
        input_frame_container = ttk.LabelFrame(main_frame, text="Input Data", padding="10")
        input_frame_container.pack(fill=tk.X, pady=(0, 10))
        
        # Canvas for scrolling
        canvas = tk.Canvas(input_frame_container, height=200)
        scrollbar = ttk.Scrollbar(input_frame_container, orient="vertical", command=canvas.yview)
        self.input_frame = ttk.Frame(canvas)
        
        self.input_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.input_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=140, height=20, 
                                                      font=("Courier", 9))
        self.results_text.pack(fill="both", expand=True)
        
        # Generate initial fields
        self.generate_fields()
        
    def get_unit_label(self):
        """Return the current unit label"""
        return "ft" if self.units.get() == "english" else "m"
    
    def get_unit_name(self):
        """Return the full unit name"""
        return "feet" if self.units.get() == "english" else "meters"
        
    def on_units_change(self):
        """Handle units change - preserve existing input data"""
        # Save current input data
        saved_bearings = []
        saved_distances = []
        for i in range(len(self.bearing_entries)):
            saved_bearings.append(self.bearing_entries[i].get())
            saved_distances.append(self.distance_entries[i].get())
        
        # Regenerate fields to update unit labels
        self.generate_fields()
        
        # Restore input data
        for i in range(min(len(saved_bearings), len(self.bearing_entries))):
            self.bearing_entries[i].insert(0, saved_bearings[i])
            self.distance_entries[i].insert(0, saved_distances[i])
        
        self.is_modified = True
        
    def on_traverse_type_change(self):
        """Handle traverse type change"""
        self.is_modified = True
        
    def generate_fields(self):
        # Clear existing entries
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        self.angle_entries = []
        self.bearing_entries = []
        self.distance_entries = []
        
        n = self.num_sides.get()
        unit_label = self.get_unit_label()
        
        # Headers
        ttk.Label(self.input_frame, text="Side", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Label(self.input_frame, text="Bearing (e.g., N45.30E or 045.30)", font=("Arial", 10, "bold")).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Label(self.input_frame, text=f"Distance ({unit_label})", font=("Arial", 10, "bold")).grid(
            row=0, column=2, padx=5, pady=5)
        
        # Input fields for each side
        for i in range(n):
            ttk.Label(self.input_frame, text=f"{i+1}").grid(row=i+1, column=0, padx=5, pady=2)
            
            bearing_entry = ttk.Entry(self.input_frame, width=25)
            bearing_entry.grid(row=i+1, column=1, padx=5, pady=2)
            self.bearing_entries.append(bearing_entry)
            
            distance_entry = ttk.Entry(self.input_frame, width=15)
            distance_entry.grid(row=i+1, column=2, padx=5, pady=2)
            self.distance_entries.append(distance_entry)
    
    def dms_to_decimal(self, dms_str):
        """Convert DD.MMSS to decimal degrees"""
        try:
            parts = dms_str.split('.')
            degrees = float(parts[0])
            if len(parts) > 1:
                mmss = parts[1].ljust(4, '0')[:4]
                minutes = float(mmss[:2])
                seconds = float(mmss[2:4])
                decimal = abs(degrees) + minutes/60 + seconds/3600
                return decimal if degrees >= 0 else -decimal
            return degrees
        except:
            return float(dms_str)
    
    def bearing_to_azimuth(self, bearing_str):
        """Convert bearing to azimuth (0-360 from North)"""
        bearing_str = bearing_str.strip().upper()
        
        try:
            # Check if it's already azimuth (just numbers)
            if bearing_str.replace('.', '').replace('-', '').isdigit():
                return self.dms_to_decimal(bearing_str)
            
            # Parse quadrant bearing (e.g., N45.30E)
            if 'N' in bearing_str and 'E' in bearing_str:
                angle = self.dms_to_decimal(bearing_str.replace('N', '').replace('E', ''))
                return angle
            elif 'S' in bearing_str and 'E' in bearing_str:
                angle = self.dms_to_decimal(bearing_str.replace('S', '').replace('E', ''))
                return 180 - angle
            elif 'S' in bearing_str and 'W' in bearing_str:
                angle = self.dms_to_decimal(bearing_str.replace('S', '').replace('W', ''))
                return 180 + angle
            elif 'N' in bearing_str and 'W' in bearing_str:
                angle = self.dms_to_decimal(bearing_str.replace('N', '').replace('W', ''))
                return 360 - angle
            else:
                return self.dms_to_decimal(bearing_str)
        except Exception as e:
            raise ValueError(f"Invalid bearing format: {bearing_str}")
    
    def azimuth_to_bearing(self, azimuth):
        """Convert azimuth to quadrant bearing string (e.g., N 45°30'15" E)"""
        # Normalize azimuth to 0-360
        azimuth = azimuth % 360
        
        if azimuth <= 90:
            # NE quadrant
            degrees = int(azimuth)
            minutes = int((azimuth - degrees) * 60)
            seconds = int(((azimuth - degrees) * 60 - minutes) * 60)
            return f"N {degrees:02d}°{minutes:02d}'{seconds:02d}\" E"
        elif azimuth <= 180:
            # SE quadrant
            angle = 180 - azimuth
            degrees = int(angle)
            minutes = int((angle - degrees) * 60)
            seconds = int(((angle - degrees) * 60 - minutes) * 60)
            return f"S {degrees:02d}°{minutes:02d}'{seconds:02d}\" E"
        elif azimuth <= 270:
            # SW quadrant
            angle = azimuth - 180
            degrees = int(angle)
            minutes = int((angle - degrees) * 60)
            seconds = int(((angle - degrees) * 60 - minutes) * 60)
            return f"S {degrees:02d}°{minutes:02d}'{seconds:02d}\" W"
        else:
            # NW quadrant
            angle = 360 - azimuth
            degrees = int(angle)
            minutes = int((angle - degrees) * 60)
            seconds = int(((angle - degrees) * 60 - minutes) * 60)
            return f"N {degrees:02d}°{minutes:02d}'{seconds:02d}\" W"
    
    def calculate_interior_angles(self, bearings):
        """Calculate interior angles from consecutive bearings"""
        n = len(bearings)
        angles = []
        
        for i in range(n):
            current_bearing = bearings[i]
            next_bearing = bearings[(i + 1) % n]
            
            back_azimuth = (current_bearing + 180) % 360
            interior_angle = (back_azimuth - next_bearing) % 360
            
            angles.append(interior_angle)
        
        return angles
    
    def calculate(self):
        try:
            n = self.num_sides.get()
            unit_label = self.get_unit_label()
            
            # Read input data
            bearings = []
            distances = []
            
            for i in range(n):
                bearing = self.bearing_to_azimuth(self.bearing_entries[i].get())
                distance = float(self.distance_entries[i].get())
                
                bearings.append(bearing)
                distances.append(distance)
            
            # Calculate interior angles from bearings
            angles = self.calculate_interior_angles(bearings)
            
            # Clear results
            self.results_text.delete(1.0, tk.END)
            
            # Build results string
            results = []
            
            # 1. Check sum of interior angles
            theoretical_sum = (n - 2) * 180
            actual_sum = sum(angles)
            angular_misclosure = actual_sum - theoretical_sum
            
            results.append("=" * 120)
            results.append("POLYGON TRAVERSE CALCULATION RESULTS")
            results.append("=" * 120)
            results.append("")
            
            # Project info header
            if self.project_name.get() or self.user_name.get() or self.project_address.get() or self.traverse_id.get():
                results.append("PROJECT INFORMATION")
                results.append("-" * 120)
                if self.project_name.get():
                    results.append(f"Project Name: {self.project_name.get()}")
                if self.user_name.get():
                    results.append(f"User Name: {self.user_name.get()}")
                if self.project_address.get():
                    results.append(f"Project Address: {self.project_address.get()}")
                if self.traverse_id.get():
                    results.append(f"Traverse ID: {self.traverse_id.get()}")
                results.append(f"Units: {self.get_unit_name().title()}")
                results.append(f"Date: {datetime.now().strftime('%m/%d/%Y %I:%M %p')}")
                results.append("")
            
            # Display computed interior angles
            results.append("COMPUTED INTERIOR ANGLES FROM BEARINGS")
            results.append("-" * 120)
            results.append(f"{'Side':<6} {'Bearing':<20} {'Interior Angle':<20}")
            results.append("-" * 120)
            for i in range(n):
                results.append(f"{i+1:<6} {bearings[i]:>15.6f}°   {angles[i]:>15.6f}°")
            results.append("")
            
            results.append("1. ANGULAR MISCLOSURE CHECK")
            results.append("-" * 120)
            results.append(f"Number of sides: {n}")
            results.append(f"Theoretical sum of interior angles: {theoretical_sum:.4f}°")
            results.append(f"Actual sum of interior angles: {actual_sum:.4f}°")
            results.append(f"Angular misclosure: {angular_misclosure:.4f}°")
            results.append(f"Allowable error (±√n minutes): ±{math.sqrt(n):.2f}'")
            
            # 2. Distribute angular error
            angular_correction = -angular_misclosure / n
            adjusted_angles = [angle + angular_correction for angle in angles]
            
            results.append(f"\nCorrection per angle: {angular_correction:.6f}°\n")
            
            # 3. Compute azimuths
            azimuths = []
            azimuth = bearings[0]
            azimuths.append(azimuth)
            
            for i in range(1, n):
                azimuth = (azimuth + 180 - adjusted_angles[i-1]) % 360
                azimuths.append(azimuth)
            
            results.append("2. ADJUSTED ANGLES AND AZIMUTHS")
            results.append("-" * 120)
            results.append(f"{'Side':<6} {'Original Angle':<20} {'Correction':<20} {'Adjusted Angle':<20} {'Azimuth':<20}")
            results.append("-" * 120)
            
            for i in range(n):
                results.append(
                    f"{i+1:<6} {angles[i]:>15.6f}°   {angular_correction:>15.6f}°   "
                    f"{adjusted_angles[i]:>15.6f}°   {azimuths[i]:>15.6f}°")
            
            # 4. Calculate latitudes and departures
            latitudes = []
            departures = []
            
            for i in range(n):
                lat = distances[i] * math.cos(math.radians(azimuths[i]))
                dep = distances[i] * math.sin(math.radians(azimuths[i]))
                latitudes.append(lat)
                departures.append(dep)
            
            sum_lat = sum(latitudes)
            sum_dep = sum(departures)
            
            results.append(f"\n3. LATITUDES AND DEPARTURES")
            results.append("-" * 120)
            results.append(f"{'Side':<6} {'Distance':<15} {'Azimuth':<20} {'Latitude':<20} {'Departure':<20}")
            results.append("-" * 120)
            
            total_perimeter = sum(distances)
            for i in range(n):
                results.append(
                    f"{i+1:<6} {distances[i]:>12.3f} {unit_label}   {azimuths[i]:>15.6f}°   "
                    f"{latitudes[i]:>15.6f} {unit_label}   {departures[i]:>15.6f} {unit_label}")
            
            results.append("-" * 120)
            results.append(f"{'TOTAL':<6} {total_perimeter:>12.3f} {unit_label}   {'':<19} "
                          f"{sum_lat:>15.6f} {unit_label}   {sum_dep:>15.6f} {unit_label}")
            
            # 5. Linear misclosure
            linear_misclosure = math.sqrt(sum_lat**2 + sum_dep**2)
            relative_accuracy = f"1:{int(total_perimeter/linear_misclosure)}" if linear_misclosure > 0 else "Perfect"
            
            results.append(f"\n4. LINEAR MISCLOSURE")
            results.append("-" * 120)
            results.append(f"Error in latitude (ΣL): {sum_lat:.6f} {unit_label}")
            results.append(f"Error in departure (ΣD): {sum_dep:.6f} {unit_label}")
            results.append(f"Total linear misclosure: {linear_misclosure:.6f} {unit_label}")
            results.append(f"Relative accuracy: {relative_accuracy}\n")
            
            # 6. Apply Bowditch corrections
            lat_corrections = []
            dep_corrections = []
            adjusted_lats = []
            adjusted_deps = []
            
            for i in range(n):
                lat_corr = -(sum_lat * distances[i]) / total_perimeter
                dep_corr = -(sum_dep * distances[i]) / total_perimeter
                lat_corrections.append(lat_corr)
                dep_corrections.append(dep_corr)
                adjusted_lats.append(latitudes[i] + lat_corr)
                adjusted_deps.append(departures[i] + dep_corr)
            
            results.append("5. CORRECTIONS AND ADJUSTED VALUES (Bowditch Method)")
            results.append("-" * 120)
            results.append(f"{'Side':<6} {'Lat Corr':<15} {'Dep Corr':<15} {'Adjusted Lat':<20} {'Adjusted Dep':<20}")
            results.append("-" * 120)
            
            for i in range(n):
                results.append(
                    f"{i+1:<6} {lat_corrections[i]:>12.6f} {unit_label}  {dep_corrections[i]:>12.6f} {unit_label}  "
                    f"{adjusted_lats[i]:>15.6f} {unit_label}   {adjusted_deps[i]:>15.6f} {unit_label}")
            
            results.append("-" * 120)
            results.append(f"{'TOTAL':<6} {'':<15} {'':<15} "
                          f"{sum(adjusted_lats):>15.6f} {unit_label}   {sum(adjusted_deps):>15.6f} {unit_label}")
            
            # 7. FINAL CORRECTED BEARINGS AND DISTANCES
            results.append("\n" + "=" * 120)
            results.append("6. FINAL CORRECTED BEARINGS AND DISTANCES")
            results.append("=" * 120)
            results.append(f"{'Side':<6} {'Corrected Bearing':<25} {'Corrected Distance':<20}")
            results.append("-" * 120)
            
            corrected_distances = []
            corrected_bearings = []
            
            for i in range(n):
                # Calculate corrected distance from adjusted lat/dep
                corr_dist = math.sqrt(adjusted_lats[i]**2 + adjusted_deps[i]**2)
                corrected_distances.append(corr_dist)
                
                # Calculate corrected bearing from adjusted lat/dep
                if adjusted_lats[i] == 0:
                    if adjusted_deps[i] > 0:
                        corr_azimuth = 90
                    else:
                        corr_azimuth = 270
                else:
                    corr_azimuth = math.degrees(math.atan2(adjusted_deps[i], adjusted_lats[i]))
                    if corr_azimuth < 0:
                        corr_azimuth += 360
                
                corr_bearing = self.azimuth_to_bearing(corr_azimuth)
                corrected_bearings.append(corr_bearing)
                
                results.append(f"{i+1:<6} {corr_bearing:<25} {corr_dist:>15.3f} {unit_label}")
            
            results.append("-" * 120)
            results.append(f"{'TOTAL':<6} {'':<25} {sum(corrected_distances):>15.3f} {unit_label}")
            
            results.append("\n" + "=" * 120)
            results.append("CALCULATION COMPLETED SUCCESSFULLY")
            results.append("=" * 120)
            
            # Store results for export
            self.last_results = "\n".join(results)
            
            # Display results
            self.results_text.insert(tk.END, self.last_results)
            
            messagebox.showinfo("Success", "Calculation completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    # File operations
    def get_project_data(self):
        """Get all project data as a dictionary"""
        data = {
            "project_info": {
                "project_name": self.project_name.get(),
                "user_name": self.user_name.get(),
                "project_address": self.project_address.get(),
                "traverse_id": self.traverse_id.get()
            },
            "settings": {
                "traverse_type": self.traverse_type.get(),
                "units": self.units.get()
            },
            "num_sides": self.num_sides.get(),
            "data": []
        }
        
        for i in range(len(self.bearing_entries)):
            bearing = self.bearing_entries[i].get()
            distance = self.distance_entries[i].get()
            data["data"].append({
                "bearing": bearing,
                "distance": distance
            })
        
        return data
    
    def load_project_data(self, data):
        """Load project data from a dictionary"""
        # Load project info
        self.project_name.set(data.get("project_info", {}).get("project_name", ""))
        self.user_name.set(data.get("project_info", {}).get("user_name", ""))
        self.project_address.set(data.get("project_info", {}).get("project_address", ""))
        self.traverse_id.set(data.get("project_info", {}).get("traverse_id", ""))
        
        # Load settings
        self.traverse_type.set(data.get("settings", {}).get("traverse_type", "closed"))
        self.units.set(data.get("settings", {}).get("units", "metric"))
        self.on_traverse_type_change()
        
        # Load sides
        self.num_sides.set(data.get("num_sides", 4))
        self.generate_fields()
        
        # Load data
        for i, item in enumerate(data.get("data", [])):
            if i < len(self.bearing_entries):
                self.bearing_entries[i].delete(0, tk.END)
                self.bearing_entries[i].insert(0, item.get("bearing", ""))
                self.distance_entries[i].delete(0, tk.END)
                self.distance_entries[i].insert(0, item.get("distance", ""))
    
    def save_file(self):
        """Save to current file or prompt for new file"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save with a new filename"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".trv",
            filetypes=[("Traverse Files", "*.trv"), ("All Files", "*.*")],
            title="Save Traverse File"
        )
        if filename:
            self.save_to_file(filename)
    
    def save_to_file(self, filename):
        """Save project data to file"""
        try:
            data = self.get_project_data()
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.current_file = filename
            self.is_modified = False
            self.file_label.config(text=f"File: {os.path.basename(filename)}")
            messagebox.showinfo("Success", f"File saved successfully:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def import_file(self):
        """Import a traverse file"""
        filename = filedialog.askopenfilename(
            defaultextension=".trv",
            filetypes=[("Traverse Files", "*.trv"), ("All Files", "*.*")],
            title="Import Traverse File"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                self.load_project_data(data)
                self.current_file = filename
                self.is_modified = False
                self.file_label.config(text=f"File: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"File imported successfully:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import file:\n{str(e)}")
    
    def print_output(self):
        """Print the output (platform dependent)"""
        if not self.last_results:
            messagebox.showwarning("Warning", "No results to print. Please calculate first.")
            return
        
        # Create a temporary file and open with default application
        try:
            import tempfile
            import webbrowser
            
            # Create HTML version for printing
            html_content = f"""
            <html>
            <head>
                <title>Traverse Calculation Results</title>
                <style>
                    body {{ font-family: Courier, monospace; font-size: 10pt; white-space: pre; }}
                </style>
            </head>
            <body>
{self.last_results}
            </body>
            </html>
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                temp_path = f.name
            
            webbrowser.open(f'file://{temp_path}')
            messagebox.showinfo("Print", "The results have been opened in your browser.\nUse the browser's print function (Ctrl+P or Cmd+P) to print.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print:\n{str(e)}")
    
    def export_pdf(self):
        """Export results to PDF using browser print"""
        if not self.last_results:
            messagebox.showwarning("Warning", "No results to export. Please calculate first.")
            return
        
        try:
            import tempfile
            import webbrowser
            
            # Create a nicely formatted HTML for PDF export
            project_title = self.project_name.get() or "Traverse Calculation"
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{project_title} - Results</title>
    <style>
        @media print {{
            body {{ margin: 0.5in; }}
        }}
        body {{ 
            font-family: 'Courier New', Courier, monospace; 
            font-size: 9pt; 
            white-space: pre; 
            line-height: 1.3;
        }}
        h1 {{
            font-family: Arial, sans-serif;
            font-size: 14pt;
            text-align: center;
            margin-bottom: 20px;
        }}
        .instructions {{
            font-family: Arial, sans-serif;
            background: #ffffcc;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            font-size: 10pt;
        }}
        @media print {{
            .instructions {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="instructions">
        <strong>To save as PDF:</strong> Press <kbd>Cmd+P</kbd> (Mac) or <kbd>Ctrl+P</kbd> (Windows), 
        then select "Save as PDF" as the destination.
    </div>
    <h1>{project_title}</h1>
<pre>{self.last_results}</pre>
</body>
</html>
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                temp_path = f.name
            
            webbrowser.open(f'file://{temp_path}')
            messagebox.showinfo("Export to PDF", 
                "The results have been opened in your browser.\n\n"
                "To save as PDF:\n"
                "1. Press Cmd+P (Mac) or Ctrl+P (Windows)\n"
                "2. Select 'Save as PDF' as the destination\n"
                "3. Click Save")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\\n{str(e)}")
    
    def close_project(self):
        """Close current project"""
        if self.is_modified:
            result = messagebox.askyesnocancel("Save Changes", 
                "Do you want to save changes before closing?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()
        
        # Reset everything
        self.project_name.set("")
        self.user_name.set("")
        self.project_address.set("")
        self.traverse_id.set("")
        self.num_sides.set(4)
        self.generate_fields()
        self.results_text.delete(1.0, tk.END)
        self.current_file = None
        self.is_modified = False
        self.file_label.config(text="File: <new file>")
        self.last_results = ""
    
    def exit_app(self):
        """Exit the application"""
        if self.is_modified:
            result = messagebox.askyesnocancel("Save Changes", 
                "Do you want to save changes before exiting?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()
        
        self.root.destroy()
    
    def check_for_updates(self):
        """Manually check for updates"""
        if UPDATER_AVAILABLE:
            updater.check_for_updates_async(self.root, show_no_update_message=True)
        else:
            messagebox.showerror("Error", "Update module not available.")
    
    def show_about(self):
        """Show about dialog"""
        version = updater.CURRENT_VERSION if UPDATER_AVAILABLE else "1.0.0"
        messagebox.showinfo("About Traverse Calculator",
            f"Traverse Calculator\n"
            f"Version {version}\n\n"
            "A professional tool for polygon traverse calculations\n"
            "with Bowditch adjustment method.\n\n"
            "Features:\n"
            "• Closed traverse calculations\n"
            "• Angular and linear misclosure checks\n"
            "• Bowditch adjustment\n"
            "• English and Metric units\n"
            "• Save/Load traverse files (.trv)\n"
            "• PDF export\n"
            "• Auto-updates from GitHub")


def main():
    root = tk.Tk()
    app = PolygonTraverseCalculator(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    
    root.mainloop()


if __name__ == "__main__":
    main()