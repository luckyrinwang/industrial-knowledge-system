<template>
  <div class="file-management-container">
    <div class="page-header">
      <h2>文件管理</h2>
      <div class="header-actions">
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedFiles.length === 0">
          <el-icon><DeleteFilled /></el-icon>
          批量删除 ({{ selectedFiles.length }})
        </el-button>
        <el-button type="primary" @click="showUploadDialog">
          <el-icon><UploadFilled /></el-icon>
          上传文件
        </el-button>
      </div>
    </div>

    <!-- 文件类型筛选 -->
    <div class="filter-container">
      <el-radio-group v-model="fileTypeFilter" @change="handleFilterChange">
        <el-radio-button :value="''">全部文件</el-radio-button>
        <el-radio-button :value="'document'">文档</el-radio-button>
        <el-radio-button :value="'spreadsheet'">表格</el-radio-button>
        <el-radio-button :value="'pdf'">PDF</el-radio-button>
        <el-radio-button :value="'image'">图片</el-radio-button>
        <el-radio-button :value="'video'">视频</el-radio-button>
      </el-radio-group>
      
      <!-- 搜索框 -->
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件名或描述"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 文件列表 -->
    <el-card shadow="never" class="file-list-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="files.length === 0" class="empty-container">
        <el-empty description="暂无文件" />
      </div>
      <div v-else class="file-list">
        <div class="file-list-header">
          <el-checkbox 
            v-model="selectAll" 
            @change="handleSelectAllChange" 
            :indeterminate="isIndeterminate">
            全选
          </el-checkbox>
          <span v-if="selectedFiles.length > 0" class="selection-info">
            已选择 {{ selectedFiles.length }} 个文件
          </span>
        </div>
        <div v-for="file in files" :key="file.id" class="file-item">
          <div class="file-checkbox">
            <el-checkbox v-model="file.isSelected" @change="updateSelection"></el-checkbox>
          </div>
          <div class="file-icon file-thumb-animated">
            <img v-if="file.file_type === 'document'" src="https://img.icons8.com/color/48/000000/ms-word.png" class="file-thumb-img" alt="文档" />
            <img v-else-if="file.file_type === 'spreadsheet'" src="https://img.icons8.com/color/48/000000/ms-excel.png" class="file-thumb-img" alt="表格" />
            <img v-else-if="file.file_type === 'pdf'" src="https://img.icons8.com/color/48/000000/pdf.png" class="file-thumb-img" alt="PDF" />
            <img v-else-if="file.file_type === 'image'" src="https://img.icons8.com/color/48/000000/picture.png" class="file-thumb-img" alt="图片" />
            <img v-else-if="file.file_type === 'video'" src="https://img.icons8.com/color/48/000000/video.png" class="file-thumb-img" alt="视频" />
            <img v-else src="https://img.icons8.com/color/48/000000/file.png" class="file-thumb-img" alt="文件" />
          </div>
          <div class="file-info">
            <div class="file-name" @click="handlePreview(file)">{{ file.original_filename }}</div>
            <div class="file-description" v-if="file.description">
              <el-tooltip 
                :content="file.description" 
                placement="top" 
                :disabled="file.description.length < 50"
                :hide-after="2000"
              >
                <span>{{ truncateText(file.description, 50) }}</span>
              </el-tooltip>
            </div>
            <div class="file-meta">
              <span>{{ formatFileSize(file.file_size) }}</span>
              <span>{{ formatDate(file.created_at) }}</span>
              <span>{{ getFileTypeLabel(file.file_type) }}</span>
            </div>
          </div>
          <div class="file-actions">
            <!-- 文档类PDF预览和下载（最左侧） -->
            <el-tooltip v-if="file.file_type === 'document' && file.pdf_path" content="PDF预览" placement="top">
              <el-button circle size="small" type="success" @click="handlePdfPreview(file)">
                <el-icon><Document /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip v-if="file.file_type === 'document' && file.pdf_path" content="PDF下载" placement="top">
              <el-button circle size="small" type="info" @click="handlePdfDownload(file)">
                <el-icon><DocumentRemove /></el-icon>
              </el-button>
            </el-tooltip>
            <!-- 原始文件预览（所有类型统一样式） -->
            <el-tooltip v-if="file.file_type !== 'spreadsheet'" content="预览" placement="top">
              <el-button circle size="small" type="primary" @click="handlePreview(file)">
                <el-icon><View /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip v-if="file.file_type === 'spreadsheet'" content="预览表格" placement="top">
              <el-button circle size="small" type="primary" @click="handleSpreadsheetPreview(file)">
                <el-icon><Grid /></el-icon>
              </el-button>
            </el-tooltip>
            <!-- 原始文件下载（所有类型统一样式） -->
            <el-tooltip content="下载" placement="top">
              <el-button circle size="small" type="primary" @click="handleDownload(file)">
                <el-icon><Download /></el-icon>
              </el-button>
            </el-tooltip>
            <!-- 原始文件删除（所有类型统一样式） -->
            <el-tooltip content="删除" placement="top">
              <el-button circle size="small" type="danger" @click="handleDelete(file)">
                <el-icon><DeleteFilled /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          :current-page="currentPage"
          :page-size="pageSize"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 文件上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传文件"
      width="650px"
      destroy-on-close
      @close="resetUploadForm"
    >
      <el-form :model="uploadForm" ref="uploadFormRef" label-width="80px" :rules="uploadRules">
        <el-form-item label="文件类型" prop="fileType" required>
          <el-select v-model="uploadForm.fileType" placeholder="请选择文件类型" @change="handleFileTypeChange">
            <el-option label="文档" value="document"></el-option>
            <el-option label="表格" value="spreadsheet"></el-option>
            <el-option label="PDF" value="pdf"></el-option>
            <el-option label="图片" value="image"></el-option>
            <el-option label="视频" value="video"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="文件" prop="files" required>
          <el-upload
            ref="uploadRef"
            multiple
            :auto-upload="false"
            :limit="10"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleExceed"
            :before-upload="beforeUpload"
            :file-list="fileList"
            :accept="getAcceptFileTypes()"
            :show-file-list="true"
            :disabled="!uploadForm.fileType"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">
                <template v-if="uploadForm.fileType === 'document'">
                  支持的文件格式：doc, docx
                </template>
                <template v-else-if="uploadForm.fileType === 'spreadsheet'">
                  支持的文件格式：xls, xlsx
                </template>
                <template v-else-if="uploadForm.fileType === 'pdf'">
                  支持的文件格式：pdf
                </template>
                <template v-else-if="uploadForm.fileType === 'image'">
                  支持的文件格式：jpg, jpeg, png, gif
                </template>
                <template v-else-if="uploadForm.fileType === 'video'">
                  支持的文件格式：mp4, avi, mkv
                </template>
                <template v-else>
                  请先选择文件类型
                </template>
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- 每个文件单独描述输入框区域 -->
        <div v-if="fileList && fileList.length > 0">
          <el-divider content-position="center">
            <el-tag type="info" size="large" effect="plain">为每个文件填写描述</el-tag>
          </el-divider>
          <div
            v-for="(file, index) in fileList"
            :key="file.uid"
            class="file-description-item"
            style="margin-bottom: 12px;"
          >
            <div style="margin-bottom: 4px; color: #606266;">
              <el-icon style="vertical-align: middle;"><document /></el-icon>
              <span style="margin-left: 6px;">{{ file.name }}</span>
            </div>
            <el-input
              v-model="descriptions[index]"
              type="textarea"
              :rows="2"
              maxlength="200"
              show-word-limit
              placeholder="请输入该文件的描述（选填，最多200字）"
            ></el-input>
          </div>
        </div>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="submitUpload"
            :loading="uploading"
            :disabled="!canUpload"
          >
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewFile ? previewFile.original_filename : '文件预览'"
      width="80%"
      destroy-on-close
      class="preview-dialog"
      fullscreen
    >
      <div v-if="previewFile" class="preview-container">
        <!-- 图片预览 -->
        <div v-if="previewFile && previewFile.file_type === 'image'" class="image-preview">
          <img :src="previewUrl" :alt="previewFile ? previewFile.original_filename : ''" />
        </div>

        <!-- 文档类文件的PDF内容预览 -->
        <div v-else-if="previewFile && previewFile.file_type === 'document' && previewFile.pdf_path" class="pdf-preview">
          <iframe :src="getPdfPreviewUrl(previewFile)" width="100%" height="600"></iframe>
          <div style="margin-top: 10px; text-align: right;">
            <el-button type="info" @click="handlePdfDownload(previewFile)">
              <el-icon><DocumentRemove /></el-icon> 下载PDF
            </el-button>
          </div>
        </div>

        <!-- PDF文件预览 -->
        <div v-else-if="previewFile && previewFile.file_type === 'pdf'" class="pdf-preview">
          <iframe :src="previewUrl" width="100%" height="600"></iframe>
        </div>

        <!-- 视频预览 -->
        <div v-else-if="previewFile && previewFile.file_type === 'video'" class="video-preview">
          <video controls width="100%" height="auto">
            <source :src="previewUrl" :type="getVideoMimeType(previewFile.file_format)" />
            您的浏览器不支持视频标签
          </video>
        </div>

        <!-- 其他文件 -->
        <div v-else class="other-preview">
          <el-empty description="该文件类型不支持在线预览，请下载后查看">
            <template #extra>
              <el-button type="primary" @click="handleDownload(previewFile)">
                <el-icon><Download /></el-icon>
                下载文件
              </el-button>
            </template>
          </el-empty>
        </div>

        <!-- 文件信息 -->
        <div class="file-details" v-if="previewFile">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">
              {{ previewFile ? previewFile.original_filename : '' }}
            </el-descriptions-item>
            <el-descriptions-item label="大小">
              {{ previewFile ? formatFileSize(previewFile.file_size) : '' }}
            </el-descriptions-item>
            <el-descriptions-item label="上传时间">
              {{ previewFile ? formatDate(previewFile.created_at) : '' }}
            </el-descriptions-item>
            <el-descriptions-item label="文件类型">
              {{ previewFile ? getFileTypeLabel(previewFile.file_type) : '' }}
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ previewFile && previewFile.description ? previewFile.description : '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <!-- 表格预览对话框 -->
    <el-dialog
      v-model="sheetPreviewVisible"
      title="表格预览"
      width="80%"
      destroy-on-close
    >
      <el-table :data="sheetData" v-if="sheetHeader.length > 0">
        <el-table-column
          v-for="(col, idx) in sheetHeader"
          :key="idx"
          :label="col"
          :prop="idx"
          :formatter="(row) => row[idx]"
        />
      </el-table>
      <div v-else>表格内容为空</div>
    </el-dialog>

    <!-- 批量删除确认对话框 -->
    <el-dialog
      v-model="batchDeleteDialogVisible"
      title="批量删除文件"
      width="550px"
    >
      <div v-if="fileTypeGroups" class="batch-delete-content">
        <p class="batch-delete-info">您选择了 {{ selectedFiles.length }} 个文件，按类型分组如下：</p>
        
        <el-descriptions border :column="1">
          <el-descriptions-item 
            v-for="(files, type) in fileTypeGroups" 
            :key="type"
            :label="getFileTypeLabel(type) + ' (' + files.length + '个)'"
          >
            <div class="file-type-group">
              <div v-for="file in files" :key="file.id" class="file-type-item">
                <el-icon>
                  <Document v-if="type === 'document'" />
                  <Grid v-else-if="type === 'spreadsheet'" />
                  <DocumentRemove v-else-if="type === 'pdf'" />
                  <Picture v-else-if="type === 'image'" />
                  <VideoCamera v-else-if="type === 'video'" />
                </el-icon>
                <span class="file-name-small">{{ file.original_filename }}</span>
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <div class="delete-options">
          <p class="delete-strategy-title">删除策略：</p>
          <el-radio-group v-model="deleteStrategy">
            <el-radio label="soft">软删除（仅标记为已删除，可恢复）</el-radio>
            <el-radio label="hard">硬删除（彻底删除文件，无法恢复）</el-radio>
            <el-radio label="type">按类型删除（推荐）</el-radio>
          </el-radio-group>
          
          <div v-if="deleteStrategy === 'type'" class="delete-type-explanation">
            <p><el-tag type="info">按文件类型采用最优删除策略：</el-tag></p>
            <ul>
              <li><b>文档和PDF文件</b>：清理关联的PDF、Markdown和图片，从RAGFlow知识库移除</li>
              <li><b>表格和图片文件</b>：直接从服务器移除</li>
              <li><b>视频文件</b>：考虑文件大小，选择性地彻底删除或软删除</li>
            </ul>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchDeleteDialogVisible = false">取消</el-button>
          <el-button
            type="danger"
            @click="confirmBatchDelete"
            :loading="batchDeleting"
          >
            确认删除
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ElMessage, 
  ElMessageBox, 
  ElNotification
} from 'element-plus'
import {
  getFiles,
  getFile,
  uploadFile,
  batchUploadFiles,
  deleteFile,
  batchDeleteFiles,
  getFileDownloadUrl,
  getFilePreviewUrl
} from '@/api/file'
import * as XLSX from 'xlsx'

