import { get, post, put, del } from '@/utils/request'
import type {
  CommentAddRequest,
  CommentUpdateRequest,
  CommentQueryRequest,
  CommentVO,
  PageResponse,
  BatchDeleteRequest,
} from '@/types'

// 分页查询评论（公开）
export function listComment(data: CommentQueryRequest) {
  return post<PageResponse<CommentVO>>('/comment/list', data)
}

// 查询单个评论（公开）
export function getComment(commentId: number) {
  return get<CommentVO>(`/comment/${commentId}`)
}

// 新增评论（公开，自动采集IP/UA）
export function addComment(data: CommentAddRequest) {
  return post<number>('/comment', data)
}

// 更新评论状态（登录）
export function updateComment(data: CommentUpdateRequest) {
  return put<number>('/comment', data)
}

// 删除评论（登录）
export function deleteComment(commentId: number) {
  return del<number>(`/comment/${commentId}`)
}

// 批量删除评论（登录）
export function batchDeleteComment(data: BatchDeleteRequest) {
  return post<number>('/comment/batch/delete', data)
}
