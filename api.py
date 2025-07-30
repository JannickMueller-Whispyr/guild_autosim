# USAGE:
# python3 api.py API_KEY test.simc
# file is saved to [simId].json

from __future__ import print_function

import time
import sys
import argparse
import json
import urllib.request
import urllib.parse
import os

API_KEY_PATH = r"D:/python/secrets/RAIDBOTS_API_KEY.txt"

def get_api_key():
    with open(API_KEY_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

parser = argparse.ArgumentParser()
parser.add_argument("input_file", nargs="?", help="Path to .simc file")
parser.add_argument("--simc_version", default="nightly")
parser.add_argument("--batch", action="store_true", help="Run all .simc files in simc_inputs folder")
args = parser.parse_args()

HOST = 'https://www.raidbots.com'

SIM_SUBMIT_URL = "%s/sim" % HOST

def run_simc_file(input_file, simc_version="nightly"):
    with open(input_file, 'r', encoding='utf-8') as simc_file:
        simc_input = simc_file.read()
    api_key = get_api_key()
    data = {
        'apiKey': api_key,
        'type': 'advanced',
        'advancedInput': simc_input,
        'simcVersion': simc_version,
    }
    body = json.dumps(data).encode('utf8')
    SIM_SUBMIT_URL = "https://www.raidbots.com/sim"
    res = urllib.request.urlopen(urllib.request.Request(
        SIM_SUBMIT_URL,
        data=body,
        headers={
            'content-type': 'application/json',
            'User-Agent': 'Whispyr\'s Raidbots API Script'
        }
    ))
    sim = json.loads(res.read().decode('utf8'))
    simId = sim['simId']
    while True:
        req = urllib.request.Request(
            f"https://www.raidbots.com/api/job/{simId}",
            headers={
                'content-type': 'application/json',
                'User-Agent': 'Whispyr\'s Raidbots API Script'
            }
        )
        res = urllib.request.urlopen(req)
        sim_status = json.loads(res.read().decode('utf8'))
        state = sim_status['job']['state']
        progress = sim_status['job']['progress']
        print(f"Sim {simId} progress: {progress}")
        if state == "complete":
            break
        time.sleep(5)
    req = urllib.request.Request(
        f"https://www.raidbots.com/reports/{simId}/data.json",
        headers={
            'User-Agent': 'Whispyr\'s Raidbots API Script'
        }
    )
    res = urllib.request.urlopen(req)
    sim_data = json.loads(res.read().decode('utf8'))
    results_folder = "results"
    os.makedirs(results_folder, exist_ok=True)
    output_path = os.path.join(results_folder, f"{simId}.json")
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(json.dumps(sim_data))
    print(f"Result saved to {output_path}")

if __name__ == "__main__":
    if args.batch:
        folder = "simc_inputs"
        for filename in os.listdir(folder):
            if filename.endswith(".simc"):
                run_simc_file(os.path.join(folder, filename))
    elif args.input_file:
        run_simc_file(args.input_file, args.simc_version)
    else:
        print("Usage: python api.py <input_file> [--simc_version VERSION] or python api.py --batch")
        sys.exit(1)