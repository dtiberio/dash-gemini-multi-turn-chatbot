# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# app_helpers.py
"""Enhanced helper functions for the Dash chatbot application.
This module provides intelligent response generation with automatic function calling
for creating data visualizations using Google's Gemini API with comprehensive logging.
Now properly handles 2-step workflow (data generation → visualization).
Now implements multi-turn conversation to solve the 2-step workflow problem.
Now includes deep debugging to inspect Gemini response structures.
"""

from typing import Union, List, Dict, Any, Optional
from app_llm import genai_client
from google import genai

from app_helpers_utils import (
    get_appropriate_config,
    build_completion_conversation,
    format_conversation_for_gemini,
    execute_function_manually,
    create_mixed_content_message
)

import logging
# Enhanced logging imports
from logger_config import (
    get_logger,               # generic module-scoped logger
    get_function_call_logger, # specialised function-call logger
    get_api_logger,           # low-level API traffic logger
    get_chart_logger,
    LoggedOperation,
    FunctionCallTracker
)

# Initialize specialized loggers
helpers_logger = get_logger('gemini_chatbot.helpers')
function_logger = get_function_call_logger()
api_logger = get_api_logger()  # ← used inside build_completion_conversation
chart_logger = get_chart_logger()
logger = helpers_logger  # For backward compatibility, used by generate_chat_response

# ----------------------------------------------------------------------
# Phase-A utilities for large-data handling
# ----------------------------------------------------------------------

MAX_INLINE_TOKENS = 8_000           # ≈24 KB of JSON; tune as needed
DATA_CACHE: dict[str, dict] = {}    # maps data_id → full result


def estimate_token_count(payload: str) -> int:
    """
    Very fast, coarse token estimator:
    • Gemini tokens ~≈ 3-4 characters each for ASCII JSON.
    • We divide the character count by 3 to stay on the safe side.

    Args:
        payload: JSON-encoded string.

    Returns:
        Rough token count (int).
    """
    return len(payload) // 3


def attach_function_message(
    conv: list,
    fn_name: str,
    result: dict,
) -> None:
    """
    Inject a 'function'-role message into the conversation that represents
    the output of a data-generation tool call.

    * If the JSON is small enough (≤ MAX_INLINE_TOKENS) we inline it.
    * Otherwise we store it in DATA_CACHE and send a lightweight
      { "data_id": "<uuid>" } stub instead.

    Args:
        conv:       The conversation list to mutate.
        fn_name:    Name of the function that produced `result`.
        result:     Dict returned by manual execution.
    """
    import json
    import uuid

    payload = json.dumps(result, separators=(",", ":"))

    if estimate_token_count(payload) < MAX_INLINE_TOKENS:
        conv.append({
            "role": "function",
            "name": fn_name,
            "content": payload,
        })
    else:
        data_id = uuid.uuid4().hex
        DATA_CACHE[data_id] = result
        conv.append({
            "role": "function",
            "name": fn_name,
            "content": json.dumps({"data_id": data_id}),
        })


def generate_chat_response(conversation: list, model: str = "gemini-2.5-flash") -> str:
    """
    High-level orchestrator:
      1) send initial request
      2) process response + manual tool execution
      3) if workflow incomplete → build completion turn and call Gemini again
      4) return final text (or chart response) to caller
    """
    # ---- First turn --------------------------------------------------------
    response_1 = make_gemini_api_call(conversation, model)
    parsed_1   = process_gemini_response(response_1, workflow_logger=logger)

    # ---- Happy path: got chart in first turn ------------------------------
    if parsed_1["workflow_type"] == "complete":
        return parsed_1["text"]

    # ---- Second turn (completion) -----------------------------------------
    completion_conv = build_completion_conversation(
        conversation,
        workflow_type     = parsed_1["workflow_type"],
        function_messages = parsed_1["function_messages"],
        assistant_reply   = parsed_1["text"]
    )
    response_2 = make_gemini_api_call(completion_conv, model)
    parsed_2   = process_gemini_response(response_2, workflow_logger=logger)

    # ---- Fallback if still incomplete -------------------------------------
    if parsed_2["workflow_type"] == "complete":
        return parsed_2["text"]

    # Final fallback – text only
    return parsed_2["text"] or "I've processed your request, but encountered an issue generating the response."


