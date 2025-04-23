import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime
import numpy as np
from climate_analysis import ClimateAnalysis

class ClimateAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Climate Analysis Dashboard")
        self.root.geometry("1200x800")
        
        # Initialize the analysis
        self.analysis = ClimateAnalysis()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Initialize the dashboard
        self.load_dashboard()

    def create_sidebar(self):
        """Create the sidebar with analysis options"""
        sidebar = ttk.Frame(self.main_container, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Dataset selection
        ttk.Label(sidebar, text="Dataset Selection", font=('Helvetica', 12, 'bold')).pack(pady=(0, 10))
        self.dataset_var = tk.StringVar(value="AIRS v7")
        for dataset in ["AIRS v6", "AIRS v7", "GHCNv4/ERSSTv5"]:
            ttk.Radiobutton(sidebar, text=dataset, variable=self.dataset_var, 
                           value=dataset, command=self.update_analysis).pack(anchor=tk.W)
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Analysis options
        ttk.Label(sidebar, text="Visualization Options", font=('Helvetica', 12, 'bold')).pack(pady=(0, 10))
        
        self.viz_buttons = []
        viz_options = [
            ("Temperature Trends", self.show_temperature_trends),
            ("Monthly Patterns", self.show_monthly_patterns),
            ("Seasonal Analysis", self.show_seasonal_analysis),
            ("Decadal Changes", self.show_decadal_changes),
            ("Statistical Summary", self.show_statistical_summary),
            ("Export Report", self.export_report)
        ]
        
        for text, command in viz_options:
            btn = ttk.Button(sidebar, text=text, command=command)
            btn.pack(fill=tk.X, pady=2)
            self.viz_buttons.append(btn)

    def create_main_content(self):
        """Create the main content area"""
        self.main_content = ttk.Frame(self.main_container)
        self.main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Frame(self.main_content)
        header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header, text="Climate Analysis Dashboard", 
                 font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_content, textvariable=self.status_var)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Content area
        self.content_area = ttk.Frame(self.main_content)
        self.content_area.pack(fill=tk.BOTH, expand=True)

    def load_dashboard(self):
        """Initialize the dashboard with default view"""
        self.show_temperature_trends()
        self.update_status("Dashboard loaded successfully")

    def update_status(self, message):
        """Update the status bar with a message"""
        self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

    def update_analysis(self):
        """Update the analysis when dataset selection changes"""
        self.update_status(f"Analyzing {self.dataset_var.get()} dataset...")
        # Refresh the current view
        self.show_temperature_trends()

    def show_temperature_trends(self):
        """Display temperature trends visualization"""
        self.update_status("Generating temperature trends...")
        fig = self.analysis.plot_global_temperature_trend()
        self.save_and_show_plot(fig, "temperature_trends")

    def show_monthly_patterns(self):
        """Display monthly temperature patterns"""
        self.update_status("Generating monthly patterns...")
        fig = self.analysis.plot_monthly_trends()
        self.save_and_show_plot(fig, "monthly_patterns")

    def show_seasonal_analysis(self):
        """Display seasonal temperature analysis"""
        self.update_status("Generating seasonal analysis...")
        # Add seasonal analysis visualization
        seasons = ['DJF', 'MAM', 'JJA', 'SON']
        seasonal_data = self.analysis.df[['Year'] + seasons].copy()
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=seasons)
        for i, season in enumerate(seasons, 1):
            row = (i-1) // 2 + 1
            col = (i-1) % 2 + 1
            fig.add_trace(
                go.Scatter(x=seasonal_data['Year'], y=seasonal_data[season],
                          name=season, mode='lines+markers'),
                row=row, col=col
            )
        
        fig.update_layout(height=800, title_text="Seasonal Temperature Patterns")
        self.save_and_show_plot(fig, "seasonal_analysis")

    def show_decadal_changes(self):
        """Display decadal temperature changes"""
        self.update_status("Generating decadal analysis...")
        fig = self.analysis.calculate_decadal_changes()
        self.save_and_show_plot(fig, "decadal_changes")

    def show_statistical_summary(self):
        """Display statistical summary of the data"""
        self.update_status("Generating statistical summary...")
        
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Create text widget for summary
        text_widget = tk.Text(self.content_area, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Calculate statistics
        monthly_cols = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        stats = self.analysis.df[monthly_cols].describe()
        
        # Add summary to text widget
        text_widget.insert(tk.END, "Statistical Summary\n\n", "heading")
        text_widget.insert(tk.END, f"Data Range: {self.analysis.df['Year'].min()} - {self.analysis.df['Year'].max()}\n\n")
        text_widget.insert(tk.END, "Monthly Temperature Statistics:\n\n")
        text_widget.insert(tk.END, stats.to_string())
        
        # Make text widget read-only
        text_widget.configure(state='disabled')

    def export_report(self):
        """Export analysis report"""
        self.update_status("Generating report...")
        
        # Create output directory if it doesn't exist
        os.makedirs('outputs', exist_ok=True)
        
        # Generate all visualizations
        figs = {
            'temperature_trends': self.analysis.plot_global_temperature_trend(),
            'monthly_patterns': self.analysis.plot_monthly_trends(),
            'decadal_changes': self.analysis.calculate_decadal_changes()
        }
        
        # Save all figures
        for name, fig in figs.items():
            fig.write_html(f"outputs/{name}.html")
        
        # Create summary report
        with open('outputs/report.html', 'w') as f:
            f.write(f"""
            <html>
            <head>
                <title>Climate Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #2c3e50; }}
                    .viz {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1>Climate Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Dataset: {self.dataset_var.get()}</p>
                
                <div class="viz">
                    <h2>Temperature Trends</h2>
                    <iframe src="temperature_trends.html" width="100%" height="600px"></iframe>
                </div>
                
                <div class="viz">
                    <h2>Monthly Patterns</h2>
                    <iframe src="monthly_patterns.html" width="100%" height="600px"></iframe>
                </div>
                
                <div class="viz">
                    <h2>Decadal Changes</h2>
                    <iframe src="decadal_changes.html" width="100%" height="600px"></iframe>
                </div>
            </body>
            </html>
            """)
        
        # Open the report in browser
        webbrowser.open('outputs/report.html')
        self.update_status("Report generated successfully")

    def save_and_show_plot(self, fig, name):
        """Save and display a plotly figure"""
        # Save the figure
        os.makedirs('outputs', exist_ok=True)
        output_path = f"outputs/{name}.html"
        fig.write_html(output_path)
        
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Create and pack a button to open the plot
        ttk.Button(
            self.content_area,
            text="Open Interactive Plot",
            command=lambda: webbrowser.open(output_path)
        ).pack(pady=10)
        
        # Display success message
        self.update_status(f"Generated {name} visualization")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClimateAnalysisGUI(root)
    root.mainloop() 