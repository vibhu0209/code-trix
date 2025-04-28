import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from climate_analysis import ClimateAnalysis
from matplotlib.animation import FuncAnimation
import matplotlib as mpl

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.config(background='#2c3e50')
        for button in self.winfo_children():
            if isinstance(button, tk.Button):
                button.configure(background='#34495e', foreground='white',
                               activebackground='#3498db', activeforeground='white')

class RoundedButton(tk.Canvas):
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
    def __init__(self, parent, text="ℹ️", **kwargs):
        super().__init__(parent, text=text, width=30, height=30, corner_radius=15, bg='#34495e', hover_color='#3498db', **kwargs)

class ClimateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Climate Analysis Viewer")
        self.root.geometry("1200x800")
        
        self.explanations = {
            "temperature": """
Temperature Trends Analysis 📈

This graph shows the global temperature anomalies over time:
• Blue line: Annual temperature variations
• Red dashed line: Long-term temperature trend
• Green line: 10-year moving average for smoother trend visualization

Why This Matters:
The accelerating rise in global temperatures shown here isn't just a statistical trend – it's a clear warning signal. The steepening curve indicates we're approaching critical tipping points in the Earth's climate system. Each fraction of a degree increase brings us closer to irreversible changes in weather patterns, ecosystem stability, and food security.

Key Findings:
• The rate of warming has increased significantly in recent decades, showing climate change is accelerating
• Temperature variations are becoming more extreme, with new records being set more frequently
• The 10-year average shows a clear upward trend that exceeds natural climate variability

Real-World Impact:
These temperature changes directly affect everything from crop yields to water availability. The trends we see here are already translating into more frequent extreme weather events, rising sea levels, and threats to food security. Understanding these patterns is crucial for developing effective climate adaptation and mitigation strategies.
""",
            "monthly": """
Monthly Temperature Patterns 🌡️

This heatmap visualizes temperature changes across months and years:
• Red colors: Warmer temperatures
• Blue colors: Cooler temperatures
• Vertical patterns: Seasonal changes
• Horizontal patterns: Long-term trends

Why This Matters:
Monthly temperature patterns reveal how climate change is disrupting natural seasonal rhythms. These disruptions have profound implications for agriculture, ecosystems, and human activities. The changing patterns we observe here are already affecting growing seasons, wildlife migration, and energy consumption patterns worldwide.

Key Findings:
• Winter months are warming faster than summer months, disrupting natural cycles
• Shoulder seasons (spring/fall) show increasing instability
• Heat waves are becoming more intense and occurring earlier in the year

Real-World Impact:
These shifting seasonal patterns affect everything from crop planting times to energy grid management. For farmers, changing frost dates and growing seasons require adaptive strategies. For cities, altered temperature patterns mean rethinking urban planning and emergency preparedness.
""",
            "seasonal": """
Seasonal Temperature Analysis 🌍

These four plots show temperature changes for each season:
• DJF: Winter (December, January, February)
• MAM: Spring (March, April, May)
• JJA: Summer (June, July, August)
• SON: Fall (September, October, November)

Why This Matters:
Seasonal temperature changes are not just about comfort – they're reshaping ecosystems and agricultural systems that have evolved over thousands of years. The uneven warming across seasons is disrupting delicate natural balances, from pollination cycles to pest control, threatening biodiversity and food production.

Key Findings:
• Winters are warming faster than other seasons, affecting snow cover and water resources
• Spring temperatures are becoming more erratic, impacting plant flowering and animal migration
• Summer heat extremes are intensifying, creating new challenges for public health

Real-World Impact:
These seasonal shifts have cascading effects through our natural and human systems. Earlier springs affect pollination timing, warmer winters fail to kill off pest populations, and hotter summers strain power grids and public health systems. Understanding these patterns is crucial for climate adaptation planning.
""",
            "decadal": """
Decadal Temperature Changes 📊

This bar chart shows temperature changes between decades:
• Blue bars: Temperature difference between consecutive decades
• Positive values: Warming trends
• Negative values: Cooling trends

Why This Matters:
The decadal view reveals the long-term acceleration of global warming, cutting through year-to-year noise to show the undeniable trend. This perspective is crucial because it demonstrates how each decade is systematically warmer than the last, creating a new normal that Earth's systems must adapt to at an unprecedented pace.

Key Findings:
• Recent decades show larger temperature jumps than earlier periods
• The rate of warming between decades is accelerating
• Natural cooling periods are becoming less frequent and less intense

Real-World Impact:
These decadal changes represent fundamental shifts in our climate system that will persist for generations. The accelerating warming trend means we have less time to adapt our infrastructure, agriculture, and economies. This data underscores the urgency of immediate action to reduce emissions and build resilience into our systems.
"""
        }
        
        self.style = ttk.Style()
        self.style.configure('Main.TFrame', background='#2c3e50')
        self.style.configure('Button.TFrame', background='#2c3e50')
        self.style.configure('Plot.TFrame', background='#2c3e50')
        
        self.analysis = ClimateAnalysis()
        self.temp_unit = tk.StringVar(value='Celsius')
        
        self.main_frame = ttk.Frame(self.root, padding="20", style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(self.main_frame, 
                             text="Climate Analysis Dashboard",
                             font=('Helvetica', 24, 'normal'),
                             fg='white',
                             bg='#2c3e50',
                             pady=20)
        title_label.pack(fill=tk.X)
        
        self.create_control_panel()
        
        self.button_frame = ttk.Frame(self.main_frame, style='Button.TFrame')
        self.button_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("Temperature Trends", "temperature"),
            ("Monthly Trends", "monthly"),
            ("Seasonal Analysis", "seasonal"),
            ("Decadal Changes", "decadal"),
            ("Statistics", "stats")
        ]
        
        for text, cmd in buttons:
            btn_container = ttk.Frame(self.button_frame, style='Button.TFrame')
            btn_container.pack(side=tk.LEFT, padx=5)
            
            btn = RoundedButton(btn_container, text=text, 
                              command=lambda c=cmd: self.show_plot(c),
                              width=150)
            btn.pack(side=tk.LEFT)
            
            if cmd != "stats":
                info_btn = InfoButton(btn_container,
                                    command=lambda c=cmd: self.show_explanation(c))
                info_btn.pack(side=tk.LEFT, padx=5)
        
        self.plot_frame = ttk.Frame(self.main_frame, style='Plot.TFrame')
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        plt.style.use('dark_background')
        mpl.rcParams['axes.facecolor'] = '#2c3e50'
        mpl.rcParams['figure.facecolor'] = '#2c3e50'
        mpl.rcParams['savefig.facecolor'] = '#2c3e50'
        
        self.fig = plt.figure(figsize=(10, 6), facecolor='#2c3e50')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.toolbar = CustomToolbar(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        self.text_widget = scrolledtext.ScrolledText(
            self.plot_frame,
            wrap=tk.WORD,
            height=20,
            bg='#34495e',
            fg='white',
            font=('Helvetica', 10),
            insertbackground='white',
            relief='flat',
            bd=0,
            highlightthickness=0
        )
        
        self.root.configure(bg='#2c3e50')
        self.show_plot("temperature")
    
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
            
        reset_btn = RoundedButton(self.main_frame, text="Reset View",
                                command=lambda: self.show_plot(self.current_plot))
        reset_btn.pack(side=tk.TOP, pady=5)
        self.reset_btn = reset_btn
        
    def animate_temperature_trends(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
        years = self.analysis.df['Year'].values
        temps = self.analysis.df['annual_temp'].values
        
        if self.temp_unit.get() == 'Fahrenheit':
            temps = self.celsius_to_fahrenheit(temps)
        
        ax.set_xlim(years.min(), years.max())
        ax.set_ylim(temps.min() - 0.1, temps.max() + 0.1)
        line, = ax.plot([], [], color='#3498db', linewidth=2)
        
        ax.set_title('Temperature Change Animation', color='white')
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel(f'Temperature (°{self.temp_unit.get()[0]})', color='white')
        ax.grid(True, alpha=0.2)
        ax.tick_params(colors='white')
        
        for spine in ax.spines.values():
            spine.set_color('#3498db')
        
        def animate(frame):
            if frame > 0:
                line.set_data(years[:frame], temps[:frame])
            return [line]
        
        self.anim = FuncAnimation(
            self.fig, animate, frames=len(years) + 1,
            interval=50, blit=True, repeat=False
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
        
        self.fig.suptitle('Seasonal Temperature Patterns', color='white', 
                         y=0.95, font={'size': 14, 'weight': 'normal'})
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f']
        lines = []
        
        for i, ((season_code, season_name), color) in enumerate(zip(seasons.items(), colors), 1):
            ax = self.fig.add_subplot(2, 2, i)
            ax.set_facecolor('#34495e')
            temps = self.analysis.df[season_code].values
            
            if self.temp_unit.get() == 'Fahrenheit':
                temps = self.celsius_to_fahrenheit(temps)
            
            ax.set_xlim(years.min(), years.max())
            ax.set_ylim(min(temps) - 0.1, max(temps) + 0.1)
            line, = ax.plot([], [], color=color, linewidth=2)
            lines.append(line)
            
            ax.set_title(season_name, color='white')
            ax.set_xlabel('Year', color='white')
            ax.set_ylabel(f'Temperature (°{self.temp_unit.get()[0]})', color='white')
            ax.grid(True, alpha=0.2)
            ax.tick_params(colors='white')
            
            for spine in ax.spines.values():
                spine.set_color('#3498db')
        
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
            interval=50, blit=True, repeat=False
        )
        self.canvas.draw()
        
    def animate_monthly_trends(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data = self.analysis.df[months].values
        
        if self.temp_unit.get() == 'Fahrenheit':
            data = self.celsius_to_fahrenheit(data)
            
        years = self.analysis.df['Year'].values
        
        ax.set_title('Monthly Temperature Patterns', color='white')
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel('Month', color='white')
        ax.set_yticks(range(12))
        ax.set_yticklabels(months, color='white')
        
        def animate(frame):
            if frame > 0:
                ax.clear()
                ax.set_facecolor('#34495e')
                ax.set_title('Monthly Temperature Patterns', color='white')
                ax.set_xlabel('Year', color='white')
                ax.set_ylabel('Month', color='white')
                ax.set_yticks(range(12))
                ax.set_yticklabels(months, color='white')
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_color('#3498db')
                
                im = ax.imshow(data[:frame].T, aspect='auto', cmap='RdYlBu_r',
                             extent=[years[0], years[frame-1] if frame > 1 else years[0], -0.5, 11.5])
                return [im]
            return []
        
        self.anim = FuncAnimation(
            self.fig, animate, frames=len(years) + 1,
            interval=50, blit=True, repeat=False
        )
        self.canvas.draw()
        
    def animate_decadal_changes(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
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
                          color='#3498db', capsize=5, capthick=2,
                          marker='o', linewidth=2, label='Decadal Average')
        
        # Calculate and plot trend line
        if len(decades) > 1:
            z = np.polyfit(decades, decadal_avg, 1)
            p = np.poly1d(z)
            trend_line, = ax.plot(decades, p(decades), 
                                color='#e74c3c', linestyle='--', 
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
                              color='white', fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', 
                                      facecolor='#34495e', 
                                      edgecolor='#3498db', 
                                      alpha=0.9))
        
        # Add value labels
        for x, y in zip(decades, decadal_avg):
            ax.text(x, y + 0.02, f'{y:.2f}{unit_symbol}',
                   ha='center', va='bottom', color='white')
        
        ax.set_title('Decadal Temperature Changes', color='white', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Decade', color='white')
        ax.set_ylabel(f'Temperature ({unit_symbol})', color='white')
        ax.grid(True, alpha=0.2)
        ax.tick_params(colors='white')
        
        for spine in ax.spines.values():
            spine.set_color('#3498db')
            
        ax.legend(facecolor='#34495e', edgecolor='white', loc='upper left')
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
        ax.set_facecolor('#34495e')
        
        years = self.analysis.df['Year']
        temps = self.analysis.df['annual_temp']
        
        if self.temp_unit.get() == 'Fahrenheit':
            temps = self.celsius_to_fahrenheit(temps)
        
        ax.plot(years, temps, color='#3498db', linewidth=2, label='Annual Temperature')
        
        z = np.polyfit(years, temps, 1)
        p = np.poly1d(z)
        ax.plot(years, p(years), color='#e74c3c', linestyle='--', 
                linewidth=2, label=f'Trend (slope: {z[0]:.4f}°{self.temp_unit.get()[0]}/year)')
        
        rolling_avg = temps.rolling(window=10).mean()
        ax.plot(years, rolling_avg, color='#2ecc71', linewidth=2, 
                label='10-Year Moving Average')
        
        ax.set_title('Global Temperature Anomalies', color='white', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel(f'Temperature Anomaly (°{self.temp_unit.get()[0]})', color='white')
        ax.grid(True, alpha=0.2, color='#3498db')
        ax.legend(facecolor='#34495e', edgecolor='white')
        
        ax.spines['bottom'].set_color('#3498db')
        ax.spines['top'].set_color('#3498db')
        ax.spines['left'].set_color('#3498db')
        ax.spines['right'].set_color('#3498db')
        ax.tick_params(colors='white')
        
        self.add_hover_annotation(ax)
    
    def plot_monthly_trends(self):
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        data = self.analysis.df[months].values
        years = self.analysis.df['Year'].values
        
        im = ax.imshow(data.T, aspect='auto', cmap='RdYlBu_r',
                      extent=[years[0], years[-1], -0.5, 11.5])
        
        ax.set_title('Monthly Temperature Patterns', color='white', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel('Month', color='white')
        ax.set_yticks(range(12))
        ax.set_yticklabels(months, color='white')
        ax.tick_params(colors='white')
        
        colorbar = self.fig.colorbar(im, ax=ax)
        colorbar.set_label('Temperature Anomaly (°C)', color='white', 
                          fontsize=10, labelpad=10)
        colorbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(colorbar.ax.get_yticklabels(), color='white')
        
        ax.grid(True, alpha=0.2, color='#3498db')
        
        for spine in ax.spines.values():
            spine.set_color('#3498db')
        
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
        
        self.fig.suptitle('Seasonal Temperature Patterns', color='white', 
                         y=0.95, font={'size': 14, 'weight': 'normal'})
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f']
        
        for i, ((season_code, season_name), color) in enumerate(zip(seasons.items(), colors), 1):
            ax = self.fig.add_subplot(2, 2, i)
            ax.set_facecolor('#34495e')
            temps = self.analysis.df[season_code]
            
            if self.temp_unit.get() == 'Fahrenheit':
                temps = self.celsius_to_fahrenheit(temps)
            
            ax.plot(years, temps, color=color, linewidth=2, label='Temperature')
            
            z = np.polyfit(years, temps, 1)
            p = np.poly1d(z)
            ax.plot(years, p(years), color='white', linestyle='--', 
                   linewidth=2, label=f'Trend: {z[0]:.4f}{unit_symbol}/year')
            
            ax.set_title(season_name, color='white')
            ax.set_xlabel('Year', color='white')
            ax.set_ylabel(f'Temperature ({unit_symbol})', color='white')
            ax.grid(True, alpha=0.2, color='#3498db')
            ax.legend(facecolor='#34495e', edgecolor='white')
            ax.tick_params(colors='white')
            
            for spine in ax.spines.values():
                spine.set_color('#3498db')
            
            self.add_hover_annotation(ax)
    
    def plot_decadal_changes(self):
        self.clear_plot()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
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
                          color='#3498db', capsize=5, capthick=2,
                          marker='o', linewidth=2, label='Decadal Average')
        
        # Calculate and plot trend line
        if len(decades) > 1:
            z = np.polyfit(decades, decadal_avg, 1)
            p = np.poly1d(z)
            trend_line, = ax.plot(decades, p(decades), 
                                color='#e74c3c', linestyle='--', 
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
                              color='white', fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', 
                                      facecolor='#34495e', 
                                      edgecolor='#3498db', 
                                      alpha=0.9))
        
        # Add value labels
        for x, y in zip(decades, decadal_avg):
            ax.text(x, y + 0.02, f'{y:.2f}{unit_symbol}',
                   ha='center', va='bottom', color='white')
        
        ax.set_title('Decadal Temperature Changes', color='white', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Decade', color='white')
        ax.set_ylabel(f'Temperature ({unit_symbol})', color='white')
        ax.grid(True, alpha=0.2)
        ax.tick_params(colors='white')
        
        for spine in ax.spines.values():
            spine.set_color('#3498db')
            
        ax.legend(facecolor='#34495e', edgecolor='white', loc='upper left')
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
        self.text_widget.delete(1.0, tk.END)
        
        stats = self.analysis.calculate_statistics()
        df = self.analysis.df
        unit_symbol = '°F' if self.temp_unit.get() == 'Fahrenheit' else '°C'
        
        monthly_std = df[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']].std()
        most_variable_month = monthly_std.idxmax()
        least_variable_month = monthly_std.idxmin()
        
        extreme_threshold = df['annual_temp'].mean() + 2 * df['annual_temp'].std()
        extreme_years = df[df['annual_temp'] > extreme_threshold]['Year'].tolist()
        
        early_trend = np.polyfit(df['Year'][:len(df)//2], df['annual_temp'][:len(df)//2], 1)[0]
        late_trend = np.polyfit(df['Year'][len(df)//2:], df['annual_temp'][len(df)//2:], 1)[0]
        warming_acceleration = late_trend - early_trend
        
        self.text_widget.tag_configure('title', 
                                    font=('Helvetica', 16, 'bold'),
                                    foreground='#ffffff',
                                    spacing1=10,
                                    spacing3=5)
        
        self.text_widget.tag_configure('header', 
                                    font=('Helvetica', 12, 'bold'),
                                    foreground='#e74c3c',
                                    spacing1=5,
                                    spacing3=3)
        
        self.text_widget.tag_configure('subheader', 
                                    font=('Helvetica', 11, 'bold'),
                                    foreground='#3498db',
                                    spacing1=3,
                                    spacing3=2)
        
        self.text_widget.tag_configure('value', 
                                    font=('Helvetica', 10),
                                    foreground='#bdbdbd',
                                    spacing1=2)
        
        self.text_widget.tag_configure('impact', 
                                    font=('Helvetica', 10, 'italic'),
                                    foreground='#e67e22',
                                    spacing1=2)
        
        self.text_widget.tag_configure('alert', 
                                    font=('Helvetica', 10, 'bold'),
                                    foreground='#e74c3c',
                                    spacing1=2)
        
        self.text_widget.insert(tk.END, "Climate Change Impact Analysis\n", 'title')
        self.text_widget.insert(tk.END, "Understanding the Human Impact of Temperature Changes\n\n", 'subheader')
        
        self.text_widget.insert(tk.END, "🔍 Key Findings\n", 'header')
        total_change = stats['extremes']['warmest_temp'] - stats['extremes']['coldest_temp']
        
        self.text_widget.insert(tk.END, "Temperature Change:\n", 'subheader')
        self.text_widget.insert(tk.END, 
            f"• Total temperature change: {total_change:.2f}{unit_symbol}\n", 'value')
        self.text_widget.insert(tk.END,
            "→ This change is equivalent to the difference between a comfortable spring day "
            "and a severe heat warning.\n", 'impact')
        
        self.text_widget.insert(tk.END, "\nWarming Acceleration:\n", 'subheader')
        self.text_widget.insert(tk.END,
            f"• Recent warming rate: {late_trend:.4f}{unit_symbol}/year\n"
            f"• Earlier warming rate: {early_trend:.4f}{unit_symbol}/year\n"
            f"• Acceleration: {warming_acceleration:.4f}{unit_symbol}/year²\n", 'value')
        self.text_widget.insert(tk.END,
            "→ The rate of warming is increasing, making adaptation more challenging for "
            "communities and ecosystems.\n", 'impact')
        
        self.text_widget.insert(tk.END, "\n⚠️ Extreme Events:\n", 'header')
        self.text_widget.insert(tk.END,
            f"• Number of extreme temperature years: {len(extreme_years)}\n"
            f"• Most recent extreme years: {', '.join(map(str, sorted(extreme_years)[-3:]))}\n", 'value')
        if len(extreme_years) > 0:
            self.text_widget.insert(tk.END,
                "→ Extreme temperatures increase risks of:\n"
                "   - Heat-related health issues\n"
                "   - Strain on power grids\n"
                "   - Agricultural challenges\n"
                "   - Water resource stress\n", 'alert')
        
        self.text_widget.insert(tk.END, "\n🌡️ Seasonal Vulnerability:\n", 'header')
        winter_trend = stats['seasonal_trends']['DJF']
        summer_trend = stats['seasonal_trends']['JJA']
        
        self.text_widget.insert(tk.END,
            f"• Winter warming rate: {winter_trend:.4f}{unit_symbol}/year\n"
            f"• Summer warming rate: {summer_trend:.4f}{unit_symbol}/year\n"
            f"• Most variable month: {most_variable_month}\n", 'value')
        
        seasonal_impact = (
            "→ Changing seasonal patterns affect:\n"
            "   - Agricultural growing seasons\n"
            "   - Wildlife migration patterns\n"
            "   - Winter recreation activities\n"
            "   - Energy consumption patterns\n"
        )
        self.text_widget.insert(tk.END, seasonal_impact, 'impact')
        
        self.text_widget.insert(tk.END, "\n🔮 Future Implications:\n", 'header')
        years_to_threshold = 10
        projected_change = late_trend * years_to_threshold
        
        self.text_widget.insert(tk.END,
            f"• Projected {years_to_threshold}-year change: {projected_change:.2f}{unit_symbol}\n", 'value')
        
        projection_impact = (
            "→ Without intervention, we can expect:\n"
            "   - Increased frequency of extreme weather\n"
            "   - Greater stress on vulnerable populations\n"
            "   - More challenges for agriculture and food security\n"
            "   - Higher adaptation costs for communities\n"
        )
        self.text_widget.insert(tk.END, projection_impact, 'alert')
        
        self.text_widget.insert(tk.END, "\n💡 What Can Be Done:\n", 'header')
        action_items = (
            "• Support climate-resilient infrastructure\n"
            "• Implement early warning systems for extreme weather\n"
            "• Develop community cooling centers\n"
            "• Protect vulnerable populations\n"
            "• Invest in renewable energy\n"
            "• Enhance urban green spaces\n"
        )
        self.text_widget.insert(tk.END, action_items, 'value')
        
        self.text_widget.configure(state='disabled')

    def clear_plot(self):
        self.fig.clf()

def main():
    root = tk.Tk()
    app = ClimateGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 