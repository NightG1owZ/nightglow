import { get, post, put, del } from '@/utils/request'
import type {
  ConfigAddRequest,
  ConfigUpdateRequest,
  ConfigQueryRequest,
  ConfigVO,
  PageResponse,
  BatchDeleteRequest,
} from '@/types'

// 根据键查询配置（公开）
export function getConfigByKey(configKey: string) {
  return get<ConfigVO>(`/config/key/${configKey}`)
}

// 分页查询配置（登录）
export function listConfig(data: ConfigQueryRequest) {
  return post<PageResponse<ConfigVO>>('/config/list', data)
}

// 查询单个配置（登录）
export function getConfig(configId: number) {
  return get<ConfigVO>(`/config/${configId}`)
}

// 新增配置（登录）
export function addConfig(data: ConfigAddRequest) {
  return post<number>('/config', data)
}

// 更新配置（登录）
export function updateConfig(data: ConfigUpdateRequest) {
  return put<number>('/config', data)
}

// 删除配置（登录）
export function deleteConfig(configId: number) {
  return del<number>(`/config/${configId}`)
}

// 批量删除配置（登录）
export function batchDeleteConfig(data: BatchDeleteRequest) {
  return post<number>('/config/batch/delete', data)
}
