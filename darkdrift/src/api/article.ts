import { get, post, put, del } from '@/utils/request'
import type {
  ArticleAddRequest,
  ArticleUpdateRequest,
  ArticleQueryRequest,
  ArticleVO,
  ArticleLikeAddRequest,
  ArticleLikeCancelRequest,
  ArticleLikeQueryRequest,
  ArticleLikeVO,
  ArticleViewAddRequest,
  ArticleViewQueryRequest,
  ArticleViewVO,
  ArticleTagAddRequest,
  ArticleTagQueryRequest,
  ArticleTagVO,
  PageResponse,
  BatchDeleteRequest,
} from '@/types'

// ======== 文章 ========
// 分页查询文章
export function listArticle(data: ArticleQueryRequest) {
  return post<PageResponse<ArticleVO>>('/article/list', data)
}

// 查询单个文章（浏览量+1）
export function getArticle(articleId: number) {
  return get<ArticleVO>(`/article/${articleId}`)
}

// 新增文章
export function addArticle(data: ArticleAddRequest) {
  return post<number>('/article', data)
}

// 更新文章
export function updateArticle(data: ArticleUpdateRequest) {
  return put<number>('/article', data)
}

// 删除文章
export function deleteArticle(articleId: number) {
  return del<number>(`/article/${articleId}`)
}

// 批量删除文章
export function batchDeleteArticle(data: BatchDeleteRequest) {
  return post<number>('/article/batch/delete', data)
}

// ======== 点赞 ========
// 点赞文章（公开，IP去重）
export function likeArticle(data: ArticleLikeAddRequest) {
  return post<number>('/article/like', data)
}

// 取消点赞（公开，按IP取消）
export function cancelLikeArticle(data: ArticleLikeCancelRequest) {
  return post<number>('/article/like/cancel', data)
}

// 分页查询点赞（登录）
export function listArticleLike(data: ArticleLikeQueryRequest) {
  return post<PageResponse<ArticleLikeVO>>('/article/like/list', data)
}

// 删除点赞记录（登录，点赞数-1）
export function deleteArticleLike(likeId: number) {
  return del<number>(`/article/like/${likeId}`)
}

// 批量删除点赞（登录）
export function batchDeleteArticleLike(data: BatchDeleteRequest) {
  return post<number>('/article/like/batch/delete', data)
}

// ======== 浏览 ========
// 新增浏览记录（登录）
export function addArticleView(data: ArticleViewAddRequest) {
  return post<number>('/article/view', data)
}

// 分页查询浏览（登录）
export function listArticleView(data: ArticleViewQueryRequest) {
  return post<PageResponse<ArticleViewVO>>('/article/view/list', data)
}

// 删除浏览记录（登录）
export function deleteArticleView(viewId: number) {
  return del<number>(`/article/view/${viewId}`)
}

// 批量删除浏览（登录）
export function batchDeleteArticleView(data: BatchDeleteRequest) {
  return post<number>('/article/view/batch/delete', data)
}

// ======== 文章标签关联 ========
// 新增关联（登录）
export function addArticleTag(data: ArticleTagAddRequest) {
  return post<number>('/article/tag', data)
}

// 分页查询关联（登录）
export function listArticleTag(data: ArticleTagQueryRequest) {
  return post<PageResponse<ArticleTagVO>>('/article/tag/list', data)
}

// 删除关联（登录）
export function deleteArticleTag(articleTagId: number) {
  return del<number>(`/article/tag/${articleTagId}`)
}

// 批量删除关联（登录）
export function batchDeleteArticleTag(data: BatchDeleteRequest) {
  return post<number>('/article/tag/batch/delete', data)
}