// 文件列表
const files = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const fileTypeFilter = ref('')
const searchQuery = ref('')
const searchTimeout = ref(null)

// 上传相关
const uploadDialogVisible = ref(false)
const uploadFormRef = ref(null)
const uploadForm = reactive({
  fileType: ''
})
const fileList = ref([])
const descriptions = ref([])
const uploading = ref(false)
const uploadRef = ref(null)

// 表单验证规则
const uploadRules = reactive({
  fileType: [
    { required: true, message: '请选择文件类型', trigger: 'change' }
  ]
})

// 计算属性：是否可以上传
const canUpload = computed(() => {
  return uploadForm.fileType && fileList.value && fileList.value.length > 0;
})

// 计算属性：是否显示文件描述区域
const showDescriptionArea = computed(() => {
  return fileList.value && fileList.value.length > 0;
})

// 预览相关
const previewDialogVisible = ref(false)
const previewFile = ref(null)
const previewUrl = ref('')

// 新增表格预览相关变量
const sheetData = ref([])
const sheetHeader = ref([])
const sheetPreviewVisible = ref(false)

// 文件选择相关
const selectedFiles = ref([])
const selectAll = ref(false)
const isIndeterminate = ref(false)
const batchDeleteDialogVisible = ref(false)
const fileTypeGroups = ref(null)
const deleteStrategy = ref('type')
const batchDeleting = ref(false)

