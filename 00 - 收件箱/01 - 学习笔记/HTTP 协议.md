---
date: 2025-11-21
tags:
  - 学习笔记
---
# HTTP 协议概览

**HTTP (Hyper Text Transfer Protocol)**，即超文本传输协议，是互联网上应用最为广泛的一种网络协议
- **基础架构**：HTTP 是建立在 **TCP/IP** 协议之上的应用层协议。这意味着它继承了 TCP 的可靠性（不丢失数据），主要用于传输 HTML 文件、图片、查询结果等超文本数据。
- **工作模式**：典型的 **C/S (Client-Server)** 架构。
    - **客户端 (User Agent)**：通常是浏览器，也可以是爬虫、移动 App 或任何发起请求的实体。
    - **服务端**：处理请求并返回响应（Response）。
    - **中间实体**：在客户端和服务器之间，可能存在网关 (Gateways)、缓存 (Caches) 或代理 (Proxies) 等中间节点，用于转发或处理流量。
- 核心特点
	1. **简单快速**
		- **原理**：通信格式简单（纯文本）。客户端请求时只需传送**请求方法**（如 GET、POST）和**路径**。
		- **优势**：协议解析成本低，服务器程序规模小，通信效率高。
	2. **灵活**
		- **多媒体支持**：HTTP 允许传输任意类型的数据对象（文本、视频、二进制流）
		- **实现方式**：通过头部字段 `Content-Type` 标记数据类型（MIME Type），例如 `text/html` 或 `image/jpeg`。
	- **无连接**
		- **原始定义**：HTTP 每次连接只处理一个请求。服务器处理完并发送应答后，立即断开 TCP 连接，以节省服务器套接字资源。
	    - **解释 (Keep-Alive)**：
		    - 虽然 HTTP 协议本身被定义为无连接，但频繁建立/断开 TCP 连接（三次握手/四次挥手）开销很大。
		    - **HTTP/1.1** 默认开启了 `Connection: keep-alive`，允许在同一个 TCP 连接上发送多个 HTTP 请求，这是对“无连接”特性的重要优化。
	- **无状态** (Stateless)
		- **定义**：HTTP 协议不对请求和响应之间的通信状态进行保存。服务器记不住你上一次请求了什么，每个请求都是独立的
![](images/HTTP%20协议/file-20251121090756522.jpg)
		- **痛点**：无法实现连续交互（如购物车、用户登录状态）。
		- **解决方案 (Cookie/Session)**
			- 使用扩展头部 **HTTP Cookies**
			- 服务器在响应中下发 Cookie，客户端在后续请求中自动携带 Cookie，从而在“无状态”的协议上建立了“有状态”的会话上下文
# HTTP 报文结构
HTTP 通信本质上是 TCP 数据段的封装与拆解。报文分为**请求报文**和**响应报文**，它们都遵循严格的 ASCII 格式规范。
## 报文通用结构
所有 HTTP 报文都由以下四部分组成：
1. **起始行 (Start Line)**：请求行或状态行。
2. **头部字段 (Headers)**：键值对形式，每行以 `\r\n` 结束。
3. **空行 (Empty Line)**：即单独的 `\r\n`，**非常重要**，用于分隔头部和包体。
4. **包体 (Body)**：实际传输的数据（可为空）。
## 典型请求报文
```http
GET /repo/boa-0.100.9.tgz HTTP/1.1    <-- 请求行 (方法 URL 版本)
Range: bytes=0-                       <-- 头部字段
Host: www.boa.org                     <-- 头部字段
\r\n                                  <-- 空行 (必须存在)
(此处为空包体)
```

- **请求行**：包含请求方法、URL 和协议版本，以 `\r\n` 结束。
    ![](images/HTTP%20协议/file-20251121091014238.jpg)
### 典型响应报文 (Response)
```http
HTTP/1.1 206 Partial Content          <-- 状态行 (版本 状态码 描述)
Server: nginx                         <-- 头部字段
Content-Type: application/x-xz        <-- 头部字段
Content-Length: 2889                  <-- 头部字段
\r\n                                  <-- 空行
(二进制文件数据...)                    <-- 响应包体
```

