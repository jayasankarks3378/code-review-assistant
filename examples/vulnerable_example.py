import os
import subprocess


def execute_command(command):
    password = "admin123"
    subprocess.run(command, shell=True)
    return password