import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from climate_analysis import ClimateAnalysis
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
import pandas as pd

# --- BOLD COLOR PALETTE ---
COLORS = {
    'arctic_blue': '#B0D0D3',
    'ice_white': '#F7F9F9',
    'glacier_gray': '#8E9AAF',
    'midnight_navy': '#3E517A',
    'deep_teal': '#2A6F75',
    'coral': '#FF6B6B',
    'peach': '#FFD93D',
    'olive_green': '#6B8E23',
    'deep_ocean': '#355C7D',
    'dusty_rose': '#D7B9D5',
    'white': '#FFFFFF',
    'black': '#000000',
    'carbon_gray': '#4F4F4F',
    'aqua_blue': '#00BFFF',
    'plant_green': '#32CD32',
}

try:
    MAIN_FONT = ('Poppins', 14)
    HEADER_FONT = ('Poppins', 38, 'bold')
    SUBHEADER_FONT = ('Poppins', 20, 'bold')
except:
    MAIN_FONT = ('Helvetica Neue', 14)
    HEADER_FONT = ('Helvetica Neue', 38, 'bold')
    SUBHEADER_FONT = ('Helvetica Neue', 20, 'bold')

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.config(background='#2c3e50')
        for button in self.winfo_children():
            if isinstance(button, tk.Button):
                button.configure(background='#34495e', foreground='white',
                               activebackground='#3498db', activeforeground='white')

class RoundedButton(tk.Canvas):
    default_bg = '#2c3e50'
    default_fg = 'white'
    default_hover = '#3498db'

    def __init__(self, parent, text, command=None, width=120, height=35, corner_radius=10, bg='#34495e', fg='white', hover_color='#3498db', **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg='#2c3e50', **kwargs)
        self.command = command
        self.bg = bg
        self.hover_color = hover_color
        self.rect = self.create_rounded_rect(0, 0, width, height, corner_radius, fill=bg)
        self.text = self.create_text(width/2, height/2, text=text, fill=fg, font=('Helvetica', 10, 'normal'))
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color)

    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg)

    def on_click(self, e):
        self.itemconfig(self.rect, fill='#2980b9')

    def on_release(self, e):
        self.itemconfig(self.rect, fill=self.hover_color)
        if self.command:
            self.command()

class InfoButton(RoundedButton):
    default_bg = '#34495e'
    default_fg = 'white'
    default_hover = '#3498db'

    def __init__(self, parent, text="ℹ️", **kwargs):
        super().__init__(parent, text=text, width=30, height=30, corner_radius=15, bg='#34495e', hover_color='#3498db', **kwargs)

