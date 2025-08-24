# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# chart_functions.py
"""Chart generation functions for Gemini function calling.
Each function returns a Plotly figure dictionary compatible with dash-chat's graph renderer.
Modified functions to handle JSON string parameters for complex data types.
Includes comprehensive logging for debugging chart generation issues.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any, Optional

# Enhanced logging imports
from logger_config import (
    get_chart_logger,
    LoggedOperation
)

# Initialize chart logger
chart_logger = get_chart_logger()

def create_bar_chart(
    categories: List[str], 
    values: List[float], 
    title: str = "Bar Chart",
    x_title: str = "Categories",
    y_title: str = "Values",
    color_scheme: str = "plotly"
) -> Dict[str, Any]:
    """
    Create a bar chart for comparing categories.
    FIXED: Color scheme handling and error prevention.
    ENHANCED: Comprehensive logging and error handling.
    """
    with LoggedOperation(chart_logger, "create_bar_chart", 
                        categories_count=len(categories),
                        values_count=len(values),
                        title=title):
        
        try:
            # Input validation with logging
            chart_logger.info(f"Creating bar chart: '{title}'")
            chart_logger.debug(f"Categories: {categories[:5]}{'...' if len(categories) > 5 else ''}")
            chart_logger.debug(f"Values: {values[:5]}{'...' if len(values) > 5 else ''}")
            chart_logger.debug(f"Color scheme: {color_scheme}")
            
            # Validate inputs
            if len(categories) != len(values):
                chart_logger.error(f"Length mismatch: {len(categories)} categories vs {len(values)} values")
                raise ValueError(f"Categories and values must have same length: {len(categories)} vs {len(values)}")
            
            if len(categories) == 0:
                chart_logger.warning("Empty categories list provided")
                raise ValueError("Categories list cannot be empty")
            
            # Create DataFrame
            chart_logger.debug("Creating pandas DataFrame")
            df = pd.DataFrame({
                'categories': categories,
                'values': values
            })
            chart_logger.debug(f"DataFrame created with shape: {df.shape}")
            
            # Create the bar chart
            chart_logger.debug("Creating Plotly bar chart")
            fig = px.bar(
                df, 
                x='categories', 
                y='values', 
                title=title,
                labels={'categories': x_title, 'values': y_title}
            )
            chart_logger.debug("Bar chart figure created successfully")
            
            # Update layout
            chart_logger.debug("Updating chart layout")
            fig.update_layout(
                xaxis_title=x_title,
                yaxis_title=y_title,
                template="plotly_white",
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            # FIXED: Correct method name
            chart_logger.debug("Updating x-axis configuration")
            fig.update_xaxes(
                categoryorder='array',
                categoryarray=categories
            )
            
            # Convert to dictionary
            chart_logger.debug("Converting figure to dictionary")
            chart_dict = fig.to_dict()
            chart_logger.info(f"✅ Bar chart created successfully with {len(categories)} categories")
            
            return chart_dict
            
        except Exception as e:
            chart_logger.error(f"❌ Bar chart creation failed: {str(e)}", exc_info=True)
            chart_logger.error(f"Input details - Categories: {len(categories) if categories else 'None'}, Values: {len(values) if values else 'None'}")
            
            # Create error visualization
            chart_logger.debug("Creating error visualization")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Chart creation failed.<br>Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, 
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title="Chart Generation Error",
                template="plotly_white",
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            chart_logger.info("Error visualization created")
            return fig.to_dict()


def create_line_chart(
    x_data: List[Any], 
    y_data: List[float], 
    title: str = "Line Chart",
    x_title: str = "X-axis",
    y_title: str = "Y-axis",
    line_color: str = "blue"
) -> Dict[str, Any]:
    """
    Create a line chart for showing trends over time or continuous data.
    ENHANCED: Comprehensive logging and error handling.
    
    Args:
        x_data: List of x-axis values (can be dates, numbers, etc.)
        y_data: List of y-axis numerical values
        title: Chart title
        x_title: X-axis label
        y_title: Y-axis label
        line_color: Color of the line
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    with LoggedOperation(chart_logger, "create_line_chart",
                        x_data_count=len(x_data),
                        y_data_count=len(y_data),
                        title=title):
        
        try:
            chart_logger.info(f"Creating line chart: '{title}'")
            chart_logger.debug(f"X data length: {len(x_data)}, Y data length: {len(y_data)}")
            chart_logger.debug(f"Line color: {line_color}")
            
            # Input validation
            if len(x_data) != len(y_data):
                chart_logger.error(f"Length mismatch: {len(x_data)} x_data vs {len(y_data)} y_data")
                raise ValueError(f"X and Y data must have same length: {len(x_data)} vs {len(y_data)}")
            
            df = pd.DataFrame({
                'x': x_data,
                'y': y_data
            })
            
            fig = px.line(
                df, 
                x='x', 
                y='y', 
                title=title,
                line_shape='linear'
            )
            
            fig.update_traces(line_color=line_color)
            fig.update_layout(
                xaxis_title=x_title,
                yaxis_title=y_title,
                template="plotly_white",
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            chart_logger.info(f"✅ Line chart created successfully with {len(x_data)} data points")
            return fig.to_dict()
            
        except Exception as e:
            chart_logger.error(f"❌ Line chart creation failed: {str(e)}", exc_info=True)
            
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating line chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(title="Chart Generation Error")
            return fig.to_dict()


def create_scatter_plot(
    x_data: List[float], 
    y_data: List[float], 
    title: str = "Scatter Plot",
    x_title: str = "X-axis",
    y_title: str = "Y-axis",
    size_data: Optional[List[float]] = None,
    color_data: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a scatter plot for showing relationships between two variables.
    
    Args:
        x_data: List of x-axis numerical values
        y_data: List of y-axis numerical values
        title: Chart title
        x_title: X-axis label
        y_title: Y-axis label
        size_data: Optional list of values for point sizes
        color_data: Optional list of categories for point colors
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    try:
        df_dict = {'x': x_data, 'y': y_data}
        
        if size_data:
            df_dict['size'] = size_data
        if color_data:
            df_dict['color'] = color_data
            
        df = pd.DataFrame(df_dict)
        
        fig = px.scatter(
            df, 
            x='x', 
            y='y', 
            title=title,
            size='size' if size_data else None,
            color='color' if color_data else None
        )
        
        fig.update_layout(
            xaxis_title=x_title,
            yaxis_title=y_title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_dict()
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating scatter plot: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Chart Generation Error")
        return fig.to_dict()


def create_pie_chart(
    labels: List[str], 
    values: List[float], 
    title: str = "Pie Chart",
    show_percentages: bool = True
) -> Dict[str, Any]:
    """
    Create a pie chart for showing proportions.
    ENHANCED: Comprehensive logging and error handling.
    
    Args:
        labels: List of category labels
        values: List of numerical values for each category
        title: Chart title
        show_percentages: Whether to display percentages on the chart
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    with LoggedOperation(chart_logger, "create_pie_chart",
                        labels_count=len(labels),
                        values_count=len(values),
                        title=title):
        
        try:
            chart_logger.info(f"Creating pie chart: '{title}'")
            chart_logger.debug(f"Labels: {labels[:5]}{'...' if len(labels) > 5 else ''}")
            chart_logger.debug(f"Show percentages: {show_percentages}")
            
            # Input validation
            if len(labels) != len(values):
                chart_logger.error(f"Length mismatch: {len(labels)} labels vs {len(values)} values")
                raise ValueError(f"Labels and values must have same length: {len(labels)} vs {len(values)}")
            
            # Check for non-negative values
            if any(v < 0 for v in values):
                chart_logger.warning("Negative values found in pie chart data")
            
            df = pd.DataFrame({
                'labels': labels,
                'values': values
            })
            
            fig = px.pie(
                df, 
                names='labels', 
                values='values', 
                title=title
            )
            
            if show_percentages:
                fig.update_traces(textposition='inside', textinfo='percent+label')
            else:
                fig.update_traces(textposition='inside', textinfo='label')
                
            fig.update_layout(
                template="plotly_white",
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            chart_logger.info(f"✅ Pie chart created successfully with {len(labels)} segments")
            return fig.to_dict()
            
        except Exception as e:
            chart_logger.error(f"❌ Pie chart creation failed: {str(e)}", exc_info=True)
            
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating pie chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(title="Chart Generation Error")
            return fig.to_dict()


def create_histogram(
    data: List[float], 
    bins: int = 20, 
    title: str = "Histogram",
    x_title: str = "Values",
    y_title: str = "Frequency"
) -> Dict[str, Any]:
    """
    Create a histogram for showing data distribution.
    
    Args:
        data: List of numerical values
        bins: Number of bins for the histogram
        title: Chart title
        x_title: X-axis label
        y_title: Y-axis label
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    try:
        df = pd.DataFrame({'values': data})
        
        fig = px.histogram(
            df, 
            x='values', 
            nbins=bins,
            title=title
        )
        
        fig.update_layout(
            xaxis_title=x_title,
            yaxis_title=y_title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_dict()
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating histogram: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Chart Generation Error")
        return fig.to_dict()


def create_heatmap(
    data: List[List[float]], 
    x_labels: List[str], 
    y_labels: List[str], 
    title: str = "Heatmap",
    color_scale: str = "Viridis"
) -> Dict[str, Any]:
    """
    Create a heatmap for showing relationships in matrix data.
    
    Args:
        data: 2D list of numerical values
        x_labels: List of labels for x-axis
        y_labels: List of labels for y-axis
        title: Chart title
        color_scale: Color scale for the heatmap
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    try:
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=x_labels,
            y=y_labels,
            colorscale=color_scale
        ))
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_dict()
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating heatmap: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Chart Generation Error")
        return fig.to_dict()


def create_box_plot(
    data_groups_json: str, 
    title: str = "Box Plot",
    y_title: str = "Values"
) -> Dict[str, Any]:
    """
    Create a box plot for showing data distribution across categories.
    UPDATED: Now accepts JSON string for data_groups to work with Gemini API.
    
    Args:
        data_groups_json: JSON string representing dictionary where keys are group names 
                         and values are lists of numbers
        title: Chart title
        y_title: Y-axis label
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    try:
        # Parse JSON string to dictionary
        data_groups = json.loads(data_groups_json)
        
        # Convert data_groups to DataFrame format
        data_list = []
        for group_name, values in data_groups.items():
            for value in values:
                data_list.append({'group': group_name, 'value': value})
        
        df = pd.DataFrame(data_list)
        
        fig = px.box(
            df, 
            x='group', 
            y='value', 
            title=title
        )
        
        fig.update_layout(
            xaxis_title="Groups",
            yaxis_title=y_title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_dict()
        
    except json.JSONDecodeError as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error parsing JSON data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="JSON Parse Error")
        return fig.to_dict()
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating box plot: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Chart Generation Error")
        return fig.to_dict()


def create_area_chart(
    x_data: List[Any], 
    y_data: List[float], 
    title: str = "Area Chart",
    x_title: str = "X-axis",
    y_title: str = "Y-axis",
    fill_color: str = "lightblue"
) -> Dict[str, Any]:
    """
    Create an area chart for showing filled trends.
    
    Args:
        x_data: List of x-axis values
        y_data: List of y-axis numerical values
        title: Chart title
        x_title: X-axis label
        y_title: Y-axis label
        fill_color: Color for the filled area
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    try:
        df = pd.DataFrame({
            'x': x_data,
            'y': y_data
        })
        
        fig = px.area(
            df, 
            x='x', 
            y='y', 
            title=title
        )
        
        fig.update_traces(fill='tonexty', fillcolor=fill_color)
        fig.update_layout(
            xaxis_title=x_title,
            yaxis_title=y_title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_dict()
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating area chart: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Chart Generation Error")
        return fig.to_dict()


def create_violin_plot(
    data_groups_json: str, 
    title: str = "Violin Plot",
    y_title: str = "Values"
) -> Dict[str, Any]:
    """
    Create a violin plot for showing data distribution shapes.
    UPDATED: Now accepts JSON string for data_groups to work with Gemini API.
    
    Args:
        data_groups_json: JSON string representing dictionary where keys are group names 
                         and values are lists of numbers
        title: Chart title
        y_title: Y-axis label
    
    Returns:
        Dictionary containing Plotly figure data and layout
    """
    try:
        # Parse JSON string to dictionary
        data_groups = json.loads(data_groups_json)
        
        # Convert data_groups to DataFrame format
        data_list = []
        for group_name, values in data_groups.items():
            for value in values:
                data_list.append({'group': group_name, 'value': value})
        
        df = pd.DataFrame(data_list)
        
        fig = px.violin(
            df, 
            x='group', 
            y='value', 
            title=title
        )
        
        fig.update_layout(
            xaxis_title="Groups",
            yaxis_title=y_title,
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig.to_dict()
        
    except json.JSONDecodeError as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error parsing JSON data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="JSON Parse Error")
        return fig.to_dict()
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating violin plot: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Chart Generation Error")
        return fig.to_dict()