- **状态行**：包含协议版本、状态码和状态描述
# 请求方法与 URL
## 常见请求方法
虽然 HTTP 定义了很多方法，但由服务器决定支持哪些。
- **GET**：获取资源。参数通常拼接在 URL 后面，适合查询。
- **POST**：提交数据（如表单）。数据包含在**包体**中，相对 GET 更安全且无长度限制。
- **HEAD**：类似于 GET，但**只返回头部**，不返回包体。常用于检测文件是否存在或获取文件大小 (`Content-Length`)。
- **PUT**：上传或修改资源。
## URL 与 协议版本
- **URL (统一资源定位符)**：`协议://域名:端口/路径`。例如 `https://cdn.kernel.org/...`。
- **协议版本**：
    - **HTTP/1.0** (1996)：确立了基本标准。
    - **HTTP/1.1** (1997)：当前最主流版本，支持持久连接、分块传输等。
    - **HTTP/2.0**：二进制分帧，多路复用，主要用于 HTTPS。
        
## 关键头部字段 (Request)
- **Host**：**HTTP/1.1 唯一强制要求的字段**，指定目标主机名（解决虚拟主机问题）。
- **Accept**: 告诉服务器客户端能处理什么数据类型。
- **Range**: 实现**断点续传**的核心。
    - `bytes=0-`：请求全文。
    - `bytes=-1000`：请求最后 1000 字节。
    - `bytes=100-`：从第 100 字节开始请求。
# 响应状态与传输机制

## 状态码 (Status Codes)
状态码是服务器处理结果的数字化表达：
- **1xx**：通知/提示信息。
- **2xx (成功)**：
    - `200 OK`：请求正常处理。
    - `206 Partial Content`：范围请求成功（对应 Range 请求，如下载工具）。
- **3xx (重定向)**：
    - `301 Moved Permanently`：永久移动。
    - `302/307`：临时重定向。
- **4xx (客户端错误)**：
    - `400 Bad Request`：请求报文语法错误。
    - `403 Forbidden`：有权限但被禁止访问。
    - `404 Not Found`：资源不存在。
- **5xx (服务端错误)**：
    - `500 Internal Server Error`：服务器内部炸了。
    - `503 Service Unavailable`：服务器超载或维护。
## 传输方式：定长 vs 分块
服务器如何告诉客户端“数据传完了”？主要有两种方式：
1. **Content-Length (定长)**
    - 在发送数据前，服务器已知数据总大小。
    - 头部包含 `Content-Length: 2889`。
    - 客户端读取指定长度后认为传输结束。
2. **Transfer-Encoding: chunked (分块/流式)**
    - **场景**：服务器产生动态数据（如 ChatGPT 的回复），无法预知总大小。
    - **机制**：
        - 不发送 Content-Length。
        - 数据被拆分成若干块 (Chunk)。
        - 每块格式：`16进制长度\r\n数据\r\n`。
        - **结束标志**：长度为 0 的块 (`0\r\n\r\n`)。
            

---

# 代码示例
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h> // for gethostbyname

// 简单的 URL 编码函数 (针对中文等非 ASCII 字符)
// 实际项目中建议使用成熟的库
void url_encode(const char *src, char *dest, int dest_len) {
    char *hex = "0123456789ABCDEF";
    int pos = 0;
    for (int i = 0; src[i] != '\0' && pos < dest_len - 3; i++) {
        // 仅对非字母数字进行编码 (简化版逻辑)
        if (src[i] == ' ' || (unsigned char)src[i] > 127) {
            dest[pos++] = '%';
            dest[pos++] = hex[((unsigned char)src[i] >> 4) & 0xF];
            dest[pos++] = hex[((unsigned char)src[i]) & 0xF];
        } else {
            dest[pos++] = src[i];
        }
    }
    dest[pos] = '\0';
}

