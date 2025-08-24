# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# function_declarations.py
"""Gemini function calling configuration and declarations.
This module defines all the functions that Gemini can call for chart generation and data creation.
System instruction enforces proper 2-step workflow (data generation → visualization).
"""

from google.genai import types
from typing import Dict, List, Any

# Chart function declarations
BAR_CHART_FUNCTION = types.FunctionDeclaration(
    name='create_bar_chart',
    description='Create a bar chart for comparing categories or discrete values',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'categories': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of category names for the x-axis'
            ),
            'values': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='List of numerical values corresponding to each category'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'x_title': types.Schema(
                type='STRING',
                description='Label for the x-axis'
            ),
            'y_title': types.Schema(
                type='STRING',
                description='Label for the y-axis'
            ),
            'color_scheme': types.Schema(
                type='STRING',
                description='Color scheme for the chart (plotly, viridis, blues, etc.)'
            )
        },
        required=['categories', 'values']
    )
)

LINE_CHART_FUNCTION = types.FunctionDeclaration(
    name='create_line_chart',
    description='Create a line chart for showing trends over time or continuous data',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'x_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of x-axis values (dates, numbers, or categories)'
            ),
            'y_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='List of y-axis numerical values'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'x_title': types.Schema(
                type='STRING',
                description='Label for the x-axis'
            ),
            'y_title': types.Schema(
                type='STRING',
                description='Label for the y-axis'
            ),
            'line_color': types.Schema(
                type='STRING',
                description='Color of the line'
            )
        },
        required=['x_data', 'y_data']
    )
)

SCATTER_PLOT_FUNCTION = types.FunctionDeclaration(
    name='create_scatter_plot',
    description='Create a scatter plot for showing relationships between two numerical variables',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'x_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='List of x-axis numerical values'
            ),
            'y_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='List of y-axis numerical values'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'x_title': types.Schema(
                type='STRING',
                description='Label for the x-axis'
            ),
            'y_title': types.Schema(
                type='STRING',
                description='Label for the y-axis'
            ),
            'size_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='Optional list of values for point sizes'
            ),
            'color_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='Optional list of categories for point colors'
            )
        },
        required=['x_data', 'y_data']
    )
)

PIE_CHART_FUNCTION = types.FunctionDeclaration(
    name='create_pie_chart',
    description='Create a pie chart for showing proportions or percentages of a whole',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'labels': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of category labels'
            ),
            'values': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='List of numerical values for each category'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'show_percentages': types.Schema(
                type='BOOLEAN',
                description='Whether to display percentages on the chart'
            )
        },
        required=['labels', 'values']
    )
)

HISTOGRAM_FUNCTION = types.FunctionDeclaration(
    name='create_histogram',
    description='Create a histogram for showing data distribution and frequency',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='List of numerical values to create histogram from'
            ),
            'bins': types.Schema(
                type='INTEGER',
                description='Number of bins for the histogram'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'x_title': types.Schema(
                type='STRING',
                description='Label for the x-axis'
            ),
            'y_title': types.Schema(
                type='STRING',
                description='Label for the y-axis'
            )
        },
        required=['data']
    )
)

HEATMAP_FUNCTION = types.FunctionDeclaration(
    name='create_heatmap',
    description='Create a heatmap for showing relationships in matrix data or correlation',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'data': types.Schema(
                type='ARRAY',
                items=types.Schema(
                    type='ARRAY',
                    items=types.Schema(type='NUMBER')
                ),
                description='2D array of numerical values for the heatmap'
            ),
            'x_labels': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of labels for x-axis'
            ),
            'y_labels': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of labels for y-axis'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'color_scale': types.Schema(
                type='STRING',
                description='Color scale for the heatmap (Viridis, Blues, Reds, etc.)'
            )
        },
        required=['data', 'x_labels', 'y_labels']
    )
)

BOX_PLOT_FUNCTION = types.FunctionDeclaration(
    name='create_box_plot',
    description='Create a box plot for showing data distribution and outliers across categories',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'data_groups_json': types.Schema(
                type='STRING',
                description='JSON string representing dictionary where keys are group names and values are arrays of numbers. Example: {"Group A": [1,2,3], "Group B": [4,5,6]}'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'y_title': types.Schema(
                type='STRING',
                description='Label for the y-axis'
            )
        },
        required=['data_groups_json']
    )
)