def make_gemini_api_call(
    messages: List[Dict],
    model_name: str,
    is_completion_call: bool = False
) -> Any:
    """
    Centralized Gemini API call with context awareness.
    ENHANCED: Now includes deep debugging for completion calls.
    """
    
    with LoggedOperation(api_logger, "gemini_api_call",
                        model_name=model_name,
                        message_count=len(messages),
                        call_type="completion" if is_completion_call else "initial"):
        
        try:
            # Log request details
            latest_message = messages[-1]["content"] if messages else ""
            helpers_logger.info(f"Processing request: {latest_message[:200]}...")
            
            # Format the conversation history for Gemini
            helpers_logger.debug("Formatting conversation for Gemini API")
            formatted_messages = format_conversation_for_gemini(messages)
            
            # Choose appropriate configuration
            config = get_appropriate_config(messages, is_completion_call)
            
            # ENHANCED DEBUGGING: Log what we're sending to Gemini in completion calls
            if is_completion_call:
                api_logger.debug(f"🔍 COMPLETION CALL - Request details:")
                api_logger.debug(f"🔍 Model: {model_name}")
                api_logger.debug(f"🔍 Messages count: {len(formatted_messages) if len(messages) > 1 else 1}")
                
                if len(messages) > 1:
                    # Multi-turn - log the conversation we're sending
                    for i, msg in enumerate(formatted_messages):
                        msg_role = msg.get('role', 'unknown')
                        msg_content = str(msg.get('parts', [{}])[0].get('text', ''))[:200]
                        api_logger.debug(f"🔍 Message {i+1} ({msg_role}): {msg_content}...")
                else:
                    # Single message
                    api_logger.debug(f"🔍 Single message content: {messages[0]['content'][:200]}...")
                
                # Log the config being used
                api_logger.debug(f"🔍 Config tools count: {len(config.tools) if hasattr(config, 'tools') and config.tools else 0}")
                api_logger.debug(f"🔍 Config max calls: {config.automatic_function_calling.maximum_remote_calls if hasattr(config, 'automatic_function_calling') else 'Unknown'}")
                api_logger.debug(f"🔍 Config system instruction length: {len(config.system_instruction) if hasattr(config, 'system_instruction') and config.system_instruction else 0}")
            
            api_logger.info(f"Making {'completion' if is_completion_call else 'initial'} API call")
            
            if len(messages) == 1:
                # Single message - use simple content format
                api_logger.debug("Using single message format")
                response = genai_client.models.generate_content(
                    model=model_name,
                    contents=messages[0]["content"],
                    config=config
                )
            else:
                # Multi-turn conversation - use formatted conversation history
                api_logger.debug(f"Using multi-turn format with {len(formatted_messages)} messages")
                response = genai_client.models.generate_content(
                    model=model_name,
                    contents=formatted_messages,
                    config=config
                )
            
            api_logger.info("API call completed successfully")
            
            # ENHANCED DEBUGGING: Inspect response structure for completion calls
            if is_completion_call:
                api_logger.debug(f"🔍 COMPLETION CALL - Response inspection:")
                api_logger.debug(f"🔍 Response type: {type(response)}")
                api_logger.debug(f"🔍 Has text: {hasattr(response, 'text')}")
                api_logger.debug(f"🔍 Has function_calls: {hasattr(response, 'function_calls')}")
                
                if hasattr(response, 'function_calls'):
                    fc = response.function_calls
                    api_logger.debug(f"🔍 function_calls object: {fc}")
                    api_logger.debug(f"🔍 function_calls bool value: {bool(fc)}")
                    
                # Check SDK HTTP response for raw data
                if hasattr(response, 'sdk_http_response'):
                    sdk_resp = response.sdk_http_response
                    api_logger.debug(f"🔍 SDK HTTP status: {sdk_resp.status_code if hasattr(sdk_resp, 'status_code') else 'Unknown'}")
                    api_logger.debug(f"🔍 SDK HTTP headers: {dict(sdk_resp.headers) if hasattr(sdk_resp, 'headers') else 'Unknown'}")
                
                # Check usage metadata
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    api_logger.debug(f"🔍 Usage metadata: {usage}")
            
            return response
            
        except Exception as e:
            api_logger.error(f"API call failed: {str(e)}", exc_info=True)
            raise

