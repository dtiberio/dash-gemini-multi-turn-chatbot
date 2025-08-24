# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# app_helpers_utils.py
"""Includes utility functions for generating chat responses,
handling multi-turn workflows, and processing Gemini API responses.
Enhanced with detailed logging and debugging capabilities.
This module is designed to support app_helpers.py.
"""

from typing import Union, List, Dict, Any, Optional
from app_llm import GENERATION_CONFIG, DATA_HEAVY_CONFIG
import chart_functions
import data_generators
import json

# Enhanced logging imports
from logger_config import (
    get_logger,
    get_function_call_logger, 
    get_api_logger,
    get_chart_logger,
    LoggedOperation,
    FunctionCallTracker
)

# Initialize specialized loggers
helpers_logger = get_logger('gemini_chatbot.helpers')
function_logger = get_function_call_logger()
api_logger = get_api_logger()
chart_logger = get_chart_logger()

def get_appropriate_config(messages: List[Dict], is_completion_call: bool):
    """
    Always returns the DATA_HEAVY_CONFIG configuration.
    """
    
    return DATA_HEAVY_CONFIG

def get_completion_system_instruction() -> str:
    """
    Get the system instruction for completion calls.
    ENHANCED: More explicit about data structures and function requirements.
    """
    
    return """You are in a completion step of a 2-step visualization workflow.

CONTEXT: You have already generated data in a previous step. Now you MUST create a visualization using that data.

YOUR TASK:
1. Identify what data was generated in the previous step
2. Choose the most appropriate chart type for that data
3. Call the appropriate create_* function to generate the visualization
4. Provide a complete response with the chart

AVAILABLE CHART FUNCTIONS:
- create_line_chart: for time series, trends over time
- create_bar_chart: for categories, comparisons
- create_pie_chart: for proportions, percentages
- create_scatter_plot: for relationships between variables
- create_histogram: for statistical distributions and frequency analysis (use this for generated statistical data)
- create_heatmap: for correlation matrices
- create_area_chart: for filled trends
- create_box_plot: for distribution analysis
- create_violin_plot: for distribution shapes

IMPORTANT DATA STRUCTURE NOTES:
- If statistical data was generated (with 'data', 'distribution', 'size' fields), use create_histogram with the 'data' field
- If business/categorical data was generated (with 'categories', 'values' fields), use create_bar_chart
- If time series data was generated (with 'dates', 'values' fields), use create_line_chart

CRITICAL: You MUST call a chart creation function. Do not return only text.
Look at the conversation context to understand what data is available and create an appropriate visualization."""

def build_completion_conversation(
    conversation      : list,
    workflow_type     : str,
    function_messages : list | None = None,
    assistant_reply   : str | None = None
) -> list:
    """
    Create the follow-up conversation when the initial workflow is incomplete.
    Inserts any function-role messages (with data JSON or data_id) *before*
    the user prompt that forces the chart call.
    Assemble the second-turn conversation for a 2-step workflow.
        • Reinsert Gemini's own step-1 reply (assistant role)
        • Expose the tool output via function-role messages
        • Finish with a user prompt that forces the chart call    
    """
    import copy

    conv = copy.deepcopy(conversation)

    # 0)Re-add the assistant text so Gemini has continuity
    if assistant_reply:
        conv.append({"role": "assistant", "content": assistant_reply.strip()})

    # 1) expose tool results, if any ----------------------------------------
    if function_messages:
        conv.extend(function_messages)

    # 2) user prompt that forces the next step ------------------------------
    if workflow_type == "incomplete":
        conv.append({
            "role": "user",
            "content": (
                "You have generated the required dataset. "
                "Now you MUST call the appropriate chart-creation function "
                "to visualise it. Use either the full 'data' list or the "
                "'data_id' provided earlier."
            )
        })

    return conv


