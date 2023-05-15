#!/usr/bin/python3

import openai
import json
import time
from dotenv import dotenv_values
import os
import re
import sys
import fileinput
import math
import argparse

# VARIABLES
Verbose = False
config = dotenv_values(".env")
OPENAI_API_KEY = config["OPENAI_API_KEY"]
OPENAI_MODEL = "gpt-3.5-turbo"
mood = "First respond correctly and appropriately to user prompts, and finish with very bad jokes about the conversation."
usage_examples = '''
    Usage examples:

    1. INTERACTIVE MODE:

    Interactive mode, with a template given:
        termbot -i "You're a robot from 2067 and will answer my questions with a very robotic manner"

    Interactive mode, with no template given, will just open a chat from scratch:
        termbot -i

    2. PROMPT MODE:

    termbot -p "Analyze the contents of /file:hello_world.py and do X and Y"

    curl ifconfig.io | termbot -p "Tell me something about my IP address"

    echo "A box" | termbot -p "What can I do with this?"

    cat strange_program.py | termbot -p "Explain this strange python program for me"

'''

termbot_logo = '''

  _______                  _           _     ____   ___   ___   ___
 |__   __|                | |         | |   |___ \ / _ \ / _ \ / _ \
    | | ___ _ __ _ __ ___ | |__   ___ | |_    __) | | | | | | | | | |
    | |/ _ \ '__| '_ ` _ \| '_ \ / _ \| __|  |__ <| | | | | | | | | |
    | |  __/ |  | | | | | | |_) | (_) | |_   ___) | |_| | |_| | |_| |
    |_|\___|_|  |_| |_| |_|_.__/ \___/ \__| |____/ \___/ \___/ \___/



'''

# Define the gradient colors
blue = (0, 0, 255)  # RGB value for blue
pink = (255, 105, 180)  # RGB value for pink

# Split the ASCII art into lines
lines = termbot_logo.strip().split('\n')

# Determine the number of color steps based on the number of lines
num_steps = len(lines)

# Apply color formatting and display the ASCII art with gradient
colored_ascii_art = ''
for i, line in enumerate(lines):
    # Calculate the interpolation factor for the gradient
    factor = i / (num_steps - 1)

    # Interpolate the RGB values between blue and pink
    r = math.floor(blue[0] * (1 - factor) + pink[0] * factor)
    g = math.floor(blue[1] * (1 - factor) + pink[1] * factor)
    b = math.floor(blue[2] * (1 - factor) + pink[2] * factor)

    # Convert the RGB values to ANSI escape code for the corresponding color
    color_code = f'\033[38;2;{r};{g};{b}m'

    # Apply the color code to the line and append to the output
    colored_ascii_art += color_code + line + '\n'

# Reset the color to default
colored_ascii_art += '\033[0m'

# Define color codes
purple = '\033[95m'
blue = '\033[94m'
reset = '\033[0m'


# AUTH
openai.api_key = OPENAI_API_KEY

# COLORS
GRAY = "\033[90m"
LIGHT_BLUE = "\033[94m"
PINK = "\033[95m"
RESET = "\033[0m"

# ARGUMENT PARSER

# Create the parser
parser = argparse.ArgumentParser(description='Welcome!! _______________')

parser.add_argument('--interactive', '-i', nargs='?', const=True, default=None, help='Interactive mode')
parser.add_argument('--prompt', '-p', help='Enter prompt mode')
parser.add_argument('--verbose', '-v', help='Add some verbosity')
parser.add_argument('--silent', '-s', help='Don\'t print banner')
parser.add_argument('--examples', '-e', action='store_true', help="Print some example usage")

# ARGUMENT PROCESSING
args = parser.parse_args()

# FUNCTION AREA:

def print_verbosity(filename, file_provided, tokens_used, cost, execution_time):
    if filename is not None:
        print(f'{GRAY}[i] File provided: {file_provided:<25}\n[i] Tokens used: {tokens_used:<6}\n[i] Model: {OPENAI_MODEL}\n[i] Cost: ${cost:>8}\n[i] Execution time: {execution_time:>6}{RESET}')
    else:
        print(f'{GRAY}[i] Tokens used: {tokens_used:<6}\n[i] Model: {OPENAI_MODEL}\n[i] Cost: ${cost:>8}\n[i] Execution time: {execution_time:>6}{RESET}')


