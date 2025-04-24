import tkinter as tk
from tkinter import ttk, messagebox
import webview
import os
from climate_analysis import ClimateAnalysis

class ClimateGUI:
    def __init__(self):
        # Initialize climate analysis
        self.analysis = ClimateAnalysis()
        
        # Generate initial plots
        self.generate_plots()
        
        # Create webview windows
        self.windows = {}
        
    def generate_plots(self):
        """Generate all plots and save them"""
        # Create outputs directory if it doesn't exist
        os.makedirs('outputs', exist_ok=True)
        
        # Generate plots
        temp_trend = self.analysis.plot_global_temperature_trend()
        if temp_trend:
            self.analysis.save_plot(temp_trend, "temperature_trend.html")
        
        monthly_trends = self.analysis.plot_monthly_trends()
        if monthly_trends:
            self.analysis.save_plot(monthly_trends, "monthly_trends.html")
        
        decadal_changes = self.analysis.calculate_decadal_changes()
        if decadal_changes:
            self.analysis.save_plot(decadal_changes, "decadal_changes.html")
    
    def show_plot(self, filename):
        """Show the selected plot in a webview window"""
        plot_path = os.path.abspath(os.path.join('outputs', filename))
        if os.path.exists(plot_path):
            if filename not in self.windows:
                self.windows[filename] = webview.create_window(
                    f'Climate Analysis - {filename}',
                    url=plot_path,
                    width=1000,
                    height=800
                )
            else:
                self.windows[filename].show()
        else:
            print(f"Error: Plot file not found: {filename}")

def create_window():
    window = webview.create_window('Climate Analysis',
                                 html='<h1>Climate Analysis Dashboard</h1><p>Select a plot to view:</p>')
    
    gui = ClimateGUI()
    
    # Add buttons to the window
    window.evaluate_js("""
        document.body.innerHTML += `
            <button onclick="pywebview.api.show_plot('temperature_trend.html')">Temperature Trends</button>
            <button onclick="pywebview.api.show_plot('monthly_trends.html')">Monthly Trends</button>
            <button onclick="pywebview.api.show_plot('decadal_changes.html')">Decadal Changes</button>
        `;
    """)
    
    # Expose the show_plot method to JavaScript
    window.expose(gui.show_plot)
    
    return window

def main():
    window = create_window()
    webview.start(debug=True)

if __name__ == "__main__":
    main() 