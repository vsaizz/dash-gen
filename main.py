# Turns user input into interactive dashboard populated with NASA data using OpenAI agents

import streamlit as st
import openai
import os
import subprocess
import time

from dotenv import load_dotenv
load_dotenv()

from agents import planning_agent, data_agent, coder_agent, debug_agent

openai.api_key = os.getenv("OPENAI_API_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")


def main():
    # get user prompt
    st.title("Dashboard Generator for NASA Data")

    prompt = st.text_area("Describe dashboard concept:", 
                          placeholder="Say something like... \n"
                          "'I want a dashboard that shows Mars weather trends for the past week.'\n"
                          "'Show me asteroids near Earth and let me sort by size and distance.'")
    
    show_code = st.checkbox("Show code outputs", value=True)

    # planning agent
    if st.button("Generate Dashboard"):
        with st.spinner("Planning dashboard..."):
           plan = planning_agent(prompt)
           if show_code:
            st.subheader("Plan")
            st.json(plan)

        # data agent
        with st.spinner("Sourcing data..."):
            data_info = data_agent(plan)
            if show_code:
                st.subheader("Data Info")
                st.code(data_info, language='python')

        with st.spinner("Generating dashboard code..."):
            raw_code = coder_agent(plan, data_info)
            if show_code:
                st.subheader("Dashboard Code")
                st.code(raw_code, language="python")

        with st.spinner("Debugging dashboard code..."):
            final_code = debug_agent(raw_code)
            if show_code:
                st.subheader("Final Debugged Code")
                st.code(final_code, language="python")

        st.success("Dashboard code generated and debugged.")

        # save to file
        with open("dashboard_generated.py", "w") as f:
            f.write(final_code["cleaned_code"])
        st.success("Dashboard code saved to dashboard_generated.py")



        # Launch in new subprocess
        subprocess.Popen(["streamlit", "run", "dashboard_generated.py", "--server.port", "8502"])
        time.sleep(3)

        st.markdown("### Dashboard Launched:")
        st.markdown("[Open dashboard](http://localhost:8502)", unsafe_allow_html=True)




if __name__ == "__main__":
    main()
