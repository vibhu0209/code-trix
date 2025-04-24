import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from climate_analysis import ClimateAnalysis

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.config(background='#1a1a1a')
        for button in self.winfo_children():
            if isinstance(button, tk.Button):
                button.configure(background='#2d2d2d', foreground='#e0e0e0',
                               activebackground='#3d3d3d', activeforeground='#ffffff')

class ClimateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Climate Analysis Viewer")
        self.root.geometry("1200x800")
        
        # Set color scheme
        self.style = ttk.Style()
        self.style.configure('Main.TFrame', background='#121212')
        self.style.configure('Button.TFrame', background='#121212')
        self.style.configure('Plot.TFrame', background='#121212')
        
        # Initialize climate analysis
        self.analysis = ClimateAnalysis()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20", style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title label
        title_label = tk.Label(self.main_frame, 
                             text="Climate Analysis Dashboard",
                             font=('Helvetica', 18, 'normal'),
                             fg='#e0e0e0',
                             bg='#121212',
                             pady=20)
        title_label.pack(fill=tk.X)
        
        # Create buttons frame
        self.button_frame = ttk.Frame(self.main_frame, style='Button.TFrame')
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Create buttons with minimal style
        button_width = 20
        buttons = [
            ("Temperature Trends", "temperature"),
            ("Monthly Trends", "monthly"),
            ("Seasonal Analysis", "seasonal"),
            ("Decadal Changes", "decadal"),
            ("Statistics", "stats")
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(self.button_frame, 
                          text=text, 
                          width=button_width,
                          command=lambda c=cmd: self.show_plot(c),
                          bg='#2d2d2d',
                          fg='#e0e0e0',
                          activebackground='#3d3d3d',
                          activeforeground='#ffffff',
                          font=('Helvetica', 10, 'normal'),
                          relief='flat',
                          padx=10,
                          pady=5,
                          bd=1,
                          highlightthickness=1,
                          highlightbackground='#3d3d3d',
                          highlightcolor='#3d3d3d')
            btn.pack(side=tk.LEFT, padx=5)
        
        # Create plot frame
        self.plot_frame = ttk.Frame(self.main_frame, style='Plot.TFrame')
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Set matplotlib style
        plt.style.use('dark_background')
        
        # Create matplotlib figure
        self.fig = plt.figure(figsize=(10, 6), facecolor='#121212')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add custom toolbar
        self.toolbar = CustomToolbar(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        # Create text widget for statistics with minimal styling
        self.stats_text = scrolledtext.ScrolledText(
            self.plot_frame,
            wrap=tk.WORD,
            height=20,
            bg='#1a1a1a',
            fg='#e0e0e0',
            font=('Helvetica', 10),
            insertbackground='#e0e0e0',
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground='#3d3d3d',
            highlightcolor='#3d3d3d'
        )
        
        # Configure root background
        self.root.configure(bg='#121212')
        
        # Show initial plot
        self.show_plot("temperature")
    
    def clear_plot_frame(self):
        """Clear all widgets in the plot frame"""
        self.stats_text.pack_forget()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_plot(self, plot_type):
        """Show the selected plot type"""
        try:
            if plot_type == "stats":
                self.canvas.get_tk_widget().pack_forget()
                self.toolbar.pack_forget()
                self.show_statistics()
            else:
                self.clear_plot_frame()
                self.fig.clear()
                
                if plot_type == "temperature":
                    self.plot_temperature_trends()
                elif plot_type == "monthly":
                    self.plot_monthly_trends()
                elif plot_type == "seasonal":
                    self.plot_seasonal_analysis()
                elif plot_type == "decadal":
                    self.plot_decadal_changes()
                
                self.fig.set_facecolor('#121212')
                self.fig.tight_layout()
                self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying plot: {str(e)}")
    
    def plot_temperature_trends(self):
        """Plot temperature trends using matplotlib"""
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1a1a1a')
        
        years = self.analysis.df['Year']
        temps = self.analysis.df['annual_temp']
        
        # Plot temperature data with minimal colors
        ax.plot(years, temps, color='#e0e0e0', linewidth=1.5, label='Annual Temperature')
        
        # Add trend line
        z = np.polyfit(years, temps, 1)
        p = np.poly1d(z)
        ax.plot(years, p(years), color='#9e9e9e', linestyle='--', 
                linewidth=1.5, label=f'Trend (slope: {z[0]:.4f}°C/year)')
        
        # Add rolling average
        rolling_avg = self.analysis.df['annual_temp'].rolling(window=10).mean()
        ax.plot(years, rolling_avg, color='#ffffff', linewidth=1.5, 
                label='10-Year Moving Average')
        
        ax.set_title('Global Temperature Anomalies', color='#e0e0e0', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Year', color='#e0e0e0')
        ax.set_ylabel('Temperature Anomaly (°C)', color='#e0e0e0')
        ax.grid(True, alpha=0.2, color='#3d3d3d')
        ax.legend(facecolor='#1a1a1a', edgecolor='#3d3d3d')
        
        # Style the axis
        ax.spines['bottom'].set_color('#3d3d3d')
        ax.spines['top'].set_color('#3d3d3d')
        ax.spines['left'].set_color('#3d3d3d')
        ax.spines['right'].set_color('#3d3d3d')
        ax.tick_params(colors='#e0e0e0')
    
    def plot_monthly_trends(self):
        """Plot monthly trends using matplotlib"""
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1a1a1a')
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        data = self.analysis.df[months].values
        years = self.analysis.df['Year'].values
        
        # Use a more informative colormap
        im = ax.imshow(data.T, aspect='auto', cmap='RdYlBu_r',
                      extent=[years[0], years[-1], -0.5, 11.5])
        
        ax.set_title('Monthly Temperature Patterns', color='#e0e0e0', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Year', color='#e0e0e0')
        ax.set_ylabel('Month', color='#e0e0e0')
        ax.set_yticks(range(12))
        ax.set_yticklabels(months, color='#e0e0e0')
        ax.tick_params(colors='#e0e0e0')
        
        # Add colorbar with better styling
        colorbar = self.fig.colorbar(im, ax=ax)
        colorbar.set_label('Temperature Anomaly (°C)', color='#e0e0e0', 
                          fontsize=10, labelpad=10)
        colorbar.ax.yaxis.set_tick_params(color='#e0e0e0')
        plt.setp(colorbar.ax.get_yticklabels(), color='#e0e0e0')
        
        # Add grid lines for better readability
        ax.grid(True, alpha=0.2, color='#3d3d3d')
        
        # Style the axis
        for spine in ax.spines.values():
            spine.set_color('#3d3d3d')
    
    def plot_seasonal_analysis(self):
        """Plot seasonal temperature analysis"""
        seasons = ['DJF', 'MAM', 'JJA', 'SON']
        years = self.analysis.df['Year']
        
        self.fig.suptitle('Seasonal Temperature Patterns', color='#e0e0e0', 
                         y=0.95, font={'size': 14, 'weight': 'normal'})
        
        colors = ['#e0e0e0', '#bdbdbd', '#9e9e9e', '#757575']
        
        for i, (season, color) in enumerate(zip(seasons, colors), 1):
            ax = self.fig.add_subplot(2, 2, i)
            ax.set_facecolor('#1a1a1a')
            temps = self.analysis.df[season]
            
            # Plot temperature data
            ax.plot(years, temps, color=color, linewidth=1.5, label='Temperature')
            
            # Add trend line
            z = np.polyfit(years, temps, 1)
            p = np.poly1d(z)
            ax.plot(years, p(years), color='#9e9e9e', linestyle='--', 
                   linewidth=1.5, label=f'Trend: {z[0]:.4f}°C/year')
            
            ax.set_title(f'{season} Season', color='#e0e0e0')
            ax.set_xlabel('Year', color='#e0e0e0')
            ax.set_ylabel('Temperature Anomaly (°C)', color='#e0e0e0')
            ax.grid(True, alpha=0.2, color='#3d3d3d')
            ax.legend(facecolor='#1a1a1a', edgecolor='#3d3d3d')
            ax.tick_params(colors='#e0e0e0')
            
            # Style the axis
            for spine in ax.spines.values():
                spine.set_color('#3d3d3d')
    
    def plot_decadal_changes(self):
        """Plot decadal changes using matplotlib"""
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#1a1a1a')
        
        self.analysis.df['Decade'] = (self.analysis.df['Year'] // 10) * 10
        decadal_avg = self.analysis.df.groupby('Decade')['annual_temp'].mean()
        decadal_change = decadal_avg.diff()
        
        # Plot bar chart with minimal colors
        bars = ax.bar(decadal_change.index, decadal_change.values, 
                     color='#2d2d2d', edgecolor='#3d3d3d')
        
        ax.set_title('Decadal Temperature Changes', color='#e0e0e0', pad=20,
                    font={'size': 14, 'weight': 'normal'})
        ax.set_xlabel('Decade', color='#e0e0e0')
        ax.set_ylabel('Temperature Change (°C)', color='#e0e0e0')
        ax.grid(True, alpha=0.2, color='#3d3d3d')
        ax.tick_params(colors='#e0e0e0')
        
        # Style the axis
        for spine in ax.spines.values():
            spine.set_color('#3d3d3d')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if not np.isnan(height):
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}°C',
                       ha='center', va='bottom' if height >= 0 else 'top',
                       color='#e0e0e0')
    
    def show_statistics(self):
        """Display statistical summary"""
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.stats_text.delete(1.0, tk.END)
        
        # Calculate statistics
        stats = self.analysis.calculate_statistics()
        
        # Configure text tags with better styling
        self.stats_text.tag_configure('title', 
                                    font=('Helvetica', 16, 'normal'),
                                    foreground='#ffffff',
                                    spacing1=10,
                                    spacing3=5)
        
        self.stats_text.tag_configure('header', 
                                    font=('Helvetica', 12, 'normal'),
                                    foreground='#e0e0e0',
                                    spacing1=5,
                                    spacing3=3)
        
        self.stats_text.tag_configure('value', 
                                    font=('Consolas', 10),
                                    foreground='#bdbdbd',
                                    spacing1=2)
        
        self.stats_text.tag_configure('divider', 
                                    font=('Helvetica', 10),
                                    foreground='#3d3d3d',
                                    spacing1=5,
                                    spacing3=5)
        
        # Insert title
        self.stats_text.insert(tk.END, "Climate Analysis Statistics\n", 'title')
        self.stats_text.insert(tk.END, "─" * 30 + "\n\n", 'divider')
        
        # Date range section
        self.stats_text.insert(tk.END, "Date Range\n", 'header')
        self.stats_text.insert(tk.END, 
            f"   {stats['date_range']['start']} - {stats['date_range']['end']}\n\n", 'value')
        
        # Overall statistics section
        self.stats_text.insert(tk.END, "Overall Statistics\n", 'header')
        self.stats_text.insert(tk.END, 
            f"   Mean Temperature Anomaly: {stats['overall']['mean']:.3f}°C\n", 'value')
        self.stats_text.insert(tk.END,
            f"   Standard Deviation: {stats['overall']['std']:.3f}°C\n", 'value')
        self.stats_text.insert(tk.END,
            f"   Temperature Trend: {stats['overall']['trend']:.4f}°C/year\n\n", 'value')
        
        # Extreme values section
        self.stats_text.insert(tk.END, "Extreme Values\n", 'header')
        self.stats_text.insert(tk.END,
            f"   Warmest Year: {stats['extremes']['warmest_year']} "
            f"({stats['extremes']['warmest_temp']:.3f}°C)\n", 'value')
        self.stats_text.insert(tk.END,
            f"   Coldest Year: {stats['extremes']['coldest_year']} "
            f"({stats['extremes']['coldest_temp']:.3f}°C)\n\n", 'value')
        
        # Seasonal trends section
        self.stats_text.insert(tk.END, "Seasonal Trends (°C/year)\n", 'header')
        for season, trend in stats['seasonal_trends'].items():
            self.stats_text.insert(tk.END, f"   {season}: {trend:.4f}\n", 'value')
        
        # Add final divider
        self.stats_text.insert(tk.END, "\n" + "─" * 30, 'divider')
        
        # Make text widget read-only
        self.stats_text.configure(state='disabled')

def main():
    root = tk.Tk()
    app = ClimateGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 