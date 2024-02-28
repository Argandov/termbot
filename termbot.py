#!/usr/bin/env python3

import openai
import os
import json
import time
from dotenv import dotenv_values
from openai import OpenAI
import re
import sys
import math
import argparse
import numpy as np

# VARIABLES
addons_path = "context" 
GPT_3_5_TURBO_COST = 0.002 / 1000
GPT_4_COST = 0.06 / 1000
Verbose = False
config = dotenv_values("YOUR_DOTENV_FILEPATH")
OPENAI_MODEL = "gpt-4"
OPENAI_API_KEY = config["OPENAI_API_KEY"]

# OpenAI API Setup:
openai.api_key = OPENAI_API_KEY
OpenAI_Client = OpenAI(
        api_key=OPENAI_API_KEY,
        )

usage_examples = '''

    -s, --silent    | Silent mode: Does not display "Termbot 3000 Banner",
    -v, --verbose   | Verbose Mode: Display, on every question, with information about its current processing (Approximate prompt cost, tokens, etc.)

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

    3. CONTEXT MODE:

    a) List Available contexts:

        termbot -l
            Will list all the available contexts under the "context" folder
    
    b) Use the available contexts:

        termbot -s -v -p "File: /file:file_for_analysis.txt" -c ./sample_joke
            (Where sample_joke is a file with custom instructions for GPT in ./context directory)
        
            Or a triple input for Termbot: 1. Stdin (Piping) + 2. Prompt + 3. Context File
        pbpaste | termbot -s -v -p "Please give me the tl;dr of this information" -c sample_joke
            (Where "sample_joke" is a file with custom instructions for GPT under context/ folder)

[i] Please visit https://github.com/Argandov/termbot for more example and use cases. 
There's a really wide use case potential for Termbot..

'''

termbot_logo = r"""
  _______                  _           _     ____   ___   ___   ___
 |__   __|                | |         | |   |___ \ / _ \ / _ \ / _ \
    | | ___ _ __ _ __ ___ | |__   ___ | |_    __) | | | | | | | | | |
    | |/ _ \ '__| '_ ` _ \| '_ \ / _ \| __|  |__ <| | | | | | | | | |
    | |  __/ |  | | | | | | |_) | (_) | |_   ___) | |_| | |_| | |_| |
    |_|\___|_|  |_| |_| |_|_.__/ \___/ \__| |____/ \___/ \___/ \___/

"""

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

# COLORS
GRAY = "\033[90m"
LIGHT_BLUE = "\033[94m"
PINK = "\033[95m"
RESET = "\033[0m"

# ARGUMENT PARSER
parser = argparse.ArgumentParser(description='Termbot\'s Help:')

parser.add_argument('--interactive', '-i', nargs='?', const=True, default=None, help='Interactive mode')
parser.add_argument('--prompt', '-p', help='Enter prompt mode')
parser.add_argument('--context', '-c', help='Use a given custom Context file. DO NOT USE \"PROMPT MODE\"')
parser.add_argument('--outfile', help='Send the raw output from GPT to a new specified file')
parser.add_argument('--verbose', '-v', action='store_true', help='Add some verbosity')
parser.add_argument('--list', '-l', action='store_true', help='List available contexts')
parser.add_argument('--slim', '-s', action='store_true', help='Enable slim mode')
parser.add_argument('--examples', '-e', action='store_true', help="Print some example usage")
parser.add_argument('--gpt4', action='store_true', help='Use GPT 4 instead of 3.5 Turbo (Defaults to 3.5 Turbo)')

# ARGUMENT PROCESSING
args = parser.parse_args()

# FUNCTION AREA:
def print_verbosity(filename, file_provided, tokens_used, cost, execution_time):
    if filename is not None:
        print(f'{GRAY}[i] File provided: {file_provided:<25}\n[i] Tokens used: {tokens_used:<6}\n[i] Model: {OPENAI_MODEL}\n[i] Cost: ${cost:>8}\n[i] Execution time: {execution_time:>6}{RESET}')
    else:
        print(f'{GRAY}[i] Tokens used: {tokens_used:<6}\n[i] Model: {OPENAI_MODEL}\n[i] Cost: ${cost:>8}\n[i] Execution time: {execution_time:>6}{RESET}')

def calculate_prompt_cost(MODEL):
    if MODEL == "gpt-3.5-turbo":
        return GPT_3_5_TURBO_COST 
    elif MODEL == "gpt-4":
        return GPT_4_COST

def _list_contexts(addons_path):
    #  Absolute path of the contexts folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    addons_path = os.path.join(script_dir, addons_path)

    files = []
    file_paths = []
    for filename in os.listdir(addons_path):
        files.append(filename)
    for _files in files:
        print(_files)

def _get_context(selected_context, addons_path): # WORK IN PROGRESS!!
    #  Absolute path of the contexts folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    addons_path = os.path.join(script_dir, addons_path)

    files = []
    file_paths = []
    for filename in os.listdir(addons_path):
        files.append(filename)
        file_path = os.path.join(addons_path, filename)
        file_paths.append(file_path)
    
    if selected_context in files:
        selected_context = addons_path + "/" + selected_context
        with open(selected_context, "r", encoding="utf-8") as context_file:
            context = context_file.read()
        return context
    else:
        print(f"[!] Context \"{selected_context}\" does not exist")
        sys.exit(1)

