# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# app.py
"""Main application file for the Dash chatbot using Google Gemini API, with integrated Gemini function calling.
This file initializes the Dash app, sets up the layout, and defines callbacks for handling chat interactions.
Includes comprehensive logging to track all application behavior and debug critical issues.
Supports multi-turn function calling for complete 2-step visualization workflow.
"""

import dash
from dash import html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_chat import ChatComponent
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import traceback
from typing import Union, Dict, Any

# Load environment variables FIRST (before any other imports that might use them)
load_dotenv()

# Enhanced logging imports - must come after load_dotenv()
from logger_config import (
    get_logger,
    get_function_call_logger,
    get_api_logger,
    LoggedOperation
)

# Import application modules
from app_helpers import generate_chat_response
from app_llm import MODELS

# Initialize specialized loggers
app_logger = get_logger('gemini_chatbot.app')
function_logger = get_function_call_logger()
api_logger = get_api_logger()

# Log application startup
app_logger.info("🚀 Starting Gemini Agent application with Multi-Turn Function Calling")
app_logger.info(f"Available models: {[model['value'] for model in MODELS]}")
app_logger.info("✨ Enhanced with 2-step visualization workflow support")

# Initialize Dash app with enhanced logging
try:
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap"
        ],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    
    app_logger.info("✅ Dash app initialized successfully")
    app_logger.debug("External stylesheets and meta tags configured")
    
except Exception as e:
    app_logger.critical(f"❌ Failed to initialize Dash app: {str(e)}", exc_info=True)
    raise

app.title = "Gemini Agent - Multi-Turn"
server = app.server

app_logger.info("📱 App title and server configured")

# Generate a unique session ID for this app instance
SESSION_ID = str(uuid.uuid4())[:8]
app_logger.info(f"🔑 Session ID generated: {SESSION_ID}")

# Enhanced layout with logging
app_logger.debug("🎨 Building application layout")