// 文件类型对应的允许扩展名
const ALLOWED_EXTENSIONS = {
  'document': ['doc', 'docx', 'rtf'],
  'spreadsheet': ['xls', 'xlsx', 'csv'],
  'pdf': ['pdf'],
  'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
  'video': ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm']
};

/**
 * 检查文件是否为允许的类型
 * @param {string} filename 文件名
 * @param {string} fileType 文件类型分类
 * @returns {boolean} 是否允许
 */
const isAllowedFile = (filename, fileType) => {
  if (!filename || !fileType || !ALLOWED_EXTENSIONS[fileType]) {
    return false;
  }
  
  const extension = filename.split('.').pop().toLowerCase();
  return ALLOWED_EXTENSIONS[fileType].includes(extension);
};

/**
 * 检查文件大小是否超过限制
 * @param {number} size 文件大小（字节）
 * @returns {boolean} 是否超过限制
 */
const isFileSizeExceeded = (size) => {
  const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
  return size > MAX_FILE_SIZE;
};

// 初始化时加载文件列表
onMounted(() => {
  fetchFiles()
})

// 监听文件类型变化时，清空已选文件
watch(() => uploadForm.fileType, () => {
  resetFileList()
})

// 获取文件列表
async function fetchFiles() {
  loading.value = true
  console.log('开始获取文件列表', {
    page: currentPage.value,
    pageSize: pageSize.value,
    fileType: fileTypeFilter.value || null,
    searchQuery: searchQuery.value || null
  })
  try {
    const response = await getFiles(
      currentPage.value,
      pageSize.value,
      fileTypeFilter.value || null,
      searchQuery.value || null
    )
    console.log('文件列表获取成功', response)
    // 检查响应格式
    if (!response || typeof response !== 'object') {
      throw new Error('无效的响应格式')
    }
    // 给每个文件添加选中属性
    files.value = Array.isArray(response.items) ? 
      response.items.map(file => ({
        ...file,
        isSelected: false
      })) : []
    total.value = response.total || 0
    // 重置选择状态
    if (typeof updateSelection === 'function') {
      updateSelection()
    }
    // 如果没有文件，显示提示
    if (files.value.length === 0) {
      console.log('未找到任何文件')
    }
  } catch (error) {
    console.error('获取文件列表失败', error)
    if (error.response) {
      console.error('响应错误:', error.response.status, error.response.data)
    }
    ElMessage.error('获取文件列表失败: ' + (error.message || '未知错误'))
    files.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = setTimeout(() => {
    currentPage.value = 1
    fetchFiles()
  }, 500)
}

// 处理分页变化
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchFiles()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchFiles()
}

