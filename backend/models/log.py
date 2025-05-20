from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

class OperationLog(db.Model):
    __tablename__ = 'operation_logs'

    id = Column(Integer, primary_key=True)
    operation_type = Column(String(20), nullable=False)  # 操作类型：create, read, update, delete
    operation_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(50))  # 操作者IP地址
    details = Column(Text)  # 操作详情，可以存储JSON格式的额外信息
    
    # 冗余存储文件信息，防止文件删除后无法显示
    file_name = Column(String(255))  # 文件名
    file_type = Column(String(50))   # 文件类型
    
    # 外键关联用户
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='operations')
    
    # 外键关联文件
    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship('File', backref='operations')
    
    def __init__(self, operation_type, user_id, file_id, ip_address=None, details=None, file_name=None, file_type=None):
        self.operation_type = operation_type
        self.user_id = user_id
        self.file_id = file_id
        self.ip_address = ip_address
        self.details = details
        self.file_name = file_name
        self.file_type = file_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'operation_type': self.operation_type,
            'operation_time': self.operation_time.isoformat() if self.operation_time else None,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'ip_address': self.ip_address,
            'details': self.details
        } 