def prepare_response(res,st,filename=None):
    role = res['choices'][0]['message']['role']
    completion_tokens = res['usage']['completion_tokens']
    prompt_tokens = res['usage']['prompt_tokens']
    total_tokens = res['usage']['total_tokens']
    content = res['choices'][0]['message']['content']

    # Print out information in desired format
    print(f"{LIGHT_BLUE}[Response]> {content}{RESET}")

    # Calculate and print out cost based on total tokens used
    cost_per_token = 0.002 / 1000  # Price per token in dollars
    total_cost = total_tokens * cost_per_token
    et = time.time() # End Time
    execution_time = et - st
    cost = f'{total_cost:.4f}'
    tokens_used = total_tokens
    if isinstance(execution_time, str):
    # Format the execution time string
        execution_time = float(execution_time)
        execution_time = f"{execution_time:.2f} seconds"
        print("debug")
    # execution_time = f'{execution_time:.2f} seconds'
    file_provided = filename
    tokens_used = total_tokens
    cost = f'{total_cost:.4f}'
    execution_time = f'{execution_time:.2f} seconds'
    if Verbose == True:
        print_verbosity(filename, file_provided, tokens_used, cost, execution_time)

def chatter(msg, st, mood, filename=None):

    if filename is not None:
        with open(filename) as _file:
            if filename.endswith(".json"):
                JSON_DATA = json.load(_file)
                FILE_CONTENTS = json.dumps(JSON_DATA)
            else:
                FILE_CONTENTS = _file.read()

        # Create new message string with file contents appended
        FILE_CONTENTS = f"\n\nHere is what {filename} contains:" + "\n" + FILE_CONTENTS
        new_msg = msg + FILE_CONTENTS

        messages = [
            {"role": "system", "content": mood},
            {"role": "user", "content": new_msg}
        ]
    else:
        messages = [
            {"role": "system", "content": mood},
            {"role": "user", "content": msg}
        ]

    res = openai.ChatCompletion.create(
        model = OPENAI_MODEL,
        messages = messages
    )

    return prepare_response(res,st,filename)

def _prepare_input(prompt):
    filename_match = re.search(r'/file:(\S+)', prompt)
    if filename_match:
        filename = filename_match.group(1)
        filename_clean = re.sub(r'[^\w.]+$', '', filename)
        clean_message = prompt.replace('/file:' + filename, filename_clean)
    else:
        filename_clean = None
        clean_message = prompt
    return clean_message, filename_clean

def _gpt_caller(Interactive_mode, mood, prompt=""):
    msg, filename = _prepare_input(prompt)

    if Interactive_mode == False:
        st = time.time()
        chatter(msg,st,mood, filename)

    # Make it continuous for Interactive mode
    if Interactive_mode == True:
        while True:
            msg, filename = _prepare_input(input(f"{PINK}[Prompt]> {RESET}"))
            st = time.time()
            chatter(msg,st,mood, filename)

if not args.silent:
    print(colored_ascii_art)
if not any(vars(args).values()):
    parser.print_help()
if args.interactive:
    if args.interactive is not True:
        mood = args.interactive
    Interactive_mode = True
    print('[i] Initializing interactive mode')

    if args.verbose:
        print('[i] Verbosity Mode activated')
        Verbose = True

    _gpt_caller(Interactive_mode, mood)
elif args.examples:
    print(usage_examples)

elif args.prompt:
    input_lines = []
    # IF program starts with stdin:
    if not sys.stdin.isatty():
        for line in sys.stdin:
            input_lines.append(line.strip())
            mood = args.prompt
            print(f"MOOD: {mood}")
            prompt = '\n'.join(input_lines)
            Interactive_mode = False
            _gpt_caller(Interactive_mode, mood, prompt)

    # IF program starts without stdin:
    elif args.prompt:
        #prompt = input_lines.append(args.prompt) # ESTO ES NONE - POR?
        Interactive_mode = False
        _gpt_caller(False, mood, args.prompt)
    # Process the input
    stdin_content = '\n'.join(input_lines)
