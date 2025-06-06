# AI-Powered Dashboard Generator

### Purpose: 

Demonstrate LLM application generation techniques. This generator prompts the user for dashboard requirements and uses the OpenAI API to run a set of agents to create Streamlit dashboard. The NASA API is used as an example of a data source that AI-driven tools could access and analyze.

### Steps:

1. Prompt user for dashboard requirements.
2. Generate task list for dashboard.
3. Find data using NASA API or other free sources online.
4. Generate Streamlit dashboard.
5. Iteratively run and debug the dashboard in background.
6. Launch the working dashboard using Streamlit.

### Agents

- Planner: Creates a development outline based on user input. *(Future: Outputs the outline and checks with the user for revisions.)*
- Data Agent: Determine if necessary data exists and generates a script to fetch it.
- Coder: Recieves the plan+data and generates the dashboard script.
- Bug Fixer / Optimizer: Reviews the full code and think of ways to improve/catch potential errors.

### Demo

- [![Exoplanets Dashboard Demo](thumbnail_exoplanets.png)](https://youtube.com/shorts/k1Szktv6YOQ?feature=share)
- [![Mars Weather Dashboard Demo](thumbnail_mars_weather.png](https://youtube.com/shorts/5LjwMMhAAM0)