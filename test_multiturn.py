# SPDX-License-Identifier: MIT
# Copyright © 2025 github.com/dtiberio

# test_multiturn.py
"""
Test script to verify Multi-Turn Function Calling implementation is working correctly.
This script tests the 2-step visualization workflow without running the full Dash app.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

# Import the enhanced modules
from app_helpers import (
    generate_chat_response, 
    is_incomplete_visualization_workflow,
    is_data_generation_function,
    is_chart_creation_function
)
from logger_config import get_logger

# Initialize logger
test_logger = get_logger('multiturn_test')

def test_multiturn_workflow():
    """
    Test the multi-turn workflow with various visualization requests.
    """
    
    test_logger.info("🧪 Starting Multi-Turn Function Calling Tests")
    
    # Test cases for different types of visualization requests
    test_cases = [
        {
            "name": "Time Series Request",
            "message": "Show me quarterly sales trends for the last year",
            "expected_workflow": "time_series",
            "expected_functions": ["generate_time_series_data", "create_line_chart"]
        },
        {
            "name": "Category Comparison",
            "message": "Compare sales performance across different product categories",
            "expected_workflow": "categorical",
            "expected_functions": ["generate_business_data", "create_bar_chart"]
        },
        {
            "name": "Market Share Analysis",
            "message": "Show market share breakdown by region",
            "expected_workflow": "proportional", 
            "expected_functions": ["generate_demographic_data", "create_pie_chart"]
        },
        {
            "name": "Performance Distribution",
            "message": "Create a histogram showing employee performance distribution",
            "expected_workflow": "distribution",
            "expected_functions": ["generate_statistical_data", "create_histogram"]
        }
    ]
    
    model = "gemini-2.5-flash"
    
    for i, test_case in enumerate(test_cases, 1):
        test_logger.info(f"\n{'='*60}")
        test_logger.info(f"🧪 Test {i}: {test_case['name']}")
        test_logger.info(f"Request: '{test_case['message']}'")
        test_logger.info(f"Expected workflow: {test_case['expected_workflow']}")
        
        # Create test message
        messages = [{
            "role": "user",
            "content": test_case['message']
        }]
        
        try:
            # Test the multi-turn response generation
            test_logger.info("🔄 Testing multi-turn response generation...")
            response = generate_chat_response(messages, model)
            
            # Analyze the response
            if isinstance(response, dict) and "content" in response:
                # Check if it's mixed content (has visualizations)
                content = response["content"]
                
                if isinstance(content, list):
                    # Mixed content - should have text + graph
                    has_text = any(item.get("type") == "text" for item in content if isinstance(item, dict))
                    has_graph = any(item.get("type") == "graph" for item in content if isinstance(item, dict))
                    
                    if has_text and has_graph:
                        test_logger.info("✅ SUCCESS: Mixed content with text and chart detected!")
                        test_logger.info("🎉 2-step workflow completed successfully!")
                        
                        # Count charts
                        chart_count = sum(1 for item in content if isinstance(item, dict) and item.get("type") == "graph")
                        test_logger.info(f"📊 Charts generated: {chart_count}")
                        
                    else:
                        test_logger.warning("⚠️ Mixed content found but missing expected components")
                        test_logger.warning(f"Has text: {has_text}, Has graph: {has_graph}")
                        
                elif isinstance(content, dict) and content.get("type") == "graph":
                    # Single chart response
                    test_logger.info("✅ SUCCESS: Single chart response detected!")
                    test_logger.info("🎉 2-step workflow completed successfully!")
                    
                else:
                    # Text only response - likely incomplete workflow
                    test_logger.warning("⚠️ Text-only response - workflow may be incomplete")
                    test_logger.warning(f"Response type: {type(content)}")
                    
            elif isinstance(response, str):
                # String response - check for workflow indicators
                if any(indicator in response.lower() for indicator in 
                       ["visualization", "chart", "graph", "here's"]):
                    test_logger.warning("⚠️ Text response but mentions visualization - check implementation")
                else:
                    test_logger.warning("⚠️ Plain text response - multi-turn workflow may have failed")
                
                test_logger.info(f"Response preview: '{response[:200]}{'...' if len(response) > 200 else ''}'")
            
            else:
                test_logger.error(f"❌ Unexpected response type: {type(response)}")
            
        except Exception as e:
            test_logger.error(f"❌ Test failed with error: {str(e)}")
            import traceback
            test_logger.error(f"Stack trace: {traceback.format_exc()}")
    
    test_logger.info(f"\n{'='*60}")
    test_logger.info("🏁 Multi-Turn Function Calling Tests Completed")


def test_helper_functions():
    """
    Test the individual helper functions.
    """
    
    test_logger.info("\n🔧 Testing Helper Functions")
    
    # Test function type detection
    test_logger.info("Testing function type detection...")
    
    # Test data generation function detection
    assert is_data_generation_function("generate_business_data") == True
    assert is_data_generation_function("generate_time_series_data") == True
    assert is_data_generation_function("create_bar_chart") == False
    test_logger.info("✅ Data generation function detection working")
    
    # Test chart creation function detection
    assert is_chart_creation_function("create_bar_chart") == True
    assert is_chart_creation_function("create_line_chart") == True
    assert is_chart_creation_function("generate_business_data") == False
    test_logger.info("✅ Chart creation function detection working")
    
    test_logger.info("✅ All helper function tests passed")


def main():
    """
    Main test function.
    """
    
    # Check environment setup
    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        test_logger.error("❌ GOOGLE_API_KEY not found in environment variables")
        test_logger.error("Please set your Google API key in the .env file")
        return

    test_logger.info("✅ Google API key found")

    # Test helper functions first
    test_helper_functions()
    
    # Test the full multi-turn workflow
    test_multiturn_workflow()
    
    print("\n" + "="*60)
    print("🎯 TESTING COMPLETE")
    print("="*60)
    print("Check the logs above for test results.")
    print("✅ SUCCESS indicators mean the multi-turn workflow is working")
    print("⚠️ WARNING indicators suggest issues that need investigation")
    print("❌ ERROR indicators mean critical failures")
    print("\nTo run the full app: python app.py")
    print("="*60)


if __name__ == "__main__":
    main()