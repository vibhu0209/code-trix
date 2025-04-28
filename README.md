# Planet at Risk - Climate Change Analysis

This project analyzes and visualizes global temperature data from NASA GISS (Goddard Institute for Space Studies) to understand climate change trends. Created for the CODE@TRIX competition.

## Project Structure
- `climate_analysis.py`: Main analysis script with data processing and visualization functions
- `climate_gui.py`: Interactive GUI application for climate data visualization
- `requirements.txt`: List of Python dependencies
- `data/GLB.Ts+dSST.csv`: NASA GISS global temperature dataset

## Features

### Interactive GUI Dashboard
- Modern, dark-themed interface with intuitive controls
- Multiple visualization modes:
  - Temperature Trends: Long-term temperature anomalies with trend analysis
  - Monthly Trends: Heatmap showing monthly temperature patterns
  - Seasonal Analysis: Temperature changes across different seasons
  - Decadal Changes: Temperature variations between decades
  - Sea Ice Trends: Annual average sea ice area in the Northern Hemisphere
  - Statistics: Comprehensive climate change impact analysis

### Advanced Visualization Features
- Interactive plots with hover annotations
- Temperature unit toggle (Celsius/Fahrenheit)
- Graph export functionality (PNG, JPEG, PDF)
- Animated temperature and sea ice trends
- Custom navigation toolbar
- Detailed explanations for each visualization type

### Data Analysis Capabilities
- Comprehensive statistical analysis
- Seasonal trend analysis
- Extreme event detection
- Warming acceleration calculations
- Sea ice area statistics and trend analysis
- Impact assessment and future projections

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

4. Run the application:
```bash
python climate_analysis.py
```
```bash
python climate_gui.py
```

## Data Format

The script expects the NASA GISS temperature dataset with the following structure:
- Year column
- Monthly temperature columns (Jan-Dec)
- Temperature values are anomalies in degrees Celsius relative to the base period

## Visualization Types

1. **Temperature Trends**
   - Line chart showing temperature anomalies over time
   - Includes trend line and 10-year moving average
   - Interactive hover details with exact values

2. **Monthly Trends**
   - Heatmap visualization of monthly temperature patterns
   - Color-coded temperature anomalies
   - Interactive month and year selection

3. **Seasonal Analysis**
   - Four subplots showing temperature changes for each season
   - Winter (DJF), Spring (MAM), Summer (JJA), Fall (SON)
   - Trend analysis for each season

4. **Decadal Changes**
   - Bar chart showing temperature changes between decades
   - Error bars indicating temperature variability
   - Trend line showing long-term changes

5. **Sea Ice Trends**
   - Line chart showing annual average sea ice area in the Northern Hemisphere
   - Animated visualization of sea ice decline
   - Key statistics: min, max, mean, and trend in sea ice area

6. **Statistics**
   - Comprehensive climate change impact analysis
   - Key findings and real-world implications
   - Future projections and recommendations

## Dependencies
- Python 3.x
- tkinter
- matplotlib
- numpy
- pandas
- scikit-learn
- seaborn

## Contributing
Feel free to submit issues and enhancement requests!
