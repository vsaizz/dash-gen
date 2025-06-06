# Functions dictating behavior of agents

from openai import OpenAI
import json
# import ast
# import subprocess
# import tempfile
# import os

from utils import run_code_in_sub

def planning_agent(user_prompt):
    """
    Plans dashboard project.
    
    Args:
        user_prompt: description of dashboard request

    Returns:
        plan: JSON prompt agent output describing plan for dashboard  
    """
    client = OpenAI()
    system_prompt = """You are the head AI agent working to make dashboards using NASA API data. 
    Your goal is to make interesting interactive dashboards that include tools to help users understand 
    the data. Convert user prompt into JSON plan with specific tasks for other AI developers to follow. 
    Include list of specific data needed for Data Sourcing Agent to find. Do not include ``` header."""

    response = client.chat.completions.create(
                model = "gpt-4.1-mini",
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                    ],
                temperature = 0.3
            )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": "Parsing failed", "response": response.choices[0].message.content}


def data_agent(plan):
    """
    Finds data sources based on generated plan. Validates data sourcing.

    Args: 
        plan: JSON with specific data requirements

    Returns:
        data_info: JSON with description of data requirements and Python code to pull data.
    """
    client = OpenAI()

    system_prompt = """You are a data sourcing agent. Based on the prompt plan, 
    find the proper NASA API data to get the required data. If other APIs are needed use only free sources without
    signup needed. You do not have any API keys other than NASA. Then, generate valid Python code to pull that data.
    Only return the valid Python code to source the data. This code will be used. Complete all the requirements
    given by the prompt agent. Include a test pulling all necessary data into a variable called 'data'.
    Be sure that there is actual data. Use historical data if no live data is available. Find as much data as possible.
    Do not include ``` header. Only python code."""

    user_content = json.dumps(plan)

    response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                    ],
                temperature = 0.3
            )
    data_info = response.choices[0].message.content
    return data_info
    


def coder_agent(plan, data_info):
    """
    Generates full dashboard code using the project plan and data source information.

    Args:
        plan: JSON from planning_agent
        data_info: Python code as string from data_agent #(verified by validation function)

    Returns:
        dashboard_code: string of full Python code for interactive dashboard
    """
    client = OpenAI()

    system_prompt = """You are a skilled software engineer proficient in Python. You receive a project plan and 
    Python code that pulls data from NASA APIs. Your job is to use the data to produce a complete Streamlit dashboard.
    Dashboard should be interactive, visualize data using plots as needed, include titles and explanations, 
    be readable and modular, include data fetching and loading code as given by data agent, handle errors in data.
    Return only working executable complete Python code as your final output. Do not use markdown formatting. 
    No '```python'"""
    
    user_prompt = f'''Plan:\n{json.dumps(plan, indent=1)}\nData Info:\n{data_info}'''

    response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                    ],
                temperature = 0.3
            )
    try:
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating dashboard: {str(e)}"
    


def debug_agent(initial_code, iterations=3,filename="dashboard_generated.py"):
    """
    Iteratively debug Python dashboard code by running and fixing it multiple times.
    
    Args:
        initial_code (str): Initial Python code to debug.
        iterations (int): Number of debug-run cycles to perform.
        filename (str): Temporary filename to save and run code.

    Returns:
        dict: {
            'status': 'success' or 'failure',
            'cleaned_code': final debugged code string,
            'error': error message if failure,
            'logs': list of dicts with keys ['stdout', 'stderr', 'returncode', 'timed_out'] for each run
        }
    """
    client = OpenAI()
    current_code = initial_code
    logs = []

    system_prompt = """You are in charge of debugging the dashboard python code. 
    The NASA API key is an env variable named 'NASA_API_KEY'. OpenAI API key:'OPENAI_API_KEY. Do not use streamlit secrets.
    Check that all syntax is correct. Ensure that code will run and generate a valid dashboard. 
    You are the final step before code is given to the user. Do not include '```python'. Code must
    be runnable. Only export python code. No description. use st.cache_data not st.cache. Pay attention to data types
    
    Catch any potential runtime issues, especially related to:
        - API calls returning None or missing keys
        - Unpacking errors
        - Deprecated features in Streamlit
    Ensure the function always returns safely unpackable values.
    Make sure that there is actual data and that the graphs are populated."""
    
    for i in range(iterations):
        user_prompt = f"Here is the current code:\n{current_code}\n\n" \
                      f"Here is the output from running this code:\n"
        if i > 0:
            last_log = logs[-1]
            user_prompt += f"STDOUT:\n{last_log['stdout']}\nSTDERR:\n{last_log['stderr']}\n"

        # Ask GPT to debug/fix the code given current output
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            fixed_code = response.choices[0].message.content.strip()
        except Exception as e:
            return {
                "status": "failure",
                "cleaned_code": current_code,
                "error": f"OpenAI API error: {str(e)}",
                "logs": logs,
            }

        # Save fixed code to file
        with open(filename, "w") as f:
            f.write(fixed_code)

        # Run the code in subprocess
        run_result = run_code_in_sub(filename)
        logs.append(run_result)

        # If no error and no timeout, we can stop early
        if run_result["returncode"] == 0 and not run_result["timed_out"]:
            return {
                "status": "success",
                "cleaned_code": fixed_code,
                "error": None,
                "logs": logs,
            }

        # Prepare for next iteration
        current_code = fixed_code

    # If after iterations still errors, return failure with last code and logs
    return {
        "status": "failure",
        "cleaned_code": current_code,
        "error": "Code still errors after debugging attempts.",
        "logs": logs,
    }