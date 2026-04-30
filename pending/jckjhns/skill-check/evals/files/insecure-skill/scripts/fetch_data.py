"""
TEST FIXTURE — This script deliberately contains security anti-patterns
for SkillCheck's security review to detect. Do not use in production.
"""

import os
import subprocess
import requests


API_KEY = "sk-abc123-fake-key-for-testing-purposes"


def fetch_data(url, output_path):
    response = requests.get(url, verify=False)
    with open(output_path, 'w') as f:
        f.write(response.text)


def post_process(filepath, user_command):
    os.system(f"{user_command} {filepath}")


def transform(filepath, expression):
    with open(filepath, 'r') as f:
        data = f.read()
    result = eval(expression)
    return result


def save_config(data):
    with open("/etc/app-config.json", 'w') as f:
        f.write(data)
