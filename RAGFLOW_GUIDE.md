# RAGFlow知识库集成

本文档介绍了工业知识库系统与RAGFlow知识库的集成方案和使用方法。

## 功能概述

通过集成RAGFlow知识库，工业知识库系统增加了以下功能：

1. **文档自动同步** - 系统上传的文档可自动同步到RAGFlow知识库中
2. **智能搜索** - 基于语义的文档内容搜索，返回最相关的文档片段
3. **智能问答** - 提问并获取基于知识库内容的AI回答

## 配置说明

RAGFlow知识库的配置参数存储在 `backend/config.env` 文件中：

```
# RAGFlow知识库配置
RAGFLOW_API_URL=http://52.183.67.209:6002
RAGFLOW_API_KEY=ragflow-k3YjY5Y2IwMWMxZjExZjA4ZDUwMmVjOT
RAGFLOW_DATASET_ID=ddd4765c32ab11f0a1620ac4a9677486
RAGFLOW_AUTO_SYNC=True
```

参数说明：
- `RAGFLOW_API_URL` - RAGFlow API服务器地址
- `RAGFLOW_API_KEY` - 访问RAGFlow API的密钥
- `RAGFLOW_DATASET_ID` - 要使用的知识库ID
- `RAGFLOW_AUTO_SYNC` - 是否自动同步上传的文件到知识库

## API端点

集成后系统新增以下API端点：

### 1. 测试连接
- 端点: `/api/ragflow/test-connection`
- 方法: GET
- 描述: 测试与RAGFlow知识库的连接状态
- 权限要求: `knowledge_base_view`

### 2. 搜索知识
- 端点: `/api/ragflow/search`
- 方法: POST
- 描述: 在知识库中进行语义搜索
- 权限要求: `knowledge_base_view`
- 请求参数:
  ```json
  {
    "query": "搜索关键词",
    "top_n": 5
  }
  ```

### 3. 问答
- 端点: `/api/ragflow/ask`
- 方法: POST
- 描述: 向知识库提问并获取回答
- 权限要求: `knowledge_base_view`
- 请求参数:
  ```json
  {
    "question": "你的问题",
    "stream": false
  }
  ```

### 4. 获取文档列表
- 端点: `/api/ragflow/documents`
- 方法: GET
- 描述: 获取知识库中的文档列表
- 权限要求: `knowledge_base_view`
- 查询参数:
  - `page`: 页码 (默认: 1)
  - `page_size`: 每页数量 (默认: 30)

### 5. 上传状态
- 端点: `/api/ragflow/upload-status`
- 方法: GET
- 描述: 获取文件同步状态
- 权限要求: `knowledge_base_upload`

## 使用方法

### 前端集成

在前端可以通过以下方式调用RAGFlow知识库功能：

```javascript
// 搜索知识库
async function searchKnowledge(query) {
  const response = await fetch('/api/ragflow/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${yourToken}`
    },
    body: JSON.stringify({ query, top_n: 5 })
  });
  return await response.json();
}

// 提问
async function askQuestion(question) {
  const response = await fetch('/api/ragflow/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${yourToken}`
    },
    body: JSON.stringify({ question, stream: false })
  });
  return await response.json();
}
```

### 后端集成

在后端Python代码中可以直接使用RAGFlow工具类：

```python
from utils.ragflow_utils import default_client

# 测试连接
connection_status = default_client.test_connection()

# 搜索知识
search_results = default_client.search_knowledge("工业自动化", top_n=5)

# 提问
answer = default_client.ask_question("工业4.0的核心技术有哪些?")

# 同步文件到知识库（启用自动解析）
sync_result = default_client.upload_document(
    "/path/to/file.md", 
    "文件原始名称.md",
    auto_parse=True,
    chunk_method="naive",
    parser_config={"chunk_size": 1000, "chunk_overlap": 100}
)
```

## 故障排查

如果RAGFlow功能无法正常工作，请检查：

1. 确保RAGFlow API服务器正常运行
2. 验证API密钥和知识库ID是否正确
3. 检查网络连接是否可以访问RAGFlow服务
4. 查看应用日志中是否有RAGFlow相关的错误

可以使用测试脚本验证RAGFlow连接:

```
python backend/test_ragflow.py
```

## 权限说明

RAGFlow功能需要以下权限：

- `knowledge_base_view` - 允许查看、搜索和提问知识库
- `knowledge_base_upload` - 允许向知识库上传文档

## 未来计划

1. 增加流式回答支持
2. 添加知识库管理页面
3. 实现多知识库支持
4. 改进搜索结果相关性排序