// 处理筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
  fetchFiles()
}

// 显示上传对话框
const showUploadDialog = () => {
  console.log('显示上传对话框');
  uploadDialogVisible.value = true;
  uploadForm.fileType = '';
  resetFileList();
}

// 重置文件列表
const resetFileList = () => {
  console.log('重置文件列表');
  fileList.value = [];
  descriptions.value = [];
  if (uploadRef.value) {
    uploadRef.value.clearFiles();
  }
}

// 重置上传表单
const resetUploadForm = () => {
  uploadForm.fileType = ''
  resetFileList()
  if (uploadFormRef.value) {
    uploadFormRef.value.resetFields()
  }
}

// 文件类型变更处理
const handleFileTypeChange = () => {
  resetFileList()
}

// 获取接受的文件类型字符串
const getAcceptFileTypes = () => {
  if (!uploadForm.fileType) {
    return '';
  }
  
  if (!ALLOWED_EXTENSIONS[uploadForm.fileType]) {
    return '';
  }
  return ALLOWED_EXTENSIONS[uploadForm.fileType].map(ext => `.${ext}`).join(',');
}

// 获取视频MIME类型
const getVideoMimeType = (format) => {
  const mimeTypes = {
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mkv': 'video/x-matroska',
    'mov': 'video/quicktime',
    'wmv': 'video/x-ms-wmv',
    'flv': 'video/x-flv',
    'webm': 'video/webm'
  };
  
  return mimeTypes[format?.toLowerCase()] || 'video/mp4'; // 默认使用mp4
}

