<!--
SPDX-License-Identifier: CC-BY-SA-4.0
Copyright © 2025 github.com/dtiberio
-->

## **Gemini and Sequential Function Calling 🔍**

### **Gemini's Design Philosophy**

From the official documentation and multiple sources:

> **"Parallel function calling lets you execute multiple functions at once and is used when the functions are not dependent on each other."**

**Gemini is architecturally designed for PARALLEL function calls, NOT sequential dependent workflows like our data → chart pipeline.**

---

## **💡 Proven Solutions Found:**

### **Option 1: ReACT Pattern** (🏆 Most Recommended)

Multiple sources point to **ReACT (Reasoning and Acting)** as the solution:

```python
# ReACT Loop Pattern
def react_loop():
    while not_complete:
        # Step 1: THINK - Plan what to do
        thought = gemini.generate("What should I do next?")

        # Step 2: ACT - Execute function
        action_result = execute_function(thought.function_call)

        # Step 3: OBSERVE - Process results
        observation = process_results(action_result)

        # Step 4: Continue or complete
        if is_complete(observation):
            break
```

**Key insight**: Each step is a **separate API call** with **conversation history**.

### **Option 2: Planner-Executor Pattern** (🥈 Multi-Agent)

From the research on multi-agent systems:

```python
# Two separate agents
planner_agent = create_planner_agent()  # Decides what functions to call
executor_agent = create_executor_agent()  # Executes the functions

# Sequential workflow
plan = planner_agent.generate_plan(user_request)
results = executor_agent.execute_plan(plan)
```

### **Option 3: Multi-Turn Conversation** (🥉 Simpler)

From the function calling documentation:

> **"Multi-turn tool use: append the model's complete previous response to the conversation history"**

```python
# Multi-turn approach
messages = [{"role": "user", "content": "Show sales trends"}]

# Turn 1: Data generation
response1 = gemini.generate_content(messages=messages, tools=ALL_TOOLS)
messages.append(response1.to_message())

# Turn 2: Chart creation (if step 1 incomplete)
if only_has_data(response1):
    prompt2 = "Now create a line chart with this data"
    messages.append({"role": "user", "content": prompt2})
    response2 = gemini.generate_content(messages=messages, tools=ALL_TOOLS)
```

---

### **Immediate Solution: Option 3 - Multi-Turn**

```python
def generate_chat_response(messages, model_name):
    # First API call
    response1 = genai_client.models.generate_content(...)
    processed1 = process_gemini_response(response1)

    # Check if incomplete (data but no chart)
    if has_data_but_no_visualization(processed1):
        # Add conversation context
        conversation_with_data = messages + [
            {"role": "assistant", "content": "I've generated the data."},
            {"role": "user", "content": "Now create the appropriate visualization using this data."}
        ]

        # Second API call with full context
        response2 = genai_client.models.generate_content(
            contents=conversation_with_data,
            config=config
        )
        return process_gemini_response(response2)

    return processed1
```

### **Advanced Solution: Option 1 - ReACT Pattern with LangGraph**

For a more robust long-term solution:

```python
# Using LangGraph for ReACT pattern
from langgraph import StateGraph

def create_visualization_agent():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("planner", plan_visualization)      # Decide what data + chart needed
    workflow.add_node("data_generator", generate_data)    # Generate data
    workflow.add_node("visualizer", create_chart)        # Create chart
    workflow.add_node("validator", validate_complete)    # Check if complete

    # Edges (flow control)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "data_generator")
    workflow.add_conditional_edges(
        "data_generator",
        should_visualize,
        {"visualize": "visualizer", "complete": END}
    )
    workflow.add_edge("visualizer", "validator")
    workflow.add_conditional_edges(
        "validator",
        is_complete,
        {"continue": "planner", "end": END}
    )

    return workflow.compile()
```
