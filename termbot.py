#!/usr/bin/env python3

from modules.termbot_banner import \
        colored_ascii_art, \
        GRAY, LIGHT_BLUE, PINK, RESET
from modules.termbot_data import termbot_usage_examples

import os
import json
import time
import re
import sys
import math
import argparse
import numpy as np
from dotenv import dotenv_values, load_dotenv
from openai import OpenAI

addons_path = "context"
Verbose = False
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

OPENAI_MODEL = "gpt-4"
chat_history = []

# OpenAI API Setup:
OpenAI_Client = OpenAI(
        api_key=OPENAI_API_KEY,
        )

# ARGUMENT PARSER
    # Create the parser
parser = argparse.ArgumentParser(description='Termbot\'s Help:')
    # Parse arguments
parser.add_argument('--interactive', '-i', nargs='?', const=True, default=None, help='Interactive mode')
parser.add_argument('--prompt', '-p', help='Enter prompt mode')
parser.add_argument('--context', '-c', help='Use a given custom Context file. DO NOT USE \"PROMPT MODE\"')
parser.add_argument('--outfile', help='Send the raw output from GPT to a new specified file')
parser.add_argument('--verbose', '-v', action='store_true', help='Add some verbosity')
parser.add_argument('--list', '-l', action='store_true', help='List available contexts')
parser.add_argument('--slim', '-s', action='store_true', help='Enable slim mode')
parser.add_argument('--examples', '-e', action='store_true', help="Print some example usage")
parser.add_argument('--gpt4', action='store_true', help='Use GPT 4 instead of 3.5 Turbo (Defaults to 3.5 Turbo)')
    # Argument Parsing
args = parser.parse_args()

    # Verbosity for Printing General Stats about execution
def print_verbosity(filename, tokens_used, cost, execution_time):
    if filename is not None:
        print(f'\
                {GRAY}[i] File provided: {filename:<25}\n\
                [i] Tokens used: {tokens_used:<6}\n\
                [i] Model: {OPENAI_MODEL}\n\
                [i] Cost: ${cost:>8}\n\
                [i] Execution time: {execution_time:>6}{RESET}'
              )
    else:
        print(f'\
                {GRAY}[i] Tokens used: {tokens_used:<6}\n\
                [i] Model: {OPENAI_MODEL}\n\
                [i] Cost: ${cost:>8}\n\
                [i] Execution time: {execution_time:>6}{RESET}'
              )

def calculate_prompt_cost(MODEL):
    # Making a rough estimation of the token cost
    # Note: This doesn't take into account the diff. between input/output cost differences

    GPT_3_5_TURBO_COST = 0.002 / 1000
    GPT_4_COST = 0.06 / 1000
    if MODEL == "gpt-3.5-turbo":
        return GPT_3_5_TURBO_COST
    elif MODEL == "gpt-4":
        return GPT_4_COST

def _list_available_contexts(addons_path): # WORK IN PROGRESS!!
    # List available Termbot's Contexts 

        # This joins the absolute path of the contexts folder instead of trying to load them from the user's PWD context:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    addons_path = os.path.join(script_dir, addons_path)

    files = []
    file_paths = []
    for filename in os.listdir(addons_path):
        files.append(filename)

    # Extract the selected context at execution
def _get_context(selected_context, addons_path): 
    # This joins the absolute path of the contexts folder instead of trying to load them from the user's PWD context:
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

def prepare_response(openai_response,start_time,filename=None):
    # This function receives the API's response and extracts desired data

    res = openai_response
    role = res.choices[0].message.role
    completion_tokens = res.usage.completion_tokens
    prompt_tokens = res.usage.prompt_tokens
    total_tokens_used = res.usage.total_tokens
    content = res.choices[0].message.content
    chat_history.append(content)

        # Print out GPT's chat response in desired format
    print(f"{LIGHT_BLUE}{content}{RESET}")

        # Write Chat Response into a new file if desired
    if args.outfile:
        with open(args.outfile, 'w', encoding='utf-8') as outFile:
            outFile.write(content)

    # Calculate and print out cost based on total tokens used
    cost_per_token = calculate_prompt_cost(OPENAI_MODEL)
    total_cost = total_tokens_used * cost_per_token
    end_time = time.time() 
    execution_time = end_time - start_time
    cost = f'{total_cost:.4f}'
    if isinstance(execution_time, str):
    
        execution_time = float(execution_time)
        execution_time = f"{execution_time:.2f} seconds"
    
    cost = f'{total_cost:.4f}'
    execution_time = f'{execution_time:.2f} seconds'
    if Verbose:
        print_verbosity(filename, total_tokens_used, cost, execution_time)

