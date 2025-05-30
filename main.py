import subprocess
import json
import platform
import logging
import re
from system import Sys  # Assuming system.py is in the same directory

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class Main:
    def __init__(self):
        self.sys_instance = Sys()
        logging.debug("Main initialized with Sys instance")

    def runAI(self, user_input: str, timeout: int = 30) -> str:
        logging.debug(f"runAI called with user_input: {user_input}")
        try:
            with open("Prompt.txt", encoding="utf-8") as f:
                template = f.read()
        except Exception as e:
            logging.error(f"Failed to load Prompt.txt: {e}")
            raise
        prompt = template.replace("${UserInput}", user_input).strip()
        # Instruct model to output strict JSON with double quotes

        logging.debug(f"Final prompt: {prompt}")

        # Build command
        module = "deepseek-r1:latest"  # Default model
        exe = "ollama.exe" if platform.system() == "Windows" else "ollama"
        cmd = [exe, "run", module]
        logging.debug(f"Executing: {cmd}")

        try:
            result = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                check=True,
                timeout=timeout
            )
            raw = result.stdout.strip()
            logging.debug(f"Raw AI response: {raw}")

            ## formatting the output
            if not raw:
                logging.error("Empty response from AI")
                raise ValueError("AI returned empty response")
            match = re.search(r"\{.*?\}", raw)
            finalOut = match.group(0) if match else raw
            # Direct JSON parse
            logging.debug(f"Final output to process: {finalOut}")
            self.callRunFromAI(finalOut)
            return raw
        except FileNotFoundError:
            msg = "Ollama executable not found. Install Ollama and add to PATH."
            logging.error(msg)
            raise RuntimeError(msg)
        except subprocess.TimeoutExpired:
            msg = f"AI selector timed out after {timeout} seconds"
            logging.error(msg)
            raise RuntimeError(msg)
        except subprocess.CalledProcessError as e:
            logging.error(f"AI selector error: {e.stderr}")
            raise RuntimeError(f"AI selector failed: {e.stderr}")

    def callRunFromAI(self, response: str) -> None:
        logging.debug(f"callRunFromAI received: {response}")
        try:
            data = json.loads(response)
            logging.debug(f"Parsed data: {data}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON parse error: {e}")
            raise ValueError(f"Invalid JSON from AI: {e}, response: {response}")

        function = data.get("function")
        args = data.get("args", [])
        if not function:
            logging.error("Missing 'function' field in JSON")
            raise ValueError("AI JSON missing 'function' field")

        # Combine args for open if needed
        arg = None
        if function == "open":
            arg = " ".join(args) if args else None
            logging.debug(f"Open function with args: {arg}")

        self.run(function, arg)

    def run(self, process: str, arg: str = None) -> None:
        logging.debug(f"Running process: {process}, arg: {arg}")
        try:
            if process == "close":
                self.sys_instance.closeWindow()
            elif process == "open":
                if not arg:
                    logging.warning("Open called without target")
                    print("No argument provided for open.")
                else:
                    self.sys_instance.open(arg)
            else:
                logging.warning(f"Unknown process: {process}")
                print(f"Unknown process: {process}")
        except Exception as e:
            logging.error(f"Error in run: {e}")
            print(f"Failed to execute {process}: {e}")

if __name__ == "__main__":
    main = Main()
    try:
        output = main.runAI("open word")
        print(output)
    except Exception:
        logging.exception("Unrecoverable error in main")