try:
    app.layout = dmc.MantineProvider(
        theme={
            "colorScheme": "light",
            "fontFamily": "'Inter', sans-serif",
            "primaryColor": "indigo",
        },
        children=[
            dmc.Container(
                fluid=True,
                px=0,
                style={"height": "100vh", "display": "flex", "flexDirection": "column"},
                children=[
                    # Header with enhanced logging context
                    dmc.Paper(
                        h=70,
                        p="md",
                        style={"borderBottom": "1px solid #e9ecef"},
                        children=[
                            dmc.Group(
                                align="apart",
                                children=[
                                    dmc.Title("Gemini Agent - Multi-Turn", order=3, c="indigo"),
                                    dmc.Select(
                                        id="model-select",
                                        data=MODELS,
                                        value="gemini-2.5-flash",
                                        placeholder="Select a model",
                                        style={"width": 300},
                                        searchable=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Chat Component (Main Content) - Enhanced for debugging
                    dmc.Box(
                        style={
                            "flexGrow": 1,
                            "display": "flex",
                            "flexDirection": "column",
                            "overflow": "auto",
                        },
                        children=[
                            ChatComponent(
                                id="chat-component",
                                messages=[],
                                persistence=True,
                                persistence_type="local",
                                input_placeholder="Ask Gemini for visualizations (e.g., 'Show quarterly sales trends')...",
                                theme="light",
                                fill_height=True,
                                user_bubble_style={
                                    "backgroundColor": "#6741d9",
                                    "color": "white",
                                    "marginLeft": "auto",
                                    "textAlign": "right",
                                    "borderRadius": "1rem 0 1rem 1rem",
                                    "padding": "0.75rem 1rem",
                                    "maxWidth": "80%",
                                },
                                assistant_bubble_style={
                                    "backgroundColor": "#f1f3f5",
                                    "color": "#1a1b1e",
                                    "marginRight": "auto",
                                    "textAlign": "left",
                                    "borderRadius": "0 1rem 1rem 1rem",
                                    "padding": "0.75rem 1rem",
                                    "maxWidth": "80%",
                                },
                                container_style={
                                    "padding": "1rem",
                                    "backgroundColor": "#ffffff",
                                },
                            ),
                        ],
                    ),
                    # Footer with multi-turn indicator
                    dmc.Paper(
                        h=40,
                        p="xs",
                        style={"borderTop": "1px solid #e9ecef", "textAlign": "center"},
                        children=[
                            dmc.Text("Gemini Agent - Multi-Turn Function Calling for Complete Visualizations", 
                                   size="sm", c="dimmed"),
                        ],
                    ),
                ],
            ),
        ],
    )
    
    app_logger.info("✅ Application layout created successfully")
    app_logger.debug("UI components: Header, ChatComponent, Footer configured")
    
except Exception as e:
    app_logger.critical(f"❌ Failed to create application layout: {str(e)}", exc_info=True)
    raise


# Enhanced callback for model selection tracking
@callback(
    Output("model-select", "value", allow_duplicate=True),
    Input("model-select", "value"),
    prevent_initial_call=True,
)
def track_model_selection(selected_model):
    """
    Track model selection changes for analytics and debugging.
    """
    
    with LoggedOperation(app_logger, "model_selection_change", 
                        session_id=SESSION_ID,
                        selected_model=selected_model,
                        supports_multiturn=True):
        
        app_logger.info(f"🔄 User changed model to: {selected_model}")
        api_logger.info(f"Model selection updated: {selected_model}")
        
        # Validate model selection
        valid_models = [model['value'] for model in MODELS]
        if selected_model not in valid_models:
            app_logger.warning(f"⚠️ Invalid model selected: {selected_model}, valid options: {valid_models}")
        else:
            app_logger.debug(f"✅ Model selection validated: {selected_model}")
        
        return selected_model


# ENHANCED main chat handling callback with multi-turn function calling support
@callback(
    Output("chat-component", "messages"),
    Input("chat-component", "new_message"),
    [State("chat-component", "messages"), State("model-select", "value")],
    prevent_initial_call=True,
)
def handle_chat_with_multiturn(new_message, messages, model):
    """
    Handle chat messages with integrated Gemini multi-turn function calling and comprehensive logging.
    ENHANCED: Now supports 2-step workflow (data generation → visualization) through multi-turn API calls.
    
    This enhanced callback provides complete visibility into:
    - User message processing
    - Multi-turn function calling operations  
    - 2-step workflow completion
    - Response generation timing
    - Error handling and recovery
    - Performance metrics
    """
    
    # Create unique operation ID for this chat interaction
    operation_id = str(uuid.uuid4())[:8]
    
    with LoggedOperation(app_logger, "handle_chat_multiturn", 
                        session_id=SESSION_ID,
                        operation_id=operation_id, 
                        model_name=model,
                        current_message_count=len(messages) if messages else 0,
                        multiturn_enabled=True):
        
        # Log the incoming request details
        app_logger.info(f"💬 Processing multi-turn chat interaction {operation_id}")
        
        # Validate inputs with detailed logging
        if not new_message:
            app_logger.debug("❌ No new message received, returning existing messages")
            return messages or []
        
        if not model:
            app_logger.error("❌ No model selected, using default")
            model = "gemini-2.5-flash"
        
        # Log message details (truncated for security)
        message_content = new_message.get("content", "")
        message_role = new_message.get("role", "unknown")
        
        app_logger.info(f"📝 New {message_role} message: '{message_content[:100]}{'...' if len(message_content) > 100 else ''}'")
        app_logger.debug(f"Message length: {len(message_content)} characters")
        
        # Ensure messages list exists
        if messages is None:
            messages = []
            app_logger.debug("🔧 Initialized empty messages list")
        
        # Add user message to conversation with logging
        try:
            updated_messages = messages + [new_message]
            app_logger.info(f"✅ Added user message to conversation (total: {len(updated_messages)} messages)")
            
        except Exception as e:
            app_logger.error(f"❌ Failed to add user message to conversation: {str(e)}", exc_info=True)
            return messages  # Return original messages on error
        
        # Process user messages with enhanced multi-turn error handling and logging
        if new_message["role"] == "user":
            
            # Pre-processing analysis with specialized loggers
            with LoggedOperation(app_logger, "analyze_user_request", 
                               operation_id=operation_id,
                               message_length=len(message_content)):
                
                # Analyze request type for better logging context
                is_chart_request = any(keyword in message_content.lower() 
                                     for keyword in ["chart", "graph", "plot", "visualize", "show"])
                is_complex_request = any(keyword in message_content.lower() 
                                       for keyword in ["compare", "analysis", "dashboard", "multiple"])
                
                app_logger.info(f"📊 Request analysis - Chart: {is_chart_request}, Complex: {is_complex_request}")
                
                if is_chart_request:
                    function_logger.info(f"🎨 Chart/visualization request detected - Multi-turn workflow enabled")
                    app_logger.info(f"🔄 Preparing for potential 2-step visualization workflow")
                
                if is_complex_request:
                    function_logger.info(f"🔍 Complex analysis request detected in operation {operation_id}")
            
            # Generate response with comprehensive multi-turn error handling
            try:
                with LoggedOperation(app_logger, "generate_multiturn_response", 
                                   operation_id=operation_id,
                                   model_name=model,
                                   input_message_count=len(updated_messages)):
                    
                    app_logger.info(f"🤖 Generating response using {model} with multi-turn support")
                    api_logger.info(f"Multi-turn API request initiated for operation {operation_id}")
                    
                    # Call the ENHANCED multi-turn response generation function
                    response = generate_chat_response(updated_messages, model)
                    
                    # Enhanced response handling for multi-turn results
                    if isinstance(response, dict):
                        # Mixed content response (text + charts) - SUCCESS!
                        app_logger.info(f"✅ Multi-turn workflow SUCCESS - Complete visualization created!")
                        api_logger.info(f"Multi-turn visualization response received for operation {operation_id}")
                        function_logger.info(f"🎉 2-step workflow completed: Data generation → Chart creation")
                        
                        # Response is already a complete message dictionary
                        final_messages = updated_messages + [response]
                        
                    elif isinstance(response, str):
                        # Text-only response - could be single-step or error
                        response_length = len(response)
                        app_logger.info(f"✅ Text response generated - Length: {response_length} chars")
                        api_logger.info(f"Text API response received for operation {operation_id}")
                        
                        # Check if this indicates a workflow issue
                        if any(indicator in response.lower() for indicator in 
                               ["incomplete", "data generated", "need to create"]):
                            app_logger.warning(f"⚠️ Multi-turn workflow may have failed for operation {operation_id}")
                            function_logger.warning(f"Possible multi-turn workflow failure detected")
                        
                        # Create standard text message
                        bot_response = {
                            "role": "assistant", 
                            "content": response,
                            "_metadata": {
                                "operation_id": operation_id,
                                "model_used": model,
                                "timestamp": datetime.now().isoformat(),
                                "response_length": response_length,
                                "response_type": "text",
                                "multiturn_workflow": "completed_or_single_step"
                            }
                        }
                    
                        # Final message list assembly
                        final_messages = updated_messages + [bot_response]
                        
                    else:
                        # Unexpected response type
                        app_logger.error(f"Unexpected response type from multi-turn workflow: {type(response)}")
                        function_logger.error(f"Multi-turn workflow returned unexpected type: {type(response)}")
                        error_response = {
                            "role": "assistant",
                            "content": "I encountered an unexpected error in the multi-turn processing workflow."
                        }
                        final_messages = updated_messages + [error_response]                        
                    
                    app_logger.info(f"🎉 Multi-turn chat interaction {operation_id} completed successfully")
                    app_logger.info(f"📊 Final conversation length: {len(final_messages)} messages")
                    
                    # Success metrics logging for multi-turn
                    app_logger.debug(f"✅ Multi-turn operation {operation_id} metrics logged")
                    
                    return final_messages
            
            except Exception as e:
                # Comprehensive error handling with detailed multi-turn logging
                error_id = str(uuid.uuid4())[:8]
                
                app_logger.error(f"❌ Error in multi-turn response generation (Error ID: {error_id}): {str(e)}")
                app_logger.error(f"🔍 Multi-turn error occurred in operation {operation_id}")
                api_logger.error(f"Multi-turn API workflow failed for operation {operation_id}: {str(e)}")
                function_logger.error(f"Multi-turn function calling workflow failed in operation {operation_id}")
                
                # Log full stack trace for debugging
                app_logger.debug(f"📋 Full multi-turn stack trace for error {error_id}:")
                app_logger.debug(traceback.format_exc())
                
                # Create error response for user with multi-turn context
                error_message = (
                    f"I apologize, but I encountered an error while processing your visualization request "
                    f"using the multi-turn workflow. Please try again or rephrase your question.\n\n"
                    f"Error ID: {error_id} (for support reference)"
                )
                
                app_logger.info(f"🔧 Created user-friendly multi-turn error message for operation {operation_id}")
                
                # Log error recovery attempt
                try:
                    error_response = {"role": "assistant", "content": error_message}
                    recovery_messages = updated_messages + [error_response]
                    
                    app_logger.info(f"🚑 Multi-turn error recovery successful - returning {len(recovery_messages)} messages")
                    return recovery_messages
                    
                except Exception as recovery_error:
                    app_logger.critical(f"💀 Multi-turn error recovery failed: {str(recovery_error)}", exc_info=True)
                    # Last resort: return original messages
                    return messages
        
        else:
            # Handle non-user messages (shouldn't normally happen)
            app_logger.warning(f"⚠️ Received non-user message with role: {message_role}")
            app_logger.debug("Returning messages unchanged for non-user message")
            return updated_messages


# Enhanced application startup logging with multi-turn support
if __name__ == "__main__":
    
    with LoggedOperation(app_logger, "application_startup_multiturn", session_id=SESSION_ID):
        
        app_logger.info("🎯 Starting Dash application server with Multi-Turn Function Calling")
        app_logger.info(f"🌐 Server will be available at: http://localhost:3350")
        app_logger.info(f"🔧 Debug mode: True")
        app_logger.info(f"🔑 Session ID: {SESSION_ID}")
        app_logger.info(f"✨ Multi-Turn Feature: ENABLED")
        app_logger.info(f"🎨 2-Step Visualization Workflow: ACTIVE")
        
        # Log system information for debugging
        try:
            import platform
            import sys
            
            app_logger.debug(f"🖥️ System: {platform.system()} {platform.release()}")
            app_logger.debug(f"🐍 Python: {sys.version}")
            app_logger.debug(f"📁 Working directory: {os.getcwd()}")
            
        except Exception as e:
            app_logger.debug(f"Could not log system information: {e}")
        
        try:
            # Start the application with enhanced error handling
            app_logger.info("🚀 Launching Dash server with multi-turn capabilities...")
            app.run(debug=True, port=3350)
            
        except KeyboardInterrupt:
            app_logger.info("⏹️ Multi-turn application stopped by user (Ctrl+C)")
            
        except Exception as e:
            app_logger.critical(f"💀 Multi-turn application startup failed: {str(e)}", exc_info=True)
            raise
            
        finally:
            app_logger.info("👋 Multi-turn application shutdown complete")
            app_logger.info(f"📊 Multi-turn session {SESSION_ID} ended at {datetime.now().isoformat()}")