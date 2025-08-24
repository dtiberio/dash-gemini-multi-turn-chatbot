<!--
SPDX-License-Identifier: CC-BY-SA-4.0
Copyright © 2025 github.com/dtiberio
-->

This tutorial shows the latest features and examples of the **google-genai** Python SDK for Google’s Gemini v2.5 models.  
It covers installation, client creation, model usage (single-turn and multi-turn), function calling, streaming, async usage, JSON / Enum responses, advanced prompting techniques, and error handling.

---

# Google Gemini Python SDK Tutorial (Unified)

## 1. Installation

```bash
pip install google-genai
```
Or, to pin a specific version:
```bash
pip install -U -q "google-genai>=1.7.0"
```

---

## 2. Imports

```python
from google import genai
from google.genai import types
from google.genai import errors
```

### 2.1 Automated Retry Example

You can wrap certain SDK methods with retries for status codes 429, 503, etc.:

```python
from google.api_core import retry

is_retriable = lambda e: (isinstance(e, errors.APIError) and e.code in {429, 503})

if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
    genai.models.Models.generate_content = retry.Retry(
        predicate=is_retriable
    )(genai.models.Models.generate_content)
```

---

## 3. Creating a Client

You need an API key with access to the Gemini API.  
Set it in the environment variable `GOOGLE_API_KEY` or pass it explicitly to the client.

### 3.1 Environment Variable

```bash
export GOOGLE_API_KEY='your-api-key'
```

Then:

```python
client = genai.Client()  # automatically picks up GOOGLE_API_KEY from the environment
```

### 3.2 Passing API Key Directly

```python
client = genai.Client(api_key='your-api-key')
```

### 3.3 Selecting the API Version

By default, the SDK may use a beta or preview endpoint. You can set a different version:

```python
client = genai.Client(
    api_key='your-api-key',
    http_options=types.HttpOptions(api_version='v1')       # stable
    # or: http_options=types.HttpOptions(api_version='v1alpha')  # developer/preview
)
```

### 3.4 Output length
When generating text with an LLM, the output length affects cost and performance. Generating more tokens increases computation, leading to higher energy consumption, latency, and cost.

To stop the model from generating tokens past a limit, you can specify the max_output_tokens parameter when using the Gemini API. Specifying this parameter does not influence the generation of the output tokens, so the output will not become more stylistically or textually succinct, but it will stop generating tokens once the specified length is reached. Prompt engineering may be required to generate a more complete output for your given limit.

```python
from google.genai import types

short_config = types.GenerateContentConfig(max_output_tokens=200)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    config=short_config,
    contents='Write a 1000 word essay on the importance of olives in modern society.')

print(response.text)
```

### 3.5 Temperature
Temperature controls the degree of randomness in token selection. Higher temperatures result in a higher number of candidate tokens from which the next output token is selected, and can produce more diverse results, while lower temperatures have the opposite effect, such that a temperature of 0 results in greedy decoding, selecting the most probable token at each step.

Temperature doesn't provide any guarantees of randomness, but it can be used to "nudge" the output somewhat.

```python
high_temp_config = types.GenerateContentConfig(temperature=2.0)


for _ in range(5):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      config=high_temp_config,
      contents='Pick a random colour... (respond in a single word)')

  if response.text:
    print(response.text, '-' * 25)
```

Now try the same prompt with temperature set to zero. Note that the output is not completely deterministic, as other parameters affect token selection, but the results will tend to be more stable.


### 3.6 Top-P
Like temperature, the top-P parameter is also used to control the diversity of the model's output.

Top-P defines the probability threshold that, once cumulatively exceeded, tokens stop being selected as candidates.  
A top-P of 0 is typically equivalent to greedy decoding, and a top-P of 1 typically selects every token in the model's vocabulary.

You may also see top-K referenced in LLM literature.  
**Top-K is not configurable in the Gemini 2.0 series of models**, but can be changed in older models. Top-K is a positive integer that defines the number of most probable tokens from which to select the output token. A top-K of 1 selects a single token, performing greedy decoding.

```python
model_config = types.GenerateContentConfig(
    # These are the default values for gemini-2.5-flash.
    temperature=1.0,
    top_p=0.95,
)

story_prompt = "You are a creative writer. Write a short story about a cat who goes on an adventure."
response = client.models.generate_content(
    model='gemini-2.5-flash',
    config=model_config,
    contents=story_prompt)

print(response.text)
```

### 3.7 System Instructions and Other Configs

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        temperature=0.3,
    ),
)
print(response.text)
```

---

## 4. Listing Available Models

You can list the models accessible to your API key:

```python
for model in client.models.list():
    print(model.name)