def convert_gemini_response_to_message(gemini_response, processed_response) -> Dict:
    """
    Convert Gemini response to message format, preserving all attributes.
    ENHANCED: Better context building for statistical data.
    """
    
    # Start with the processed response text
    content = processed_response if isinstance(processed_response, str) else "I generated data for your request."
    
    # Add function call context if present
    if hasattr(gemini_response, 'function_calls') and gemini_response.function_calls:
        function_names = [getattr(fc, 'name', 'unknown') for fc in gemini_response.function_calls]
        function_context = f" I executed the following functions: {', '.join(function_names)}."

        # ENHANCED: Add data context for better completion prompting
        for func_call in gemini_response.function_calls:
            function_name = getattr(func_call, 'name', '')
            
            # For statistical data, mention the data characteristics
            if function_name == 'generate_statistical_data':
                if hasattr(func_call, 'args'):
                    distribution = func_call.args.get('distribution', 'unknown')
                    size = func_call.args.get('size', 'unknown')
                    function_context += f" Generated {size} data points with {distribution} distribution. This data is ready for histogram visualization to show the distribution pattern. The data is stored in a 'data' field containing numerical values."
                    
            # For time series, mention temporal aspect  
            elif function_name == 'generate_time_series_data':
                function_context += " Generated time series data for trend visualization."
                
            # For business data, mention categories
            elif function_name == 'generate_business_data':
                if hasattr(func_call, 'args'):
                    categories = func_call.args.get('categories', [])
                    if categories:
                        function_context += f" Generated data for {len(categories)} categories for comparison visualization."    

        content = f"{content} {function_context}".strip()
    
    message = {
        "role": "assistant",
        "content": content
    }
    
    helpers_logger.debug(f"Converted response to message: {len(content)} characters")
    return message

def create_completion_prompt(processed_response, gemini_response) -> str:
    """
    Create contextual prompt for visualization completion.
    ENHANCED: More explicit instructions for statistical data.
    """
    
    # Analyze what type of visualization is needed based on the previous response
    visualization_type = infer_visualization_type_from_response(processed_response, gemini_response)
    
    # Build enhanced context about the data that was generated
    data_context = ""
    if hasattr(gemini_response, 'function_calls') and gemini_response.function_calls:
        for func_call in gemini_response.function_calls:
            function_name = getattr(func_call, 'name', '')
            
            if function_name == 'generate_statistical_data':
                if hasattr(func_call, 'args'):
                    size = func_call.args.get('size', 100)
                    distribution = func_call.args.get('distribution', 'normal')
                    data_context = f"You have generated {size} numerical data points following a {distribution} distribution. "
    
    prompts = {
        "time_series": "Now create a line chart to visualize this time series data with appropriate labels and formatting.",
        "categorical": "Now create a bar chart to display this categorical data with clear labels and proper formatting.",
        "comparison": "Now create an appropriate comparison chart using this data with clear visualization.",
        "proportional": "Now create a pie chart to show the proportional breakdown of this data.",
        "distribution": f"{data_context}Now you MUST call the create_histogram function to display the distribution of this numerical data. Use the 'data' field from the generated statistical data as the input to create_histogram.",
        "correlation": "Now create a scatter plot to show the relationships in this data.",
        "default": "Now create an appropriate visualization using the data you just generated. Choose the best chart type and format it properly for display."
    }
    
    prompt = prompts.get(visualization_type, prompts["default"])
    helpers_logger.info(f"Created completion prompt for {visualization_type} visualization")
    
    return prompt

def infer_visualization_type_from_response(processed_response, gemini_response) -> str:
    """
    Infer the appropriate visualization type from the previous response.
    """
    
    # Check function calls for hints about data type
    if hasattr(gemini_response, 'function_calls') and gemini_response.function_calls:
        for func_call in gemini_response.function_calls:
            function_name = getattr(func_call, 'name', '')
            
            if function_name == 'generate_time_series_data':
                return "time_series"
            elif function_name == 'generate_business_data':
                return "categorical" 
            elif function_name == 'generate_comparison_data':
                return "comparison"
            elif function_name == 'generate_statistical_data':
                return "distribution"
            elif function_name == 'generate_demographic_data':
                return "proportional"
    
    # Analyze response text for visualization clues
    response_lower = processed_response.lower() if isinstance(processed_response, str) else ""
    
    if any(word in response_lower for word in ["trend", "time", "timeline", "over time"]):
        return "time_series"
    elif any(word in response_lower for word in ["compare", "comparison", "vs", "versus"]):
        return "comparison"
    elif any(word in response_lower for word in ["proportion", "percentage", "share", "breakdown"]):
        return "proportional"
    elif any(word in response_lower for word in ["distribution", "frequency"]):
        return "distribution"
    elif any(word in response_lower for word in ["relationship", "correlation"]):
        return "correlation"
    else:
        return "default"

