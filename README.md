# AI-Powered Dashboard Generator

### Purpose: 

Demonstrate LLM app generation techniques. Generator will allow user prompt for information to be included in dashboard. OpenAI API is used to generate code to create Streamlit dashboard. NASA API is used to simulate data that AI driven custom tools would use.

### Steps:

- Prompt user for dashboard requirements
- Use OpenAI API to generate schema
- Use OpenAI API to generate code
- Pull NASA API data to populate dashboard
- Host dashboard or dispay dashboard
- Allow app to "learn" over time. Place generic versions of code in 

### Agents

- Plan: create outline for development based on user input. Output outline and check with user for tweaks. 
- Data: Determine necessary data exists. Generate code to fetch data.
- Coder: Recieve item from planner and code as necessary.
- Assembly: View code blocks created by coder agents and combine into complete package.
- Bug/optimizer: Read over all code and think of ways to improve or potential errors.



