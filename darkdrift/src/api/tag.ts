import { get, post, put, del } from '@/utils/request'
import type {
  TagAddRequest,
  TagUpdateRequest,
  TagQueryRequest,
  TagVO,
  PageResponse,
  BatchDeleteRequest,
} from '@/types'

// 分页查询标签
export function listTag(data: TagQueryRequest) {
  return post<PageResponse<TagVO>>('/tag/list', data)
}

// 查询单个标签
export function getTag(tagId: number) {
  return get<TagVO>(`/tag/${tagId}`)
}

// 新增标签
export function addTag(data: TagAddRequest) {
  return post<number>('/tag', data)
}

// 更新标签
export function updateTag(data: TagUpdateRequest) {
  return put<number>('/tag', data)
}

// 删除标签
export function deleteTag(tagId: number) {
  return del<number>(`/tag/${tagId}`)
}

// 批量删除标签
export function batchDeleteTag(data: BatchDeleteRequest) {
  return post<number>('/tag/batch/delete', data)
}
