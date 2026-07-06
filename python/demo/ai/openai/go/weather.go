
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

// 定义消息结构，与 OpenAI API 的消息格式兼容
type Message struct {
	Role       string     `json:"role"`
	Content    string     `json:"content"`
	ToolCalls  []ToolCall `json:"tool_calls,omitempty"`   // 添加工具调用字段
	ToolCallID string     `json:"tool_call_id,omitempty"` // 添加工具调用 ID
	Name       string     `json:"name,omitempty"`         // 添加工具名称
}

// 定义工具结构，与 OpenAI Function Calling 兼容
type Tool struct {
	Type     string       `json:"type"`
	Function ToolFunction `json:"function"`
}

type ToolFunction struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
}

// 定义工具调用结构
type ToolCall struct {
	ID       string           `json:"id"`
	Type     string           `json:"type"`
	Function ToolFunctionCall `json:"function"`
}

type ToolFunctionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

// 定义 ChatCompletion 请求结构
type ChatCompletionRequest struct {
	Model      string    `json:"model"`
	Messages   []Message `json:"messages"`
	Tools      []Tool    `json:"tools,omitempty"`
	ToolChoice string    `json:"tool_choice,omitempty"`
	Stream     bool      `json:"stream"`
}

// 定义 ChatCompletion 响应结构
type ChatCompletionResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
}

// 模拟的天气数据
var weatherData = map[string]map[string]string{
	"Tokyo":    {"temperature": "10°C", "conditions": "Cloudy"},
	"London":   {"temperature": "5°C", "conditions": "Rainy"},
	"New York": {"temperature": "0°C", "conditions": "Snowy"},
}

// getWeather 工具函数
func getWeather(location string) map[string]interface{} {
	fmt.Println(location)
	if data, exists := weatherData[location]; exists {
		return map[string]interface{}{
			"temperature": data["temperature"],
			"conditions":  data["conditions"],
		}
	}
	return map[string]interface{}{
		"error": "Location not found",
	}
}

// 发送 HTTP POST 请求到 Ollama API
func sendRequest(url string, apiKey string, request ChatCompletionRequest) (ChatCompletionResponse, error) {
	// 将请求体编码为 JSON
	reqBody, err := json.Marshal(request)
	if err != nil {
		return ChatCompletionResponse{}, err
	}

	// 创建 HTTP 请求
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(reqBody))
	if err != nil {
		return ChatCompletionResponse{}, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return ChatCompletionResponse{}, err
	}
	defer resp.Body.Close()

	// 读取响应
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return ChatCompletionResponse{}, err
	}

	// 解析响应
	var response ChatCompletionResponse
	err = json.Unmarshal(body, &response)
	if err != nil {
		return ChatCompletionResponse{}, err
	}

	return response, nil
}

func main() {
	// 配置
	baseURL := "http://192.168.31.208:11434/v1/chat/completions"
	apiKey := "ollama"
	model := "qwen2.5:0.5b"

	// 定义工具列表
	tools := []Tool{
		{
			Type: "function",
			Function: ToolFunction{
				Name:        "get_weather",
				Description: "获取指定地点的天气信息，将指定地点转换为英文，首字母大写",
				Parameters: map[string]interface{}{
					"type": "object",
					"properties": map[string]interface{}{
						"location": map[string]interface{}{
							"type":        "string",
							"description": "需要查询天气的地点 (城市名称)，需要转换为英文，首字母大写",
						},
					},
					"required": []string{"location"},
				},
			},
		},
	}

	// 用户输入
	userMessage := "今天东京天气怎么样？"

	// 第一次请求
	request := ChatCompletionRequest{
		Model:      model,
		Messages:   []Message{{Role: "user", Content: userMessage}},
		Tools:      tools,
		ToolChoice: "auto",
		Stream:     false,
	}

	response, err := sendRequest(baseURL, apiKey, request)
	if err != nil {
		fmt.Printf("第一次请求失败: %v\n", err)
		return
	}

	// 检查工具调用
	message := response.Choices[0].Message
	if len(message.ToolCalls) > 0 {
		toolCall := message.ToolCalls[0]
		toolName := toolCall.Function.Name

		// 解析工具参数
		var toolArguments map[string]string
		err := json.Unmarshal([]byte(toolCall.Function.Arguments), &toolArguments)
		if err != nil {
			fmt.Printf("解析工具参数失败: %v\n", err)
			return
		}

		if toolName == "get_weather" {
			// 调用工具函数
			weatherInfo := getWeather(toolArguments["location"])

			// 第二次请求，将工具结果反馈给模型
			toolResponseRequest := ChatCompletionRequest{
				Model: model,
				Messages: []Message{
					{Role: "user", Content: userMessage},
					{
						Role:      "assistant",
						Content:   message.Content,
						ToolCalls: message.ToolCalls, // 包含工具调用信息
					},
					{
						Role:       "tool",
						Content:    string(mustMarshal(weatherInfo)),
						ToolCallID: toolCall.ID,
						Name:       toolName,
					},
				},
				Tools:      tools,
				ToolChoice: "auto",
				Stream:     false,
			}

			toolResponse, err := sendRequest(baseURL, apiKey, toolResponseRequest)
			if err != nil {
				fmt.Printf("第二次请求失败: %v\n", err)
				return
			}

			finalResponse := toolResponse.Choices[0].Message.Content
			fmt.Printf("最终回复: %s\n", finalResponse)
		}
	} else {
		fmt.Printf("模型回复: %s\n", message.Content)
	}
}

// 辅助函数：将数据转为 JSON 字节数组
func mustMarshal(data interface{}) []byte {
	bytes, err := json.Marshal(data)
	if err != nil {
		panic(err)
	}
	return bytes
}
