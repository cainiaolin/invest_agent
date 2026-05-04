/** API服务模块 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

/** 分析API */
export const analyzeApi = {
  analyze: (data: any) => api.post('/analyze/', data),
  listAgents: () => api.get('/analyze/agents')
}

/** 选股API */
export const screenApi = {
  screen: (data: any) => api.post('/screen/', data),
  listIndustries: () => api.get('/screen/industries'),
  getStatus: () => api.get('/screen/status')
}

/** 回测API */
export const backtestApi = {
  backtest: (data: any) => api.post('/backtest/', data),
  listAgents: () => api.get('/backtest/agents'),
  getStatus: () => api.get('/backtest/status')
}
