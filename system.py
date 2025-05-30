import sys
import os
import platform
import pyttsx3
import win32gui
import subprocess
import win32con
import json
from time import sleep as sp
class Sys():
  class Handelers:
        # get current window
        def getCurrentWindow(self) -> int:
            ## get current fucos window
            if platform.system() == "Windows":
                hwnd = win32gui.GetForegroundWindow()
                return hwnd
            elif platform.system() == "Linux":
                output = subprocess.check_output(["xdotool", "getwindowfocus"])
                return output.decode().strip()
            elif platform.system() == "Darwin":
                output = subprocess.check_output(["osascript", "-e", "tell application \"System Events\" to get name of first process whose frontmost is true"])
                return output.decode().strip()
        def getKeyWord(self, funName: str) -> list:
            with open("keywords.json", "r") as f:
                data = json.load(f)
            return data.get(funName, [])
  def closeWindow(self)-> None:
      current_window = self.Handelers().getCurrentWindow()
      print("🚀 ~ current_window:", current_window)
      if current_window:
          try:
              ## close window by window ID
              if platform.system() == "Windows":
                  win32gui.PostMessage(current_window, win32con.WM_CLOSE, 0, 0)
              elif platform.system() == "Linux":
                  subprocess.run(["xdotool", "windowclose", current_window])
              elif platform.system() == "Darwin":
                  subprocess.run(["osascript", "-e", f'tell application "{current_window}" to quit'])
          except SystemExit:
              pass
      else:
          print("No window to close.")
  def open(self, window_name: str) -> None:
        # Retrieve the mapping of allowed window names to executables
        mapping = self.Handelers().getKeyWord("open")  # Expects a dict: {"google": "chrome.exe", ...}
        
        # Validate the requested window name
        if window_name not in mapping:
            raise ValueError(f"Window '{window_name}' is not in the allowed list.")
        
        # Get the executable or target for the requested window
        target = mapping[window_name]
        system = platform.system()

        # Launch the target based on the OS
        try:
            if system == "Windows":
                # Use cmd start to launch GUI apps
                subprocess.run(f"start {target}", shell=True, check=True)
            elif system == "Linux":
                subprocess.run(["xdg-open", target], check=True)
            elif system == "Darwin":
                subprocess.run(["open", target], check=True)
            else:
                raise PermissionError(f"Unsupported platform: {system}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Executable for '{window_name}' not found: {target}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to open '{window_name}': {e}")



if __name__ == "__main__":
    sys_instance = Sys()
    sys_instance.open("word")
