
termbot_usage_examples = '''

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

        termbot -s -v -p "File: /file:file_for_analysis.txt" -c ./context.txt
            (Where context.txt is a file with custom instructions for GPT)
        
            Or a triple input for Termbot: 1. Stdin (Piping) + 2. Prompt + 3. Context File
        pbpaste | termbot -s -v -p "Please give me the tl;dr of this information" -c german_person
            (Where "german_person" is a file with custom instructions for GPT under context/ folder)

[i] Please visit https://github.com/Argandov/termbot for more example and use cases. 
There's a really wide use case potential for Termbot..

'''