# TEXT CHUNKING FOR HANDLING API'S RATE LIMITS:
def _text_chunking(message):
    print("[i] Message Length: " + str(len(message)))
    words = message.split(" ")
    chunk_words = np.array_split(words, 8)
    chunk_of_sentences = ' '.join(list(chunk_words[0]))
    return chunk_of_sentences

def prepare_response(res,st,filename=None):
    role = res.choices[0].message.role
    completion_tokens = res.usage.completion_tokens
    prompt_tokens = res.usage.prompt_tokens
    total_tokens = res.usage.total_tokens
    content = res.choices[0].message.content

    # Print out information in desired format
    print(f"{LIGHT_BLUE}{content}{RESET}")

    if args.outfile:
        with open(args.outfile, 'w', encoding='utf-8') as outFile:
            outFile.write(content)

    # Estimate and print out cost based on total tokens used
    cost_per_token = calculate_prompt_cost(OPENAI_MODEL)
    total_cost = total_tokens * cost_per_token
    et = time.time() # End Time
    execution_time = et - st
    cost = f'{total_cost:.4f}'
    tokens_used = total_tokens
    if isinstance(execution_time, str):
    
        execution_time = float(execution_time)
        execution_time = f"{execution_time:.2f} seconds"
    
    file_provided = filename
    tokens_used = total_tokens
    cost = f'{total_cost:.4f}'
    execution_time = f'{execution_time:.2f} seconds'
    if Verbose == True:
        print_verbosity(filename, file_provided, tokens_used, cost, execution_time)

def chatter(msg, st, mood, filename=None):

    # If /file: was provided in prompt mode
    if filename is not None:
        with open(filename) as _file:
            if filename.endswith(".json"):
                JSON_DATA = json.load(_file)
                FILE_CONTENTS = json.dumps(JSON_DATA)
            else:
                FILE_CONTENTS = _file.read()
        
        # Create new message string with file contents appended
        FILE_CONTENTS = f"\n\nHere is what {filename} contains:" + "\n" + FILE_CONTENTS

        msg = msg + FILE_CONTENTS

        messages = [
            {"role": "system", "content": mood},
            {"role": "user", "content": msg}
        ]
    else: # If it's only handling user input data (prompt) or from stdin:
        
        msg = _text_chunking(msg)
        
        messages = [
            {"role": "system", "content": mood},
            {"role": "user", "content": msg}
        ]

    print("[i] - Calling OpenAI API...")
    res = OpenAI_Client.chat.completions.create(
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

    # Infinite Looping for Interactive mode
    if Interactive_mode == True:
        while True:
            msg, filename = _prepare_input(input(f"{PINK}[Prompt]> {RESET}"))
            st = time.time()
            chatter(msg,st,mood, filename)

# ARGUMENT HANDLING (IF/ELSE HELL)
if args.list:
    _list_contexts(addons_path)
if args.gpt4:
    OPENAI_MODEL = "gpt-4"
if args.slim:
    plaintext_output = True
else: 
    print(colored_ascii_art)
if args.verbose:
        Verbose = True
if not any(vars(args).values()):
    parser.print_help()
if args.interactive:
    if args.interactive is not True:
        mood = args.interactive
    Interactive_mode = True
    print('[i] Initializing interactive mode')

    _gpt_caller(Interactive_mode, mood)
elif args.examples:
    print(f"{PINK}{usage_examples}{RESET}")

if args.context and args.prompt:
    selected_context = args.context
    context = _get_context(selected_context, addons_path)
    mood = context
    input_lines = []
    
    if not sys.stdin.isatty():
        print("[i] Reading from Stdin...")
        for line in sys.stdin:
            input_lines.append(line.strip())
        mood = mood + "\n" + args.prompt
        prompt = '\n'.join(input_lines)
        Interactive_mode = False
        _gpt_caller(Interactive_mode, mood, prompt)

    # IF program starts without stdin:
    else:
        Interactive_mode = False

        _gpt_caller(False, mood, args.prompt)
    # Process the input
    stdin_content = '\n'.join(input_lines)
    # Stop processing further IF/Else evaluations
    sys.exit(1)

if args.context and not args.prompt:
    selected_context = args.context
    context = _get_context(selected_context, addons_path)
    mood = context
    input_lines = []
    
    if not sys.stdin.isatty():
        print("[i] Reading from Stdin...")
        for line in sys.stdin:
            input_lines.append(line.strip())
        prompt = '\n'.join(input_lines)
        Interactive_mode = False
        _gpt_caller(Interactive_mode, mood, prompt)

    # IF program starts without stdin:
    else:
        Interactive_mode = False

        _gpt_caller(False, mood, args.prompt)
    # Process  input
    stdin_content = '\n'.join(input_lines)

    # Stop processing further IF/Else evaluations
    sys.exit(1)


elif args.prompt:
    input_lines = []
    # IF program starts with stdin:
    if not sys.stdin.isatty():
        print("[i] Reding input from Stdin...")
        for line in sys.stdin:
            input_lines.append(line.strip())
        mood = args.prompt
        prompt = '\n'.join(input_lines)
        Interactive_mode = False
        _gpt_caller(Interactive_mode, mood, prompt)

    # IF program starts without stdin:
    else:
        mood = args.prompt
        Interactive_mode = False

        _gpt_caller(False, mood, args.prompt)
    # Process  input
    stdin_content = '\n'.join(input_lines)
