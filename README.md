# termbot
CLI tool for interacting with GPT directly in the terminal, and chat with your local files.

`termbot.py` is a Python script that allows the user to interact with OpenAI's GPT-X natural language processing system in the terminal. It allows for both interactive mode and prompt mode, where it can analyze text data and generate text responses based on the provided prompts.

Jump to [Use cases and Examples](https://github.com/Argandov/termbot/edit/main/README.md#more-use-cases-and-examples)

![termbot-prompt-mode Image](termbot-prompt-mode.png)

## Feelin' retro

The name "termbot 3000" and the ASCII banner idea just came because I was listening to [The Midnight 🎵](https://www.youtube.com/watch?v=VoD8RSnfpyo) while I was programming this and was feeling a litte bit retro at the moment.

## Disclaimer

As always with any third-party tool, specially with GPT, be careful what information you share with OpenAI. If necessary, change sensitive information at standard output (stdout), obscure the info and then use it. Use your best judgement for this.

## Limitations

* This program does NOT have memory yet. It cannot sustain a conversation, or have any information about previous prompts/answers.
* Currently it can only analyze 1 file per prompt. (If we provide, for example `analyze /file:hello.txt, and compare it with /file:hello2.txt` the second "file:/" will be passed as a string)

# Setup

### 1. Requirements for Installation
1. A valid OpenAI API key.
2. Python 3.x Installed

### 2. Clone the repository and install the PIP required packages (openai and python-dotenv):

```bash
git clone https://github.com/Argandov/termbot.git && cd termbot && pip install -r requirements.txt
```
### 3. Setting up the environment

* Change `mood` variable for giving termbot a default context
* Change the default `.env` I provided with `OPENAI_API_KEY = "XXXXXXXXXX"`.
* To make this script launch from anywhere, we can take the following steps:
  * Move `sudo mv termbot.py /usr/local/bin/termbot` and `chmod u+x /usr/local/bin/termbot` to launch it from anywhere.
  * Move also the .env file to $HOME directory:`mv .env $HOME/.env`, `chmod 600 $HOME/.env` and add this path to the script on line 18, like this:
`config = dotenv_values("/home/jean/.env")`
* OR, just for testing purposes, do `alias termbot=/path/to/termbot.py` and execute `termbot` from anywhere.

## Usage

The following command line arguments are available for `termbot.py`:

```bash
  -h, --help            show this help message and exit
  --interactive , -i    Interactive mode
  --prompt, -p          Enter prompt mode
  --verbose, -v         Add some verbosity
  --slim, -s            Enable slim mode
  --examples, -e        Print some example usage
  --gpt4                Use GPT 4 instead of 3.5 Turbo (Defaults to 3.5 Turbo)
```

### Interactive vs. Prompt modes

* Interactive will open a TUI (Terminal User Interface) to continuously prompt GPT until `ctrl+c` breaks the execution. Works well with analyzing files. Do not pipe stdout into interactive mode.
* Prompt mode will be a one-time prompt/response interaction. This way, we can pipe stdout commands into it, or analyze files on the fly.

### Verbosity

Verbosity will add to termbot's output useful stats in color gray, such as:
* Filename (If it was used for analyzing one), 
* Model used (GPT 3.5 Turbo or GPT 4)
* Cost of individual operation (Per prompt/answer) - **Only an estimation**.
* Tokens used by the individual operation (Per prompt/answer).
* Execution time per prompt/answer

Example:
```
 termbot -s -v -p "analyze /file:output.nmap"
It seems like the nmap scan was performed on the host scanme.nmap.org and it discovered that the 5550/tcp port is open and running the sdadmind service. This information could be useful for further investigation and analysis.

[i] File provided: output.nmap
[i] Tokens used: 259
[i] Model: gpt-3.5-turbo
[i] Cost: $  0.0005
[i] Execution time: 7.89 seconds
```

### Slim Mode

Slim mode will not print the "Termbot 3000" banner (But will still use blue color for output, and gray for verbose mode).

### GPT version

By default, termbot uses GPT-3.5 Turbo. We can add `--gpt4` for changing its model.

# Analyzing local files or stdout by termbot

The 2 most interesting features of Termbot are:
* It can take Input files and analyzing them by giving it a prompt with `/file:myfile.txt`, or:
* We can "pipe" stdout into termbot `<command> | termbot -p "<do something with the command's output` 

(See [Use cases and Examples](https://github.com/Argandov/termbot/edit/main/README.md#more-use-cases-and-examples). 

The following files can be handled by termbot:

* JSON files
* Any other plain text file (txt files, programs, scripts, .conf files, etc.)

# More use cases and Examples

The use cases for this are almost endless. Here I provide some examples and ideas for its usage.

How it actually looks:
* Not interactive, verbosity enabled, slim mode, with GPT 4:

![termbot verbosity, GPT 4](termbot-verbosity-gpt4.PNG)

* Interactive, verbosity enabled. GPT 4

![Termbot Interactive + Verbosity enabled](termbot-verbosity-interactive.PNG)

1. Interactive mode

Open an interactive session (TUI or Terminal User Interface), with a specified "template" or "persona" (See "Context" when using GPT). It will override the default "mood" context.

`termbot -i "You're French, and will answer every question in French only"`

Or simply open interactive mode (TUI) without any context and it will work normally as a chatbot, with the default "mood" context.

`termbot -i`

2. Prompt mode (My favourite)

Prompt mode does the same as interactive, but it's a one-time use only. 

The most basic use case: 
- `termbot -p "Why are vegetables called that way?"`

Give it a file and "analyze" it: 
- `termbot -p "Please review the SSHD configuration file /file:/etc/ssh/sshd_config and assess its overall security security. Identify any potential vulnerabilities, recommend improvements, and suggest best practices to enhance the overall security of the SSH server.`
- `termbot -p "What does this /file:aws-iam-policy.json and what does it do?`
- `termbot -p "Analyze /file:app.py Flask app and propose a more efficient way to handle user POST data"`

...Or piping whatever into it: 
- `strings -n 8 -td malware_sample.exe | termbot -p "Extract printable strings from a malware sample and analyze any IoCs."`
- `nmap -p 445 my-target.local -sC -oN SMB-target.nmap && termbot -p "Give me a summary of SMB vulnerabilities in /file:SMB-target.nmap or interesting information for this host"`
- `net accounts /domain | termbot -p 'Retrieve and assess the Active Directory password policy settings.'`
- `curl ifconfig.io | termbot -p "Tell me something about this IP address"`
- `cat my-file.json | termbot -p "Validate this file as a valid JSON format"`

...Or simply execute commands directly:
- `termbot.py -p "$(uptime) tell me something about my computer's uptime stats"`

Actually, as a Proof of concept, the first termbot's README.md file I uploaded was written by Termbot:

`termbot -p "Analyze the script /file:termbot.py and generate a README.md for Github. Document what it does, its purposes and requirements for installation"`

---
To-Do/Wishlist for this program:
- [x] Fix Verbose + Slim mode
- [ ] Import Colors, ASCII banner as modules when necessary (Efficiency)
- [ ] Handle more than 1 file, or even recursively.
- [ ] Handle memory (Chaining)
- [ ] Handle a /url: argument and scrape it
