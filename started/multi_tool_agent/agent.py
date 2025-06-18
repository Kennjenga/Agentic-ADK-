# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import json
import aiohttp
import os

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Import the instruction string from our prompt.py file
from .prompt import multi_tool_agent_instruction

# --- Tool Functions ---
# These functions will be wrapped by FunctionTool and made available to the agent.
# They must be async and should return a string (often JSON).

async def get_weather(location: str) -> str:
    """
    Retrieves the current weather information for a specified location using live data.
    Args:
        location (str): The city or area (e.g., "London", "New York, NY").
    Returns:
        str: A JSON string containing weather data like temperature and condition.
    """
    print(f"DEBUG: Tool 'get_weather' called with location: {location}")
    
    # Get API key from environment variable
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        return json.dumps({
            "location": location, 
            "error": "Weather API key not configured. Please set OPENWEATHER_API_KEY environment variable."
        })
    
    try:
        # Use OpenWeatherMap API for live weather data
        async with aiohttp.ClientSession() as session:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"  # For Celsius
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    weather_data = {
                        "location": f"{data['name']}, {data['sys']['country']}",
                        "temperature": f"{data['main']['temp']}°C",
                        "condition": data['weather'][0]['description'].title(),
                        "humidity": f"{data['main']['humidity']}%",
                        "wind_speed": f"{data['wind']['speed']} m/s"
                    }
                    return json.dumps(weather_data)
                else:
                    error_data = await response.json()
                    return json.dumps({
                        "location": location,
                        "error": f"Weather data not found: {error_data.get('message', 'Unknown error')}"
                    })
    except Exception as e:
        return json.dumps({
            "location": location,
            "error": f"Failed to fetch weather data: {str(e)}"
        })
                    
    except Exception as e:
        return json.dumps({
            "location": location,
            "error": f"Failed to fetch weather data: {str(e)}"
        })

async def calculator(expression: str) -> str:
    """
    Evaluates a given mathematical expression.
    Args:
        expression (str): The mathematical expression to calculate (e.g., "2+2", "100 / (5-1)").
    Returns:
        str: A JSON string with the original expression and its result, or an error message.
    """
    print(f"DEBUG: Tool 'calculator' called with expression: {expression}")
    try:
        # For safety in a real application, use a dedicated math parsing library
        # instead of eval().
        allowed_chars = set("0123456789+-*/(). ")
        # Basic sanitization: remove spaces and check characters
        sanitized_expression = "".join(char for char in expression if char in allowed_chars and char != ' ')
        
        if not sanitized_expression:
            raise ValueError("Expression is empty or invalid after sanitization.")

        result = eval(sanitized_expression)
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"expression": expression, "error": str(e)})

# --- Root Agent Definition ---
# This is the agent instance that ADK will load and run.
root_agent = Agent(
    model="gemini-2.0-flash", # As per your example
    name="utility_query_agent", # A descriptive name for this agent
    description="An AI assistant that uses tools to provide weather information and perform calculations.",
    instruction=multi_tool_agent_instruction, # Using the imported instruction
    tools=[
        FunctionTool(
            func=get_weather
            # The description will be taken from the get_weather function's docstring.
        ),
        FunctionTool(
            func=calculator
            # The description will be taken from the calculator function's docstring.
        ),
    ],
)