# AI-Powered Dashboard Generator

### Purpose: 

Demonstrate LLM app generation techniques. Generator will prompt user for dashboard requirements. OpenAI API is used to run agents to create Streamlit dashboard. NASA API is used as a stand-in for data that AI-driven tools could access and analyze.

### Steps:

1. Prompt user for dashboard requirements.
2. Generate task list for dashboard.
3. Find data using NASA API or other free sources online.
4. Generate Streamlit dashboard.
5. Iteratively run the dashboard in background and correct for errors.
6. Launch working dashboard in new Streamlit.

### Agents

- Plan: create outline for development based on user input. Output outline and check with user for tweaks. 
- Data: Determine necessary data exists. Generate code to fetch data.
- Coder: Recieve plan/data and generate code for dashboard.
- Bug/optimizer: Read over all code and think of ways to improve/catch potential errors.

## Demo