```

You can also retrieve detailed information for a specific model:

```python
from pprint import pprint

for model in client.models.list():
    if model.name == 'models/gemini-2.5-pro-exp-03-25':
        pprint(model.to_json_dict())
        break
```

---

## 5. Single-Turn Requests (Text Generation)

### 5.1 Basic Text Generation

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?'
)

print(response.text)
```

**Note:** The response is typically returned in markdown format or plain text, depending on the model’s behavior.

### 5.2 Controlling Output with Config

Use `GenerateContentConfig` to set parameters like `temperature`, `top_p`, `max_output_tokens`, etc.

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Write a 1000 word essay on the importance of olives.',
    config=types.GenerateContentConfig(
        max_output_tokens=200,  # forcibly limit output
        temperature=0.7,        # adjusts randomness
        top_p=0.95,             # sets nucleus sampling probability threshold
    ),
)
print(response.text)
```

---

## 6. Multi-Part and Mixed Media Content

### 6.1 Single String

```python
contents='Can you recommend some things to do in Boston and New York in the winter?'
```

### 6.2 Single `Content` with Multiple `Part`s

```python
contents=types.Content(parts=[
    types.Part.from_text(text='Can you recommend some things to do in Boston in the winter?'),
    types.Part.from_text(text='Can you recommend some things to do in New York in the winter?')
], role='user')
```

### 6.3 Mixed Inputs (e.g., Image + Text)

```python
contents=[
    'What is this a picture of?',
    types.Part.from_uri(
        file_uri='gs://generativeai-downloads/images/scones.jpg',
        mime_type='image/jpeg',
    ),
]
```

---

## 7. System Instructions and Other Config Options

Pass additional instructions and parameters:

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        temperature=0.3,
    ),
)
print(response.text)
```

---

## 8. JSON and Enum Constrained Output

### 8.1 JSON Response Schema

You can request the output as strictly JSON, using a Python schema model (Pydantic or TypedDict).

#### 8.1.1 Pydantic Example

```python
from pydantic import BaseModel

class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=CountryInfo,
    ),
)
print(response.text)
# Also check response.parsed to see the schema-validated object
```

#### 8.1.2 TypedDict Example

```python
import typing_extensions as typing

class PizzaOrder(typing.TypedDict):
    size: str
    ingredients: list[str]
    type: str

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="I'd like a medium pizza with cheese and tomato sauce",
    config=types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
        response_schema=PizzaOrder,
    ),
)
print(response.text)       # Strict JSON
print(response.parsed)     # Python dict
```

### 8.2 Enum Constrained Output

You can force the response to be one of a set of known values.

#### 8.2.1 Text Enum

```python
from enum import Enum

class InstrumentEnum(Enum):
    PERCUSSION = 'Percussion'
    STRING = 'String'
    WOODWIND = 'Woodwind'
    BRASS = 'Brass'
    KEYBOARD = 'Keyboard'

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What instrument plays multiple notes at once?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': InstrumentEnum,
    },
)
print(response.text)         # e.g. "Keyboard"
print(response.parsed)       # an Enum object
```

#### 8.2.2 JSON Enum

Set `response_mime_type` to `'application/json'` for an enum in JSON format (quoted string):

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What instrument plays multiple notes at once?',
    config={
        'response_mime_type': 'application/json',
        'response_schema': InstrumentEnum,
    },
)
print(response.text)       # e.g. "Keyboard"
print(response.parsed)     # an Enum object
```

---

## 9. Prompting Techniques

### 9.1 Zero-Shot

No examples provided, just an instruction or question:

```python
zero_shot_prompt = """Classify movie reviews as POSITIVE, NEUTRAL or NEGATIVE.
Review: "Her" is a disturbing study of AI..."
Sentiment: """

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=zero_shot_prompt,
    config=types.GenerateContentConfig(
        temperature=0.1,
        top_p=1,
        max_output_tokens=5,
    ),
)
print(response.text)
```

### 9.2 One-Shot / Few-Shot

Provide examples (one or several) so the model learns the pattern from them:

```python
few_shot_prompt = """Parse a customer's pizza order into valid JSON:

EXAMPLE:
I want a small pizza with cheese, tomato sauce, and pepperoni.
JSON Response:
{
"size": "small",
"type": "normal",
"ingredients": ["cheese", "tomato sauce", "pepperoni"]
}

EXAMPLE:
Can I get a large pizza with tomato sauce, basil, and mozzarella
JSON Response:
{
"size": "large",
"type": "normal",
"ingredients": ["tomato sauce", "basil", "mozzarella"]
}

ORDER:
"""