AREA_CHART_FUNCTION = types.FunctionDeclaration(
    name='create_area_chart',
    description='Create an area chart for showing filled trends or cumulative data',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'x_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of x-axis values (dates, categories, etc.)'
            ),
            'y_data': types.Schema(
                type='ARRAY',
                items=types.Schema(type='NUMBER'),
                description='List of y-axis numerical values'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'x_title': types.Schema(
                type='STRING',
                description='Label for the x-axis'
            ),
            'y_title': types.Schema(
                type='STRING',
                description='Label for the y-axis'
            ),
            'fill_color': types.Schema(
                type='STRING',
                description='Color for the filled area'
            )
        },
        required=['x_data', 'y_data']
    )
)

VIOLIN_PLOT_FUNCTION = types.FunctionDeclaration(
    name='create_violin_plot',
    description='Create a violin plot for showing data distribution shapes and density',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'data_groups_json': types.Schema(
                type='STRING',
                description='JSON string representing dictionary where keys are group names and values are arrays of numbers. Example: {"Group A": [1,2,3], "Group B": [4,5,6]}'
            ),
            'title': types.Schema(
                type='STRING',
                description='Title for the chart'
            ),
            'y_title': types.Schema(
                type='STRING',
                description='Label for the y-axis'
            )
        },
        required=['data_groups_json']
    )
)

# Data generation function declarations
BUSINESS_DATA_FUNCTION = types.FunctionDeclaration(
    name='generate_business_data',
    description='Generate business-related data like sales, revenue, or performance metrics',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'data_type': types.Schema(
                type='STRING',
                description='Type of business data: sales, revenue, customers, growth, etc.'
            ),
            'categories': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of categories (products, regions, departments, etc.)'
            ),
            'trend': types.Schema(
                type='STRING',
                description='Overall trend: increasing, decreasing, random, seasonal'
            ),
            'base_value': types.Schema(
                type='NUMBER',
                description='Base value around which data is generated'
            ),
            'variation': types.Schema(
                type='NUMBER',
                description='Amount of variation (0.0 to 1.0)'
            )
        },
        required=['data_type', 'categories']
    )
)

TIME_SERIES_DATA_FUNCTION = types.FunctionDeclaration(
    name='generate_time_series_data',
    description='Generate time series data with various patterns over time',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'start_date': types.Schema(
                type='STRING',
                description='Start date in YYYY-MM-DD format'
            ),
            'end_date': types.Schema(
                type='STRING',
                description='End date in YYYY-MM-DD format'
            ),
            'pattern': types.Schema(
                type='STRING',
                description='Pattern type: linear, exponential, seasonal, trend_seasonal'
            ),
            'frequency': types.Schema(
                type='STRING',
                description='Data frequency: daily, weekly, monthly'
            ),
            'base_value': types.Schema(
                type='NUMBER',
                description='Base value for the series'
            ),
            'noise_level': types.Schema(
                type='NUMBER',
                description='Amount of random noise (0.0 to 1.0)'
            )
        },
        required=['start_date', 'end_date']
    )
)

STATISTICAL_DATA_FUNCTION = types.FunctionDeclaration(
    name='generate_statistical_data',
    description='Generate data following specific statistical distributions',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'distribution': types.Schema(
                type='STRING',
                description='Type of distribution: normal, uniform, exponential, gamma'
            ),
            'size': types.Schema(
                type='INTEGER',
                description='Number of data points to generate'
            ),
            'parameters_json': types.Schema(
                type='STRING',
                description='JSON string of distribution parameters (mean, std, min, max, scale, shape, etc.). Example: {"mean": 0, "std": 1}'
            )
        },
        required=['distribution', 'size', 'parameters_json']
    )
)

COMPARISON_DATA_FUNCTION = types.FunctionDeclaration(
    name='generate_comparison_data',
    description='Generate comparison data for multiple items across multiple metrics',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'items': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of items to compare (products, companies, etc.)'
            ),
            'metrics': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of metrics to compare (performance, cost, quality, etc.)'
            ),
            'min_value': types.Schema(
                type='NUMBER',
                description='Minimum value for generated data'
            ),
            'max_value': types.Schema(
                type='NUMBER', 
                description='Maximum value for generated data'
            )
        },
        required=['items', 'metrics']
    )
)

