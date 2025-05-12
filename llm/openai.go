package llm

// OpenAI API

import (
	"context"
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
	"github.com/openai/openai-go"
)

func init() {
	home, _ := os.UserHomeDir()
	godotenv.Load(filepath.Join(home, ".env"))
}

// message is a big body of text. The function returns another big body of text

func Call_openai(message string, systemPrompt string) string {

	client := openai.NewClient()

	ctx := context.Background()

	params := openai.ChatCompletionNewParams{
		Messages: []openai.ChatCompletionMessageParamUnion{
			openai.UserMessage(message),
			openai.SystemMessage(systemPrompt),
		},
		Seed:  openai.Int(0),
		Model: openai.ChatModelGPT4o,
	}

	completion, err := client.Chat.Completions.New(ctx, params)

	if err != nil {
		panic(err)
	}

	return completion.Choices[0].Message.Content
}
