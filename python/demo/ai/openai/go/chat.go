
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Stream   bool      `json:"stream"`
}

type StreamChunk struct {
	Choices []struct {
		Delta struct {
			Content string `json:"content"`
		} `json:"delta"`
	} `json:"choices"`
}

func main() {
	// 配置
	url := "http://localhost:11434/v1/chat/completions"
	apiKey := "ollama"

	// 第一次对话
	message1 := Message{Role: "user", Content: "请问北京有哪些著名的旅游景点？"}
	request1 := ChatRequest{
		Model:    "deepseek-r1:14b",
		Messages: []Message{message1},
		Stream:   true,
	}

	// 发送第一次请求
	resp1, err := sendRequest(url, apiKey, request1)
	if err != nil {
		fmt.Printf("第一次请求失败: %v\n", err)
		return
	}
	defer resp1.Body.Close()

	// 处理第一次响应
	fmt.Print("第一轮会话: ")
	assistantResponse := ""
	scanner := bufio.NewScanner(resp1.Body)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "data: ") {
			data := strings.TrimPrefix(line, "data: ")
			if data == "[DONE]" {
				break
			}
			var chunk StreamChunk
			if err := json.Unmarshal([]byte(data), &chunk); err == nil {
				content := chunk.Choices[0].Delta.Content
				fmt.Print(content)
				assistantResponse += content
			}
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Printf("读取流失败: %v\n", err)
		return
	}

	// 第二次对话，携带历史
	messages := []Message{
		{Role: "user", Content: "请问北京有哪些著名的旅游景点？"},
		{Role: "assistant", Content: assistantResponse},
		{Role: "user", Content: "在这些景点中，哪个最适合春天去游玩？"},
	}
	request2 := ChatRequest{
		Model:    "deepseek-r1:14b",
		Messages: messages,
		Stream:   true,
	}

	// 发送第二次请求
	resp2, err := sendRequest(url, apiKey, request2)
	if err != nil {
		fmt.Printf("第二次请求失败: %v\n", err)
		return
	}
	defer resp2.Body.Close()

	// 处理第二次响应
	fmt.Print("\n第二轮会话: ")
	scanner = bufio.NewScanner(resp2.Body)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "data: ") {
			data := strings.TrimPrefix(line, "data: ")
			if data == "[DONE]" {
				break
			}
			var chunk StreamChunk
			if err := json.Unmarshal([]byte(data), &chunk); err == nil {
				content := chunk.Choices[0].Delta.Content
				fmt.Print(content)
			}
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Printf("读取流失败: %v\n", err)
		return
	}

	fmt.Println() // 换行
}

func sendRequest(url, apiKey string, request ChatRequest) (*http.Response, error) {
	// 构造请求体
	reqBody, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}

	// 创建 HTTP 请求
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	// 发送请求
	client := &http.Client{}
	return client.Do(req)
}