// 上传前验证
const beforeUpload = (file) => {
  const fileType = uploadForm.fileType
  if (!fileType) {
    ElMessage.error('请先选择文件类型')
    return false
  }
  
  // 检查文件扩展名
  if (!isAllowedFile(file.name, fileType)) {
    ElMessage.error(`不支持的文件格式，当前选择类型为${getFileTypeLabel(fileType)}`)
    return false
  }
  
  // 检查文件大小
  if (isFileSizeExceeded(file.size)) {
    ElMessage.error('文件大小不能超过100MB')
    return false
  }
  
  return true
}

// 处理超出文件数量限制
const handleExceed = () => {
  ElMessage.warning('一次最多上传10个文件')
}

// 处理文件变化
const handleFileChange = (file, uploadedFileList) => {
  console.log('文件变化, 当前文件列表:', uploadedFileList);
  console.log('新增文件:', file);
  
  // 确保uploadedFileList是数组
  if (!Array.isArray(uploadedFileList)) {
    console.error('上传文件列表不是数组:', uploadedFileList);
    return;
  }
  
  // 更新组件的fileList
  fileList.value = [...uploadedFileList];
  
  // 重新构建descriptions数组以匹配新的fileList
  // 确保每个新增的文件都有对应的描述字段
  const newDescriptions = [];
  
  // 对于每个文件，初始化一个空描述
  uploadedFileList.forEach((file, index) => {
    // 对于新文件，添加空描述
    if (index >= descriptions.value.length) {
      newDescriptions.push('');
    } else {
      // 保留已有文件的描述
      newDescriptions.push(descriptions.value[index] || '');
    }
  });
  
  // 更新描述数组
  descriptions.value = newDescriptions;
  console.log('更新后的描述数组:', JSON.stringify(descriptions.value));
  
  // 强制更新视图
  nextTick(() => {
    console.log('视图已更新, 当前文件列表长度:', fileList.value.length);
  });
}

// 处理文件移除
const handleFileRemove = (file, uploadedFileList) => {
  console.log('文件移除:', file);
  console.log('移除后的文件列表:', uploadedFileList);
  
  // 确保uploadedFileList是数组
  if (!Array.isArray(uploadedFileList)) {
    console.error('上传文件列表不是数组:', uploadedFileList);
    fileList.value = [];
    descriptions.value = [];
    return;
  }
  
  // 更新组件的fileList，使用展开运算符创建新数组
  fileList.value = [...uploadedFileList];
  
  // 确保descriptions数组长度与新的文件列表匹配
  if (uploadedFileList.length < descriptions.value.length) {
    descriptions.value = descriptions.value.slice(0, uploadedFileList.length);
  }
  
  console.log('描述数组已更新:', descriptions.value);
  
  // 强制更新视图
  nextTick(() => {
    console.log('视图已更新, 当前文件列表长度:', fileList.value.length);
  });
}