def chatter(msg, start_time, mood, filename=None):
    # Prepare data and send to OpenAI API

    FILE_CONTENTS = ""
    # If /file: was provided in the prompt
    if filename is not None:

        # If only one file was provided
        if len(filename) == 1:
            filename = filename[0]
            if filename.endswith(".json"):
                with open(filename) as f:
                    FILE_CONTENTS += "[INFO] BEGINNING of File: " + filename + " ---------- \n"
                    FILE_CONTENTS +=  f.read()
                    
                    FILE_CONTENTS += "[INFO] END of File: " + filename + " ---------- \n"

            else:
                with open(filename) as f:
                    FILE_CONTENTS += "[INFO] BEGINNING of File: " + filename + " ---------- \n"
                    FILE_CONTENTS += f.read()
                    FILE_CONTENTS += "[INFO] END of File: " + filename + " ---------- \n"

        elif len(filename) > 1:

            # If multiple files were provided at prompt
            for f in filename:
                print(f"Opening {f}...")
                with open(f) as _file:
                    if f.endswith(".json"):
                        # Load json file
                        JSON_DATA = json.load(_file)
                        # Put the raw string of the json file into the FILE_CONTENTS variable
                        FILE_CONTENTS += "[INFO] BEGINNING of File: " + f + " ---------- \n"
                        FILE_CONTENTS += json.dumps(JSON_DATA)
                        FILE_CONTENTS += "[INFO] END of File: " + f + " ---------- \n"
                    else:
                        # Load _file and append it to the FILE_CONTENTS variable:
                        FC = _file.read()
                        FILE_CONTENTS += "[INFO] BEGINNING of File: " + f + " ---------- \n"
                        FILE_CONTENTS += FC
                        FILE_CONTENTS += "[INFO] END of File: " + f + " ---------- \n"
            
        # Create new message string with file contents appended
            # This Message is for OpenAI API
        FILE_CONTENTS = f"\n\nFile Contents:" + "\n" + FILE_CONTENTS
        
        msg = msg + FILE_CONTENTS

        messages = [
            {"role": "system", "content": mood},
            {"role": "user", "content": msg}
        ]

    else: # If it's only handling user input data (prompt) or from stdin:
        
        messages = [
            {"role": "system", "content": mood},
            {"role": "user", "content": msg}
        ]

    chat_history.append(mood)
    chat_history.append(msg)

    try:
        openai_response = OpenAI_Client.chat.completions.create(
            model = OPENAI_MODEL,
            messages = messages
        )

    except Exception as e:
        print("[X] Error: :\n", e)
        sys.exit(1)

    return prepare_response(openai_response,start_time,filename)

def input_linter(prompt):
    # Search for user input data containing "/file:" 
    filename_match = re.search(r'/file:(\S+)', prompt)
    pattern = r"/file:([^ ]+)"

    matches = re.findall(pattern, prompt)

        # Process each match
    for filename in matches:
        # Clean up the filename (similar to what you did before but adapted for this context)
        filename_clean = re.sub(r'[^\w.]+$', '', filename)

        # Replace the original "hello:/" prefixed string with the cleaned filename in the prompt
        # Note: This replaces all instances of the exact match. If you have identical filenames, they'll all be replaced.
        clean_message = prompt.replace('/file:' + filename, filename_clean)

    if not matches:
        filename_clean = None
        
    return clean_message, matches

def filter_interactive_mode(Interactive_mode, mood, prompt=""):
    # initialize interactive mode if chosen 

        # Extract filename if user input contains "/file:"
    msg, filename = input_linter(prompt)

    if Interactive_mode == False:
        start_time = time.time()
        chatter(msg,start_time,mood, filename)

    # Make it continuous for Interactive mode
    if Interactive_mode == True:
        conversation_history = []
        while True:
            user_input = input(f"{PINK}[Prompt]> {RESET}")
            msg, filename = input_linter(user_input)
            start_time = time.time()
            chatter(msg,start_time,mood, filename)

# PREPARE ARGUMENTS

def process_with_context_and_prompt(context, prompt, addons_path, verbose):
    selected_context = context
    if args.context:
        context = _get_context(selected_context, addons_path)
        mood = context
    else:
        mood = prompt
    input_lines = []
    prompt = gather_input_from_stdin(input_lines, mood, prompt, verbose)

    # Process the input
    stdin_content = '\n'.join(input_lines)
    sys.exit(1)

def gather_input_from_stdin(input_lines, mood, prompt, verbose):
    if not sys.stdin.isatty():
        if verbose:
            print("[i] Reading from Stdin...")
        for line in sys.stdin:
            input_lines.append(line.strip())
        mood = mood + "\n" + prompt
        prompt = '\n'.join(input_lines)
        filter_interactive_mode(False, mood, prompt)

        # Process the input
        stdin_content = '\n'.join(input_lines)

    else:
        Interactive_mode = False
        filter_interactive_mode(False, mood, prompt)
    return prompt

def handle_args(args):
    if args.list:
        _list_available_contexts(addons_path)

    OPENAI_MODEL = "gpt-4" if args.gpt4 else "gpt-4"
    plaintext_output = True if args.slim else print(colored_ascii_art)
    Verbose = True if args.verbose else False

    if not any(vars(args).values()):
        parser.print_help()

    Interactive_mode = False

    if args.interactive and args.context:
        mood = args.interactive if args.interactive is not True else ""
        Interactive_mode = True
        process_with_context_and_prompt(args.context, args.prompt, addons_path, Verbose) if args.context and args.prompt else filter_interactive_mode(False, mood, args.prompt)

    elif args.examples:
        print(f"{PINK}{termbot_usage_examples}{RESET}")

    elif args.context and args.prompt:
        process_with_context_and_prompt(args.context, args.prompt, addons_path, Verbose)

    elif args.context and not args.prompt:
        process_with_context_and_prompt(args.context, "", addons_path, Verbose)

    elif args.prompt:
        process_with_context_and_prompt("", args.prompt, addons_path, Verbose)

handle_args(args)
