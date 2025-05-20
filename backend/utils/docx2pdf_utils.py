import os
import sys
import time

if sys.platform.startswith('win'):
    import win32com.client
    import pythoncom

    def docx_to_pdf(input_path, output_path):
        """
        Windows下用Word自动将doc/docx转为pdf。
        input_path/output_path建议用绝对路径且无中文。
        """
        pythoncom.CoInitialize()  # 关键：初始化COM
        word = None
        doc = None
        
        try:
            # 确保输入路径存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
                
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            # 创建Word实例
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            
            # 打开文档并转换
            # 使用绝对路径避免路径问题
            abs_input_path = os.path.abspath(input_path)
            abs_output_path = os.path.abspath(output_path)
            
            # 输出调试信息
            print(f"尝试打开文档: {abs_input_path}")
            print(f"输出PDF路径: {abs_output_path}")
            
            # 打开文档前先等待释放资源
            time.sleep(0.5)
            
            # 直接通过Documents集合打开并操作
            try:
                doc = word.Documents.Open(abs_input_path)
                
                if doc is None:
                    raise RuntimeError("无法打开文档")
                    
                # 使用正确的SaveAs方法及参数
                time.sleep(0.5)  # 给Word一些处理时间
                
                # Word中PDF格式的常量值为17
                wdFormatPDF = 17
                doc.SaveAs(FileName=abs_output_path, FileFormat=wdFormatPDF)
                
                # 确保保存完成后再关闭
                time.sleep(0.5)
                doc.Close(SaveChanges=False)
                doc = None
                
                # 确保文件已经生成
                retry_count = 0
                while not os.path.exists(abs_output_path) and retry_count < 3:
                    time.sleep(0.5)
                    retry_count += 1
                    
                if not os.path.exists(abs_output_path):
                    raise FileNotFoundError(f"PDF文件未能生成: {abs_output_path}")
            except Exception as e:
                print(f"文档处理过程中出错: {str(e)}")
                raise
                
            return True
        except Exception as e:
            print(f"Word转PDF异常: {str(e)}")
            raise RuntimeError(f"Word转PDF失败: {str(e)}")
        finally:
            # 确保资源正确释放
            try:
                if doc is not None:
                    try:
                        doc.Close(SaveChanges=False)
                    except Exception as e:
                        print(f"关闭文档时出错: {str(e)}")
                    doc = None
            except Exception as e:
                print(f"处理文档对象时出错: {str(e)}")
                
            try:
                if word is not None:
                    try:
                        word.Quit()
                    except Exception as e:
                        print(f"退出Word时出错: {str(e)}")
                    word = None
            except Exception as e:
                print(f"处理Word对象时出错: {str(e)}")
            
            # 强制执行一次垃圾回收
            import gc
            gc.collect()
            
            # 等待一会儿确保资源释放
            time.sleep(0.5)
            
            # 释放COM
            try:
                pythoncom.CoUninitialize()
            except Exception as e:
                print(f"COM资源释放时出错: {str(e)}")
else:
    import subprocess

    def docx_to_pdf(input_path, output_path):
        """
        Linux下用unoconv+LibreOffice将doc/docx转为pdf。
        """
        try:
            # 确保输入路径存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
                
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            # 使用绝对路径
            abs_input_path = os.path.abspath(input_path)
            abs_output_path = os.path.abspath(output_path)
            
            # 执行转换
            subprocess.check_call([
                'unoconv', '-f', 'pdf', '-o', abs_output_path, abs_input_path
            ])
            
            # 确保文件已经生成
            if not os.path.exists(abs_output_path):
                raise FileNotFoundError(f"PDF文件未能生成: {abs_output_path}")
                
            return True
        except Exception as e:
            raise RuntimeError(f"unoconv转换失败: {str(e)}")