customer_order = "Give me a large pizza with cheese & pineapple"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(
        temperature=0.1,
        top_p=1,
        max_output_tokens=250,
    ),
    contents=[few_shot_prompt, customer_order]
)

print(response.text)
```

---

## 10. Chat Sessions (Multi-Turn)

Instead of single-turn calls, you can keep a conversation state with a `chat` object.

### 10.1 Basic Chat

```python
chat = client.chats.create(model='gemini-2.5-flash')

response = chat.send_message('Hello! My name is Zlork.')
print(response.text)

response = chat.send_message('Tell me something about dinosaurs.')
print(response.text)

response = chat.send_message('Do you remember what my name is?')
print(response.text)
```

### 10.2 Streaming in Chats

```python
chat = client.chats.create(model='gemini-2.5-flash')
for chunk in chat.send_message_stream('tell me a story'):
    print(chunk.text)
```

---

## 11. Function Calling

### 11.1 Automatic Python Function Support

Simply pass Python functions as `tools`. The model can call them if needed. By default, the SDK attempts to automatically call the function and include its response.

```python
def get_current_weather(location: str) -> str:
    """Returns the current weather."""
    return "sunny"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(
        tools=[get_current_weather]
    ),
)
print(response.text)
```

### 11.2 Manual Declaration & Invocation

If you prefer to handle function calls yourself, define a `FunctionDeclaration` and pass it in a `Tool`:

```python
function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters=types.Schema(
        type='OBJECT',
        properties={
            'location': types.Schema(
                type='STRING',
                description='The city and state, e.g. San Francisco, CA',
            ),
        },
        required=['location'],
    ),
)

tool = types.Tool(function_declarations=[function])

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[tool]),
)

print(response.function_calls[0])  # function call part from the model
```

After receiving the function call from the model, you can manually invoke your Python function, then pass the function’s result back into the model if you want the model to integrate that result into a final answer:

```python
user_prompt_content = types.Content(
    role='user',
    parts=[types.Part.from_text(text='What is the weather like in Boston?')],
)
function_call_part = response.function_calls[0]
function_call_content = response.candidates[0].content

def get_current_weather(location: str) -> str:
    return 'sunny in ' + location

try:
    function_result = get_current_weather(**function_call_part.function_call.args)
    function_response = {'result': function_result}
except Exception as e:
    function_response = {'error': str(e)}

function_response_part = types.Part.from_function_response(
    name=function_call_part.name,
    response=function_response,
)
function_response_content = types.Content(role='tool', parts=[function_response_part])

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        user_prompt_content,
        function_call_content,
        function_response_content,
    ],
    config=types.GenerateContentConfig(tools=[tool]),
)

print(response.text)
```

### 11.3 Function Calling Modes (ANY, NONE, etc.)

The `FunctionCallingConfig` can be set to `ANY` to force the model to *always* return function calls, or to “auto.” You can also configure automatic function calling turn limits or disable it:

```python
def get_current_weather(location: str) -> str:
    return "sunny"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

Or limit calls:

```python
def get_current_weather(location: str) -> str:
    return "sunny"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the weather like in Boston?",
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=2
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode='ANY')
        ),
    ),
)
```

---

## 12. Streaming & Async

### 12.1 Streaming

```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### 12.2 Async Methods

The client also has an async interface:

```python
# Use client.aio for async usage
response = await client.aio.models.generate_content(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
)

print(response.text)
```

#### 12.2.1 Async Streaming

```python
async for chunk in client.aio.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### 12.3 Async Chat

```python
chat = client.aio.chats.create(model='gemini-2.5-flash')
response = await chat.send_message('tell me a story')
print(response.text)

async for chunk in chat.send_message_stream('tell me more'):
    print(chunk.text)
```

---

## 13. Error Handling

To handle errors raised by the model service, catch `google.genai.errors.APIError`:

```python
from google.genai import errors

try:
    client.models.generate_content(
        model="invalid-model-name",
        contents="What is your name?",
    )
except errors.APIError as e:
    print(e.code)     # e.g. 404
    print(e.message)  # details about the error
```

---

## 14. (Optional) Evaluating Output

You can also use the LLM to evaluate or “score” the quality of its own output by providing a specialized “evaluation agent” prompt. 
This is an advanced topic, but typically it involves instructing the model on how to rate answers according to a rubric. 
For example:

```python
evaluation_prompt = f"""
You are an evaluator. The user request is: "{user_request}"
The model's answer is: "{model_answer}"
Rate it on a scale of 1 to 5 based on correctness and clarity.
Explain your reasoning.
"""

eval_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=evaluation_prompt,
)

print(eval_response.text)
```
