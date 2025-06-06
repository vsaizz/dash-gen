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

#### Exoplanets Dashboard Demo

[![Watch the video](https://raw.githubusercontent.com/vsaizz/dash-gen/a48dc9cc00c47a9bea894869759c0fb0ff26b050/thumbnail_exoplanets.png)](https://raw.githubusercontent.com/vsaizz/dash-gen/a48dc9cc00c47a9bea894869759c0fb0ff26b050/test_exoplanets.mp4)


#### Mars Weather Dashboard Demo


[![Watch the video](https://raw.githubusercontent.com/vsaizz/dash-gen/a48dc9cc00c47a9bea894869759c0fb0ff26b050/thumbnail_mars_weather.png)](https://raw.githubusercontent.com/vsaizz/dash-gen/a48dc9cc00c47a9bea894869759c0fb0ff26b050/test_mars_weather.mp4)

### Demo

#### Exoplanets Dashboard Demo

<video src="test_exoplanets.mp4" muted playsinline controls></video>

https://github.com/vsaizz/dash-gen/blob/main/test_exoplanets.mp4

#### Mars Weather Dashboard Demo

<video src="test_mars_weather.mp4" muted playsinline controls></video>


### Demo

#### Exoplanets Dashboard Demo

[![Watch the Exoplanets Demo](https://raw.githubusercontent.com/vsaizz/dash-gen/main/thumbnail_exoplanets.png)](https://youtube.com/shorts/5LjwMMhAAM0?feature=share)

#### Mars Weather Dashboard Demo

[![Watch the Mars Weather Demo](https://raw.githubusercontent.com/vsaizz/dash-gen/main/thumbnail_mars_weather.png)](https://youtube.com/shorts/k1Szktv6YOQ?feature=share)
