# RAGFlow文档删除功能实现说明

## 功能概述

本次实现了在删除doc/docx/pdf文件时，自动从RAGFlow知识库中删除对应文档的功能。当用户删除系统中的文件时，系统会查找该文件是否有关联的RAGFlow文档ID（`ragflow_doc_id`字段），如果有，则调用RAGFlow API删除对应的文档。

## 实现细节

1. **新增RAGFlowClient方法**:
   - 在`ragflow_utils.py`中添加了`delete_document`和`delete_documents`方法
   - `delete_document`方法是对`delete_documents`的单文档封装，保持向后兼容性
   - `delete_documents`方法支持批量删除多个文档，遵循RAGFlow API规范

2. **更新文件删除功能**:
   - 修改`file.py`中的`delete_file`函数，添加RAGFlow文档删除逻辑
   - 将`ragflow_doc_id`字段设为`None`，防止重复删除

3. **添加批量删除功能**:
   - 新增`batch-delete`路由，支持一次删除多个文件及其对应的RAGFlow文档
   - 实现了优化的批量删除逻辑，先收集所有需要删除的文档ID，再一次性调用API删除
   - 返回详细的删除结果，包括成功和失败的情况

4. **添加测试脚本**:
   - 创建`test_ragflow_doc_deletion.py`测试脚本，用于验证单文档删除功能
   - 创建`test_batch_delete.py`测试脚本，用于验证批量文档删除功能
   - 创建对应的批处理脚本，方便在Windows环境下运行测试

5. **更新文档**:
   - 更新`RAGFLOW_GUIDE.md`，添加关于文档删除功能的详细说明
   - 添加故障排查和API参考信息

## 功能使用

### 单文件删除

当用户通过API删除文件时，系统会自动处理以下操作：

1. 检查文件是否存在RAGFlow文档ID
2. 如果存在，调用RAGFlow API删除对应文档
3. 删除系统中的物理文件和相关资源
4. 将文件标记为已删除（软删除）
5. 清除`ragflow_doc_id`字段

### 批量删除

用户可以通过`POST /api/files/batch-delete`接口批量删除文件：

```json
{
  "file_ids": [1, 2, 3, 4]
}
```

系统会返回每个文件的处理结果：

```json
{
  "message": "批量删除完成: 3个成功, 1个失败",
  "results": {
    "success": [
      {
        "file_id": 1,
        "original_filename": "文档1.docx",
        "ragflow_result": {"status": "success", "message": "文档删除成功"}
      },
      ...
    ],
    "failed": [
      {
        "file_id": 4,
        "error": "文件不存在"
      }
    ]
  }
}
```

## 测试验证

可以通过以下方式测试功能是否正常工作：

1. 运行`test_ragflow_deletion.bat`或直接执行`python test_ragflow_doc_deletion.py`
2. 通过API接口测试文件删除功能
3. 检查RAGFlow知识库，确认文档已被删除

## 注意事项

1. 文件删除是软删除，仅将`is_deleted`字段设为`True`
2. RAGFlow文档删除是永久性的，无法恢复
3. 如果RAGFlow API调用失败，文件仍会被标记为已删除
4. 系统会记录RAGFlow文档删除的操作日志
