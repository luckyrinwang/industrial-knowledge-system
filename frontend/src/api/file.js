import request from '@/utils/request'

/**
 * 获取文件列表
 * @param {number} page 页码
 * @param {number} perPage 每页数量
 * @param {string} fileType 文件类型筛选
 * @param {string} searchQuery 搜索关键词
 * @returns {Promise} 文件列表
 */
export function getFiles(page = 1, perPage = 20, fileType = null, searchQuery = null) {
  const params = { page, per_page: perPage, debug: 1 }
  
  if (fileType) {
    params.file_type = fileType
  }
  
  if (searchQuery) {
    params.search = searchQuery
  }
  console.log('调用获取文件API, 参数:', params);
  
  // 修改URL格式，确保与后端和Nginx配置匹配 - 使用带斜杠的形式
  const url = '/files/';
  console.log('请求URL:', url);
  return request({
    url: url,
    method: 'get',
    params
  })
}

/**
 * 获取单个文件详情
 * @param {number} fileId 文件ID
 * @returns {Promise} 文件详情
 */
export function getFile(fileId) {
  return request({
    url: `/files/${fileId}`,
    method: 'get'
  })
}

/**
 * 上传单个文件
 * @param {FormData} formData 包含文件和描述的表单数据
 * @returns {Promise} 上传结果
 */
export function uploadFile(formData) {
  console.log('调用上传单个文件API', {
    文件名: formData.get('file') ? formData.get('file').name : '未知',
    类型: formData.get('file_type'),
    描述: formData.get('description') || '无'
  });
  
  return request({
    url: '/files/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 批量上传文件
 * @param {FormData} formData 包含多个文件和描述的表单数据
 * @returns {Promise} 上传结果
 */
export function batchUploadFiles(formData) {
  // 获取表单中的所有文件信息
  const files = formData.getAll('files');
  const fileType = formData.get('file_type');
  const descriptions = formData.getAll('descriptions');
  
  console.log('调用批量上传文件API', {
    文件数量: files.length,
    文件类型: fileType,
    描述数量: descriptions.length,
    文件列表: files.map(file => file.name)
  });
  
  return request({
    url: '/files/batch-upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除文件
 * @param {number} fileId 文件ID
 * @returns {Promise} 删除结果
 */
export function deleteFile(fileId) {
  console.log(`调用删除文件API, ID: ${fileId}`);
  
  return request({
    url: `/files/${fileId}`,
    method: 'delete'
  })
}

/**
 * 批量删除文件
 * @param {Array} fileIds 文件ID数组
 * @param {string} deleteStrategy 删除策略 (可选): 'soft'软删除, 'hard'硬删除, 'type'按类型删除
 * @returns {Promise} 删除结果
 */
export function batchDeleteFiles(fileIds, deleteStrategy = 'type') {
  console.log('调用批量删除API', { fileIds, deleteStrategy });
  return request({
    url: '/files/batch-delete',
    method: 'post',
    data: {
      file_ids: fileIds,
      delete_strategy: deleteStrategy
    }
  })
}

/**
 * 获取文件下载URL
 * @param {number} fileId 文件ID
 * @returns {string} 下载URL
 */
export function getFileDownloadUrl(fileId) {
  return `/files/download/${fileId}`
}

/**
 * 获取文件预览URL
 * @param {number} fileId 文件ID
 * @returns {string} 预览URL
 */
export function getFilePreviewUrl(fileId) {
  return `/files/preview/${fileId}`
}