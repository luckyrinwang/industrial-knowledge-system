# RAGFlow知识库集成说明

## 概述

系统集成了RAGFlow知识库服务，支持文档的自动上传和解析，可用于构建基于知识的智能问答系统。

## 功能特点

1. **文档自动上传**: 系统支持将上传的文档（特别是经过转换的PDF和Markdown）自动同步到RAGFlow知识库。
2. **文档自动解析**: 上传到RAGFlow的文档可以自动解析为知识块，便于检索和问答。
3. **解析配置自定义**: 支持通过环境变量或API调用自定义文档解析方法和配置参数。
4. **环境变量配置**: 通过环境变量可以灵活配置RAGFlow的连接和功能启用状态。

## 配置说明

在`config.env`文件中配置以下环境变量：

```
# RAGFlow配置
RAGFLOW_API_URL=http://your-ragflow-url:port
RAGFLOW_API_KEY=your-api-key
RAGFLOW_DATASET_ID=your-dataset-id
RAGFLOW_AUTO_SYNC=True
RAGFLOW_AUTO_PARSE=True
RAGFLOW_CHUNK_METHOD=naive
RAGFLOW_PARSER_CONFIG={"chunk_size": 1000, "chunk_overlap": 100}
```

各配置项说明：

- `RAGFLOW_API_URL`: RAGFlow API的URL地址
- `RAGFLOW_API_KEY`: RAGFlow API的访问密钥
- `RAGFLOW_DATASET_ID`: 要使用的知识库ID
- `RAGFLOW_AUTO_SYNC`: 是否自动同步文档到RAGFlow（True/False）
- `RAGFLOW_AUTO_PARSE`: 是否在同步文档后自动解析（True/False）
- `RAGFLOW_CHUNK_METHOD`: 文档解析方法，可选值：
  - `naive`: 通用解析（默认）
  - `manual`: 手动解析
  - `qa`: 问答解析
  - `table`: 表格解析
  - `paper`: 论文解析
  - `book`: 图书解析
  - `laws`: 法律文档解析
  - `presentation`: 演示文稿解析
  - `picture`: 图片解析
  - `one`: 单文件解析
  - `email`: 邮件解析
- `RAGFLOW_PARSER_CONFIG`: 解析配置参数（JSON格式），各解析方法的参数不同

### 常用解析配置示例

1. **通用解析(naive)配置**:
```json
{
  "chunk_token_count": 256,
  "layout_recognize": true,
  "html4excel": false,
  "delimiter": "\n",
  "task_page_size": 12,
  "raptor": {"use_raptor": false}
}
```

2. **问答解析(qa)配置**:
```json
{
  "raptor": {"use_raptor": true}
}
```

3. **图书解析(book)配置**:
```json
{
  "raptor": {"use_raptor": false}
}
```

## 使用说明

系统会在以下情况自动同步并解析文档：

1. 上传文档类型（doc, docx）文件时，会将转换后的Markdown自动同步到RAGFlow
2. 上传PDF文件时，会将解析后的Markdown自动同步到RAGFlow

如果`RAGFLOW_AUTO_PARSE`设置为`True`，则上传的文档会被自动解析成知识块，便于后续检索和问答。

## 数据存储

系统会在文件上传到RAGFlow知识库后，将返回的文档ID存储在数据库中：

1. **文档ID存储**: 上传文档到RAGFlow后，系统会将返回的文档ID存储在数据库的`files`表的`ragflow_doc_id`字段中
2. **文档ID用途**: 存储的文档ID可用于后续操作，如：
   - 查询文档解析状态
   - 更新文档配置
   - 删除知识库中的文档
   - 执行特定文档的问答操作

## 文档删除机制

系统实现了文件删除与RAGFlow知识库文档同步删除的功能：

1. **单文件删除**: 当删除系统中的文档类型(doc/docx)或PDF文件时，系统会自动：
   - 删除物理存储的原始文件
   - 删除关联的PDF文件(如果有)
   - 删除关联的Markdown文件和图片(如果有)
   - 从RAGFlow知识库中删除对应的文档(使用存储的`ragflow_doc_id`)
   - 记录删除操作日志

2. **批量删除**: 系统支持批量删除文件及其在RAGFlow中的对应文档：
   - API接口: `POST /api/files/batch-delete`
   - 请求格式: `{"file_ids": [1, 2, 3, ...]}`
   - 响应包含每个文件的删除结果
   - 优化批量删除: 当多个文件同时删除时，系统会收集所有RAGFlow文档ID，并通过一次API调用批量删除，提高效率

3. **删除流程**:
   - 检查文件是否存在`ragflow_doc_id`
   - 调用RAGFlow API删除知识库中的文档
   - 删除本地存储的相关文件
   - 更新数据库记录(软删除，设置`is_deleted=True`并清除`ragflow_doc_id`)

## 测试脚本

系统提供了以下测试脚本，用于验证RAGFlow的连接和功能：

1. **连接测试**: `python utils/ragflow_utils.py`
   - 测试与RAGFlow API的连接
   - 列出知识库中的文档
   - 执行示例搜索和问答

2. **解析配置测试**: `python test_ragflow_config.py`
   - 测试不同解析方法的配置参数

3. **文档解析测试**: `python test_ragflow_parse.py`
   - 测试文档上传和解析功能

4. **文档删除测试**: `python test_ragflow_doc_deletion.py`
   - 测试从RAGFlow知识库中删除文档的功能
   - 验证文件删除与RAGFlow文档删除的同步机制

5. **批量删除测试**: `python test_batch_delete.py`
   - 测试批量删除RAGFlow文档的功能
   - 验证优化的批量删除机制

6. **批处理测试脚本**: 
   - `test_ragflow_deletion.bat`: 测试单文档删除
   - `test_batch_delete.bat`: 测试批量文档删除

## 故障排查

若遇到RAGFlow集成问题，请检查以下几点：

1. **连接问题**:
   - 确认`RAGFLOW_API_URL`可访问
   - 确认`RAGFLOW_API_KEY`有效
   - 确认`RAGFLOW_DATASET_ID`存在

2. **同步失败**:
   - 检查网络连接
   - 检查`RAGFLOW_AUTO_SYNC`设置
   - 查看系统日志中的错误信息

3. **解析失败**:
   - 确认`RAGFLOW_AUTO_PARSE`设置为True
   - 检查`RAGFLOW_CHUNK_METHOD`是否适合当前文档类型
   - 查看`RAGFLOW_PARSER_CONFIG`配置是否正确

4. **删除失败**:
   - 检查`ragflow_doc_id`是否存在且正确
   - 确认文档ID在RAGFlow知识库中存在
   - 查看系统日志中的错误信息

## API参考

系统封装了以下RAGFlow API调用：

1. `test_connection()`: 测试与RAGFlow API的连接
2. `upload_document()`: 上传文档到RAGFlow知识库
3. `list_documents()`: 列出知识库中的文档
4. `search_knowledge()`: 在知识库中搜索内容
5. `delete_document()`: 删除单个文档
6. `delete_documents()`: 批量删除多个文档（优化的删除方法）
7. `ask_question()`: 向知识库提问
