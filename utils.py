import subprocess
from playwright.sync_api import sync_playwright
import time

def run_code_in_sub(filename, timeout=10, html_capture_timeout=10):
    """
    Runs a Streamlit dashboard from Python file as subprocess and captures the HTML output.

    Args:
        filename: path to the Python script to run
        timeout: seconds to wait before killing the process
        html_capture_timeout: seconds to wait before capturing dashboard html
    
    Returns:
        dict: {
            "stdout": str,
            "stderr": str,
            "returncode": int,
            "timed_out": bool
            "html": str
        }
    """
    process = subprocess.Popen(
        ["streamlit", "run", filename, "--server.headless true", "--server.port", "8502"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(html_capture_timeout)

    html = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("http://localhost:8502")
            page.wait_for_timeout(3000)  # allow rendering
            html = page.content()
            browser.close()
    except Exception as e:
        html = f"HTML capture failed: {str(e)}"

    # Clean up subprocess
    process.terminate()
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        returncode = process.returncode
        timed_out = False
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = "", "Process timed out."
        returncode = None
        timed_out = True

    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "timed_out": timed_out,
        "html": html
    }

