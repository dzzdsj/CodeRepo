
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

// EmbeddingRequest 定义嵌入请求结构
type EmbeddingRequest struct {
	Model string `json:"model"`
	Input string `json:"input"`
}

// EmbeddingResponse 定义嵌入响应结构
type EmbeddingResponse struct {
	Data []struct {
		Embedding []float64 `json:"embedding"`
	} `json:"data"`
}

func main() {
	// 配置
	url := "http://localhost:11434/v1/embeddings"
	apiKey := "ollama"

	// 输入文本
	text := "这是一个测试句子，用于生成文本向量。"

	// 构造请求
	request := EmbeddingRequest{
		Model: "bge-m3", // 使用支持嵌入的模型
		Input: text,     // 输入单个字符串
	}

	// 发送 HTTP 请求
	reqBody, err := json.Marshal(request)
	if err != nil {
		fmt.Printf("请求编码失败: %v\n", err)
		return
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(reqBody))
	if err != nil {
		fmt.Printf("创建请求失败: %v\n", err)
		return
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("发送请求失败: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// 读取和解析响应
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("读取响应失败: %v\n", err)
		return
	}

	var response EmbeddingResponse
	err = json.Unmarshal(body, &response)
	if err != nil {
		fmt.Printf("解析响应失败: %v\n", err)
		return
	}

	// 获取生成的向量
	embedding := response.Data[0].Embedding

	// 打印向量的前几个值和长度
	fmt.Println("生成的文本向量（前5个值）：", embedding[:5])
	fmt.Println("向量长度：", len(embedding))
}
