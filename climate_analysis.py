import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from scipy import stats
import os
from datetime import datetime

class ClimateAnalysis:
    def __init__(self, data_path='data/GLB.Ts+dSST.csv'):
        self.data_path = data_path
        self.df = None
        self.dataset_type = None
        self.load_and_clean_data()

    def load_and_clean_data(self):
        try:
            with open(self.data_path, 'r') as file:
                content = file.readlines()

            sections = {
                'AIRS v6': [],
                'AIRS v7': [],
                'GHCNv4/ERSSTv5': []
            }
            
            current_section = None
            for line in content:
                if 'AIRS v6' in line:
                    current_section = 'AIRS v6'
                elif 'AIRS v7' in line:
                    current_section = 'AIRS v7'
                elif 'GHCNv4/ERSSTv5' in line:
                    current_section = 'GHCNv4/ERSSTv5'
                elif current_section and line.strip():
                    sections[current_section].append(line)

            self.dataset_type = 'GHCNv4/ERSSTv5'
            data_lines = sections[self.dataset_type]
            
            header = data_lines[0].strip().split(',')
            data = [line.strip().split(',') for line in data_lines[1:]]
            
            self.df = pd.DataFrame(data, columns=header)
            self.clean_data()
            
            print("Data loaded and cleaned successfully!")
            print(f"Dataset covers years from {self.df['Year'].min()} to {self.df['Year'].max()}")
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise

    def clean_data(self):
        self.df['Year'] = pd.to_numeric(self.df['Year'], errors='coerce')
        
        month_columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for col in month_columns:
            self.df[col] = self.df[col].replace('*******', np.nan)
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        season_columns = ['DJF', 'MAM', 'JJA', 'SON']
        for col in season_columns:
            self.df[col] = self.df[col].replace('*******', np.nan)
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        self.df['annual_temp'] = self.df[month_columns].mean(axis=1)
        
        self.df = self.df.dropna(subset=['Year'])
        self.df = self.df[self.df['Year'] != '*******']

    def change_dataset(self, dataset_type):
        if dataset_type in ['AIRS v6', 'AIRS v7', 'GHCNv4/ERSSTv5']:
            self.dataset_type = dataset_type
            self.load_and_clean_data()
        else:
            raise ValueError("Invalid dataset type")

    def plot_global_temperature_trend(self):
        if 'Year' in self.df.columns and 'annual_temp' in self.df.columns:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(
                    x=self.df['Year'],
                    y=self.df['annual_temp'],
                    name="Annual Temperature",
                    mode='lines+markers',
                    marker=dict(size=6)
                ),
                secondary_y=False
            )
            
            z = np.polyfit(self.df['Year'], self.df['annual_temp'], 1)
            p = np.poly1d(z)
            
            fig.add_trace(
                go.Scatter(
                    x=self.df['Year'],
                    y=p(self.df['Year']),
                    name=f'Trend Line (slope: {z[0]:.4f}°C/year)',
                    line=dict(color='red', dash='dash')
                ),
                secondary_y=False
            )
            
            rolling_avg = self.df['annual_temp'].rolling(window=10).mean()
            fig.add_trace(
                go.Scatter(
                    x=self.df['Year'],
                    y=rolling_avg,
                    name='10-Year Moving Average',
                    line=dict(color='green')
                ),
                secondary_y=False
            )
            
            temp_change = self.df['annual_temp'].diff()
            fig.add_trace(
                go.Scatter(
                    x=self.df['Year'],
                    y=temp_change,
                    name='Year-over-Year Change',
                    line=dict(color='orange')
                ),
                secondary_y=True
            )
            
            fig.update_layout(
                title=f"Global Temperature Anomalies ({self.dataset_type})",
                xaxis_title="Year",
                yaxis_title="Temperature Anomaly (°C)",
                yaxis2_title="Year-over-Year Change (°C)",
                template="plotly_dark",
                showlegend=True,
                hovermode='x unified'
            )
            
            return fig
        else:
            print("Required columns not found in dataset")

    def plot_monthly_trends(self):
        month_columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        monthly_data = self.df[['Year'] + month_columns].copy()
        monthly_data = monthly_data.melt(
            id_vars=['Year'], 
            value_vars=month_columns,
            var_name='Month', 
            value_name='Temperature'
        )
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Monthly Temperature Patterns", "Monthly Temperature Distributions"),
            vertical_spacing=0.2,
            row_heights=[0.7, 0.3]
        )
        
        heatmap = go.Heatmap(
            x=monthly_data['Month'],
            y=monthly_data['Year'],
            z=monthly_data['Temperature'],
            colorscale='RdBu_r',
            colorbar=dict(title='Temperature Anomaly (°C)')
        )
        fig.add_trace(heatmap, row=1, col=1)
        
        for month in month_columns:
            fig.add_trace(
                go.Box(
                    y=self.df[month],
                    name=month,
                    boxpoints='outliers'
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=1000,
            title_text=f"Monthly Temperature Analysis ({self.dataset_type})",
            template="plotly_dark"
        )
        
        return fig

    def calculate_decadal_changes(self):
        self.df['Decade'] = (self.df['Year'] // 10) * 10
        decadal_avg = self.df.groupby('Decade')['annual_temp'].agg(['mean', 'std', 'count'])
        decadal_change = decadal_avg['mean'].diff()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Decadal Temperature Changes", "Decadal Statistics"),
            vertical_spacing=0.2
        )
        
        fig.add_trace(
            go.Bar(
                x=decadal_change.index,
                y=decadal_change.values,
                name='Temperature Change',
                text=decadal_change.values.round(3),
                textposition='auto'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=decadal_avg.index,
                y=decadal_avg['mean'],
                name='Mean Temperature',
                mode='lines+markers'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=decadal_avg.index,
                y=decadal_avg['mean'] + decadal_avg['std'],
                name='Upper Bound',
                line=dict(dash='dash'),
                showlegend=False
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=decadal_avg.index,
                y=decadal_avg['mean'] - decadal_avg['std'],
                name='Lower Bound',
                line=dict(dash='dash'),
                showlegend=False,
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=800,
            title_text=f"Decadal Temperature Analysis ({self.dataset_type})",
            template="plotly_dark",
            showlegend=True
        )
        
        return fig

    def calculate_statistics(self):
        stats = {}
        
        stats['extremes'] = {
            'warmest_temp': self.df['annual_temp'].max(),
            'coldest_temp': self.df['annual_temp'].min(),
            'warmest_year': self.df.loc[self.df['annual_temp'].idxmax(), 'Year'],
            'coldest_year': self.df.loc[self.df['annual_temp'].idxmin(), 'Year']
        }
        
        stats['trends'] = {
            'linear_trend': np.polyfit(self.df['Year'], self.df['annual_temp'], 1)[0],
            'quadratic_trend': np.polyfit(self.df['Year'], self.df['annual_temp'], 2)[0],
            'rolling_std': self.df['annual_temp'].rolling(window=10).std().mean()
        }
        
        stats['seasonal_trends'] = {
            'DJF': np.polyfit(self.df['Year'], self.df['DJF'], 1)[0],
            'MAM': np.polyfit(self.df['Year'], self.df['MAM'], 1)[0],
            'JJA': np.polyfit(self.df['Year'], self.df['JJA'], 1)[0],
            'SON': np.polyfit(self.df['Year'], self.df['SON'], 1)[0]
        }
        
        stats['variability'] = {
            'annual_std': self.df['annual_temp'].std(),
            'monthly_std': self.df[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']].std().mean(),
            'seasonal_std': self.df[['DJF', 'MAM', 'JJA', 'SON']].std().mean()
        }
        
        return stats

    def save_plot(self, fig, filename):
        if not os.path.exists('plots'):
            os.makedirs('plots')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('plots', f'{filename}_{timestamp}.html')
        fig.write_html(filepath)
        print(f"Plot saved to {filepath}")

if __name__ == "__main__":
    # Initialize analysis
    analysis = ClimateAnalysis()
    
    # Create output directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    # Generate and save visualizations
    temp_trend = analysis.plot_global_temperature_trend()
    if temp_trend:
        analysis.save_plot(temp_trend, "temperature_trend.html")
    
    monthly_trends = analysis.plot_monthly_trends()
    if monthly_trends:
        analysis.save_plot(monthly_trends, "monthly_trends.html")
    
    decadal_changes = analysis.calculate_decadal_changes()
    if decadal_changes:
        analysis.save_plot(decadal_changes, "decadal_changes.html")
    
    # Calculate and save statistics
    stats = analysis.calculate_statistics()
    with open('outputs/statistics.txt', 'w') as f:
        f.write("Climate Analysis Statistics\n")
        f.write("=========================\n\n")
        f.write(f"Dataset: {analysis.dataset_type}\n")
        f.write(f"Year Range: {analysis.df['Year'].min()} - {analysis.df['Year'].max()}\n\n")
        
        f.write("Extreme Values:\n")
        f.write(f"Warmest Year: {stats['extremes']['warmest_year']} ({stats['extremes']['warmest_temp']:.3f}°C)\n")
        f.write(f"Coldest Year: {stats['extremes']['coldest_year']} ({stats['extremes']['coldest_temp']:.3f}°C)\n\n")
        
        f.write("Temperature Trends:\n")
        f.write(f"Linear Trend: {stats['trends']['linear_trend']:.4f}°C/year\n")
        f.write(f"Quadratic Trend: {stats['trends']['quadratic_trend']:.4f}°C/year²\n")
        f.write(f"10-Year Rolling Standard Deviation: {stats['trends']['rolling_std']:.4f}°C\n\n")
        
        f.write("Seasonal Trends (°C/year):\n")
        for season, trend in stats['seasonal_trends'].items():
            f.write(f"{season}: {trend:.4f}\n")
        
        f.write("\nTemperature Variability:\n")
        f.write(f"Annual Standard Deviation: {stats['variability']['annual_std']:.4f}°C\n")
        f.write(f"Monthly Standard Deviation: {stats['variability']['monthly_std']:.4f}°C\n")
        f.write(f"Seasonal Standard Deviation: {stats['variability']['seasonal_std']:.4f}°C\n") 