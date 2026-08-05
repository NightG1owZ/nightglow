import { get, post, put, del } from '@/utils/request'
import type {
  CategoryAddRequest,
  CategoryUpdateRequest,
  CategoryQueryRequest,
  CategoryVO,
  PageResponse,
  BatchDeleteRequest,
} from '@/types'

// 分页查询分类
export function listCategory(data: CategoryQueryRequest) {
  return post<PageResponse<CategoryVO>>('/category/list', data)
}

// 查询单个分类
export function getCategory(categoryId: number) {
  return get<CategoryVO>(`/category/${categoryId}`)
}

// 新增分类
export function addCategory(data: CategoryAddRequest) {
  return post<number>('/category', data)
}

// 更新分类
export function updateCategory(data: CategoryUpdateRequest) {
  return put<number>('/category', data)
}

// 删除分类
export function deleteCategory(categoryId: number) {
  return del<number>(`/category/${categoryId}`)
}

// 批量删除分类
export function batchDeleteCategory(data: BatchDeleteRequest) {
  return post<number>('/category/batch/delete', data)
}
