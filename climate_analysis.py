import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import os

class ClimateAnalysis:
    def __init__(self, data_path='data/GLB.Ts+dSST.csv'):
        """Initialize the ClimateAnalysis class with data path."""
        self.data_path = data_path
        self.df = None
        self.load_and_clean_data()

    def load_and_clean_data(self):
        """Load and clean the NASA GISS temperature dataset."""
        try:
            # Read the data, skipping the header rows
            self.df = pd.read_csv(self.data_path, skiprows=1)
            
            # Clean column names
            self.df.columns = [col.strip() for col in self.df.columns]
            
            # Convert Year column
            self.df['Year'] = pd.to_numeric(self.df['Year'], errors='coerce')
            
            # Process monthly temperature columns (Jan-Dec)
            month_columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # Convert monthly temperatures to numeric, handling any non-numeric values
            for month in month_columns:
                self.df[month] = pd.to_numeric(self.df[month], errors='coerce')
            
            # Calculate annual average temperature
            self.df['annual_temp'] = self.df[month_columns].mean(axis=1)
            
            # Basic cleaning
            self.df = self.df.replace([np.inf, -np.inf], np.nan)
            self.df = self.df.dropna(subset=['Year', 'annual_temp'])
            
            print("Data loaded and cleaned successfully!")
            print(f"Dataset covers years from {self.df['Year'].min()} to {self.df['Year'].max()}")
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise

    def plot_global_temperature_trend(self):
        """Create a line plot for global temperature trends."""
        if 'Year' in self.df.columns and 'annual_temp' in self.df.columns:
            fig = px.line(self.df, x='Year', y='annual_temp',
                         title='Global Temperature Anomalies Over Time')
            
            # Add a trend line
            z = np.polyfit(self.df['Year'], self.df['annual_temp'], 1)
            p = np.poly1d(z)
            
            fig.add_trace(
                go.Scatter(
                    x=self.df['Year'],
                    y=p(self.df['Year']),
                    name='Trend Line',
                    line=dict(color='red', dash='dash')
                )
            )
            
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Temperature Anomaly (°C)",
                template="plotly_dark",
                showlegend=True
            )
            return fig
        else:
            print("Required columns not found in dataset")

    def plot_monthly_trends(self):
        """Create a heatmap of monthly temperature trends over years."""
        month_columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create a pivot table for the heatmap
        monthly_data = self.df[['Year'] + month_columns].copy()
        monthly_data = monthly_data.melt(
            id_vars=['Year'], 
            value_vars=month_columns,
            var_name='Month', 
            value_name='Temperature'
        )
        
        fig = px.density_heatmap(
            monthly_data,
            x='Month',
            y='Year',
            z='Temperature',
            title='Monthly Temperature Anomalies Over Time',
            labels={'Temperature': 'Temperature Anomaly (°C)'}
        )
        
        fig.update_layout(template="plotly_dark")
        return fig

    def calculate_decadal_changes(self):
        """Calculate temperature changes by decade."""
        self.df['Decade'] = (self.df['Year'] // 10) * 10
        decadal_avg = self.df.groupby('Decade')['annual_temp'].mean()
        decadal_change = decadal_avg.diff()
        
        fig = px.bar(
            x=decadal_change.index,
            y=decadal_change.values,
            title='Temperature Change by Decade',
            labels={
                'x': 'Decade',
                'y': 'Temperature Change (°C)'
            }
        )
        
        fig.update_layout(template="plotly_dark")
        return fig

if __name__ == "__main__":
    # Initialize analysis
    analysis = ClimateAnalysis()
    
    # Create output directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    # Generate and save visualizations
    temp_trend = analysis.plot_global_temperature_trend()
    if temp_trend:
        temp_trend.write_html("outputs/temperature_trend.html")
    
    monthly_trends = analysis.plot_monthly_trends()
    if monthly_trends:
        monthly_trends.write_html("outputs/monthly_trends.html")
    
    decadal_changes = analysis.calculate_decadal_changes()
    if decadal_changes:
        decadal_changes.write_html("outputs/decadal_changes.html") 