def is_incomplete_visualization_workflow(processed_response, gemini_response) -> bool:
    """
    Detect if response has data but no visualization.
    """
    
    with LoggedOperation(function_logger, "detect_incomplete_workflow"):
        
        # Check if response is text-only and indicates incomplete workflow
        if isinstance(processed_response, str):
            incomplete_indicators = [
                "I generated the data",
                "data you requested", 
                "⚠️ INCOMPLETE WORKFLOW",
                "Let me know what type of chart",
                "I need to create a visualization"
            ]
            
            has_incomplete_text = any(indicator in processed_response for indicator in incomplete_indicators)
            
            if has_incomplete_text:
                function_logger.info("🚨 Incomplete workflow detected from response text")
                return True
        
        # Check if we have data generation function calls but no chart function calls
        if hasattr(gemini_response, 'function_calls') and gemini_response.function_calls:
            data_functions = 0
            chart_functions = 0
            
            for func_call in gemini_response.function_calls:
                function_name = getattr(func_call, 'name', '')
                
                if is_data_generation_function(function_name):
                    data_functions += 1
                elif is_chart_creation_function(function_name):
                    chart_functions += 1
            
            if data_functions > 0 and chart_functions == 0:
                function_logger.info(f"🚨 Incomplete workflow: {data_functions} data functions, {chart_functions} chart functions")
                return True
        
        function_logger.debug("Workflow appears complete")
        return False

def process_gemini_response(
    response: "genai.GenerateContentResponse",
    workflow_logger: "logging.Logger | None" = None,
) -> dict:
    """
    Parse Gemini response, run any tool calls server-side and return:
        • 'text'   : str | dict  – either plain text **or** the mixed-content message
        • 'data_results'         – list of data-gen payloads
        • 'chart_results'        – list of Plotly figure dicts
        • 'workflow_type'        – 'complete' | 'incomplete' | 'text_only'
        • 'function_messages'    – conversation snippets to expose tool output
    """
    from google.genai.types import FunctionCall  # local import
    import json

    _log = (lambda m: workflow_logger.debug(m)) if workflow_logger else (lambda *_: None)

    text_content        = response.text or ""
    data_results        : list = []
    chart_results       : list = []
    function_messages   : list = []

    # ------------------------------------------------------------
    # 1.  Execute any function calls that Gemini returned
    # ------------------------------------------------------------
    for call in (response.function_calls or []):
        if not isinstance(call, FunctionCall):
            continue

        fn_name  = call.name
        fn_args  = call.args or {}
        _log(f"⇢ executing {fn_name}({fn_args})")

        result = execute_function_manually(fn_name, fn_args)

        if is_data_generation_function(fn_name):
            data_results.append(result)
            attach_function_message(function_messages, fn_name, result)
        elif is_chart_creation_function(fn_name):
            chart_results.append(result)

    # ------------------------------------------------------------
    # 2.  Decide what kind of turn we just processed
    #     (Fix A – chart ⇒ complete even without data repetition)
    # ------------------------------------------------------------
    if chart_results:               # at least one visualisation created
        workflow_type = "complete"
    elif data_results:              # only data so far
        workflow_type = "incomplete"
    else:                           # text only
        workflow_type = "text_only"

    # ------------------------------------------------------------
    # 3.  Build the payload that the caller should send back
    # ------------------------------------------------------------
    if chart_results:                                             # Fix B
        if not text_content.strip():
            text_content = "Here’s the visualisation you requested:"
        mixed_msg = create_mixed_content_message(text_content, chart_results)
        text_field = mixed_msg                                    # Fix C
    else:
        text_field = text_content.strip()

    return {
        "text"             : text_field,
        "data_results"     : data_results,
        "chart_results"    : chart_results,
        "workflow_type"    : workflow_type,
        "function_messages": function_messages,
    }

# Helper functions...
def is_data_generation_function(function_name: str) -> bool:
    """Check if a function is a data generation function."""
    data_functions = [
        'generate_business_data', 'generate_time_series_data', 'generate_statistical_data',
        'generate_comparison_data', 'generate_demographic_data', 'generate_performance_data',
        'generate_financial_data'
    ]
    return function_name in data_functions

def is_chart_creation_function(function_name: str) -> bool:
    """Check if a function is a chart creation function."""
    chart_functions_list = [
        'create_bar_chart', 'create_line_chart', 'create_scatter_plot', 'create_pie_chart',
        'create_histogram', 'create_heatmap', 'create_box_plot', 'create_area_chart',
        'create_violin_plot'
    ]
    return function_name in chart_functions_list
