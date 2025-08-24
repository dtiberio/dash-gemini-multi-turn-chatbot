# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# app_llm.py
"""Enhanced module to handle interactions with the Gemini API for the Dash chatbot application.
This module initializes the Gemini client with function calling capabilities for chart generation
and provides comprehensive configuration for intelligent visualization creation.
"""

import os
from google import genai
from google.genai import types
from function_declarations import CHART_TOOLS, SYSTEM_INSTRUCTION

# Load GCP Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
genai_client = genai.Client(api_key=GEMINI_API_KEY)

# Comprehensive generation configuration with function calling
GENERATION_CONFIG = types.GenerateContentConfig(
    temperature=0.7,  # Good balance for creativity and consistency
    max_output_tokens=2000,  # Sufficient for explanations + function calls
    system_instruction=SYSTEM_INSTRUCTION,  # Intelligent chart selection instructions
    tools=CHART_TOOLS,  # All chart and data generation functions
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=False,  # Enable automatic function calling
        maximum_remote_calls=3  # Limit to prevent excessive function calls
    )
)

# Enhanced models list with function calling descriptions
MODELS = [
    {
        "value": "gemini-2.5-flash", 
        "label": "Gemini 2.5 Flash - Speed and efficiency with intelligent visualization"
    },
    {
        "value": "gemini-2.5-flash-lite", 
        "label": "Gemini 2.5 Flash-Lite - Cost efficiency with basic function calling"
    },
]

# Additional configuration options for different use cases
BASIC_CONFIG = types.GenerateContentConfig(
    temperature=0.5,
    max_output_tokens=1000,
    system_instruction="You are a helpful assistant that provides clear and concise responses."
)

# Configuration for data-heavy requests
DATA_HEAVY_CONFIG = types.GenerateContentConfig(
    temperature=0.3,  # Lower temperature for more consistent data generation
    max_output_tokens=3000,  # More tokens for complex visualizations
    system_instruction=SYSTEM_INSTRUCTION,
    tools=CHART_TOOLS,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=False,
        maximum_remote_calls=5  # Allow more function calls for complex requests
    )
)

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