# Keep all existing helper functions...

def create_mixed_content_message(text: str, charts: List[Dict]) -> Dict[str, Any]:
    """Create a dash-chat message with mixed content (text + graphs)."""
    
    with LoggedOperation(chart_logger, "create_mixed_content", 
                        text_length=len(text) if text else 0,
                        chart_count=len(charts)):
        
        content_parts = []
        
        # Add text content first
        if text and text.strip():
            content_parts.append({
                "type": "text",
                "text": text.strip()
            })
            chart_logger.debug("Added text content to mixed message")
        
        # Add chart content
        for i, chart in enumerate(charts):
            if chart and isinstance(chart, dict):
                # Ensure the chart has the proper structure for dash-chat
                chart_part = {
                    "type": "graph",
                    "props": {
                        "figure": chart,
                        "config": {
                            # "displayModeBar": True, 
                            "responsive": True,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": ['pan2d', 'lasso2d']
                        },
                        "responsive": True,
                        "style": {"height": "400px", "width": "100%"}
                    }
                }
                content_parts.append(chart_part)
                chart_logger.info(f"Added chart {i+1} to mixed message")
            else:
                chart_logger.warning(f"Invalid chart data at index {i}: {type(chart)}")
        
        # Create final message structure for dash-chat
        if len(content_parts) == 0:
            # Fallback if no content
            final_content = "I processed your request but couldn't generate content."
        elif len(content_parts) == 1:
            # Single content type
            final_content = content_parts[0]
        else:
            # Multiple content parts - use list format
            final_content = content_parts
        
        message = {
            "role": "assistant",
            "content": final_content
        }
        
        chart_logger.info(f"Created mixed content message with {len(content_parts)} parts")
        return message

def execute_function_manually(function_name: str, args: Dict[str, Any]) -> Optional[Dict]:
    """Manually execute a function call if needed (fallback for automatic function calling)."""
    
    with FunctionCallTracker(function_logger, function_name, args):
        
        try:
            # Map function names to actual functions
            function_map = {
                # Chart functions
                'create_bar_chart': chart_functions.create_bar_chart,
                'create_line_chart': chart_functions.create_line_chart,
                'create_scatter_plot': chart_functions.create_scatter_plot,
                'create_pie_chart': chart_functions.create_pie_chart,
                'create_histogram': chart_functions.create_histogram,
                'create_heatmap': chart_functions.create_heatmap,
                'create_box_plot': chart_functions.create_box_plot,
                'create_area_chart': chart_functions.create_area_chart,
                'create_violin_plot': chart_functions.create_violin_plot,
                
                # Data generation functions
                'generate_business_data': data_generators.generate_business_data,
                'generate_time_series_data': data_generators.generate_time_series_data,
                'generate_statistical_data': data_generators.generate_statistical_data,
                'generate_comparison_data': data_generators.generate_comparison_data,
                'generate_demographic_data': data_generators.generate_demographic_data,
                'generate_performance_data': data_generators.generate_performance_data,
                'generate_financial_data': data_generators.generate_financial_data
            }
            
            if function_name in function_map:
                function = function_map[function_name]
                function_logger.info(f"Executing function: {function_name}")
                function_logger.debug(f"Function arguments: {args}")
                
                # Handle special parameter transformations for updated functions
                processed_args = args.copy()
                
                # Handle box plot and violin plot - convert data_groups to data_groups_json
                if function_name in ['create_box_plot', 'create_violin_plot']:
                    if 'data_groups' in processed_args:
                        # Convert dict to JSON string
                        processed_args['data_groups_json'] = json.dumps(processed_args['data_groups'])
                        del processed_args['data_groups']
                        function_logger.debug(f"Converted data_groups to JSON string for {function_name}")
                
                # Handle statistical data - convert parameters to parameters_json
                elif function_name == 'generate_statistical_data':
                    if 'parameters' in processed_args:
                        # Convert dict to JSON string
                        processed_args['parameters_json'] = json.dumps(processed_args['parameters'])
                        del processed_args['parameters']
                        function_logger.debug(f"Converted parameters to JSON string for {function_name}")
                
                # Handle comparison data - convert data_range to min_value and max_value
                elif function_name == 'generate_comparison_data':
                    if 'data_range' in processed_args:
                        data_range = processed_args['data_range']
                        if isinstance(data_range, (list, tuple)) and len(data_range) == 2:
                            processed_args['min_value'] = data_range[0]
                            processed_args['max_value'] = data_range[1]
                            del processed_args['data_range']
                            function_logger.debug(f"Converted data_range to min_value/max_value for {function_name}")
                
                # Execute the function with processed arguments
                result = function(**processed_args)
                
                function_logger.info(f"Function {function_name} executed successfully")
                function_logger.debug(f"Result type: {type(result)}")
                
                return result
            else:
                function_logger.error(f"Unknown function: {function_name}")
                function_logger.debug(f"Available functions: {list(function_map.keys())}")
                return None
                
        except Exception as e:
            function_logger.error(f"Error executing function {function_name} manually: {str(e)}", exc_info=True)
            return None

