/**
 * 文件工具函数
 */

// 文件类型扩展名映射
export const ALLOWED_EXTENSIONS = {
  document: ['doc', 'docx'],
  spreadsheet: ['xls', 'xlsx'],
  pdf: ['pdf'],
  image: ['jpg', 'jpeg', 'png', 'gif'],
  video: ['mp4', 'avi', 'mkv']
};

// 文件类型中文标签
export const FILE_TYPE_LABELS = {
  document: '文档',
  spreadsheet: '表格',
  pdf: 'PDF',
  image: '图片',
  video: '视频'
};

// 文件类型MIME映射
export const MIME_TYPES = {
  // 图片
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  png: 'image/png',
  gif: 'image/gif',
  // 视频
  mp4: 'video/mp4',
  avi: 'video/x-msvideo',
  mkv: 'video/x-matroska',
  // PDF
  pdf: 'application/pdf',
  // 文档 (仅用于识别，不能直接预览)
  doc: 'application/msword',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  // 表格 (仅用于识别，不能直接预览)
  xls: 'application/vnd.ms-excel',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
};

/**
 * 获取文件扩展名
 * @param {string} filename 文件名
 * @returns {string} 文件扩展名（小写）
 */
export function getFileExtension(filename) {
  return filename.slice(filename.lastIndexOf('.') + 1).toLowerCase();
}

/**
 * 检查文件是否允许上传
 * @param {string} filename 文件名
 * @param {string} fileType 文件类型
 * @returns {boolean} 是否允许上传
 */
export function isAllowedFile(filename, fileType) {
  const extension = getFileExtension(filename);
  return ALLOWED_EXTENSIONS[fileType]?.includes(extension) || false;
}

/**
 * 根据文件扩展名获取文件类型
 * @param {string} filename 文件名
 * @returns {string|null} 文件类型
 */
export function getFileTypeByExtension(filename) {
  const extension = getFileExtension(filename);
  for (const [type, extensions] of Object.entries(ALLOWED_EXTENSIONS)) {
    if (extensions.includes(extension)) {
      return type;
    }
  }
  return null;
}

/**
 * 获取文件类型中文标签
 * @param {string} fileType 文件类型
 * @returns {string} 中文标签
 */
export function getFileTypeLabel(fileType) {
  return FILE_TYPE_LABELS[fileType] || fileType;
}

/**
 * 获取文件格式的MIME类型
 * @param {string} format 文件格式/扩展名
 * @returns {string|null} MIME类型
 */
export function getMimeType(format) {
  return MIME_TYPES[format.toLowerCase()] || null;
}

/**
 * 格式化文件大小
 * @param {number} bytes 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 格式化日期
 * @param {string} dateString 日期字符串
 * @returns {string} 格式化后的日期
 */
export function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

/**
 * 检查文件大小是否超出限制
 * @param {number} fileSize 文件大小（字节）
 * @param {number} maxSize 最大文件大小（字节），默认100MB
 * @returns {boolean} 是否超出限制
 */
export function isFileSizeExceeded(fileSize, maxSize = 100 * 1024 * 1024) {
  return fileSize > maxSize;
} 