// 提交上传
const submitUpload = async () => {
  if (!uploadForm.fileType) {
    ElMessage.error('请选择文件类型')
    return
  }
  
  if (!fileList.value || fileList.value.length === 0) {
    ElMessage.error('请选择要上传的文件')
    return
  }
  
  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file_type', uploadForm.fileType)
    
    if (fileList.value.length > 1) {
      // 批量上传多个文件，为每个文件使用对应的描述
      fileList.value.forEach((file, index) => {
        formData.append('files', file.raw || file)
        formData.append('descriptions', descriptions.value[index] || '')
      })
      const result = await batchUploadFiles(formData)
      if (result.failed_files && result.failed_files.length > 0) {
        ElMessage({
          message: `成功上传 ${result.uploaded_files.length} 个文件，${result.failed_files.length} 个文件失败`,
          type: 'warning',
          duration: 5000
        })
      } else {
        ElMessage.success(`成功上传 ${fileList.value.length} 个文件`)
      }
    } else {
      // 上传单个文件
      formData.append('file', fileList.value[0].raw || fileList.value[0])
      formData.append('description', descriptions.value[0] || '')
      await uploadFile(formData)
      ElMessage.success('文件上传成功')
    }
    uploadDialogVisible.value = false
    resetUploadForm()
    fetchFiles()
  } catch (error) {
    console.error('上传文件失败', error)
    ElMessage.error('上传文件失败: ' + (error.message || '服务器错误'))
  } finally {
    uploading.value = false
  }
}

// 工具函数：带token获取文件blob
const fetchFileWithToken = async (url) => {
  const token = localStorage.getItem('token')
  const response = await fetch(url, {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  })
  if (!response.ok) throw new Error('预览失败，权限不足或文件不存在')
  return await response.blob()
}

// 处理文件预览
const handlePreview = async (file) => {
  if (file.file_type === 'spreadsheet') {
    handleSpreadsheetPreview(file)
    return
  }
  previewFile.value = file
  // 需要token的类型：图片、pdf、视频
  if (['image', 'pdf', 'video'].includes(file.file_type)) {
    try {
      const url = getFilePreviewUrl(file.id)
      const blob = await fetchFileWithToken(url)
      previewUrl.value = window.URL.createObjectURL(blob)
    } catch (e) {
      ElMessage.error(e.message)
      previewUrl.value = ''
    }
  } else if (file.file_type === 'document' && file.pdf_path) {
    previewUrl.value = getPdfPreviewUrl(file)
  } else {
    previewUrl.value = getFilePreviewUrl(file.id)
  }
  previewDialogVisible.value = true
}

// 处理文件下载
const handleDownload = async (file) => {
  const url = getFileDownloadUrl(file.id)
  const token = localStorage.getItem('token')
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    })
    if (!response.ok) {
      throw new Error('下载失败，权限不足或文件不存在')
    }
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = file.original_filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(link.href)
  } catch (error) {
    ElMessage.error(error.message)
  }
}

