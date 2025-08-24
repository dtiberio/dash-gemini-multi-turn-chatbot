# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# data_generators.py
"""Intelligent data generation functions for creating contextually appropriate datasets.
These functions generate realistic data patterns based on user context and domain.
Modified functions to handle new parameter structures from fixed function declarations.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Optional
import random
import math
import json


def generate_business_data(
    data_type: str, 
    categories: List[str], 
    trend: str = "random",
    base_value: float = 100,
    variation: float = 0.3
) -> Dict[str, List]:
    """
    Generate business-related data like sales, revenue, performance metrics.
    
    Args:
        data_type: Type of business data ('sales', 'revenue', 'customers', 'growth')
        categories: List of categories (products, regions, departments, etc.)
        trend: Overall trend ('increasing', 'decreasing', 'random', 'seasonal')
        base_value: Base value around which data is generated
        variation: Amount of variation (0.0 to 1.0)
    
    Returns:
        Dictionary with 'categories' and 'values' keys
    """
    try:
        np.random.seed(42)  # For consistent results
        n_categories = len(categories)
        
        # Generate base values
        if trend == "increasing":
            base_values = np.linspace(base_value * 0.7, base_value * 1.3, n_categories)
        elif trend == "decreasing":
            base_values = np.linspace(base_value * 1.3, base_value * 0.7, n_categories)
        elif trend == "seasonal":
            # Create a seasonal pattern
            x = np.linspace(0, 2 * np.pi, n_categories)
            base_values = base_value + (base_value * 0.3 * np.sin(x))
        else:  # random
            base_values = np.full(n_categories, base_value)
        
        # Add variation
        noise = np.random.normal(0, base_value * variation, n_categories)
        values = base_values + noise
        
        # Ensure positive values for business data
        values = np.maximum(values, base_value * 0.1)
        
        # Apply data type specific adjustments
        if data_type.lower() in ['sales', 'revenue']:
            values = np.round(values, 2)
        elif data_type.lower() == 'customers':
            values = np.round(values).astype(int)
        elif data_type.lower() == 'growth':
            # Convert to percentage
            values = ((values / base_value) - 1) * 100
            values = np.round(values, 1)
        
        return {
            'categories': categories,
            'values': values.tolist()
        }
        
    except Exception as e:
        # Return simple default data on error
        return {
            'categories': categories,
            'values': [100] * len(categories)
        }


def generate_time_series_data(
    start_date: str, 
    end_date: str, 
    pattern: str = "linear",
    frequency: str = "daily",
    base_value: float = 100,
    noise_level: float = 0.1
) -> Dict[str, List]:
    """
    Generate time series data with various patterns.
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        pattern: Pattern type ('linear', 'exponential', 'seasonal', 'trend_seasonal')
        frequency: Data frequency ('daily', 'weekly', 'monthly')
        base_value: Base value for the series
        noise_level: Amount of random noise (0.0 to 1.0)
    
    Returns:
        Dictionary with 'dates' and 'values' keys
    """
    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Generate date range
        if frequency == "daily":
            dates = pd.date_range(start=start, end=end, freq='D')
        elif frequency == "weekly":
            dates = pd.date_range(start=start, end=end, freq='W')
        elif frequency == "monthly":
            dates = pd.date_range(start=start, end=end, freq='M')
        else:
            dates = pd.date_range(start=start, end=end, freq='D')
        
        n_points = len(dates)
        x = np.linspace(0, 1, n_points)
        
        # Generate base pattern
        if pattern == "linear":
            values = base_value + (base_value * 0.5 * x)
        elif pattern == "exponential":
            values = base_value * np.exp(x * 0.5)
        elif pattern == "seasonal":
            values = base_value + (base_value * 0.3 * np.sin(2 * np.pi * x * 4))
        elif pattern == "trend_seasonal":
            trend = base_value + (base_value * 0.3 * x)
            seasonal = base_value * 0.2 * np.sin(2 * np.pi * x * 4)
            values = trend + seasonal
        else:
            values = np.full(n_points, base_value)
        
        # Add noise
        if noise_level > 0:
            noise = np.random.normal(0, base_value * noise_level, n_points)
            values += noise
        
        # Ensure positive values
        values = np.maximum(values, base_value * 0.1)
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'values': np.round(values, 2).tolist()
        }
        
    except Exception as e:
        # Return simple default data on error
        default_dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in default_dates],
            'values': [100] * 30
        }


# Updated generate_statistical_data function in data_generators.py
# Replace the existing function with this version

def generate_statistical_data(
    distribution: str, 
    size: int, 
    parameters_json: str
) -> Dict[str, Any]:
    """
    Generate data following specific statistical distributions.
    UPDATED: Now returns consistent Dict structure like other data generation functions.
    
    Args:
        distribution: Type of distribution ('normal', 'uniform', 'exponential', 'gamma')
        size: Number of data points to generate
        parameters_json: JSON string of distribution parameters (mean, std, min, max, etc.)
    
    Returns:
        Dict with consistent structure: {'data': List[float], 'distribution': str, 'size': int, 'parameters': dict}
    """
    try:
        np.random.seed(42)
        
        # Parse JSON string to dictionary
        parameters = json.loads(parameters_json)
        
        if distribution == "normal":
            mean = parameters.get('mean', 0)
            std = parameters.get('std', 1)
            values = np.random.normal(mean, std, size)
            
        elif distribution == "uniform":
            min_val = parameters.get('min', 0)
            max_val = parameters.get('max', 1)
            values = np.random.uniform(min_val, max_val, size)
            
        elif distribution == "exponential":
            scale = parameters.get('scale', 1)
            values = np.random.exponential(scale, size)
            
        elif distribution == "gamma":
            shape = parameters.get('shape', 2)
            scale = parameters.get('scale', 1)
            values = np.random.gamma(shape, scale, size)
            
        else:
            # Default to normal distribution
            values = np.random.normal(0, 1, size)
        
        # FIXED: Return consistent Dict structure like other data generation functions
        return {
            'data': np.round(values, 3).tolist(),
            'distribution': distribution,
            'size': size,
            'parameters': parameters,
            'type': 'statistical'  # Helps with visualization type detection
        }
        
    except json.JSONDecodeError as e:
        # Return simple random data on JSON parse error with consistent structure
        return {
            'data': [round(random.random() * 100, 2) for _ in range(size)],
            'distribution': 'uniform',
            'size': size,
            'parameters': {'min': 0, 'max': 100},
            'type': 'statistical'
        }
        
    except Exception as e:
        # Return simple random data on error with consistent structure
        return {
            'data': [round(random.random() * 100, 2) for _ in range(size)],
            'distribution': 'uniform', 
            'size': size,
            'parameters': {'min': 0, 'max': 100},
            'type': 'statistical'
        }


def generate_comparison_data(
    items: List[str], 
    metrics: List[str],
    min_value: float = 50,
    max_value: float = 150
) -> Dict[str, Any]:
    """
    Generate comparison data for multiple items across multiple metrics.
    UPDATED: Now accepts separate min_value and max_value parameters instead of data_range tuple.
    
    Args:
        items: List of items to compare (products, companies, etc.)
        metrics: List of metrics to compare (performance, cost, quality, etc.)
        min_value: Minimum value for generated data
        max_value: Maximum value for generated data
    
    Returns:
        Dictionary with structured comparison data
    """
    try:
        np.random.seed(42)
        
        data = {}
        
        # Generate data for each metric
        for metric in metrics:
            # Add some realistic variation per metric
            if 'cost' in metric.lower():
                # Cost metrics might be inversely related to quality
                base_values = np.random.uniform(min_value, max_value, len(items))
            elif 'quality' in metric.lower() or 'performance' in metric.lower():
                # Quality/performance might be normally distributed
                base_values = np.random.normal((min_value + max_value) / 2, 
                                             (max_value - min_value) / 6, len(items))
                base_values = np.clip(base_values, min_value, max_value)
            else:
                # Default random distribution
                base_values = np.random.uniform(min_value, max_value, len(items))
            
            data[metric] = np.round(base_values, 2).tolist()
        
        data['items'] = items
        return data
        
    except Exception as e:
        # Return simple default data on error
        return {
            'items': items,
            metrics[0] if metrics else 'value': [100] * len(items)
        }


# Keep other functions unchanged for now - they didn't have problematic function declarations
def generate_demographic_data(
    categories: List[str], 
    total_population: int = 10000,
    distribution: str = "realistic"
) -> Dict[str, List]:
    """
    Generate demographic data with realistic distributions.
    
    Args:
        categories: Demographic categories (age groups, regions, etc.)
        total_population: Total population to distribute
        distribution: Type of distribution ('uniform', 'realistic', 'skewed')
    
    Returns:
        Dictionary with categories and population counts
    """
    try:
        np.random.seed(42)
        n_categories = len(categories)
        
        if distribution == "uniform":
            # Equal distribution
            values = [total_population // n_categories] * n_categories
            # Handle remainder
            remainder = total_population % n_categories
            for i in range(remainder):
                values[i] += 1
                
        elif distribution == "realistic":
            # More realistic demographic distribution (some categories larger)
            weights = np.random.dirichlet(np.ones(n_categories) * 2)  # Somewhat even but varied
            values = (weights * total_population).astype(int)
            
        elif distribution == "skewed":
            # Heavily skewed distribution
            weights = np.random.power(2, n_categories)
            weights = weights / weights.sum()
            values = (weights * total_population).astype(int)
            
        else:
            # Default to uniform
            values = [total_population // n_categories] * n_categories
        
        # Ensure total adds up
        values = values.tolist()
        difference = total_population - sum(values)
        if difference != 0:
            values[0] += difference
        
        return {
            'categories': categories,
            'values': values
        }
        
    except Exception as e:
        # Return simple default data on error
        equal_share = total_population // len(categories)
        return {
            'categories': categories,
            'values': [equal_share] * len(categories)
        }


def generate_performance_data(
    entities: List[str],
    time_periods: List[str],
    metric_type: str = "score",
    trend: str = "mixed"
) -> Dict[str, Any]:
    """
    Generate performance data across entities and time periods.
    
    Args:
        entities: List of entities (employees, teams, products, etc.)
        time_periods: List of time periods (months, quarters, etc.)
        metric_type: Type of metric ('score', 'percentage', 'rating')
        trend: Overall trend ('improving', 'declining', 'mixed', 'stable')
    
    Returns:
        Dictionary with performance matrix data
    """
    try:
        np.random.seed(42)
        n_entities = len(entities)
        n_periods = len(time_periods)
        
        # Generate base performance matrix
        if metric_type == "score":
            base_range = (60, 95)  # Scores from 60-95
        elif metric_type == "percentage":
            base_range = (70, 100)  # Percentages 70-100%
        elif metric_type == "rating":
            base_range = (3, 5)  # Ratings 3-5
        else:
            base_range = (50, 100)
        
        min_val, max_val = base_range
        data_matrix = []
        
        for i, entity in enumerate(entities):
            entity_data = []
            
            # Generate trend for this entity
            if trend == "improving":
                base_values = np.linspace(min_val + random.uniform(0, 10), 
                                        max_val - random.uniform(0, 5), n_periods)
            elif trend == "declining":
                base_values = np.linspace(max_val - random.uniform(0, 5), 
                                        min_val + random.uniform(0, 10), n_periods)
            elif trend == "stable":
                base_val = random.uniform(min_val + 10, max_val - 10)
                base_values = np.full(n_periods, base_val)
            else:  # mixed
                # Random trend for each entity
                if random.random() < 0.33:
                    base_values = np.linspace(min_val + random.uniform(0, 10), 
                                            max_val - random.uniform(0, 5), n_periods)
                elif random.random() < 0.66:
                    base_values = np.linspace(max_val - random.uniform(0, 5), 
                                            min_val + random.uniform(0, 10), n_periods)
                else:
                    base_val = random.uniform(min_val + 10, max_val - 10)
                    base_values = np.full(n_periods, base_val)
            
            # Add noise
            noise = np.random.normal(0, (max_val - min_val) * 0.05, n_periods)
            values = base_values + noise
            values = np.clip(values, min_val, max_val)
            
            if metric_type == "rating":
                values = np.round(values, 1)
            else:
                values = np.round(values, 2)
            
            entity_data = values.tolist()
            data_matrix.append(entity_data)
        
        return {
            'entities': entities,
            'time_periods': time_periods,
            'data_matrix': data_matrix,
            'metric_type': metric_type
        }
        
    except Exception as e:
        # Return simple default data on error
        default_value = 85 if metric_type == "score" else 4.0
        return {
            'entities': entities,
            'time_periods': time_periods,
            'data_matrix': [[default_value] * len(time_periods) for _ in entities],
            'metric_type': metric_type
        }


def generate_financial_data(
    securities: List[str],
    start_date: str,
    end_date: str,
    volatility: float = 0.02
) -> Dict[str, Any]:
    """
    Generate financial time series data (stock prices, returns, etc.).
    
    Args:
        securities: List of security names/tickers
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        volatility: Daily volatility (standard deviation of returns)
    
    Returns:
        Dictionary with financial time series data
    """
    try:
        np.random.seed(42)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        n_days = len(dates)
        
        financial_data = {}
        
        for security in securities:
            # Generate random walk for stock price
            initial_price = random.uniform(50, 200)
            returns = np.random.normal(0, volatility, n_days)
            
            # Convert returns to prices using cumulative product
            price_ratios = np.exp(np.cumsum(returns))
            prices = initial_price * price_ratios
            
            financial_data[security] = np.round(prices, 2).tolist()
        
        financial_data['dates'] = [d.strftime('%Y-%m-%d') for d in dates]
        
        return financial_data
        
    except Exception as e:
        # Return simple default data on error
        default_dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        result = {'dates': [d.strftime('%Y-%m-%d') for d in default_dates]}
        
        for security in securities:
            result[security] = [100.0] * 30
            
        return result