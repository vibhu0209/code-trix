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
        # Initialize with transparent background
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg='#2c3e50', **kwargs)
        self.command = command
        self.bg = bg
        self.hover_color = hover_color

        # Create rounded rectangle
        self.rect = self.create_rounded_rect(0, 0, width, height, corner_radius, fill=bg)
        self.text = self.create_text(width/2, height/2, text=text, fill=fg, font=('Helvetica', 10, 'normal'))

        # Bind events
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
        
        # Graph explanations
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
        
        # Set color scheme
        self.style = ttk.Style()
        self.style.configure('Main.TFrame', background='#2c3e50')
        self.style.configure('Button.TFrame', background='#2c3e50')
        self.style.configure('Plot.TFrame', background='#2c3e50')
        
        # Initialize climate analysis
        self.analysis = ClimateAnalysis()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20", style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title label
        title_label = tk.Label(self.main_frame, 
                             text="Climate Analysis Dashboard",
                             font=('Helvetica', 24, 'normal'),
                             fg='white',
                             bg='#2c3e50',
                             pady=20)
        title_label.pack(fill=tk.X)
        
        # Create buttons frame
        self.button_frame = ttk.Frame(self.main_frame, style='Button.TFrame')
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Create button and info pairs
        buttons = [
            ("Temperature Trends", "temperature"),
            ("Monthly Trends", "monthly"),
            ("Seasonal Analysis", "seasonal"),
            ("Decadal Changes", "decadal"),
            ("Statistics", "stats")
        ]
        
        for text, cmd in buttons:
            # Create container frame for button pair
            btn_container = ttk.Frame(self.button_frame, style='Button.TFrame')
            btn_container.pack(side=tk.LEFT, padx=5)
            
            # Create main button
            btn = RoundedButton(btn_container, text=text, 
                              command=lambda c=cmd: self.show_plot(c),
                              width=150)
            btn.pack(side=tk.LEFT)
            
            # Create info button if not statistics
            if cmd != "stats":
                info_btn = InfoButton(btn_container,
                                    command=lambda c=cmd: self.show_explanation(c))
                info_btn.pack(side=tk.LEFT, padx=5)
        
        # Create plot frame
        self.plot_frame = ttk.Frame(self.main_frame, style='Plot.TFrame')
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Set matplotlib style
        plt.style.use('dark_background')
        mpl.rcParams['axes.facecolor'] = '#2c3e50'
        mpl.rcParams['figure.facecolor'] = '#2c3e50'
        mpl.rcParams['savefig.facecolor'] = '#2c3e50'
        
        # Create matplotlib figure
        self.fig = plt.figure(figsize=(10, 6), facecolor='#2c3e50')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add custom toolbar
        self.toolbar = CustomToolbar(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        # Create text widget for statistics and explanations
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
        
        # Configure root background
        self.root.configure(bg='#2c3e50')
        
        # Show initial plot
        self.show_plot("temperature")
    
    def animate_plot(self, ax, data, line, xdata, ydata):
        """Animate the plot with a smooth drawing effect"""
        def update(frame):
            line.set_data(xdata[:frame], ydata[:frame])
            return line,
        
        anim = FuncAnimation(self.fig, update, frames=len(xdata),
                           interval=20, blit=True)
        return anim
    
    def show_explanation(self, plot_type):
        """Show explanation for the selected plot type"""
        explanation = self.explanations.get(plot_type, "No explanation available.")
        messagebox.showinfo(f"About {plot_type.title()} Graph", explanation)
    
    def show_plot(self, plot_type):
        """Show the selected plot type"""
        try:
            if plot_type == "stats":
                self.canvas.get_tk_widget().pack_forget()
                self.toolbar.pack_forget()
                self.show_statistics()
            else:
                # Clear previous plot and show canvas
                self.text_widget.pack_forget()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
                self.fig.clear()
                
                # Select and display the appropriate plot
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
        """Plot temperature trends using matplotlib"""
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
        years = self.analysis.df['Year']
        temps = self.analysis.df['annual_temp']
        
        # Plot temperature data
        ax.plot(years, temps, color='#3498db', linewidth=2, label='Annual Temperature')
        
        # Add trend line
        z = np.polyfit(years, temps, 1)
        p = np.poly1d(z)
        ax.plot(years, p(years), color='#e74c3c', linestyle='--', 
                linewidth=2, label=f'Trend (slope: {z[0]:.4f}°C/year)')
        
        # Add rolling average
        rolling_avg = self.analysis.df['annual_temp'].rolling(window=10).mean()
        ax.plot(years, rolling_avg, color='#2ecc71', linewidth=2, 
                label='10-Year Moving Average')
        
        ax.set_title('Global Temperature Anomalies', color='white', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel('Temperature Anomaly (°C)', color='white')
        ax.grid(True, alpha=0.2, color='#3498db')
        ax.legend(facecolor='#34495e', edgecolor='white')
        
        # Style the axis
        ax.spines['bottom'].set_color('#3498db')
        ax.spines['top'].set_color('#3498db')
        ax.spines['left'].set_color('#3498db')
        ax.spines['right'].set_color('#3498db')
        ax.tick_params(colors='white')
        
        # Add hover annotation
        self.add_hover_annotation(ax)
    
    def plot_monthly_trends(self):
        """Plot monthly trends using matplotlib"""
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        data = self.analysis.df[months].values
        years = self.analysis.df['Year'].values
        
        # Use a more informative colormap
        im = ax.imshow(data.T, aspect='auto', cmap='RdYlBu_r',
                      extent=[years[0], years[-1], -0.5, 11.5])
        
        ax.set_title('Monthly Temperature Patterns', color='white', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel('Month', color='white')
        ax.set_yticks(range(12))
        ax.set_yticklabels(months, color='white')
        ax.tick_params(colors='white')
        
        # Add colorbar with better styling
        colorbar = self.fig.colorbar(im, ax=ax)
        colorbar.set_label('Temperature Anomaly (°C)', color='white', 
                          fontsize=10, labelpad=10)
        colorbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(colorbar.ax.get_yticklabels(), color='white')
        
        # Add grid lines for better readability
        ax.grid(True, alpha=0.2, color='#3498db')
        
        # Style the axis
        for spine in ax.spines.values():
            spine.set_color('#3498db')
        
        # Add hover annotation
        self.add_hover_annotation(ax)
    
    def plot_seasonal_analysis(self):
        """Plot seasonal temperature analysis"""
        seasons = ['DJF', 'MAM', 'JJA', 'SON']
        years = self.analysis.df['Year']
        
        self.fig.suptitle('Seasonal Temperature Patterns', color='white', 
                         y=0.95, font={'size': 14, 'weight': 'normal'})
        
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f']
        
        for i, (season, color) in enumerate(zip(seasons, colors), 1):
            ax = self.fig.add_subplot(2, 2, i)
            ax.set_facecolor('#34495e')
            temps = self.analysis.df[season]
            
            # Plot temperature data
            ax.plot(years, temps, color=color, linewidth=2, label='Temperature')
            
            # Add trend line
            z = np.polyfit(years, temps, 1)
            p = np.poly1d(z)
            ax.plot(years, p(years), color='white', linestyle='--', 
                   linewidth=2, label=f'Trend: {z[0]:.4f}°C/year')
            
            ax.set_title(f'{season} Season', color='white')
            ax.set_xlabel('Year', color='white')
            ax.set_ylabel('Temperature Anomaly (°C)', color='white')
            ax.grid(True, alpha=0.2, color='#3498db')
            ax.legend(facecolor='#34495e', edgecolor='white')
            ax.tick_params(colors='white')
            
            # Style the axis
            for spine in ax.spines.values():
                spine.set_color('#3498db')
            
            # Add hover annotation
            self.add_hover_annotation(ax)
    
    def plot_decadal_changes(self):
        """Plot decadal changes using matplotlib"""
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#34495e')
        
        self.analysis.df['Decade'] = (self.analysis.df['Year'] // 10) * 10
        decadal_avg = self.analysis.df.groupby('Decade')['annual_temp'].mean()
        decadal_change = decadal_avg.diff()
        
        # Plot bar chart
        bars = ax.bar(decadal_change.index, decadal_change.values, 
                     color='#3498db', edgecolor='#3498db')
        
        ax.set_title('Decadal Temperature Changes', color='white', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Decade', color='white')
        ax.set_ylabel('Temperature Change (°C)', color='white')
        ax.grid(True, alpha=0.2, color='#3498db')
        ax.tick_params(colors='white')
        
        # Style the axis
        for spine in ax.spines.values():
            spine.set_color('#3498db')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if not np.isnan(height):
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}°C',
                       ha='center', va='bottom' if height >= 0 else 'top',
                       color='white')
        
        # Add hover annotation
        self.add_hover_annotation(ax)
    
    def add_hover_annotation(self, ax):
        """Add hover annotation to the plot"""
        annot = ax.annotate("", xy=(0,0), xytext=(10,10),
                           textcoords="offset points",
                           bbox=dict(boxstyle="round", fc="#34495e", ec="white", alpha=0.8),
                           color='white',
                           fontsize=10)
        annot.set_visible(False)

        def hover(event):
            if event.inaxes == ax:
                # Get data coordinates
                x, y = event.xdata, event.ydata
                annot.xy = (x, y)
                
                # Format text based on plot type
                if hasattr(ax, 'collections') and ax.collections:  # Monthly heatmap
                    row = int(y)
                    col = int(x)
                    if 0 <= row < 12:
                        month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][row]
                        text = f'Year: {int(x)}\nMonth: {month}\nTemp: {y:.2f}°C'
                else:  # Line or bar plots
                    text = f'Year: {int(x)}\nTemp: {y:.2f}°C'
                
                annot.set_text(text)
                annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                annot.set_visible(False)
                self.fig.canvas.draw_idle()

        self.fig.canvas.mpl_connect('motion_notify_event', hover)
    
    def show_statistics(self):
        """Display statistical summary"""
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.delete(1.0, tk.END)
        
        # Calculate statistics
        stats = self.analysis.calculate_statistics()
        
        # Configure text tags with better styling
        self.text_widget.tag_configure('title', 
                                    font=('Helvetica', 16, 'normal'),
                                    foreground='#ffffff',
                                    spacing1=10,
                                    spacing3=5)
        
        self.text_widget.tag_configure('header', 
                                    font=('Helvetica', 12, 'normal'),
                                    foreground='#e0e0e0',
                                    spacing1=5,
                                    spacing3=3)
        
        self.text_widget.tag_configure('value', 
                                    font=('Consolas', 10),
                                    foreground='#bdbdbd',
                                    spacing1=2)
        
        self.text_widget.tag_configure('divider', 
                                    font=('Helvetica', 10),
                                    foreground='#3498db',
                                    spacing1=5,
                                    spacing3=5)
        
        # Insert title
        self.text_widget.insert(tk.END, "Climate Analysis Statistics\n", 'title')
        self.text_widget.insert(tk.END, "─" * 30 + "\n\n", 'divider')
        
        # Date range section
        self.text_widget.insert(tk.END, "Date Range\n", 'header')
        self.text_widget.insert(tk.END, 
            f"   {stats['date_range']['start']} - {stats['date_range']['end']}\n\n", 'value')
        
        # Overall statistics section
        self.text_widget.insert(tk.END, "Overall Statistics\n", 'header')
        self.text_widget.insert(tk.END, 
            f"   Mean Temperature Anomaly: {stats['overall']['mean']:.3f}°C\n", 'value')
        self.text_widget.insert(tk.END,
            f"   Standard Deviation: {stats['overall']['std']:.3f}°C\n", 'value')
        self.text_widget.insert(tk.END,
            f"   Temperature Trend: {stats['overall']['trend']:.4f}°C/year\n\n", 'value')
        
        # Extreme values section
        self.text_widget.insert(tk.END, "Extreme Values\n", 'header')
        self.text_widget.insert(tk.END,
            f"   Warmest Year: {stats['extremes']['warmest_year']} "
            f"({stats['extremes']['warmest_temp']:.3f}°C)\n", 'value')
        self.text_widget.insert(tk.END,
            f"   Coldest Year: {stats['extremes']['coldest_year']} "
            f"({stats['extremes']['coldest_temp']:.3f}°C)\n\n", 'value')
        
        # Seasonal trends section
        self.text_widget.insert(tk.END, "Seasonal Trends (°C/year)\n", 'header')
        for season, trend in stats['seasonal_trends'].items():
            self.text_widget.insert(tk.END, f"   {season}: {trend:.4f}\n", 'value')
        
        # Add final divider
        self.text_widget.insert(tk.END, "\n" + "─" * 30, 'divider')
        
        # Make text widget read-only
        self.text_widget.configure(state='disabled')

def main():
    root = tk.Tk()
    app = ClimateGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 