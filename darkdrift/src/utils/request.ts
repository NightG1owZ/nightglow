import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import type { BaseResponse } from '@/types'
import { ErrorCode } from '@/types'

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  },
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<BaseResponse>) => {
    const res = response.data
    if (res.code === ErrorCode.SUCCESS) {
      return res.data
    }
    // 未登录
    if (res.code === ErrorCode.NOT_LOGIN) {
      console.warn('未登录或登录已过期:', res.message)
      // 如果不在登录页，可跳转到登录页
      if (
        !window.location.pathname.includes('/login') &&
        !window.location.pathname.includes('/register')
      ) {
        // router.push('/login')
      }
    }
    console.error('API error:', res.message || `Error code: ${res.code}`)
    return Promise.reject(new Error(res.message || `Error code: ${res.code}`))
  },
  (error) => {
    console.error('Network error:', error.message)
    return Promise.reject(error)
  },
)

// 封装请求方法，返回 data 直接就是业务层数据
export function request<T = any>(config: AxiosRequestConfig): Promise<T> {
  return service.request(config) as unknown as Promise<T>
}

export function get<T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
  return request<T>({ ...config, method: 'GET', url, params })
}

export function post<T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig,
): Promise<T> {
  return request<T>({ ...config, method: 'POST', url, data })
}

export function put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return request<T>({ ...config, method: 'PUT', url, data })
}

export function del<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return request<T>({ ...config, method: 'DELETE', url })
}

export default service
