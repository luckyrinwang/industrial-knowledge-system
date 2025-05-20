from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

class File(db.Model):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 文档、表格、PDF、图片、视频
    file_format = Column(String(10), nullable=False)  # 文件扩展名：docx, xlsx, pdf, jpg, mp4等
    file_path = Column(String(255), nullable=False)  # 存储路径
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    description = Column(Text)  # 文件描述
    is_deleted = Column(Boolean, default=False)  # 标记文件是否被删除
    pdf_path = Column(String(255), nullable=True)  # 文档类文件转换后的PDF路径
    md_path = Column(String(255), nullable=True)  # PDF转md后的Markdown文件路径
    images_dir = Column(String(255), nullable=True)  # PDF转md后图片保存目录
    ragflow_doc_id = Column(String(255), nullable=True)  # RAGFlow文档ID
    
    # 外键关联上传用户
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='uploaded_files')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, filename, original_filename, file_type, file_format, file_path, file_size, user_id, description=None, pdf_path=None, md_path=None, images_dir=None, ragflow_doc_id=None):
        self.filename = filename
        self.original_filename = original_filename
        self.file_type = file_type
        self.file_format = file_format
        self.file_path = file_path
        self.file_size = file_size
        self.user_id = user_id
        self.description = description
        self.is_deleted = False
        self.pdf_path = pdf_path
        self.md_path = md_path
        self.images_dir = images_dir
        self.ragflow_doc_id = ragflow_doc_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_format': self.file_format,
            'file_size': self.file_size,
            'description': self.description,
            'user_id': self.user_id,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'pdf_path': self.pdf_path,
            'md_path': self.md_path,
            'images_dir': self.images_dir,
            'ragflow_doc_id': self.ragflow_doc_id
        }