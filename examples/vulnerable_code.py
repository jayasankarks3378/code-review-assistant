import subprocess


def execute_command(command: str) -> None:
    subprocess.run(command, shell=True)