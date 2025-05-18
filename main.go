package main

import (
	"fmt"
	"io"
	"os"

	"path/filepath"

	"github.com/spf13/cobra"

	"github.com/Argandov/termbot/helpers"
	"github.com/Argandov/termbot/llm"
)

func main() {
	if err := buildCLI().Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func isPipedInput() bool {
	stat, _ := os.Stdin.Stat()
	return (stat.Mode() & os.ModeCharDevice) == 0
}

func listAvailableContexts() {
	home, err := os.UserHomeDir()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Could not determine home directory")
		os.Exit(1)
	}

	contextDir := filepath.Join(home, ".config", "termbot", "context")
	files, err := os.ReadDir(contextDir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Could not read context directory: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Available contexts:")
	for i, file := range files {
		if !file.IsDir() {
			fmt.Printf("%d. %s\n", i+1, file.Name())
		}
	}
}

func readContextFile(contextName string) string {
	home, err := os.UserHomeDir()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Could not determine home directory")
		os.Exit(1)
	}

	contextPath := filepath.Join(home, ".config", "termbot", "context", contextName)
	data, err := os.ReadFile(contextPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Could not read context file '%s': %v\n", contextName, err)
		os.Exit(1)
	}

	return string(data)
}

func readFileFromCLI(path string) (string, error) {
	// First: try as-is (cwd)
	data, err := os.ReadFile(path)
	if err == nil {
		return string(data), nil
	}

	// Second: try as absolute path
	absPath, absErr := filepath.Abs(path)
	if absErr != nil {
		return "", fmt.Errorf("failed to resolve path: %v", absErr)
	}

	data, err = os.ReadFile(absPath)
	if err != nil {
		return "", fmt.Errorf("file not found in CWD or as absolute: %v", err)
	}

	return string(data), nil
}

func buildCLI() *cobra.Command {
	var prompt string
	var verbose bool
	var contextName string
	var listOption bool
	var doSetup bool
	var printExamples bool
	var dryRun bool
	var inputFile string
	var slimMode bool

	cmd := &cobra.Command{
		Use:   "termbot",
		Short: "\nTermbot is a command-line interface tool for conveniently interacting with OpenAI's GPT-X natural language processing system, directly from your terminal. It allows the user to use standard ChatGPT-like question/answer functionality, with added flexibility such as interacting with local file contents, sending large data from STDIN, using custom local instructions, and more.",
		Run: func(cmd *cobra.Command, args []string) {
			if doSetup {
				helpers.PerformSetup()
				os.Exit(0)
			}

			if printExamples {
				helpers.PrintExamples()
				os.Exit(0)
			}

			if listOption {
				// List available contexts and exit
				listAvailableContexts()
				os.Exit(0)
			}

			if isPipedInput() {
				stdinBytes, err := io.ReadAll(os.Stdin)
				if err != nil {
					fmt.Fprintln(os.Stderr, "Failed to read from stdin:", err)
					os.Exit(1)
				}
				prompt = fmt.Sprintf("%s\n\n(piped input):\n\n%s", prompt, string(stdinBytes))
			}

			if prompt == "" && inputFile != "" && contextName != "default" /* Zero prompt option */ {
				fileContent, err := readFileFromCLI(inputFile)
				if err != nil {
					fmt.Fprintln(os.Stderr, err)
					os.Exit(1)
				}
				prompt = fmt.Sprintf("%s\n\n(file %s contents:)\n\n%s", prompt, inputFile, fileContent)
			} else if prompt == "" && inputFile == "" && contextName == "default" {
				cmd.Help()
				os.Exit(0)
			} else if prompt == "" && inputFile != "" && contextName == "default" {
				fmt.Println("Zero prompt option requires input file and context. Read examples with -e flag.")
				os.Exit(1)
			} else if prompt != "" && inputFile != "" /* OK */ {
				fileContent, err := readFileFromCLI(inputFile)
				if err != nil {
					fmt.Fprintln(os.Stderr, err)
					os.Exit(1)
				}
				prompt = fmt.Sprintf("%s\n\nfile %s contents:\n\n%s", prompt, inputFile, fileContent)
			}

			runApp(prompt, verbose, contextName, dryRun, slimMode)
		},
	}

	cmd.Flags().StringVarP(&prompt, "prompt", "p", "", "LLM prompt (required)")
	cmd.Flags().StringVarP(&contextName, "context", "c", "default", "Choose a context to use")
	cmd.Flags().StringVarP(&inputFile, "file", "f", "", "File input (Absolute or relative path)")
	cmd.Flags().BoolVarP(&listOption, "list-contexts", "l", false, "List available contexts")
	cmd.Flags().BoolVarP(&printExamples, "examples", "e", false, "Print examples and additional usage")
	cmd.Flags().BoolVarP(&dryRun, "dry-run", "d", false, "Print the prompts without actually running it")
	cmd.Flags().BoolVarP(&verbose, "verbose", "v", false, "Enable verbose mode")
	cmd.Flags().BoolVarP(&doSetup, "setup", "", false, "Make termbot set itself up in your system")
	cmd.Flags().BoolVarP(&slimMode, "slim-mode", "m", false, "Enable slim mode (No ANSI colors)")

	return cmd
}

func runApp(prompt string, verbose bool, contextName string, dryRun bool, slimMode bool) {

	systemPrompt := readContextFile(contextName)
	response := llm.Call_openai(prompt, systemPrompt)

	// CONTROL FLOW:
	if dryRun {
		fmt.Printf("%s\n\n%v\n\n", "[Prompt]", prompt)
		fmt.Println()
		fmt.Printf("%s\n\n%v\n\n", "[System Prompt]", systemPrompt)
		fmt.Println()
		os.Exit(0)
	}

	if verbose && slimMode {
		fmt.Printf("%s\n\n%v\n\n", "[prompt]", prompt)
		fmt.Println()
		fmt.Printf("%s\n\n%v\n\n", "[system prompt]", systemPrompt)
		fmt.Println()
		fmt.Printf("%s\n%v\n\n", "[LLM response]", response)
		os.Exit(0)
	}

	if !verbose && slimMode {
		fmt.Println(response)
		os.Exit(0)
	}

	if verbose && !slimMode {
		var promptColor string
		var systemPromptColor string
		promptColor = "\033[90m[Prompt]\033[0m"
		systemPromptColor = "\033[90m[System Prompt]\033[0m"
		fmt.Printf("%s\n\n%v\n\n", promptColor, prompt)
		fmt.Println()
		fmt.Printf("%s\n\n%v\n\n", systemPromptColor, systemPrompt)
		fmt.Printf("\033[35m%s\033[0m\n", response)
		os.Exit(0)
	}
	if !verbose && !slimMode {
		fmt.Printf("\033[35m%s\033[0m\n", response)
		os.Exit(0)
	}

}