# Additional data generation functions (keeping existing ones)
DEMOGRAPHIC_DATA_FUNCTION = types.FunctionDeclaration(
    name='generate_demographic_data',
    description='Generate demographic data with realistic distributions',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'categories': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='Demographic categories (age groups, regions, etc.)'
            ),
            'total_population': types.Schema(
                type='INTEGER',
                description='Total population to distribute'
            ),
            'distribution': types.Schema(
                type='STRING',
                description='Type of distribution: uniform, realistic, skewed'
            )
        },
        required=['categories']
    )
)

PERFORMANCE_DATA_FUNCTION = types.FunctionDeclaration(
    name='generate_performance_data',
    description='Generate performance data across entities and time periods',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'entities': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of entities (employees, teams, products, etc.)'
            ),
            'time_periods': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of time periods (months, quarters, etc.)'
            ),
            'metric_type': types.Schema(
                type='STRING',
                description='Type of metric: score, percentage, rating'
            ),
            'trend': types.Schema(
                type='STRING',
                description='Overall trend: improving, declining, mixed, stable'
            )
        },
        required=['entities', 'time_periods']
    )
)

FINANCIAL_DATA_FUNCTION = types.FunctionDeclaration(
    name='generate_financial_data',
    description='Generate financial time series data (stock prices, returns, etc.)',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'securities': types.Schema(
                type='ARRAY',
                items=types.Schema(type='STRING'),
                description='List of security names/tickers'
            ),
            'start_date': types.Schema(
                type='STRING',
                description='Start date in YYYY-MM-DD format'
            ),
            'end_date': types.Schema(
                type='STRING',
                description='End date in YYYY-MM-DD format'
            ),
            'volatility': types.Schema(
                type='NUMBER',
                description='Daily volatility (standard deviation of returns)'
            )
        },
        required=['securities', 'start_date', 'end_date']
    )
)

# Collect all chart functions
CHART_FUNCTIONS = [
    BAR_CHART_FUNCTION,
    LINE_CHART_FUNCTION,
    SCATTER_PLOT_FUNCTION,
    PIE_CHART_FUNCTION,
    HISTOGRAM_FUNCTION,
    HEATMAP_FUNCTION,
    BOX_PLOT_FUNCTION,
    AREA_CHART_FUNCTION,
    VIOLIN_PLOT_FUNCTION
]

# Collect all data generation functions
DATA_GENERATION_FUNCTIONS = [
    BUSINESS_DATA_FUNCTION,
    TIME_SERIES_DATA_FUNCTION,
    STATISTICAL_DATA_FUNCTION,
    COMPARISON_DATA_FUNCTION,
    DEMOGRAPHIC_DATA_FUNCTION,
    PERFORMANCE_DATA_FUNCTION,
    FINANCIAL_DATA_FUNCTION
]

# Combine all functions
ALL_FUNCTIONS = CHART_FUNCTIONS + DATA_GENERATION_FUNCTIONS

# Create tool configuration for Gemini
CHART_TOOLS = [types.Tool(function_declarations=ALL_FUNCTIONS)]

# Configuration for different use cases
CHART_ONLY_TOOLS = [types.Tool(function_declarations=CHART_FUNCTIONS)]
DATA_ONLY_TOOLS = [types.Tool(function_declarations=DATA_GENERATION_FUNCTIONS)]

# Function mapping for execution (to be used in helper functions)
FUNCTION_MAP = {
    # Chart functions - these will be imported from chart_functions.py
    'create_bar_chart': 'chart_functions.create_bar_chart',
    'create_line_chart': 'chart_functions.create_line_chart',
    'create_scatter_plot': 'chart_functions.create_scatter_plot',
    'create_pie_chart': 'chart_functions.create_pie_chart',
    'create_histogram': 'chart_functions.create_histogram',
    'create_heatmap': 'chart_functions.create_heatmap',
    'create_box_plot': 'chart_functions.create_box_plot',
    'create_area_chart': 'chart_functions.create_area_chart',
    'create_violin_plot': 'chart_functions.create_violin_plot',
    
    # Data generation functions - these will be imported from data_generators.py
    'generate_business_data': 'data_generators.generate_business_data',
    'generate_time_series_data': 'data_generators.generate_time_series_data',
    'generate_statistical_data': 'data_generators.generate_statistical_data',
    'generate_comparison_data': 'data_generators.generate_comparison_data',
    'generate_demographic_data': 'data_generators.generate_demographic_data',
    'generate_performance_data': 'data_generators.generate_performance_data',
    'generate_financial_data': 'data_generators.generate_financial_data'
}

