"""
RAGFlow知识库工具模块
提供与RAGFlow知识库的连接和操作功能
"""
import os
import json
import base64
from typing import List, Dict, Optional, Union, Any
import sys

# 包装requests导入，确保系统在缺少依赖时不会立即崩溃
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("警告: 缺少requests库，RAGFlow功能将不可用。请运行 pip install requests 安装.")

class RAGFlowClient:
    """RAGFlow客户端类，用于连接和操作RAGFlow知识库"""
    
    def __init__(self, api_url: str, api_key: str, dataset_id: str):
        """
        初始化RAGFlow客户端
        
        Args:
            api_url: RAGFlow API的URL地址
            api_key: RAGFlow API的访问密钥
            dataset_id: 要操作的知识库ID
        """
        self.api_url = api_url.rstrip('/')  # 移除URL末尾可能的斜杠
        self.api_key = api_key
        self.dataset_id = dataset_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _check_requests_available(self) -> bool:
        """检查requests库是否可用"""
        if not REQUESTS_AVAILABLE:
            print("错误: 缺少requests库，无法执行RAGFlow操作。请运行 pip install requests 安装.")
            return False
        return True
        
    def test_connection(self) -> Dict:
        """测试与RAGFlow API的连接"""
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
            
        try:
            # 尝试获取知识库信息作为连接测试
            response = requests.get(
                f"{self.api_url}/api/v1/datasets/{self.dataset_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "成功连接到RAGFlow知识库",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"连接失败: {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"连接异常: {str(e)}",
                "error": str(e)
            }
            
    def upload_document(self, file_path: str, display_name: Optional[str] = None, auto_parse: bool = False, 
                  chunk_method: str = None, parser_config: Dict = None) -> Dict:
        """
        上传文档到RAGFlow知识库
        
        Args:
            file_path: 本地文件路径
            display_name: 显示名称，默认使用文件名
            auto_parse: 是否在上传后自动解析文档
            chunk_method: 文档解析方法，可选值：
                'naive'(通用), 'manual'(手动), 'qa'(问答), 'table'(表格),
                'paper'(论文), 'book'(图书), 'laws'(法律), 'presentation'(演示文稿),
                'picture'(图片), 'one'(单文件), 'email'(邮件)
            parser_config: 解析配置参数
            
        Returns:
            包含上传结果的字典
        """
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
            
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"文件不存在: {file_path}"}
            
        display_name = display_name or os.path.basename(file_path)
        
        try:
            # 创建认证头部，不包含Content-Type（让requests自动设置）
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 准备文件上传
            mime_type = self._get_mime_type(file_path)
            files = [
                ('file', (display_name, open(file_path, 'rb'), mime_type))
            ]
            
            # 发送上传请求
            response = requests.post(
                f"{self.api_url}/api/v1/datasets/{self.dataset_id}/documents",
                headers=headers,
                files=files
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # 检查API响应内容是否包含错误信息
                # 先检查顶层结构
                if (isinstance(response_data, dict) and response_data.get('code') and 
                    (response_data.get('code') != 0 or 'error' in response_data.get('message', '').lower() or 
                     'no file' in response_data.get('message', '').lower())):
                    return {
                        "status": "error",
                        "message": f"上传失败: {response_data.get('message', '未知错误')}",
                        "data": response_data
                    }
                # 检查嵌套在data中的错误
                if isinstance(response_data, dict) and isinstance(response_data.get('data'), dict) and response_data['data'].get('code'):
                    error_code = response_data['data'].get('code')
                    error_message = response_data['data'].get('message', '未知错误')
                    if error_code != 0 and error_code != '0':
                        return {
                            "status": "error",
                            "message": f"上传失败: {error_message}",
                            "data": response_data
                        }
                
                # 如果需要自动解析文档
                if auto_parse and 'data' in response_data and isinstance(response_data['data'], list) and len(response_data['data']) > 0:
                    document_ids = [doc['id'] for doc in response_data['data']]
                    parse_result = self.parse_documents(
                        document_ids,
                        chunk_method=chunk_method,
                        parser_config=parser_config
                    )
                    
                    # 添加解析状态到返回结果
                    response_data['parse_result'] = parse_result
                    
                return {
                    "status": "success",
                    "message": f"文件 {display_name} 上传成功" + (" 并已开始解析" if auto_parse else ""),
                    "data": response_data
                }
            else:
                return {
                    "status": "error",
                    "message": f"上传失败: {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"上传异常: {str(e)}",
                "error": str(e)
            }
        finally:
            # 确保文件句柄被关闭
            if 'files' in locals():
                for _, (_, file_obj, _) in files:
                    try:
                        if hasattr(file_obj, 'close'):
                            file_obj.close()
                    except:
                        pass
                        
    def _get_mime_type(self, file_path: str) -> str:
        """根据文件扩展名获取MIME类型"""
        extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'md': 'text/markdown',
            'html': 'text/html',
            'htm': 'text/html',
            'json': 'application/json',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'csv': 'text/csv',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    def list_documents(self, page: int = 1, page_size: int = 30) -> Dict:
        """
        列出知识库中的文档
        
        Args:
            page: 页码，从1开始
            page_size: 每页显示的文档数量
            
        Returns:
            包含文档列表的字典
        """
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
            
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/datasets/{self.dataset_id}/documents",
                headers=self.headers,
                params={"page": page, "page_size": page_size}
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "获取文档列表成功",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"获取文档列表失败: {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取文档列表异常: {str(e)}",
                "error": str(e)
            }
            
    def search_knowledge(self, query: str, top_n: int = 5) -> Dict:
        """
        在知识库中搜索内容
        
        Args:
            query: 搜索查询
            top_n: 返回的最大结果数量
            
        Returns:
            包含搜索结果的字典
        """
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
            
        try:
            # 使用检索API
            response = requests.post(
                f"{self.api_url}/api/v1/search_engine/{self.dataset_id}",
                headers=self.headers,
                json={
                    "query": query,
                    "top_n": top_n
                }
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "搜索成功",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"搜索失败: {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索异常: {str(e)}",
                "error": str(e)
            }
            
    def ask_question(self, question: str, top_n: int = 5) -> Dict:
        """
        向知识库提问
        
        Args:
            question: 问题内容
            top_n: 用于生成答案的上下文数量
            
        Returns:
            包含回答结果的字典
        """
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
            
        try:
            # 先使用检索API获取相关内容
            search_response = requests.post(
                f"{self.api_url}/api/v1/search_engine/{self.dataset_id}",
                headers=self.headers,
                json={
                    "query": question,
                    "top_n": top_n
                }
            )
            
            if search_response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"检索失败: {search_response.status_code}",
                    "error": search_response.text
                }
                
            search_data = search_response.json()
            
            # 获取检索到的内容
            contexts = []
            for item in search_data.get("documents", []):
                contexts.append({
                    "content": item.get("content", ""),
                    "document_id": item.get("document_id", ""),
                    "document_name": item.get("document_name", "")
                })
            
            # 使用聊天API生成回答
            chat_response = requests.post(
                f"{self.api_url}/api/v1/chat_engine/{self.dataset_id}",
                headers=self.headers,
                json={
                    "query": question,
                    "search_context": contexts
                }
            )
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                return {
                    "status": "success",
                    "message": "提问成功",
                    "data": {
                        "answer": chat_data.get("content", ""),
                        "references": chat_data.get("reference", [])
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": f"提问失败: {chat_response.status_code}",
                    "error": chat_response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"提问异常: {str(e)}",
                "error": str(e)
            }
            
    def sync_file(self, file_path: str, original_filename: str, auto_parse: bool = False,
                chunk_method: str = None, parser_config: Dict = None) -> Dict:
        """
        将文件同步到RAGFlow知识库
        
        Args:
            file_path: 文件的本地路径
            original_filename: 原始文件名(用于显示)
            auto_parse: 是否在上传后自动解析文档
            chunk_method: 文档解析方法
            parser_config: 解析配置参数
            
        Returns:
            包含同步结果的字典
        """
        return self.upload_document(
            file_path, 
            original_filename, 
            auto_parse=auto_parse,
            chunk_method=chunk_method,
            parser_config=parser_config
        )

    def get_configuration_status(self) -> Dict:
        """
        获取RAGFlow配置状态
        
        Returns:
            配置状态信息
        """
        connection_test = self.test_connection()
        return {
            "status": connection_test["status"],
            "is_configured": connection_test["status"] == "success",
            "api_url": self.api_url,
            "dataset_id": self.dataset_id,
            "message": connection_test["message"]
        }

    def parse_documents(self, document_ids: List[str], chunk_method: str = None, parser_config: Dict = None) -> Dict:
        """
        解析文档，将文档处理为知识块
        
        Args:
            document_ids: 要解析的文档ID列表
            chunk_method: 文档解析方法，可选值：
                'naive'(通用), 'manual'(手动), 'qa'(问答), 'table'(表格),
                'paper'(论文), 'book'(图书), 'laws'(法律), 'presentation'(演示文稿),
                'picture'(图片), 'one'(单文件), 'email'(邮件)
            parser_config: 解析配置参数，根据chunk_method不同而变化
                
        Returns:
            包含解析结果的字典
        """
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
            
        if not document_ids:
            return {"status": "error", "message": "文档ID列表不能为空"}
        
        # 如果提供了解析方法和配置，先更新文档设置
        if chunk_method or parser_config:
            update_results = []
            for doc_id in document_ids:
                update_result = self.update_document_config(
                    doc_id, 
                    chunk_method=chunk_method, 
                    parser_config=parser_config
                )
                update_results.append(update_result)
                
            # 检查配置更新是否有错误
            has_error = any(result.get("status") == "error" for result in update_results)
            if has_error:
                return {
                    "status": "error",
                    "message": "部分或全部文档配置更新失败，请检查日志",
                    "update_results": update_results
                }
            
        try:
            # 调用解析API
            response = requests.post(
                f"{self.api_url}/api/v1/datasets/{self.dataset_id}/chunks",
                headers=self.headers,
                json={"document_ids": document_ids}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # 检查API响应内容是否包含错误信息
                if isinstance(response_data, dict) and response_data.get('code'):
                    if response_data.get('code') != 0:
                        return {
                            "status": "error",
                            "message": f"解析失败: {response_data.get('message', '未知错误')}",
                            "data": response_data
                        }
                    
                return {
                    "status": "success",
                    "message": f"已开始解析 {len(document_ids)} 个文档",
                    "data": response_data
                }
            else:
                return {
                    "status": "error",
                    "message": f"解析文档请求失败: {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"解析文档异常: {str(e)}",
                "error": str(e)
            }
            
    def update_document_config(self, document_id: str, name: str = None, 
                              meta_fields: Dict = None, chunk_method: str = None, 
                              parser_config: Dict = None) -> Dict:
        """
        更新文档配置
        
        Args:
            document_id: 文档ID
            name: 文档名称，可选
            meta_fields: 元数据字段，可选
            chunk_method: 解析方法，可选值：
                'naive'(通用), 'manual'(手动), 'qa'(问答), 'table'(表格),
                'paper'(论文), 'book'(图书), 'laws'(法律), 'presentation'(演示文稿),
                'picture'(图片), 'one'(单文件), 'email'(邮件)
            parser_config: 解析配置，根据chunk_method提供相应参数
                
        Returns:
            包含更新结果的字典
        """
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
            
        if not document_id:
            return {"status": "error", "message": "文档ID不能为空"}
            
        try:
            # 准备更新数据
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if meta_fields is not None:
                update_data["meta_fields"] = meta_fields
            if chunk_method is not None:
                update_data["chunk_method"] = chunk_method
            if parser_config is not None:
                update_data["parser_config"] = parser_config
                
            if not update_data:
                return {
                    "status": "warning",
                    "message": "没有提供任何更新参数",
                    "document_id": document_id
                }
                
            # 调用更新API
            response = requests.put(
                f"{self.api_url}/api/v1/datasets/{self.dataset_id}/documents/{document_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # 检查API响应内容是否包含错误信息
                if isinstance(response_data, dict) and response_data.get('code'):
                    if response_data.get('code') != 0:
                        return {
                            "status": "error",
                            "message": f"更新文档配置失败: {response_data.get('message', '未知错误')}",
                            "document_id": document_id,
                            "data": response_data
                        }
                    
                return {
                    "status": "success",
                    "message": f"文档配置更新成功",
                    "document_id": document_id,
                    "data": response_data
                }
            else:
                return {
                    "status": "error",
                    "message": f"更新文档配置请求失败: {response.status_code}",
                    "document_id": document_id,
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"更新文档配置异常: {str(e)}",
                "document_id": document_id,
                "error": str(e)
            }
    def delete_document(self, document_id: str) -> Dict:
        """
        从RAGFlow知识库中删除单个文档
        
        Args:
            document_id: 要删除的文档ID
            
        Returns:
            包含删除结果的字典
        """
        return self.delete_documents([document_id])
            
    def delete_documents(self, document_ids: List[str] = None) -> Dict:
        """
        从RAGFlow知识库中批量删除文档
        
        Args:
            document_ids: 要删除的文档ID列表。如果为None，则删除知识库中的所有文档。
            
        Returns:
            包含删除结果的字典
        """
        if not self._check_requests_available():
            return {
                "status": "error",
                "message": "缺少requests库，请使用 pip install requests 安装",
                "error": "ModuleNotFoundError: No module named 'requests'"
            }
        
        try:
            # 调用删除API
            url = f"{self.api_url}/api/v1/datasets/{self.dataset_id}/documents"
            
            # 如果指定了文档ID列表，则添加到请求体中
            data = {}
            if document_ids:
                data = {"ids": document_ids}
            
            response = requests.delete(
                url,
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # 检查API响应内容是否包含错误信息
                if isinstance(response_data, dict) and response_data.get('code'):
                    if response_data.get('code') != 0:
                        return {
                            "status": "error",
                            "message": f"删除文档失败: {response_data.get('message', '未知错误')}",
                            "document_ids": document_ids,
                            "data": response_data
                        }
                    
                return {
                    "status": "success",
                    "message": f"文档删除成功",
                    "document_ids": document_ids,
                    "data": response_data
                }
            else:
                return {
                    "status": "error",
                    "message": f"删除文档请求失败: {response.status_code}",
                    "document_ids": document_ids,
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"删除文档异常: {str(e)}",
                "document_ids": document_ids,
                "error": str(e)
            }
            
# 从环境变量创建默认客户端实例
try:
    from flask import current_app
    
    # 创建默认RAGFlow客户端工厂函数
    def get_default_client():
        """获取默认RAGFlow客户端"""
        # 尝试从Flask应用配置获取
        try:
            import os
            from flask import current_app
            # 使用Flask应用配置
            return RAGFlowClient(
                api_url=current_app.config.get('RAGFLOW_API_URL', os.getenv('RAGFLOW_API_URL', 'http://52.183.67.209:6002')),
                api_key=current_app.config.get('RAGFLOW_API_KEY', os.getenv('RAGFLOW_API_KEY', 'ragflow-k3YjY5Y2IwMWMxZjExZjA4ZDUwMmVjOT')),
                dataset_id=current_app.config.get('RAGFLOW_DATASET_ID', os.getenv('RAGFLOW_DATASET_ID', 'ddd4765c32ab11f0a1620ac4a9677486'))
            )
        except:
            # 非Flask上下文环境下，使用环境变量
            import os
            from dotenv import load_dotenv
            
            # 加载环境变量
            try:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.env')
                load_dotenv(config_path)
            except:
                pass
                
            return RAGFlowClient(
                api_url=os.getenv('RAGFLOW_API_URL', 'http://52.183.67.209:6002'),
                api_key=os.getenv('RAGFLOW_API_KEY', 'ragflow-k3YjY5Y2IwMWMxZjExZjA4ZDUwMmVjOT'),
                dataset_id=os.getenv('RAGFLOW_DATASET_ID', 'ddd4765c32ab11f0a1620ac4a9677486')
            )
    
    # 创建默认客户端实例
    default_client = get_default_client()
    
except Exception as e:
    # 非Flask环境或出现异常，使用硬编码默认值
    print(f"初始化RAGFlow客户端时出错: {str(e)}")
    default_client = RAGFlowClient(
        api_url="http://52.183.67.209:6002",
        api_key="ragflow-k3YjY5Y2IwMWMxZjExZjA4ZDUwMmVjOT",
        dataset_id="ddd4765c32ab11f0a1620ac4a9677486"
    )

# 测试函数
def test_ragflow_connection():
    """测试RAGFlow连接"""
    result = default_client.test_connection()
    print("测试RAGFlow连接结果:", json.dumps(result, ensure_ascii=False, indent=2))
    return result

def test_list_documents():
    """测试获取文档列表"""
    result = default_client.list_documents(page=1, page_size=5)
    print("获取RAGFlow文档列表结果:", json.dumps(result, ensure_ascii=False, indent=2))
    return result

def test_search_knowledge(query="工业知识"):
    """测试搜索知识"""
    result = default_client.search_knowledge(query, top_n=3)
    print(f"搜索知识结果 (查询: '{query}'):", json.dumps(result, ensure_ascii=False, indent=2))
    return result

def test_ask_question(question="什么是工业4.0?"):
    """测试提问"""
    result = default_client.ask_question(question)
    print(f"提问结果 (问题: '{question}'):", json.dumps(result, ensure_ascii=False, indent=2))
    return result

# 如果作为主程序运行，执行测试
if __name__ == "__main__":
    print("\n===== 测试RAGFlow工具 =====\n")
    
    # 测试连接
    connection_result = test_ragflow_connection()
    
    if connection_result.get("status") == "success":
        print("\n连接成功，继续执行其他测试...\n")
        
        # 测试获取文档列表
        test_list_documents()
        
        # 测试搜索知识
        test_search_knowledge()
        
        # 测试提问
        test_ask_question()
    else:
        print("\n连接失败，请检查API配置...\n")