# Keep other existing helper functions...
def extract_text_from_content(content) -> str:
    """Extract text content from various dash-chat content structures."""
    helpers_logger.debug(f"Extracting text from content type: {type(content)}")
    
    try:
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            if content.get("type") == "text":
                return content.get("text", "")
            elif "text" in content:
                return content["text"]
            else:
                content_type = content.get("type", "unknown")
                return f"[{content_type} content displayed]"
        elif isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif "text" in item:
                        text_parts.append(item["text"])
                    else:
                        content_type = item.get("type", "unknown")
                        text_parts.append(f"[{content_type} content displayed]")
                elif isinstance(item, str):
                    text_parts.append(item)
            return " ".join(text_parts)
        else:
            helpers_logger.warning(f"Unknown content type for text extraction: {type(content)}")
            return f"[Content type: {type(content).__name__}]"
    except Exception as e:
        helpers_logger.error(f"Error extracting text from content: {str(e)}", exc_info=True)
        return "[Error extracting text content]"

def format_conversation_for_gemini(messages: List[Dict]) -> List[Dict]:
    """Format conversation history for Gemini API."""
    
    with LoggedOperation(helpers_logger, "format_conversation", 
                        input_message_count=len(messages)):
        
        formatted = []
        
        for i, msg in enumerate(messages):
            try:
                if msg["role"] == "user":
                    # User messages should always be simple text
                    content = msg["content"]
                    if isinstance(content, str):
                        formatted.append({
                            "role": "user",
                            "parts": [{"text": content}]
                        })
                        helpers_logger.debug(f"Formatted user message {i+1}")
                    else:
                        helpers_logger.warning(f"User message {i+1} has non-string content: {type(content)}")
                        # Try to extract text if it's a complex structure
                        text_content = extract_text_from_content(content)
                        formatted.append({
                            "role": "user",
                            "parts": [{"text": text_content}]
                        })
                
                else:  # assistant messages
                    # Assistant messages might have mixed content (text + charts)
                    content = msg["content"]
                    
                    if isinstance(content, str):
                        # Simple text content
                        formatted.append({
                            "role": "model", 
                            "parts": [{"text": content}]
                        })
                        helpers_logger.debug(f"Formatted assistant text message {i+1}")
                        
                    elif isinstance(content, dict):
                        # Single content item (could be text, graph, etc.)
                        text_content = extract_text_from_content(content)
                        formatted.append({
                            "role": "model", 
                            "parts": [{"text": text_content}]
                        })
                        helpers_logger.debug(f"Formatted assistant mixed content message {i+1}")
                        
                    elif isinstance(content, list):
                        # List of content items - extract all text parts
                        text_content = extract_text_from_content(content)
                        formatted.append({
                            "role": "model", 
                            "parts": [{"text": text_content}]
                        })
                        helpers_logger.debug(f"Formatted assistant multi-part message {i+1}")
                        
                    else:
                        # Fallback for unknown content types
                        helpers_logger.warning(f"Assistant message {i+1} has unknown content type: {type(content)}")
                        formatted.append({
                            "role": "model", 
                            "parts": [{"text": "Previous message contained non-text content."}]
                        })
                        
            except Exception as e:
                helpers_logger.error(f"Error formatting message {i+1}: {str(e)}", exc_info=True)
                # Add a placeholder message to keep conversation flow
                formatted.append({
                    "role": msg["role"],
                    "parts": [{"text": f"[Error formatting message: {str(e)}]"}]
                })
        
        helpers_logger.info(f"Formatted {len(formatted)} messages for Gemini API")
        return formatted
