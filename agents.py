# Functions dictating behavior of agents

from openai import OpenAI
import json
import requests

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
                model = "gpt-4.1-nano",
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
        data_info: Python code string to pull valid NASA data, based on the official NASA APIs directory.
    """
    client = OpenAI()

    # Fetch NASA API directory JSON from official GitHub source
    nasa_apis_url = "https://raw.githubusercontent.com/nasa/api-docs/gh-pages/assets/json/apis.json"
    try:
        response = requests.get(nasa_apis_url, timeout=10)
        nasa_apis = response.json()
    except Exception as e:
        return f"# Error fetching NASA APIs list: {e}"

    system_prompt = f"""You are a data sourcing agent. Based on the prompt plan, 
    find the proper NASA API data to get the required data. Use only the following list of NASA APIs and no others:

    {json.dumps(nasa_apis, indent=2)}

    If other APIs are needed use only free sources without signup needed. You do not have any API keys other than NASA. 
    Then, generate valid Python code to pull that data. Do not use placeholders.
    Only return the valid Python code to source the data. This code will be used. Complete all the requirements
    given by the prompt agent. Be sure that there is actual data. Use historical data if no live data is available. Find as much data as possible.
    Do not include any markdown or ``` headers. Only python code."""

    user_content = json.dumps(plan)

    response = client.chat.completions.create(
                model = "gpt-4.1-mini",
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
    No '```python'
    Do not make up example or synthetic data."""
    
    user_prompt = f'''Plan:\n{json.dumps(plan, indent=1)}\nData Info:\n{data_info}'''

    response = client.chat.completions.create(
                model = "gpt-4.1-nano",
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
    



def debug_agent(initial_code, iterations=2, filename="dashboard_test.py"):
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
            'logs': list of dicts with keys ['stdout', 'stderr', 'returncode', 'timed_out', 'html', 'port']
        }
    """
    client = OpenAI()
    current_code = initial_code
    logs = []

    system_prompt = """You are responsible for debugging Python code that implements a Streamlit dashboard. You will receive:
            The full Python code of the dashboard,
            The HTML output from running that dashboard (which may indicate rendering or data issues),
            Any error messages or logs generated from the last run.
        Your task is to carefully analyze all provided information and:
            Correct all errors and exceptions, including syntax, runtime, and logical issues.
            Use the NASA API key as an environment variable named NASA_API_KEY. Do not hardcode API keys or use Streamlit secrets. Do not use DEMO api key.
            Verify that all data sources used in the dashboard are valid and accessible. If data is missing or invalid, modify the code to find alternative data. Keep to the original concept.
            Ensure the final code will run without errors and generate a complete, functional dashboard with meaningful data visualizations.
            Do not include any explanations or markdown code blocks. Only output the corrected Python code.
            Your corrections should be thorough and final, as this is the last debugging step before the code is delivered to the user.
            If html does not include data, update code with new data sources using NASA API as outlined in current code.
        Do not include '```python' or any headers. Only output clean code."""

    for i in range(iterations):
        # Save current code to file
        with open(filename, "w") as f:
            f.write(current_code)

        # Run and capture output
        run_result = run_code_in_sub(filename)
        logs.append(run_result)

        # Build prompt with current code and current run output
        user_prompt = f"Here is the current code:\n{current_code}\n\n" \
                      f"STDOUT:\n{run_result['stdout']}\n" \
                      f"STDERR:\n{run_result['stderr']}\n" \
                      f"HTML OUTPUT:\n{run_result['html']}\n"

        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            current_code = response.choices[0].message.content
        except Exception as e:
            return {
                "status": "failure",
                "cleaned_code": current_code,
                "error": f"OpenAI API error: {str(e)}",
                "logs": logs,
            }

    # if run_result["returncode"] == 0 and not run_result["timed_out"]:
    return {
        "status": "success",
        "cleaned_code": current_code,
        "error": None,
        "logs": logs,
    }
        
    # return {
    #     "status": "failure",
    #     "cleaned_code": current_code,
    #     "error": "Code still errors after debugging attempts.",
    #     "logs": logs,
    # }