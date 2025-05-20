from flask import Blueprint, send_from_directory, jsonify, current_app, request
import os
from models.file import File

# 创建蓝图 - 注意这个蓝图不需要@jwt_required装饰器
public_files_bp = Blueprint('public_files', __name__)

@public_files_bp.route('/file-info/<int:file_id>', methods=['GET'])
def get_file_md_info(file_id):
    """
    获取文件的MD信息和相关的图片路径
    """
    try:
        # 从数据库查询文件
        file = File.query.get(file_id)
        
        if not file:
            return jsonify({'message': '文件不存在'}), 404
            
        # 如果文件被标记为删除，也返回不存在
        if file.is_deleted:
            return jsonify({'message': '文件已被删除'}), 404
            
        # 检查文件是否有MD和图片目录
        if not file.md_path:
            return jsonify({'message': '该文件没有对应的MD文件'}), 404
              # 提取MD文件名(不包含路径)
        md_filename = os.path.basename(file.md_path)
        md_url = f"{request.host_url.rstrip('/')}/public/md/{md_filename}"        # 构建图片目录信息
        images = []
        if file.images_dir:
            # 从images_dir获取MD ID（应该是文件名去掉.md）
            md_id = os.path.basename(file.md_path).rsplit('.', 1)[0]
            
            # 获取images_dir的绝对路径 - 图片实际存储在uploads/md/md_id目录
            images_dir_abs = os.path.join(current_app.config['UPLOAD_FOLDER'], 'md', md_id)
            
            # 如果图片目录存在，列出所有图片
            if os.path.exists(images_dir_abs) and os.path.isdir(images_dir_abs):
                for img_file in os.listdir(images_dir_abs):
                    # 只处理图片文件
                    if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                        # 直接从根路径构建URL
                        img_url = f"{request.host_url.rstrip('/')}/public/{md_id}/{img_file}"
                        images.append({
                            'filename': img_file,
                            'url': img_url
                        })
        
        return jsonify({
            'file_id': file.id,
            'original_filename': file.original_filename,
            'md_filename': md_filename,
            'md_url': md_url,
            'images': images
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取文件信息失败: {str(e)}'}), 500

@public_files_bp.route('/md/<path:md_filename>', methods=['GET'])
def get_md_file(md_filename):
    """
    获取MD文件内容，公开访问，无需身份验证
    """
    try:
        # md文件路径是：uploads/md/md文件名
        md_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'md')
        
        # 检查文件是否存在
        md_file_path = os.path.join(md_dir, md_filename)
        if not os.path.exists(md_file_path):
            return jsonify({'message': 'MD文件不存在'}), 404
        
        # 发送文件
        return send_from_directory(
            md_dir, 
            md_filename,
            mimetype='text/markdown'
        )
    except Exception as e:
        return jsonify({'message': f'获取MD文件失败: {str(e)}'}), 500

@public_files_bp.route('/images/<md_id>/<path:image_name>', methods=['GET'])
def get_md_image(md_id, image_name):
    """
    获取MD文件关联的图片，公开访问，无需身份验证
    图片路径格式为: md_id/image_name
    其中md_id是文件夹名称（对应于md文件的ID）
    """
    try:
        # 图片路径是：uploads/md/md_id/image_name
        # 例如: uploads/md/06e05c0062e84e0698fa7153aec85831/0fecec8d903d7d4d9199da35b4370d27e80bb2ec2e9eeb932d47941b91c8f895.jpg
        images_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'md', md_id)
        
        # 检查图片文件是否存在
        full_path = os.path.join(images_dir, image_name)
        if not os.path.exists(full_path):
            return jsonify({'message': '图片文件不存在'}), 404
        
        # 根据图片扩展名设置正确的MIME类型
        extension = image_name.split('.')[-1].lower()
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(extension, 'application/octet-stream')
        
        # 发送图片文件
        return send_from_directory(
            images_dir,
            image_name,
            mimetype=content_type
        )
    except Exception as e:
        return jsonify({'message': f'获取图片文件失败: {str(e)}'}), 500

@public_files_bp.route('/image/<path:image_path>', methods=['GET'])
def get_direct_image(image_path):
    """
    直接获取图片，公开访问，无需身份验证
    图片路径格式为: image_path (完整的相对路径)
    """
    try:
        # 获取文件名和目录路径
        filename = os.path.basename(image_path)
        directory = os.path.dirname(image_path)
        
        # 构建完整路径 - 这里我们假设image_path是相对于uploads目录的路径
        dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], directory)
        
        # 检查目录和文件是否存在
        full_path = os.path.join(dir_path, filename)
        if not os.path.exists(full_path):
            # 尝试直接在md目录下查找
            alt_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'md', image_path)
            if os.path.exists(alt_path):
                # 如果图片在md目录下找到了
                dir_path = os.path.dirname(alt_path)
                filename = os.path.basename(alt_path)
            else:
                return jsonify({'message': '图片文件不存在'}), 404
        
        # 根据图片扩展名设置正确的MIME类型
        extension = filename.split('.')[-1].lower()
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(extension, 'application/octet-stream')
        
        # 发送图片文件
        return send_from_directory(
            dir_path,
            filename,
            mimetype=content_type
        )
    except Exception as e:
        import traceback
        print(f"获取图片文件失败: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'获取图片文件失败: {str(e)}'}), 500

@public_files_bp.route('/<md_id>/<path:image_name>', methods=['GET'])
def get_root_image(md_id, image_name):
    """
    直接从根路径获取图片，公开访问，无需身份验证
    图片路径格式为: /{md_id}/{image_name}
    """
    try:
        # 图片路径是：uploads/md/md_id/image_name
        images_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'md', md_id)
        
        # 检查图片文件是否存在
        full_path = os.path.join(images_dir, image_name)
        if not os.path.exists(full_path):
            return jsonify({'message': '图片文件不存在'}), 404
        
        # 根据图片扩展名设置正确的MIME类型
        extension = image_name.split('.')[-1].lower()
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(extension, 'application/octet-stream')
        
        # 发送图片文件
        return send_from_directory(
            images_dir,
            image_name,
            mimetype=content_type
        )
    except Exception as e:
        import traceback
        print(f"获取图片文件失败: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'获取图片文件失败: {str(e)}'}), 500
