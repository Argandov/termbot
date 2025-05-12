package helpers

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// The following function can be called with any quantity of args, all boolean:

func PrintExamples() {
	fmt.Println(`

Examples:

  1. Simple prompt: termbot -p 'What is the capital of Germany?'
  2. Stdin input: cat test.json | termbot -p "Extract important fields from JSON"
  3. Custom Context (system prompt): termbot -c german_speaking -p "Hello"
  4. Read files directly: termbot -f script.py -p "What improvements can be made to this script?"

Zero prompt option (Requires input file -f flag and a context file -c flag):

  termbot -c analyze_script -f script.py
	
	Where "analyze_script" is a context file with specific instructions. 

	Termbot will run anyways with an empty prompt (-p "")

File path examples:

  -f can be used with either absolute or relative paths (The program with first seek relative, then absolute path if the first fails).

	Hence:

		termbot -f hello.py 

	Will seek first for hello.py in the current directory. If it's not found, it will search at /hello.py

Dry Run & Verbosity:

	This is useful for testing purposes.

	Dry Run (-d or --dry-run) will print the prompt WITHOUT sending it to the LLM.

	Verbosity (-v or --verbose) will print the user prompt AND the LLM response.

Contexts:

	Context files are inside $HOME/.config/termbot/context/ folder. They do not need to follow any format and can be raw files without any extension (i.e. "default", "analyze_document", etc).

Usage suggestion: Use aliases 

	alias t='termbot -p'

And just use it like this:

	t -p "hello world"

  `)

}

func warnUser() {
	reader := bufio.NewReader(os.Stdin)

	fmt.Print("WARNING: This will override $HOME/.env file if it already exists, and any previous $HOME/.config/termbot/context files. Proceed? [y/n] ")
	input, _ := reader.ReadString('\n')
	input = strings.ToLower(strings.TrimSpace(input))

	if input == "y" || input == "yes" {
		fmt.Println("Proceeding with setup...")
	} else {
		fmt.Println("Aborted.")
		os.Exit(0)
	}
}

func PerformSetup() {

	// GUARDRAILS:
	warnUser()

	home, err := os.UserHomeDir()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to find user home directory")
		os.Exit(1)
	} else {
		fmt.Printf("[i] Found user home directory: %s\n", home)
	}

	contextDir := filepath.Join(home, ".config", "termbot", "context")
	envFile := filepath.Join(home, ".env")

	if err := os.MkdirAll(contextDir, 0755); err != nil {
		fmt.Fprintf(os.Stderr, "[!] Could not create context directory: %v\n", err)
		os.Exit(1)
	} else {
		fmt.Printf("[i] Created context directory: %s\n", contextDir)
	}

	defaultPath := filepath.Join(contextDir, "default")
	if err := os.WriteFile(defaultPath, []byte("You're a helpful assistant."), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "[!] Could not create default context file: %v\n", err)
		os.Exit(1)
	} else {
		fmt.Printf("[i] Created default context file: %s\n", defaultPath)
	}

	fmt.Print("Enter your OpenAI API key: ")
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	apiKey := scanner.Text()

	envContent := fmt.Sprintf("OPENAI_API_KEY='%s'\n", apiKey)
	if err := os.WriteFile(envFile, []byte(envContent), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "[X] Could not write to .env file: %v\n", err)
		os.Exit(1)
	} else {
		fmt.Printf("[i] Created .env file: %s\n", envFile)
	}

	fmt.Println("[i] Setup completed successfully.")
}