int connect_server(char* host) {
    // 1. DNS 解析：通过域名获取 IP
    // 注意：gethostbyname 已过时，现代编程推荐 getaddrinfo，但此处沿用原文逻辑
    struct hostent* p = gethostbyname(host);
    if (p == NULL) {
        perror("DNS 解析失败 (get host error)");
        return -1;
    }

    // 2. 提取 IP 地址
    char server_ip[32] = {0};
    inet_ntop(AF_INET, p->h_addr_list[0], server_ip, sizeof(server_ip));
    printf("[INFO] 服务器域名: %s 解析 IP: %s\n", host, server_ip);

    // 3. 创建 TCP 套接字
    int tcp_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (tcp_socket == -1) {
        perror("Socket 创建失败");
        return -1;
    }

    // 4. 设置服务器地址结构体
    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(80); // HTTP 默认端口 80
    server_addr.sin_addr.s_addr = inet_addr(server_ip);

    // 5. 发起连接 (三次握手)
    if (connect(tcp_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) != 0) {
        perror("连接服务器失败");
        close(tcp_socket);
        return -1;
    }

    printf("[INFO] 连接服务器成功\n");
    return tcp_socket;
}

int main() {
    char *host = "api.qingyunke.com";
    int fd_server = connect_server(host);
    if (fd_server < 0) return 1;

    // --- 构建 HTTP 请求 ---
    
    // 1. 对中文参数进行 URL 编码
    char msg_raw[] = "你好啊";
    char msg_encoded[64] = {0};
    url_encode(msg_raw, msg_encoded, sizeof(msg_encoded));

    // 2. 拼接 HTTP 请求报文
    // 格式：GET [path] HTTP/1.1\r\nHost: [host]\r\n\r\n
    char request[1024];
    snprintf(request, sizeof(request), 
             "GET /api.php?key=free&appid=0&msg=%s HTTP/1.1\r\n"
             "Host: %s\r\n"
             "User-Agent: C-Client\r\n" // 良好的习惯是带上 UA
             "Connection: close\r\n"    // 告诉服务器发完就关，简化处理
             "\r\n",                    // 空行，表示头部结束
             msg_encoded, host);

    printf("[INFO] 发送请求报文:\n%s\n----------------------\n", request);

    // 3. 发送请求
    if (write(fd_server, request, strlen(request)) <= 0) {
        perror("发送失败");
        close(fd_server);
        return 1;
    }

    // 4. 接收响应
    char server_buf[4096];
    int retVal;
    int total_bytes = 0;
    
    printf("[INFO] 接收响应内容:\n");
    while (1) {
        bzero(server_buf, sizeof(server_buf));
        retVal = read(fd_server, server_buf, sizeof(server_buf) - 1);
        
        if (retVal < 0) {
            perror("读取错误");
            break;
        }
        if (retVal == 0) { // 服务器关闭连接 (EOF)
            break;
        }
        
        printf("%s", server_buf);
        total_bytes += retVal;
    }
    
    printf("\n\n[INFO] 数据接收完毕，共 %d 字节\n", total_bytes);

    // 5. 关闭连接 (四次挥手)
    close(fd_server);
    return 0;
}
```

### 6.2 代码逻辑分析

1. **DNS 解析**：HTTP 基于 IP 通信，必须先用 `gethostbyname` 将域名转换为 IP。
    
2. **构建请求**：
    
    - 手动拼接字符串遵循 `请求行 + 头部 + 空行` 的格式。
        
    - 这里特别处理了 `Host` 字段，这是 HTTP/1.1 协议必须的。
        
    - 添加了 `Connection: close`，这样服务器发送完数据后会主动断开连接，使得我们的 `read` 函数能通过返回 0 来判断结束，简化了长度解析逻辑。
        
3. **接收数据**：使用 `while` 循环读取，因为响应数据可能分多次到达。注意，实际的 HTTP 客户端还需要解析头部中的 `Content-Length` 或处理 `Chunked` 编码来精确控制读取，上述代码简化为读取直到连接关闭。

```dataviewjs
await dv.view("90 - 系统文件/92 - 插件配置/Scripts/nav")
```