# 解决Docker构建中的PIP超时问题

这个文档提供了解决在Docker中构建时遇到的pip超时问题的方法。

## 错误说明

在使用Docker构建基于大模型的工业知识库系统时，可能会遇到以下错误：

```
ERROR: Exception:
Traceback (most recent call last):
  ...
socket.timeout: The read operation timed out
```

这通常是由以下原因导致的：
1. 网络连接不稳定
2. PyPI服务器响应慢
3. 防火墙或网络策略限制
4. 代理服务器配置不正确

## 解决方案

### 方案1：使用更新的Dockerfile

已经提供了一个优化版的Dockerfile.backend文件，它采用以下措施：

- 设置更长的pip超时时间
- 使用多个可靠的PyPI镜像源
- 添加重试机制

使用方法：
```bash
docker-compose up -d
```

### 方案2：使用国内镜像源进行构建

使用修改版的docker-compose文件：
```bash
docker-compose -f docker-compose.timeout-fix.yml up -d
```

### 方案3：预下载依赖包（离线安装）

1. 首先运行预下载脚本：
```bash
# Linux
chmod +x prepare_pip_cache.sh
./prepare_pip_cache.sh

# Windows
prepare_pip_cache.bat
```

2. 使用离线安装的Dockerfile：
```bash
docker build -t industrial-knowledge-backend -f Dockerfile.backend.offline .
```

3. 或者使用docker-compose：
```bash
# 修改docker-compose.yml中的backend服务使用Dockerfile.backend.offline
docker-compose up -d
```

### 方案4：使用代理

如果你有访问代理服务器：

```bash
# 设置环境变量
export http_proxy=http://your-proxy:port
export https_proxy=http://your-proxy:port

# 然后构建
docker-compose up -d
```

## 预防措施

1. 使用代理服务器
2. 使用更快的PyPI镜像源
3. 增加网络超时时间
4. 定期预下载依赖包到本地
