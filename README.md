# Planet at Risk - Climate Change Analysis

This project analyzes and visualizes global temperature data from NASA GISS (Goddard Institute for Space Studies) to understand climate change trends. Created for the CODE@TRIX competition.

## Project Structure
- `climate_analysis.py`: Main analysis script with data processing and visualization functions
- `requirements.txt`: List of Python dependencies
- `data/GLB.Ts+dSST.csv`: NASA GISS global temperature dataset
- Generated outputs (in `outputs/` directory):
  - `temperature_trend.html`: Interactive visualization of global temperature trends with trend line
  - `monthly_trends.html`: Heatmap showing monthly temperature patterns over time
  - `decadal_changes.html`: Bar chart showing temperature changes by decade

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure the NASA GISS dataset is in the correct location:
   - Place `GLB.Ts+dSST.csv` in the `data/` directory

4. Run the analysis:
```bash
python climate_analysis.py
```

## Features

- Data cleaning and preprocessing of NASA GISS temperature data
- Interactive visualizations using Plotly
- Multiple analysis views:
  - Long-term temperature trends
  - Monthly temperature patterns
  - Decadal temperature changes
- Export of visualizations as interactive HTML files

## Data Format

The script expects the NASA GISS temperature dataset with the following structure:
- Year column
- Monthly temperature columns (Jan-Dec)
- Temperature values are anomalies in degrees Celsius relative to the base period

## Visualization Outputs

1. **Global Temperature Trends**
   - Line chart showing temperature anomalies over time
   - Includes trend line for clear visualization of long-term changes
   - Interactive hover details with exact values

2. **Monthly Temperature Patterns**
   - Heatmap showing temperature variations across months and years
   - Helps identify seasonal patterns and their changes over time
   - Interactive visualization with value display on hover

3. **Decadal Changes**
   - Bar chart showing temperature changes between decades
   - Highlights acceleration or deceleration of warming
   - Clear visualization of long-term climate change patterns 