/**
 * 格式化日期
 * @param {Date} date 要格式化的日期
 * @param {String} format 格式化模板，默认为 yyyy-MM-dd HH:mm:ss
 * @return {String} 格式化后的日期字符串
 */
export function formatDate(date, format = 'yyyy-MM-dd HH:mm:ss') {
  if (!date) return ''
  // 兼容ISO字符串
  if (typeof date === 'string') {
    // 替换T为空格，去掉毫秒和Z
    date = date.replace('T', ' ').replace(/\..*$/, '').replace('Z', '')
  }
  date = new Date(date)
  if (isNaN(date.getTime())) {
    return ''
  }
  const o = {
    'M+': date.getMonth() + 1, // 月份
    'd+': date.getDate(), // 日
    'H+': date.getHours(), // 小时
    'm+': date.getMinutes(), // 分
    's+': date.getSeconds(), // 秒
    'q+': Math.floor((date.getMonth() + 3) / 3), // 季度
    'S': date.getMilliseconds() // 毫秒
  }
  if (/(y+)/.test(format)) {
    format = format.replace(RegExp.$1, (date.getFullYear() + '').substr(4 - RegExp.$1.length))
  }
  for (let k in o) {
    if (new RegExp('(' + k + ')').test(format)) {
      format = format.replace(
        RegExp.$1, 
        RegExp.$1.length === 1 ? o[k] : ('00' + o[k]).substr(('' + o[k]).length)
      )
    }
  }
  return format
}

/**
 * 计算相对时间
 * @param {Date|String} dateTime 要计算的时间
 * @return {String} 相对时间文本
 */
export function timeAgo(dateTime) {
  if (!dateTime) return ''
  
  const date = typeof dateTime === 'object' ? dateTime : new Date(dateTime)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 0) {
    return '刚刚'
  }
  
  const minute = 1000 * 60
  const hour = minute * 60
  const day = hour * 24
  const month = day * 30
  const year = month * 12
  
  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return Math.floor(diff / minute) + '分钟前'
  } else if (diff < day) {
    return Math.floor(diff / hour) + '小时前'
  } else if (diff < month) {
    return Math.floor(diff / day) + '天前'
  } else if (diff < year) {
    return Math.floor(diff / month) + '个月前'
  } else {
    return Math.floor(diff / year) + '年前'
  }
} 