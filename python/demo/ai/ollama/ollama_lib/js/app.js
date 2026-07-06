import http from 'http';

// 创建一个 Web 服务器
const server = http.createServer((req, res) => {
    res.statusCode = 200;  // 设置状态码
    res.setHeader('Content-Type', 'text/plain');  // 设置响应头
    res.end('Hello, Node.js!');  // 发送响应
});

// 服务器监听端口 3000
server.listen(3000, '127.0.0.1', () => {
    console.log('Server is running at http://127.0.0.1:3000/');
});