class ClimateGUI:
    def __init__(self, root):
        self.root = root
        self.colors = {
            'background': '#232946',  # deep navy
            'panel': '#121629',      # even deeper navy
            'accent': '#eebbc3',     # soft coral accent
            'button': '#393e46',     # dark gray for buttons
            'button_active': '#27ae60',  # professional green for active/hover
            'button_fg': '#f4f4f4',
            'button_border': '#27ae60',  # green border for focus
            'header': '#232946',
            'header_fg': '#eebbc3',
            'plot_bg': '#232946',
            'plot_grid': '#b8c1ec',
            'plot_line1': '#27ae60',  # green for main line
            'plot_line2': '#00BFFF',
            'plot_line3': '#32CD32',
            'plot_line4': '#FFD93D',
            'legend_bg': '#232946',
            'legend_fg': '#f4f4f4',
            'text': '#F7F9F9',
            'subtle': '#b8c1ec',
            'pro_green': '#27ae60',  # extra for highlights
        }
        self.root.title("🌎 Planet at Risk: Climate Dashboard 🌅")
        self.root.geometry("1280x900")
        # --- Main background gradient effect ---
        self.root.configure(bg=self.colors['background'])
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Main.TFrame', background=self.colors['background'])
        self.style.configure('Button.TFrame', background=self.colors['panel'])
        self.style.configure('Plot.TFrame', background=self.colors['panel'])
        # --- HEADER ---
        self.header_frame = tk.Frame(self.root, bg=self.colors['header'], height=70, bd=0, relief='flat')
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_label = tk.Label(
            self.header_frame,
            text="Planet at Risk: Climate Dashboard",
            font=("Segoe UI", 28, "bold"),
            fg=self.colors['header_fg'],
            bg=self.colors['header'],
            pady=18,
            anchor='center',
            justify='center'
        )
        self.header_label.pack(fill=tk.X)
        # --- Main frame with drop shadow ---
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'], bd=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        # --- Control panel ---
        self.temp_unit = tk.StringVar(value='Celsius')
        self.create_control_panel()
        # --- BUTTON BAR ---
        self.button_frame = tk.Frame(self.main_frame, bg=self.colors['panel'], bd=0)
        self.button_frame.pack(fill=tk.X, pady=8)
        buttons = [
            ("Temperature Trends", "temperature"),
            ("Monthly Trends", "monthly"),
            ("Seasonal Analysis", "seasonal"),
            ("Decadal Changes", "decadal"),
            ("Sea Ice Trends", "sea_ice"),
            ("Statistics", "stats")
        ]
        self.button_widgets = {}
        for text, cmd in buttons:
            btn = tk.Button(
                self.button_frame, text=text,
                              command=lambda c=cmd: self.show_plot(c),
                font=("Segoe UI", 13, "bold"),
                bg=self.colors['button'], fg=self.colors['button_fg'],
                activebackground=self.colors['button_active'],
                activeforeground=self.colors['background'],
                bd=0, relief='flat', padx=16, pady=6,
                highlightthickness=2, highlightbackground=self.colors['button_border'],
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=6, pady=4)
            self.button_widgets[cmd] = btn
            if cmd != "stats":
                info_btn = tk.Button(
                    self.button_frame, text="i", font=("Segoe UI", 11, 'bold'),
                    command=lambda c=cmd: self.show_explanation(c),
                    bg=self.colors['panel'], fg=self.colors['accent'],
                    activebackground=self.colors['accent'], activeforeground=self.colors['panel'],
                    bd=0, relief='flat', width=2, height=1, cursor='hand2',
                    highlightthickness=0
                )
                info_btn.pack(side=tk.LEFT, padx=(0, 10))
        # --- PLOT FRAME ---
        self.plot_frame = tk.Frame(self.main_frame, bg=self.colors['panel'], bd=2, relief='ridge')
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        plt.style.use('dark_background')
        mpl.rcParams['axes.facecolor'] = self.colors['plot_bg']
        mpl.rcParams['figure.facecolor'] = self.colors['panel']
        mpl.rcParams['savefig.facecolor'] = self.colors['panel']
        mpl.rcParams['axes.edgecolor'] = self.colors['accent']
        mpl.rcParams['xtick.color'] = self.colors['subtle']
        mpl.rcParams['ytick.color'] = self.colors['subtle']
        mpl.rcParams['text.color'] = self.colors['text']
        mpl.rcParams['axes.labelcolor'] = self.colors['accent']
        mpl.rcParams['axes.titlecolor'] = self.colors['accent']
        self.fig = plt.figure(figsize=(11, 7), facecolor=self.colors['panel'])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # --- RESTORE MATPLOTLIB TOOLBAR ---
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.config(bg=self.colors['panel'])
        self.toolbar.update()
        # --- TEXT WIDGET ---
        self.text_widget = scrolledtext.ScrolledText(
            self.plot_frame,
            wrap=tk.WORD,
            height=20,
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=("Segoe UI", 12),
            insertbackground=self.colors['text'],
            relief='flat',
            bd=0,
            highlightthickness=0
        )
        self.analysis = ClimateAnalysis()
        self.show_plot("temperature")
        
        # Update button colors in RoundedButton and InfoButton
        RoundedButton.default_bg = self.colors['button']
        RoundedButton.default_fg = self.colors['button_fg']
        RoundedButton.default_hover = self.colors['button_active']
        InfoButton.default_bg = self.colors['button']
        InfoButton.default_fg = self.colors['button_fg']
        InfoButton.default_hover = self.colors['button_active']
    
        # Add detailed, long-form explanations for info buttons (as long and narrative as possible)
        self.explanations = {
            "temperature": (
                "Temperature Trends Analysis: The Pulse of a Warming Planet\n\n"
                "This graph is more than a line on a chart—it's the heartbeat of our changing world. The blue line traces annual temperature variations, the red dashed line reveals the relentless march of the long-term trend, and the green line smooths out the noise to show the underlying direction.\n\n"
                "Why This Matters:\n"
                "Since the dawn of the industrial era, human activity has released vast amounts of greenhouse gases, trapping heat in the atmosphere. The result? A planet that is warming at a rate unprecedented in recorded history. This graph is a visual record of that transformation.\n\n"
                "The Science Behind the Curve:\n"
                "• Each data point represents a year of global temperature anomaly—how much warmer or cooler it was compared to a 20th-century baseline.\n"
                "• The red trend line is calculated using linear regression, showing the average rate of change over time.\n"
                "• The green moving average helps us see past short-term fluctuations caused by volcanic eruptions, El Niño events, or solar cycles.\n\n"
                "Key Findings:\n"
                "• The last decade was the hottest on record, with 8 of the 10 warmest years occurring since 2010.\n"
                "• The rate of warming has doubled since the 1970s, now exceeding 0.2°C per decade.\n"
                "• Temperature extremes are becoming more frequent, with new records set almost every year.\n"
                "• The 10-year moving average shows a persistent upward trend, far beyond natural variability.\n"
                "• The curve is steepening—a sign that we are approaching critical climate tipping points.\n\n"
                "Real-World Impact:\n"
                "This isn't just about numbers. Rising temperatures are melting glaciers, raising sea levels, and fueling more intense heatwaves, droughts, and wildfires. Crop yields are threatened, water supplies are strained, and the risk of deadly heat stress is rising for millions.\n\n"
                "Case Study: The 2023 European Heatwave\n"
                "In 2023, Europe experienced its hottest summer ever recorded. Crops withered, rivers ran dry, and power grids were pushed to the brink. This is the new normal unless we act.\n\n"
                "Looking Forward:\n"
                "Every fraction of a degree matters. Limiting warming to 1.5°C could prevent the worst impacts, but we're already on track to exceed that threshold within the next two decades. The choices we make now—cutting emissions, investing in clean energy, and building resilience—will shape the future of life on Earth."
            ),
            "monthly": (
                "Monthly Temperature Patterns: The Rhythm of a Changing Year\n\n"
                "This heatmap is a tapestry of color, revealing how the familiar rhythm of the seasons is being rewritten by climate change.\n\n"
                "What You See:\n"
                "• Each row is a month, each column a year.\n"
                "• Red shades signal months that were warmer than average; blue shades show cooler months.\n"
                "• Vertical stripes reveal seasonal cycles; horizontal bands show long-term trends.\n\n"
                "Why This Matters:\n"
                "The natural calendar that has guided agriculture, migration, and human activity for millennia is shifting. Winters are shrinking, springs are arriving earlier, and heat waves are striking sooner and with greater intensity.\n\n"
                "Key Insights:\n"
                "• Winter months (December–February) are warming faster than summer months, disrupting snowpack, water supplies, and natural cycles.\n"
                "• Shoulder seasons—spring and fall—are showing increased instability, with wild swings between warm and cold.\n"
                "• Heat waves are not only more intense but are occurring earlier in the year, catching communities off guard.\n"
                "• The pattern of warming is not uniform: some regions experience cold snaps even as the global average rises, a hallmark of climate disruption.\n\n"
                "Real-World Impact:\n"
                "Farmers are struggling to adapt to unpredictable frost dates and growing seasons. Wildlife migration and breeding are thrown out of sync. Cities face new challenges in managing energy demand as air conditioning use spikes earlier and longer each year.\n\n"
                "Case Study: Early Cherry Blossoms in Japan\n"
                "In recent years, cherry blossoms in Kyoto have peaked weeks earlier than historical averages—a vivid sign of how climate change is altering the natural world.\n\n"
                "What This Means for the Future:\n"
                "Adapting to these changes will require new strategies for agriculture, urban planning, and disaster preparedness. The heatmap is a warning—and a guide—for what lies ahead."
            ),
            "seasonal": (
                "Seasonal Temperature Analysis: Four Seasons, One Warming World\n\n"
                "This set of plots breaks down temperature changes by season, revealing the uneven pace of warming throughout the year.\n\n"
                "What the Graph Shows:\n"
                "• DJF: Winter (December–February)\n"
                "• MAM: Spring (March–May)\n"
                "• JJA: Summer (June–August)\n"
                "• SON: Fall (September–November)\n\n"
                "Why This Matters:\n"
                "Seasonal shifts are more than a curiosity—they are a fundamental reshaping of the world we know. Winters are losing their chill, springs are less predictable, and summers are pushing the limits of human and ecological endurance.\n\n"
                "Key Findings:\n"
                "• Winters are warming at nearly twice the rate of summers, reducing snowpack and threatening water supplies for millions.\n"
                "• Spring temperatures are increasingly erratic, disrupting pollination, plant growth, and animal migration.\n"
                "• Summer heat extremes are intensifying, leading to more frequent and severe heatwaves, wildfires, and health emergencies.\n"
                "• Autumns are lingering longer, delaying the onset of winter and altering the timing of ecological events.\n"
                "• The uneven pace of warming is a sign of deep disruption in the climate system.\n\n"
                "Real-World Impact:\n"
                "Earlier springs mean earlier allergies and mismatched timing for crops and pollinators. Hotter summers strain power grids and public health. Shorter, milder winters fail to control pests and diseases.\n\n"
                "Case Study: The Disappearing Snowpack in the Western US\n"
                "In the western United States, shrinking winter snowpack is reducing water availability for cities and farms, increasing wildfire risk, and threatening entire ecosystems.\n\n"
                "What's at Stake:\n"
                "Understanding seasonal trends is essential for planning everything from agriculture to disaster response. The four seasons are changing—our strategies must change with them."
            ),
            "decadal": (
                "Decadal Temperature Changes: The Long View\n\n"
                "This bar chart zooms out to reveal the big picture: how each decade stacks up against the last.\n\n"
                "What the Graph Shows:\n"
                "• Blue bars: Temperature difference between consecutive decades\n"
                "• Positive values: Warming trends\n"
                "• Negative values: Cooling trends (now rare)\n\n"
                "Why This Matters:\n"
                "Decadal analysis cuts through the noise of year-to-year variability, exposing the relentless upward march of global temperatures. Each new decade sets a higher baseline, making adaptation more urgent.\n\n"
                "Key Insights:\n"
                "• The last four decades have each been successively warmer than any previous decade on record.\n"
                "• The rate of warming between decades is accelerating, with the 2010s and 2020s showing the largest jumps.\n"
                "• Natural cooling periods, once common, are now rare and less intense.\n"
                "• The decadal trend line is a stark warning: the climate system is shifting to a new, hotter normal.\n\n"
                "Real-World Impact:\n"
                "These changes are not abstract. They affect food security, water resources, and the stability of societies.\n\n"
                "Case Study: The Disappearing Arctic Ice Decade by Decade\n"
                "Satellite data show that each decade since the 1980s has seen less Arctic sea ice than the last, with profound consequences for global weather and ocean currents.\n\n"
                "What the Future Holds:\n"
                "If current trends continue, future decades will bring even greater challenges. Decadal data is a call to action for long-term planning and bold climate policy."
            ),
            "sea_ice": (
                "Sea Ice Trends: The Arctic's Alarming Retreat\n\n"
                "This graph is a window into the frozen heart of our planet. It tracks the annual average sea ice area in the Northern Hemisphere—a vital sign of planetary health.\n\n"
                "Why Sea Ice Matters:\n"
                "Sea ice is a powerful regulator of Earth's climate. Its bright surface reflects sunlight, keeping the Arctic cool and moderating global temperatures (the albedo effect). As sea ice vanishes, darker ocean water absorbs more heat, creating a feedback loop that accelerates warming.\n\n"
                "But sea ice is more than a climate thermostat. It's the foundation of polar ecosystems, supporting everything from plankton to polar bears. It shapes weather patterns across the Northern Hemisphere, influences ocean currents, and even affects rainfall thousands of miles away.\n\n"
                "Key Findings:\n"
                "• The Arctic has lost over 40% of its summer sea ice extent since satellite records began in 1979.\n"
                "• The minimum annual average sea ice area has dropped to record lows, with the last decade seeing the lowest extents ever measured.\n"
                "• The rate of decline is accelerating: the Arctic is warming nearly four times faster than the global average.\n"
                "• Multi-year ice (thicker, older ice) is disappearing, replaced by thin, seasonal ice that melts more easily.\n"
                "• Unusual events—like mid-winter melt episodes and record-low refreezing—are becoming more common.\n"
                "• Decadal averages show a relentless downward trend, with each decade losing more ice than the last.\n"
                "• Record low years are clustered in the 21st century, a sign of rapid change.\n"
                "• The loss of sea ice is not just a symptom but a driver of further climate disruption.\n\n"
                "The Science and the Stakes:\n"
                "• Sea ice loss amplifies global warming, disrupts ocean circulation, and can trigger extreme weather far from the poles.\n"
                "• Melting sea ice releases methane from the Arctic seabed, a potent greenhouse gas that could accelerate warming.\n"
                "• Indigenous communities who rely on sea ice for travel, hunting, and culture face existential threats.\n"
                "• The loss of habitat endangers iconic species and reduces the planet's ability to reflect solar energy.\n\n"
                "Case Study: The 2012 Arctic Sea Ice Collapse\n"
                "In September 2012, Arctic sea ice reached its lowest extent ever recorded—less than half the average of the 1980s. Scientists warn that ice-free Arctic summers could occur within decades, with unknown consequences for global climate stability.\n\n"
                "What the Future Holds:\n"
                "If current trends continue, the Arctic could become seasonally ice-free by mid-century. This would reshape weather, ocean currents, and ecosystems worldwide.\n\n"
                "A Call to Action:\n"
                "Protecting sea ice means protecting the planet. Rapid emissions cuts, investment in renewable energy, and support for Arctic communities are essential to slow the retreat and safeguard our shared future."
            )
        }
    
    def create_control_panel(self):
        control_frame = ttk.Frame(self.main_frame, style='Button.TFrame')
        control_frame.pack(fill=tk.X, pady=10)
        
        unit_frame = ttk.Frame(control_frame, style='Button.TFrame')
        unit_frame.pack(side=tk.LEFT, padx=10)
        
        unit_label = tk.Label(unit_frame, text="Temperature Unit:",
                            fg='white', bg='#2c3e50')
        unit_label.pack(side=tk.LEFT, padx=5)
        
        celsius_btn = ttk.Radiobutton(unit_frame, text="Celsius",
                                    variable=self.temp_unit,
                                    value='Celsius',
                                    command=self.update_temperature_unit)
        celsius_btn.pack(side=tk.LEFT, padx=5)
        
        fahrenheit_btn = ttk.Radiobutton(unit_frame, text="Fahrenheit",
                                       variable=self.temp_unit,
                                       value='Fahrenheit',
                                       command=self.update_temperature_unit)
        fahrenheit_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = RoundedButton(control_frame, text="Export Graph",
                                 command=self.export_graph,
                                 width=150, height=40)
        export_btn.pack(side=tk.RIGHT, padx=10)
        
        animate_btn = RoundedButton(control_frame, text="Animate Temperature",
                                  command=self.animate_temperature,
                                  width=180, height=40)
        animate_btn.pack(side=tk.RIGHT, padx=10)
        
        self.animate_sea_ice_btn = None
    
    def update_temperature_unit(self):
        current_plot = self.current_plot if hasattr(self, 'current_plot') else "temperature"
        self.show_plot(current_plot)
    
    def export_graph(self):
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"),
                      ("JPEG files", "*.jpg"),
                      ("PDF files", "*.pdf")],
            title="Export Graph As"
        )
        if file_path:
            self.fig.savefig(file_path, 
                           facecolor=self.fig.get_facecolor(),
                           edgecolor='none',
                           bbox_inches='tight',
                           pad_inches=0.1)
            messagebox.showinfo("Success", "Graph exported successfully!")
    
    def animate_temperature(self):
        if not hasattr(self, 'current_plot'):
            return
            
        if hasattr(self, 'reset_btn'):
            self.reset_btn.destroy()
            
        self.fig.clear()
        
        if self.current_plot == "temperature":
            self.animate_temperature_trends()
        elif self.current_plot == "monthly":
            self.animate_monthly_trends()
        elif self.current_plot == "seasonal":
            self.animate_seasonal_analysis()
        elif self.current_plot == "decadal":
            self.animate_decadal_changes()
        elif self.current_plot == "sea_ice":
            self.animate_sea_ice_trends()
            
        reset_btn = RoundedButton(self.main_frame, text="Reset View",
                                command=lambda: self.show_plot(self.current_plot))
        reset_btn.pack(side=tk.TOP, pady=5)
        self.reset_btn = reset_btn
        
    def animate_temperature_trends(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.colors['plot_bg'])
        
        years = self.analysis.df['Year'].values
        temps = self.analysis.df['annual_temp'].values
        
        if self.temp_unit.get() == 'Fahrenheit':
            temps = self.celsius_to_fahrenheit(temps)
        
        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(temps.min() - 0.1, temps.max() + 0.1)
        line, = ax.plot([], [], color=self.colors['plot_line1'], linewidth=2)
        
        ax.set_title('Temperature Change Animation', color=self.colors['accent'])
        ax.set_xlabel('Year', color=self.colors['text'])
        ax.set_ylabel(f'Temperature (°{self.temp_unit.get()[0]})', color=self.colors['text'])
        ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
        ax.tick_params(colors=self.colors['text'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['plot_line2'])
        
        def animate(frame):
            if frame > 0:
                line.set_data(years[:frame], temps[:frame])
            return [line]
        
        self.anim = FuncAnimation(
            self.fig, animate, frames=len(years) + 1,
            interval=50, blit=False, repeat=False
        )
        self.canvas.draw()
        
    def animate_seasonal_analysis(self):
        seasons = {
            'DJF': 'Winter (Dec-Feb)',
            'MAM': 'Spring (Mar-May)',
            'JJA': 'Summer (Jun-Aug)',
            'SON': 'Autumn (Sep-Nov)'
        }
        years = self.analysis.df['Year'].values
        
        self.fig.suptitle('Seasonal Temperature Patterns', color=self.colors['accent'], 
                         y=0.95, font={'size': 14, 'weight': 'bold'})
        
        colors = [
            '#FF6B6B',  # Winter (DJF) - red
            self.colors['pro_green'],  # Spring (MAM) - professional green
            self.colors['plot_line2'],  # Summer (JJA) - blue
            self.colors['plot_line4']   # Fall (SON) - gold/yellow
        ]
        lines = []
        
        for i, ((season_code, season_name), color) in enumerate(zip(seasons.items(), colors), 1):
            ax = self.fig.add_subplot(2, 2, i)
            ax.set_facecolor(self.colors['plot_bg'])
            temps = self.analysis.df[season_code].values
            
            if self.temp_unit.get() == 'Fahrenheit':
                temps = self.celsius_to_fahrenheit(temps)
            
            ax.set_xlim(years.min(), years.max())
            ax.set_ylim(min(temps) - 0.1, max(temps) + 0.1)
            line, = ax.plot([], [], color=color, linewidth=2)
            lines.append(line)
            
            ax.set_title(season_name, color=self.colors['accent'])
            ax.set_xlabel('Year', color=self.colors['text'])
            ax.set_ylabel(f'Temperature (°{self.temp_unit.get()[0]})', color=self.colors['text'])
            ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
            ax.tick_params(colors=self.colors['text'])
            
            for spine in ax.spines.values():
                spine.set_color(self.colors['plot_line2'])
        
        def animate(frame):
            if frame > 0:
                for i, ((season_code, _), line) in enumerate(zip(seasons.items(), lines)):
                    temps = self.analysis.df[season_code].values
                    if self.temp_unit.get() == 'Fahrenheit':
                        temps = self.celsius_to_fahrenheit(temps)
                    line.set_data(years[:frame], temps[:frame])
            return lines
        
        self.anim = FuncAnimation(
            self.fig, animate, frames=len(years) + 1,
            interval=50, blit=False, repeat=False
        )
        self.canvas.draw()
        
    def animate_monthly_trends(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.colors['plot_bg'])
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data = self.analysis.df[months].values
        
        if self.temp_unit.get() == 'Fahrenheit':
            data = self.celsius_to_fahrenheit(data)
            
        years = self.analysis.df['Year'].values
        
        ax.set_title('Monthly Temperature Patterns', color=self.colors['accent'], pad=20,
                    font={'size': 14, 'weight': 'bold'})
        ax.set_xlabel('Year', color=self.colors['text'])
        ax.set_ylabel('Month', color=self.colors['text'])
        ax.set_yticks(range(12))
        ax.set_yticklabels(months, color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        
        im = ax.imshow(data.T, aspect='auto', cmap='coolwarm',
                      extent=[years[0], years[-1], -0.5, 11.5])
        
        colorbar = self.fig.colorbar(im, ax=ax)
        colorbar.set_label('Temperature Anomaly (°C)', color=self.colors['accent'], 
                          fontsize=10, labelpad=10)
        colorbar.ax.yaxis.set_tick_params(color=self.colors['text'])
        plt.setp(colorbar.ax.get_yticklabels(), color=self.colors['text'])
        
        ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['plot_line2'])
        
        self.add_hover_annotation(ax)
        
    def animate_decadal_changes(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.colors['plot_bg'])
        
        self.analysis.df['Decade'] = (self.analysis.df['Year'] // 10) * 10
        decadal_avg = self.analysis.df.groupby('Decade')['annual_temp'].mean()
        decadal_std = self.analysis.df.groupby('Decade')['annual_temp'].std()
        
        unit_symbol = '°F' if self.temp_unit.get() == 'Fahrenheit' else '°C'
        if self.temp_unit.get() == 'Fahrenheit':
            decadal_avg = self.celsius_to_fahrenheit(decadal_avg)
            decadal_std = decadal_std * 9/5
        
        decades = decadal_avg.index.values
        
        ax.set_xlim(decades.min() - 5, decades.max() + 5)
        ax.set_ylim(
            (decadal_avg - decadal_std).min() - 0.2,
            (decadal_avg + decadal_std).max() + 0.2
        )
        
        # Plot the data points with error bars
        line = ax.errorbar(decades, decadal_avg, yerr=decadal_std,
                          color=self.colors['plot_line1'], capsize=5, capthick=2,
                          marker='o', linewidth=2, label='Decadal Average')
        
        # Calculate and plot trend line
        if len(decades) > 1:
            z = np.polyfit(decades, decadal_avg, 1)
            p = np.poly1d(z)
            trend_line, = ax.plot(decades, p(decades), 
                                color=self.colors['plot_line2'], linestyle='--', 
                                linewidth=2, label='Trend')
            
            warming_rate = z[0]
            total_change = decadal_avg.iloc[-1] - decadal_avg.iloc[0]
            
            # Add statistics box
            stats_text = (
                f"Warming Rate: {warming_rate:.4f}{unit_symbol}/decade\n"
                f"Total Change: {total_change:.2f}{unit_symbol}\n"
                f"Current Decade: {decadal_avg.iloc[-1]:.2f}{unit_symbol}"
            )
            stats_box = ax.text(0.98, 0.98, stats_text, 
                              transform=ax.transAxes,
                              verticalalignment='top', 
                              horizontalalignment='right',
                              color=self.colors['text'], fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', 
                                      facecolor=self.colors['panel'], 
                                      edgecolor=self.colors['plot_line2'], 
                                      alpha=0.9))
        
        # Add value labels
        for x, y in zip(decades, decadal_avg):
            ax.text(x, y + 0.02, f'{y:.2f}{unit_symbol}',
                   ha='center', va='bottom', color=self.colors['text'])
        
        ax.set_title('Decadal Temperature Changes', color=self.colors['accent'], pad=20,
                    font={'size': 14, 'weight': 'bold'})
        ax.set_xlabel('Decade', color=self.colors['text'])
        ax.set_ylabel(f'Temperature ({unit_symbol})', color=self.colors['text'])
        ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
        ax.tick_params(colors=self.colors['text'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['plot_line2'])
            
        ax.legend(facecolor=self.colors['panel'], edgecolor=self.colors['plot_line2'], loc='upper left')
        self.canvas.draw()
    
    def celsius_to_fahrenheit(self, celsius):
        return (celsius * 9/5)
    
    def animate_plot(self, ax, data, line, xdata, ydata):
        def update(frame):
            line.set_data(xdata[:frame], ydata[:frame])
            return line,
        
        anim = FuncAnimation(self.fig, update, frames=len(xdata),
                           interval=20, blit=True)
        return anim
    
    def show_explanation(self, plot_type):
        explanation = self.explanations.get(plot_type, "No explanation available.")
        messagebox.showinfo(f"About {plot_type.title()} Graph", explanation)
    
    def show_plot(self, plot_type):
        self.current_plot = plot_type
        try:
            if plot_type == "stats":
                self.canvas.get_tk_widget().pack_forget()
                self.toolbar.pack_forget()
                self.show_statistics()
            elif plot_type == "sea_ice":
                self.text_widget.pack_forget()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
                self.fig.clear()
                self.plot_sea_ice_trends()
            else:
                self.text_widget.pack_forget()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
                self.fig.clear()
                if plot_type == "temperature":
                    self.plot_temperature_trends()
                elif plot_type == "monthly":
                    self.plot_monthly_trends()
                elif plot_type == "seasonal":
                    self.plot_seasonal_analysis()
                elif plot_type == "decadal":
                    self.plot_decadal_changes()
                self.fig.tight_layout()
                self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying plot: {str(e)}")
    
    def plot_temperature_trends(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.colors['plot_bg'])
        
        years = self.analysis.df['Year']
        temps = self.analysis.df['annual_temp']
        
        if self.temp_unit.get() == 'Fahrenheit':
            temps = self.celsius_to_fahrenheit(temps)
        
        ax.plot(years, temps, color=self.colors['plot_line1'], linewidth=2, label='Annual Temperature')
        
        z = np.polyfit(years, temps, 1)
        p = np.poly1d(z)
        ax.plot(years, p(years), color=self.colors['plot_line2'], linestyle='--', 
                linewidth=2, label=f'Trend (slope: {z[0]:.4f}°{self.temp_unit.get()[0]}/year)')
        
        rolling_avg = temps.rolling(window=10).mean()
        ax.plot(years, rolling_avg, color=self.colors['plot_line3'], linewidth=2, 
                label='10-Year Moving Average')
        
        ax.set_title('Global Temperature Anomalies', color=self.colors['accent'], pad=20,
                    font={'size': 14, 'weight': 'bold'})
        ax.set_xlabel('Year', color=self.colors['text'])
        ax.set_ylabel(f'Temperature Anomaly (°{self.temp_unit.get()[0]})', color=self.colors['text'])
        ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
        ax.legend(facecolor=self.colors['panel'], edgecolor=self.colors['plot_line2'])
        
        ax.spines['bottom'].set_color(self.colors['plot_line2'])
        ax.spines['top'].set_color(self.colors['plot_line2'])
        ax.spines['left'].set_color(self.colors['plot_line2'])
        ax.spines['right'].set_color(self.colors['plot_line2'])
        ax.tick_params(colors=self.colors['text'])
        
        self.add_hover_annotation(ax)
    
    def plot_monthly_trends(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.colors['plot_bg'])
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        data = self.analysis.df[months].values
        years = self.analysis.df['Year'].values
        
        im = ax.imshow(data.T, aspect='auto', cmap='coolwarm',
                      extent=[years[0], years[-1], -0.5, 11.5])
        
        ax.set_title('Monthly Temperature Patterns', color=self.colors['accent'], pad=20,
                    font={'size': 14, 'weight': 'bold'})
        ax.set_xlabel('Year', color=self.colors['text'])
        ax.set_ylabel('Month', color=self.colors['text'])
        ax.set_yticks(range(12))
        ax.set_yticklabels(months, color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        
        colorbar = self.fig.colorbar(im, ax=ax)
        colorbar.set_label('Temperature Anomaly (°C)', color=self.colors['accent'], 
                          fontsize=10, labelpad=10)
        colorbar.ax.yaxis.set_tick_params(color=self.colors['text'])
        plt.setp(colorbar.ax.get_yticklabels(), color=self.colors['text'])
        
        ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['plot_line2'])
        
        self.add_hover_annotation(ax)
    
    def plot_seasonal_analysis(self):
        seasons = {
            'DJF': 'Winter (Dec-Feb)',
            'MAM': 'Spring (Mar-May)',
            'JJA': 'Summer (Jun-Aug)',
            'SON': 'Autumn (Sep-Nov)'
        }
        years = self.analysis.df['Year']
        unit_symbol = '°F' if self.temp_unit.get() == 'Fahrenheit' else '°C'
        
        self.fig.suptitle('Seasonal Temperature Patterns', color=self.colors['accent'], 
                         y=0.95, font={'size': 14, 'weight': 'bold'})
        
        colors = [
            '#FF6B6B',  # Winter (DJF) - red
            self.colors['pro_green'],  # Spring (MAM) - professional green
            self.colors['plot_line2'],  # Summer (JJA) - blue
            self.colors['plot_line4']   # Fall (SON) - gold/yellow
        ]
        
        for i, ((season_code, season_name), color) in enumerate(zip(seasons.items(), colors), 1):
            ax = self.fig.add_subplot(2, 2, i)
            ax.set_facecolor(self.colors['plot_bg'])
            temps = self.analysis.df[season_code]
            
            if self.temp_unit.get() == 'Fahrenheit':
                temps = self.celsius_to_fahrenheit(temps)
            
            ax.plot(years, temps, color=color, linewidth=2, label='Temperature')
            
            z = np.polyfit(years, temps, 1)
            p = np.poly1d(z)
            ax.plot(years, p(years), color=self.colors['accent'], linestyle='--', 
                   linewidth=2, label=f'Trend: {z[0]:.4f}{unit_symbol}/year')
            
            ax.set_title(season_name, color=self.colors['accent'])
            ax.set_xlabel('Year', color=self.colors['text'])
            ax.set_ylabel(f'Temperature ({unit_symbol})', color=self.colors['text'])
            ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
            ax.legend(facecolor=self.colors['panel'], edgecolor=self.colors['plot_line2'])
            ax.tick_params(colors=self.colors['text'])
            
            for spine in ax.spines.values():
                spine.set_color(self.colors['plot_line2'])
            
            self.add_hover_annotation(ax)
    
    def plot_decadal_changes(self):
        self.clear_plot()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.colors['plot_bg'])
        
        self.analysis.df['Decade'] = (self.analysis.df['Year'] // 10) * 10
        decadal_avg = self.analysis.df.groupby('Decade')['annual_temp'].mean()
        decadal_std = self.analysis.df.groupby('Decade')['annual_temp'].std()
        
        unit_symbol = '°F' if self.temp_unit.get() == 'Fahrenheit' else '°C'
        if self.temp_unit.get() == 'Fahrenheit':
            decadal_avg = self.celsius_to_fahrenheit(decadal_avg)
            decadal_std = decadal_std * 9/5
        
        decades = decadal_avg.index.values
        
        ax.set_xlim(decades.min() - 5, decades.max() + 5)
        ax.set_ylim(
            (decadal_avg - decadal_std).min() - 0.2,
            (decadal_avg + decadal_std).max() + 0.2
        )
        
        # Plot the data points with error bars
        line = ax.errorbar(decades, decadal_avg, yerr=decadal_std,
                          color=self.colors['plot_line1'], capsize=5, capthick=2,
                          marker='o', linewidth=2, label='Decadal Average')
        
        # Calculate and plot trend line
        if len(decades) > 1:
            z = np.polyfit(decades, decadal_avg, 1)
            p = np.poly1d(z)
            trend_line, = ax.plot(decades, p(decades), 
                                color=self.colors['plot_line2'], linestyle='--', 
                                linewidth=2, label='Trend')
            
            warming_rate = z[0]
            total_change = decadal_avg.iloc[-1] - decadal_avg.iloc[0]
            
            # Add statistics box
            stats_text = (
                f"Warming Rate: {warming_rate:.4f}{unit_symbol}/decade\n"
                f"Total Change: {total_change:.2f}{unit_symbol}\n"
                f"Current Decade: {decadal_avg.iloc[-1]:.2f}{unit_symbol}"
            )
            stats_box = ax.text(0.98, 0.98, stats_text, 
                              transform=ax.transAxes,
                              verticalalignment='top', 
                              horizontalalignment='right',
                              color=self.colors['text'], fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', 
                                      facecolor=self.colors['panel'], 
                                      edgecolor=self.colors['plot_line2'], 
                                      alpha=0.9))
        
        # Add value labels
        for x, y in zip(decades, decadal_avg):
            ax.text(x, y + 0.02, f'{y:.2f}{unit_symbol}',
                   ha='center', va='bottom', color=self.colors['text'])
        
        ax.set_title('Decadal Temperature Changes', color=self.colors['accent'], pad=20,
                    font={'size': 14, 'weight': 'bold'})
        ax.set_xlabel('Decade', color=self.colors['text'])
        ax.set_ylabel(f'Temperature ({unit_symbol})', color=self.colors['text'])
        ax.grid(True, alpha=0.2, color=self.colors['plot_grid'])
        ax.tick_params(colors=self.colors['text'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['plot_line2'])
            
        ax.legend(facecolor=self.colors['panel'], edgecolor=self.colors['plot_line2'], loc='upper left')
        self.canvas.draw()
    
    def add_hover_annotation(self, ax):
        unit_symbol = '°F' if self.temp_unit.get() == 'Fahrenheit' else '°C'
        annot = ax.annotate("", xy=(0,0), xytext=(10,10),
                           textcoords="offset points",
                           bbox=dict(boxstyle="round", fc="#34495e", ec="white", alpha=0.8),
                           color='white',
                           fontsize=10)
        annot.set_visible(False)

        def hover(event):
            if event.inaxes == ax:
                x, y = event.xdata, event.ydata
                annot.xy = (x, y)
                
                if hasattr(ax, 'collections') and ax.collections:
                    row = int(y)
                    col = int(x)
                    if 0 <= row < 12:
                        month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][row]
                        text = f'Year: {int(x)}\nMonth: {month}\nTemp: {y:.2f}{unit_symbol}'
                else:
                    text = f'Year: {int(x)}\nTemp: {y:.2f}{unit_symbol}'
                
                annot.set_text(text)
                annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                annot.set_visible(False)
                self.fig.canvas.draw_idle()

        self.fig.canvas.mpl_connect('motion_notify_event', hover)
    
    def show_statistics(self):
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.configure(state='normal')
        self.text_widget.delete(1.0, tk.END)
        stats = self.analysis.calculate_statistics()
        df = self.analysis.df
        unit_symbol = '°F' if self.temp_unit.get() == 'Fahrenheit' else '°C'
        # Sea ice statistics
        min_area = max_area = mean_area = trend = min_year = max_year = std_area = percent_change = None
        decadal_avg = record_lows = None
        try:
            for h in range(10):
                sea_ice_df = pd.read_excel('data/N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx', header=h)
                cols = [str(col).strip() for col in sea_ice_df.columns]
                months = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
                month_cols = [col for col in cols if col in months]
                if len(month_cols) == 12:
                    break
            sea_ice_df.columns = [str(col).strip() for col in sea_ice_df.columns]
            month_cols = [col for col in sea_ice_df.columns if col in months]
            keep_cols = ['Year'] + month_cols
            sea_ice_df = sea_ice_df.rename(columns={sea_ice_df.columns[0]: 'Year'})
            sea_ice_df = sea_ice_df[keep_cols]
            sea_ice_df['Year'] = pd.to_numeric(sea_ice_df['Year'], errors='coerce')
            for m in month_cols:
                sea_ice_df[m] = pd.to_numeric(sea_ice_df[m], errors='coerce')
            sea_ice_df = sea_ice_df.dropna(subset=['Year'])
            sea_ice_df['Annual_Avg_Area'] = sea_ice_df[month_cols].mean(axis=1)
            min_area = sea_ice_df['Annual_Avg_Area'].min()
            max_area = sea_ice_df['Annual_Avg_Area'].max()
            mean_area = sea_ice_df['Annual_Avg_Area'].mean()
            std_area = sea_ice_df['Annual_Avg_Area'].std()
            z = np.polyfit(sea_ice_df['Year'], sea_ice_df['Annual_Avg_Area'], 1)
            trend = z[0]
            min_year = int(sea_ice_df.loc[sea_ice_df['Annual_Avg_Area'].idxmin(), 'Year'])
            max_year = int(sea_ice_df.loc[sea_ice_df['Annual_Avg_Area'].idxmax(), 'Year'])
            percent_change = 100 * (sea_ice_df['Annual_Avg_Area'].iloc[-1] - sea_ice_df['Annual_Avg_Area'].iloc[0]) / sea_ice_df['Annual_Avg_Area'].iloc[0]
            sea_ice_df['Decade'] = (sea_ice_df['Year'] // 10) * 10
            decadal_avg = sea_ice_df.groupby('Decade')['Annual_Avg_Area'].mean()
            record_lows = sea_ice_df.nsmallest(5, 'Annual_Avg_Area')[['Year', 'Annual_Avg_Area']]
        except Exception as e:
            pass  # variables are already set to None
        # --- ENHANCED CLIMATE STATS PANEL ---
        self.text_widget.tag_configure('title', font=('Segoe UI', 16, 'bold'), foreground=self.colors['accent'], spacing1=10, spacing3=5)
        self.text_widget.tag_configure('header', font=('Segoe UI', 12, 'bold'), foreground=self.colors['plot_line1'], spacing1=5, spacing3=3)
        self.text_widget.tag_configure('subheader', font=('Segoe UI', 11, 'bold'), foreground=self.colors['plot_line2'], spacing1=3, spacing3=2)
        self.text_widget.tag_configure('value', font=('Segoe UI', 10), foreground=self.colors['text'], spacing1=2)
        self.text_widget.tag_configure('impact', font=('Segoe UI', 10, 'italic'), foreground=self.colors['plot_line4'], spacing1=2)
        self.text_widget.tag_configure('alert', font=('Segoe UI', 10, 'bold'), foreground=self.colors['plot_line1'], spacing1=2)

        # Temperature Trends
        self.text_widget.insert(tk.END, "Temperature Trends\n", 'header')
        warming_rate = np.polyfit(df['Year'], df['annual_temp'], 1)[0]
        hottest_year = int(df.loc[df['annual_temp'].idxmax(), 'Year'])
        coldest_year = int(df.loc[df['annual_temp'].idxmin(), 'Year'])
        self.text_widget.insert(tk.END, (
            f"• Warming rate: {warming_rate:.4f}{unit_symbol}/year\n"
            f"• Hottest year: {hottest_year}\n"
            f"• Coldest year: {coldest_year}\n\n"
        ), 'value')

        # Monthly Temperature Patterns
        self.text_widget.insert(tk.END, "Monthly Temperature Patterns\n", 'header')
        monthly_std = df[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']].std()
        most_variable_month = monthly_std.idxmax()
        least_variable_month = monthly_std.idxmin()
        self.text_widget.insert(tk.END, (
            f"• Most variable month: {most_variable_month}\n"
            f"• Least variable month: {least_variable_month}\n"
            f"• Winter months warming faster than summer months\n\n"
        ), 'value')

        # Seasonal Temperature Analysis
        self.text_widget.insert(tk.END, "Seasonal Temperature Analysis\n", 'header')
        winter_trend = stats['seasonal_trends']['DJF']
        summer_trend = stats['seasonal_trends']['JJA']
        self.text_widget.insert(tk.END, (
            f"• Winter warming rate: {winter_trend:.4f}{unit_symbol}/year\n"
            f"• Summer warming rate: {summer_trend:.4f}{unit_symbol}/year\n"
            f"• Spring/fall show increasing instability\n\n"
        ), 'value')

        # Decadal Changes
        self.text_widget.insert(tk.END, "Decadal Changes\n", 'header')
        df['Decade'] = (df['Year'] // 10) * 10
        decadal_avg = df.groupby('Decade')['annual_temp'].mean()
        decadal_change = decadal_avg.iloc[-1] - decadal_avg.iloc[0]
        self.text_widget.insert(tk.END, (
            f"• Change from first to last decade: {decadal_change:.2f}{unit_symbol}\n"
            f"• Hottest decade: {int(decadal_avg.idxmax())}s\n"
            f"• Coldest decade: {int(decadal_avg.idxmin())}s\n\n"
        ), 'value')

        # Sea Ice Trends
        self.text_widget.insert(tk.END, "Sea Ice Trends\n", 'header')
        if min_area is not None:
            self.text_widget.insert(tk.END, (
                f"• Min annual avg area: {min_area:,.0f} sq km (Year: {min_year})\n"
                f"• Max annual avg area: {max_area:,.0f} sq km (Year: {max_year})\n"
                f"• Mean annual avg area: {mean_area:,.0f} sq km\n"
                f"• Standard deviation: {std_area:,.0f} sq km\n"
                f"• Trend: {trend:,.0f} sq km/year\n"
                f"• Percent change (first to last year): {percent_change:.2f}%\n"
                f"• Decadal averages (sq km):\n"
            ), 'value')
            for decade, avg in decadal_avg.items():
                self.text_widget.insert(tk.END, f"   {int(decade)}s: {avg:,.0f} sq km\n", 'value')
            self.text_widget.insert(tk.END, "• Record low years:\n", 'value')
            for _, row in record_lows.iterrows():
                self.text_widget.insert(tk.END, f"   {int(row['Year'])}: {row['Annual_Avg_Area']:,.0f} sq km\n", 'value')
        else:
            self.text_widget.insert(tk.END, "Sea ice data unavailable or could not be processed.\n", 'alert')
        self.text_widget.configure(state='disabled')

    def clear_plot(self):
        self.fig.clf()

    def plot_sea_ice_trends(self, path='data/N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx'):
        """Process and plot annual average sea ice area over time."""
        # Try different header rows to find the one with all months
        for h in range(10):  # Try first 10 rows
            df = pd.read_excel(path, header=h)
            cols = [str(col).strip() for col in df.columns]
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
            month_cols = [col for col in cols if col in months]
            print(f"header={h}: {month_cols}")
            if len(month_cols) == 12:
                print(f"Found all months at header={h}")
                break
        df.columns = [str(col).strip() for col in df.columns]
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        # Find columns that match months exactly
        month_cols = [col for col in df.columns if col in months]
        if len(month_cols) != 12:
            print('DEBUG: Columns found:', df.columns.tolist())
            raise ValueError(f"Could not find all month columns. Found: {month_cols}")
        keep_cols = ['Year'] + month_cols
        df = df.rename(columns={df.columns[0]: 'Year'})
        df = df[keep_cols]
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        for m in month_cols:
            df[m] = pd.to_numeric(df[m], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Annual_Avg_Area'] = df[month_cols].mean(axis=1)
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(df['Year'], df['Annual_Avg_Area'], marker='o', color=self.colors['plot_line2'], label='Annual Avg Sea Ice Area', linewidth=2)
        ax.set_title('Annual Average Sea Ice Area (Northern Hemisphere)', fontsize=14, color=self.colors['accent'])
        ax.set_xlabel('Year', color=self.colors['text'])
        ax.set_ylabel('Sea Ice Area (sq km)', color=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['plot_grid'])
        ax.legend(facecolor=self.colors['panel'], edgecolor=self.colors['plot_line2'])
        ax.set_facecolor(self.colors['plot_bg'])
        ax.tick_params(colors=self.colors['text'])
        for spine in ax.spines.values():
            spine.set_color(self.colors['plot_line2'])
        self.canvas.draw()
        return df

    def animate_sea_ice_trends(self, path='data/N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx'):
        # Try different header rows to find the one with all months
        for h in range(10):
            df = pd.read_excel(path, header=h)
            cols = [str(col).strip() for col in df.columns]
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
            month_cols = [col for col in cols if col in months]
            if len(month_cols) == 12:
                break
        df.columns = [str(col).strip() for col in df.columns]
        month_cols = [col for col in df.columns if col in months]
        keep_cols = ['Year'] + month_cols
        df = df.rename(columns={df.columns[0]: 'Year'})
        df = df[keep_cols]
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        for m in month_cols:
            df[m] = pd.to_numeric(df[m], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Annual_Avg_Area'] = df[month_cols].mean(axis=1)
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        years = df['Year'].values
        area = df['Annual_Avg_Area'].values
        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(area.min() - 0.1 * area.ptp(), area.max() + 0.1 * area.ptp())
        line, = ax.plot([], [], color=self.colors['plot_line2'], linewidth=2, marker='o', label='Annual Avg Sea Ice Area')
        ax.set_title('Sea Ice Area Animation', color=self.colors['accent'])
        ax.set_xlabel('Year', color=self.colors['text'])
        ax.set_ylabel('Sea Ice Area (sq km)', color=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['plot_grid'])
        ax.legend()
        ax.set_facecolor(self.colors['plot_bg'])
        ax.tick_params(colors=self.colors['text'])
        for spine in ax.spines.values():
            spine.set_color(self.colors['plot_line2'])
        def animate(frame):
            if frame > 0:
                line.set_data(years[:frame], area[:frame])
            return [line]
        self.anim = FuncAnimation(self.fig, animate, frames=len(years) + 1, interval=50, blit=False, repeat=False)
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = ClimateGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 