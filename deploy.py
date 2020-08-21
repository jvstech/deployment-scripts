#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import os
import subprocess
import sys

# List of packages to install
packageList = [
  "binwalk",
  "gdb",
  "lib32stdc++6",
  "lib32z1",
  "libpam-cracklib",
  "netcat",
  "nmap",
  "python2.7",
  "socat",
  "tcpflow",
  "upx"
]

# List of scripts to download
scriptsList = [
  ("https://is.gd/xpattern", "pattern.py")
]

# List of other files to download
downloadList = []

# List of users to create
userList = []

# wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
# sudo dpkg -i packages-microsoft-prod.deb

def main():
  configure_logging()
  install_packages()
  
def install_packages():
  failedPackages = []
  for package in packageList:
    logging.info(f"Installing package {package} ...")
    proc = shell_exec(["apt", "install", package, "-y"])
    if (proc.returncode != 0):
      logging.error(f"Failed to install {package}. ({proc.returncode})")
      failedPackages += [package]
      
  if (len(failedPackages) > 0):
    failureMsg = "The following packages failed to install:\n"
    for package in failedPackages:
      failureMsg += f"-- {package}\n"
    logging.warning(failureMsg)

def configure_logging():
  logging.root.setLevel(logging.DEBUG)
  conHandler = logging.StreamHandler()
  conHandler.setLevel(logging.INFO)
  conFormatter = ConsoleFormatter()
  conHandler.setFormatter(conFormatter)
  logging.root.addHandler(conHandler)
  
  fileHandler = logging.FileHandler("{0}/deployment-{1}.log".format(
    os.getcwd(), datetime.now().strftime("%Y%m%d-%H%M%S")))
  fileHandler.setLevel(logging.DEBUG)
  fileFormatter = LogFileFormatter()
  fileHandler.setFormatter(fileFormatter)
  logging.root.addHandler(fileHandler)
  
def shell_exec(args):
  proc = subprocess.Popen(args)
  logging.debug(f"Executing command: {subprocess.list2cmdline(proc.args)}")
  proc.communicate()
  return proc
  
class Colors:
  """ ANSI color codes """
  BLACK = "\033[0;30m"
  RED = "\033[0;31m"
  GREEN = "\033[0;32m"
  BROWN = "\033[0;33m"
  BLUE = "\033[0;34m"
  PURPLE = "\033[0;35m"
  CYAN = "\033[0;36m"
  LIGHT_GRAY = "\033[0;37m"
  DARK_GRAY = "\033[1;30m"
  LIGHT_RED = "\033[1;31m"
  LIGHT_GREEN = "\033[1;32m"
  YELLOW = "\033[1;33m"
  LIGHT_BLUE = "\033[1;34m"
  LIGHT_PURPLE = "\033[1;35m"
  LIGHT_CYAN = "\033[1;36m"
  LIGHT_WHITE = "\033[1;37m"
  BOLD = "\033[1m"
  FAINT = "\033[2m"
  ITALIC = "\033[3m"
  UNDERLINE = "\033[4m"
  BLINK = "\033[5m"
  NEGATIVE = "\033[7m"
  CROSSED = "\033[9m"
  END = "\033[0m"
  RESET = END
  NORMAL = END
  # cancel SGR codes if we don't write to a terminal
  if not __import__("sys").stdout.isatty():
    for _ in dir():
      if isinstance(_, str) and _[0] != "_":
        locals()[_] = ""
  else:
    # set Windows console in VT mode
    if __import__("platform").system() == "Windows":
      kernel32 = __import__("ctypes").windll.kernel32
      kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
      del kernel32
      
  @staticmethod
  def wrap(color, s):
    return f"{color}{s}{Colors.END}"

class ConsoleFormatter(logging.Formatter):
  _default_fmt = f"{Colors.GREEN}%(asctime)s{Colors.END} %(levelname)-8s "
  
  @staticmethod
  def get_message_color(levelNo):
    textColors = {
      logging.NOTSET: Colors.NORMAL,
      logging.DEBUG: Colors.DARK_GRAY,
      logging.INFO: Colors.LIGHT_BLUE,
      logging.WARNING: Colors.YELLOW,
      logging.ERROR: Colors.LIGHT_RED,
      logging.CRITICAL: Colors.LIGHT_RED
    }
    
    if not levelNo in textColors:
      return Colors.NORMAL
    return textColors[levelNo]
  
  @staticmethod
  def get_bracket_token(levelNo):
    tokenStrings = {
      logging.NOTSET: "*",
      logging.DEBUG: "=",
      logging.INFO: Colors.wrap( \
        ConsoleFormatter.get_message_color(logging.INFO), "+"),
      logging.WARNING: Colors.wrap( \
        ConsoleFormatter.get_message_color(logging.WARNING), "*"),
      logging.ERROR: Colors.wrap( \
        ConsoleFormatter.get_message_color(logging.ERROR), "*"),
      logging.CRITICAL: Colors.wrap( \
        ConsoleFormatter.get_message_color(logging.CRITICAL), "!")
    }
    
    if not levelNo in tokenStrings:
      return "*"
    return tokenStrings[levelNo]
  
  @staticmethod
  def get_level_format(levelNo):
    return ConsoleFormatter._default_fmt + " [" + \
      ConsoleFormatter.get_bracket_token(levelNo) + "] " + \
      Colors.wrap(ConsoleFormatter.get_message_color(levelNo), \
        "%(message)s")
  
  def __init__(self):
    super().__init__(fmt=Colors.wrap(Colors.GREEN, "%(asctime)s") + \
      " %(levelname)-8s [*] %(message)s", 
      datefmt="%Y-%m-%d %H:%M:%S",
      style='%')
  
  def format(self, record):
    origFormat = self._style._fmt
    self._style._fmt = ConsoleFormatter.get_level_format(record.levelno)
    result = logging.Formatter.format(self, record)
    self._style._fmt = origFormat
    return result

class LogFileFormatter(logging.Formatter):
  def __init__(self):
    super().__init__("%(asctime)s %(levelname)-8s [%(process)d] %(message)s", 
      datefmt="%Y-%m-%d %H:%M:%S",
      style='%')
      
if __name__ == "__main__":
  main()