# UPDATED SYSTEM INSTRUCTION - ENFORCES 2-STEP WORKFLOW
SYSTEM_INSTRUCTION = """You are a data visualization assistant that creates charts by following a strict 2-step process.

CRITICAL WORKFLOW - ALWAYS FOLLOW THESE STEPS:

**STEP 1: ANALYZE THE REQUEST**
For every user request, first determine:
1. What type of data is needed? (business, time series, statistical, comparison, demographic, performance, financial)
2. What type of visualization is most appropriate? (bar, line, scatter, pie, histogram, heatmap, box, area, violin)
3. What parameters are needed for both data generation and visualization?

**STEP 2: EXECUTE 2-FUNCTION WORKFLOW**
For ALL visualization requests, you MUST make exactly TWO function calls in sequence:

1. **FIRST CALL**: Use appropriate data generation function to create realistic data
   - generate_business_data: for sales, revenue, performance metrics
   - generate_time_series_data: for trends over time, temporal patterns
   - generate_statistical_data: for distributions, statistical analysis
   - generate_comparison_data: for comparing items across metrics
   - generate_demographic_data: for population, demographic analysis
   - generate_performance_data: for performance across entities/time
   - generate_financial_data: for financial time series, securities data

2. **SECOND CALL**: Use appropriate chart creation function with the generated data
   - create_bar_chart: for comparing categories, discrete values
   - create_line_chart: for trends over time, continuous data
   - create_scatter_plot: for relationships between two variables
   - create_pie_chart: for proportions, percentages of whole
   - create_histogram: for data distributions, frequency analysis
   - create_heatmap: for correlation matrices, 2D relationships
   - create_box_plot: for distribution analysis, outliers
   - create_area_chart: for filled trend visualizations
   - create_violin_plot: for distribution shapes, density

**ONE-SHOT EXAMPLE:**

User Request: "Show me a bar chart of sales performance across different product categories"

Analysis:
- Data needed: Business sales data across product categories
- Visualization: Bar chart for category comparison
- Parameters: Product categories, sales values, realistic business context

Function Call 1:
```
generate_business_data(
    data_type="sales",
    categories=["Electronics", "Clothing", "Home & Garden", "Books", "Sports"],
    trend="random",
    base_value=50000,
    variation=0.3
)
```

Function Call 2 (using the generated data):
```
create_bar_chart(
    categories=["Electronics", "Clothing", "Home & Garden", "Books", "Sports"],
    values=[65000, 42000, 58000, 28000, 51000],  # Values from generated data
    title="Sales Performance by Product Category",
    x_title="Product Categories",
    y_title="Sales ($)",
    color_scheme="plotly"
)
```

**IMPORTANT RULES:**
- NEVER create charts with hardcoded sample data
- NEVER skip the data generation step for visualizations
- ALWAYS use realistic parameters that match the user's context
- If user asks for "data only" (no visualization), use only data generation functions
- If user asks for visualizations, ALWAYS use both data generation AND chart creation
- Match data generation parameters to user's specific domain (business context, time periods, etc.)
- Ensure data generation parameters create appropriate scale and variety for the visualization

**EXAMPLE REQUEST PATTERNS:**

"Show me quarterly revenue trends" →
1. generate_time_series_data(quarterly data, revenue pattern)  
2. create_line_chart(with generated time series data)

"Compare employee performance across departments" →  
1. generate_comparison_data(departments, performance metrics)
2. create_bar_chart(with generated comparison data)

"Create a scatter plot of marketing spend vs sales" →
1. generate_business_data(marketing and sales data)  
2. create_scatter_plot(with generated business data)

"Generate sales data for Q4" → 
Only: generate_business_data(Q4 sales parameters) - NO chart since no visualization requested

Always provide clear explanations of what data you're generating and why you chose the specific visualization type."""

# Export configurations for use in other modules
__all__ = [
    'genai_client',
    'GENERATION_CONFIG', 
    'BASIC_CONFIG',
    'DATA_HEAVY_CONFIG',
    'MODELS',
    'CHART_TOOLS',
    'SYSTEM_INSTRUCTION'
]