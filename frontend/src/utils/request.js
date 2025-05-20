import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || '',
  timeout: 600000 // 600秒
})

// 在localStorage不可用时使用内存缓存
let tokenCache = null;

// 获取令牌的函数
function getToken() {
  try {
    return localStorage.getItem('token') || tokenCache;
  } catch (e) {
    return tokenCache;
  }
}

// 设置令牌的函数
function setToken(token) {
  tokenCache = token;
  try {
    localStorage.setItem('token', token);
  } catch (e) {
    console.error('无法写入localStorage:', e);
  }
}

// 清除令牌的函数
function clearToken() {
  tokenCache = null;
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  } catch (e) {
    console.error('无法从localStorage移除令牌:', e);
  }
}

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = getToken();
    const requestMethod = config.method.toUpperCase();
    const requestUrl = config.url;
    const requestData = config.params || config.data;
    
    console.log(`【请求】${requestMethod} ${requestUrl}`, {
      参数: requestData,
      认证: token ? '已提供' : '未提供'
    });

    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    
    // 添加请求开始时间戳，用于计算请求耗时
    config.metadata = { startTime: new Date().getTime() };
    
    return config;
  },
  error => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data;
    const requestUrl = response.config.url;
    const requestMethod = response.config.method.toUpperCase();
    
    // 计算请求耗时
    const endTime = new Date().getTime();
    const startTime = response.config.metadata ? response.config.metadata.startTime : 0;
    const duration = endTime - startTime;
    
    console.log(`【响应】${requestMethod} ${requestUrl} - 成功 (${duration}ms)`, {
      结果: res,
      状态码: response.status
    });
    
    return res;
  },
  error => {
    // 处理错误响应
    const { response, config } = error;
    const requestUrl = config ? config.url : '未知URL';
    const requestMethod = config ? config.method.toUpperCase() : '未知方法';
    
    // 计算请求耗时
    const endTime = new Date().getTime();
    const startTime = config && config.metadata ? config.metadata.startTime : 0;
    const duration = endTime - startTime;
    
    console.error(`【响应】${requestMethod} ${requestUrl} - 失败 (${duration}ms)`, error);
    
    if (response) {
      console.error('错误详情:', {
        状态码: response.status,
        响应数据: response.data,
        请求URL: requestUrl,
        请求方法: requestMethod
      });
      
      // 只在后端返回"令牌已过期"或"未提供访问令牌"时清除token
      if (
        response.status === 401 &&
        response.data &&
        (
          response.data.message === '令牌已过期，请重新登录' ||
          response.data.message === '未提供访问令牌'
        )
      ) {
        ElMessage.warning('登录已失效，请重新登录');
        clearToken();
        router.push('/login');
      } else if (response.status === 403) {
        ElMessage.warning('权限不足，无法执行此操作');
      } else {
        // 其他错误
        ElMessage.error(response.data.message || `请求失败 (${response.status})`);
      }
    } else {
      // 网络错误
      console.error('网络错误:', {
        错误信息: error.message,
        请求URL: requestUrl,
        请求方法: requestMethod
      });
      
      ElMessage.error('网络连接失败，请检查您的网络连接或服务器状态');
    }
    
    return Promise.reject(error);
  }
)

export default service