// 处理文件删除
const handleDelete = (file) => {
  ElMessageBox.confirm(
    `确定要删除文件 "${file.original_filename}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        await deleteFile(file.id)
        ElMessage.success('文件删除成功')
        fetchFiles()
      } catch (error) {
        console.error('删除文件失败', error)
        ElMessage.error('删除文件失败: ' + (error.message || '服务器错误'))
      }
    })
    .catch(() => {
      // 用户取消删除
    })
}

/**
 * 截断文件名，使其在UI中更好地显示
 * @param {string} fileName 文件名
 * @param {number} maxLength 最大长度
 * @returns {string} 截断后的文件名
 */
const truncateFileName = (fileName, maxLength = 30) => {
  if (fileName.length <= maxLength) {
    return fileName;
  }
  
  const extension = fileName.slice(fileName.lastIndexOf('.'));
  const name = fileName.slice(0, fileName.lastIndexOf('.'));
  
  // 保留文件名前部分和扩展名
  const truncatedName = name.slice(0, maxLength - extension.length - 3) + '...';
  return truncatedName + extension;
}

/**
 * 截断文本，添加省略号
 * @param {string} text 文本
 * @param {number} maxLength 最大长度
 * @returns {string} 截断后的文本
 */
const truncateText = (text, maxLength = 50) => {
  if (!text || text.length <= maxLength) {
    return text;
  }
  return text.slice(0, maxLength) + '...';
}

// PDF相关方法
const getPdfPreviewUrl = (file) => {
  if (!file || !file.id) return ''
  return `/files/download-pdf/${file.id}?preview=1`
}
const getPdfDownloadUrl = getPdfPreviewUrl
const handlePdfPreview = (file) => {
  // 弹窗内直接切换为PDF预览
  previewFile.value = file
  previewUrl.value = getPdfPreviewUrl(file)
  previewDialogVisible.value = true
}
const handlePdfDownload = (file) => {
  if (!file || !file.id) return
  // 通过后端API接口下载pdf
  const url = `/files/download-pdf/${file.id}`
  const link = document.createElement('a')
  link.href = url
  link.target = '_blank'
  link.download = (file.original_filename ? file.original_filename.replace(/\.(docx|doc)$/i, '.pdf') : '文件.pdf')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 新增表格预览方法
const handleSpreadsheetPreview = async (file) => {
  const url = getFileDownloadUrl(file.id)
  const token = localStorage.getItem('token')
  const response = await fetch(url, {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  })
  const blob = await response.blob()
  const arrayBuffer = await blob.arrayBuffer()
  const workbook = XLSX.read(arrayBuffer, { type: 'array' })
  const firstSheetName = workbook.SheetNames[0]
  const worksheet = workbook.Sheets[firstSheetName]
  const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
  if (jsonData.length > 0) {
    sheetHeader.value = jsonData[0]
    sheetData.value = jsonData.slice(1)
  } else {
    sheetHeader.value = []
    sheetData.value = []
  }
  sheetPreviewVisible.value = true
}

// 文件选择相关方法
const updateSelection = () => {
  selectedFiles.value = files.value.filter(file => file.isSelected).map(file => ({
    id: file.id,
    original_filename: file.original_filename,
    file_type: file.file_type,
    file_format: file.file_format
  }))
  
  // 更新全选和半选状态
  const checkedCount = files.value.filter(file => file.isSelected).length
  selectAll.value = checkedCount === files.value.length && files.value.length > 0
  isIndeterminate.value = checkedCount > 0 && checkedCount < files.value.length
}

const handleSelectAllChange = (val) => {
  files.value.forEach(file => {
    file.isSelected = val
  })
  updateSelection()
}

// 批量删除相关方法
const handleBatchDelete = () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择要删除的文件')
    return
  }
  
  // 按文件类型分组
  fileTypeGroups.value = selectedFiles.value.reduce((groups, file) => {
    const type = file.file_type
    if (!groups[type]) {
      groups[type] = []
    }
    groups[type].push(file)
    return groups
  }, {})
  
  batchDeleteDialogVisible.value = true
}

const confirmBatchDelete = async () => {
  if (selectedFiles.value.length === 0) return
  
  batchDeleting.value = true
  try {
    const fileIds = selectedFiles.value.map(file => file.id)
    const result = await batchDeleteFiles(fileIds, deleteStrategy.value)
    
    const successCount = result.results?.success?.length || 0
    const failedCount = result.results?.failed?.length || 0
    
    if (failedCount > 0) {
      ElNotification({
        title: '批量删除结果',
        message: `成功删除 ${successCount} 个文件，${failedCount} 个文件删除失败`,
        type: 'warning',
        duration: 5000
      })
    } else {
      ElMessage.success(`成功删除 ${successCount} 个文件`)
    }
    
    batchDeleteDialogVisible.value = false
    fetchFiles() // 刷新文件列表
  } catch (error) {
    console.error('批量删除文件失败', error)
    ElMessage.error('批量删除文件失败: ' + (error.message || '服务器错误'))
  } finally {
    batchDeleting.value = false
  }
}

/**
 * 格式化文件大小显示
 * @param {number} size 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
const formatFileSize = (size) => {
  if (!size || size === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(size) / Math.log(1024));
  
  // 向下取整到两位小数
  return (size / Math.pow(1024, i)).toFixed(2) + ' ' + units[i];
};

/**
 * 格式化日期显示
 * @param {string} dateString 日期字符串
 * @returns {string} 格式化后的日期显示
 */
const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

/**
 * 获取文件类型的中文标签
 * @param {string} fileType 文件类型
 * @returns {string} 中文标签
 */
const getFileTypeLabel = (fileType) => {
  const typeMap = {
    'document': '文档',
    'spreadsheet': '表格',
    'pdf': 'PDF',
    'image': '图片',
    'video': '视频'
  };
  
  return typeMap[fileType] || '未知类型';
};

</script>

<style scoped>
.file-thumb-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(30,60,114,0.10);
  background: #f4f4f5;
  transition: transform 0.3s, box-shadow 0.3s;
}
.file-thumb-animated:hover .file-thumb-img {
  transform: scale(1.12) rotate(-4deg);
  box-shadow: 0 4px 16px #409eff33;
}
.file-management-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  width: 250px;
}

.file-list-card {
  margin-bottom: 20px;
}

.loading-container,
.empty-container {
  padding: 20px 0;
  text-align: center;
}

.file-list {
  display: flex;
  flex-direction: column;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.selection-info {
  font-size: 13px;
  color: #606266;
}

.file-item {
  display: flex;
  padding: 15px;
  border-bottom: 1px solid #eee;
  align-items: center;
  transition: background-color 0.3s;
}

.file-checkbox {
  margin-right: 10px;
}

.file-icon {
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: #f4f4f5;
  border-radius: 4px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  margin-bottom: 5px;
  cursor: pointer;
  color: #409eff;
}

.file-name:hover {
  text-decoration: underline;
}

.file-description {
  color: #606266;
  font-size: 13px;
  margin-bottom: 5px;
}

.file-meta {
  color: #909399;
  font-size: 12px;
  display: flex;
  gap: 10px;
}

.file-actions {
  display: flex;
  gap: 5px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.file-description-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s, transform 0.3s;
}

.file-description-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.file-info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.file-icon-small {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: #ecf5ff;
  border-radius: 4px;
  margin-right: 10px;
}

.file-name-badge {
  font-size: 14px;
  padding: 6px 10px;
  background-color: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: calc(100% - 42px);
  overflow: hidden;
}

.file-size-info {
  font-size: 12px;
  color: #606266;
  margin-left: 10px;
  white-space: nowrap;
}

.description-tip {
  margin: 10px 0;
  color: #909399;
  font-size: 13px;
  text-align: center;
}

.preview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 150px);
  overflow: auto;
}

.image-preview {
  text-align: center;
  margin: 0 auto;
  max-height: 70vh;
  overflow: auto;
}

.image-preview img {
  max-width: 100%;
}

.pdf-preview {
  width: 100%;
  height: 70vh;
}

.pdf-preview iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.video-preview {
  width: 100%;
  text-align: center;
  height: 70vh;
}

.video-preview video {
  max-height: 100%;
}

.other-preview {
  padding: 30px 0;
}

.file-details {
  margin-top: 20px;
}

.el-upload-dragger {
  width: 100%;
}

.el-upload__tip {
  line-height: 1.5;
}

.selection-info {
  margin-left: 10px;
  color: #409eff;
  font-weight: 500;
}

.batch-delete-content {
  max-height: 60vh;
  overflow-y: auto;
}

.batch-delete-info {
  margin-bottom: 15px;
  font-size: 14px;
  color: #606266;
}

.file-type-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 120px;
  overflow-y: auto;
  padding: 5px;
}

.file-type-item {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
}

.file-type-item .el-icon {
  margin-right: 5px;
  font-size: 14px;
}

.file-name-small {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-options {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.delete-strategy-title {
  margin-bottom: 10px;
  font-weight: bold;
}

.delete-type-explanation {
  margin-top: 15px;
  padding: 10px;
  border-left: 3px solid #e6a23c;
  background-color: #fdf6ec;
}

.delete-type-explanation ul {
  margin: 10px 0 0 20px;
  padding: 0;
}

.delete-type-explanation li {
  margin-bottom: 8px;
  font-size: 13px;
}
</style>  background-color: #fdf6ec;
  font-size: 13px;
