// ========== 通用响应结构 ==========
export interface BaseResponse<T = any> {
  code: number
  data: T
  message: string
}

export interface PageResponse<T> {
  records: T[]
  total: number
  current: number
  pageSize: number
}

export interface PageQueryRequest {
  current?: number
  pageSize?: number
  sortField?: string
  sortOrder?: 'ascend' | 'descend'
}

export interface BatchDeleteRequest {
  ids: number[]
}

// ========== 用户模块 ==========
export interface UserLoginRequest {
  username: string
  password: string
}

export interface UserRegisterRequest {
  username: string
  password: string
  checkPassword: string
}

export interface UserAddRequest {
  username: string
  password: string
  nickname?: string
  avatar?: string
  email?: string
  status?: number
}

export interface UserUpdateRequest {
  id: number
  nickname?: string
  avatar?: string
  email?: string
  status?: number
  password?: string
}

export interface UserQueryRequest extends PageQueryRequest {
  username?: string
  nickname?: string
  status?: number
}

export interface UserVO {
  id: number
  username: string
  nickname?: string
  avatar?: string
  email?: string
  status: number
  lastLoginTime?: string
  createTime: string
  updateTime: string
}

export interface LoginUserVO {
  id: number
  username: string
  nickname?: string
  avatar?: string
}

// ========== 分类模块 ==========
export interface CategoryAddRequest {
  name: string
  description?: string
  sort?: number
}

export interface CategoryUpdateRequest {
  id: number
  name?: string
  description?: string
  sort?: number
}

export interface CategoryQueryRequest extends PageQueryRequest {
  name?: string
}

export interface CategoryVO {
  id: number
  name: string
  description?: string
  sort: number
  article_count: number
  createTime: string
  updateTime: string
}

// ========== 标签模块 ==========
export interface TagAddRequest {
  name: string
  color?: string
}

export interface TagUpdateRequest {
  id: number
  name?: string
  color?: string
}

export interface TagQueryRequest extends PageQueryRequest {
  name?: string
}

export interface TagVO {
  id: number
  name: string
  color?: string
  article_count: number
  createTime: string
  updateTime: string
}

// ========== 文章模块 ==========
export interface ArticleAddRequest {
  title: string
  summary?: string
  cover?: string
  content: string
  categoryId?: number
  status?: number
  isTop?: number
  isOriginal?: number
  publishTime?: string
  tagIds?: number[]
}

export interface ArticleUpdateRequest {
  id: number
  title?: string
  summary?: string
  cover?: string
  content?: string
  categoryId?: number
  status?: number
  isTop?: number
  isOriginal?: number
  publishTime?: string
  tagIds?: number[]
}

export interface ArticleQueryRequest extends PageQueryRequest {
  title?: string
  categoryId?: number
  status?: number
  isTop?: number
}

export interface ArticleVO {
  id: number
  title: string
  summary?: string
  cover?: string
  content: string
  categoryId?: number
  authorId?: number
  status: number
  isTop?: number
  isOriginal?: number
  viewCount?: number
  likeCount?: number
  commentCount?: number
  publishTime?: string
  createTime: string
  updateTime: string
}

// ========== 文章点赞模块 ==========
export interface ArticleLikeAddRequest {
  articleId: number
}

export interface ArticleLikeCancelRequest {
  articleId: number
}

export interface ArticleLikeQueryRequest extends PageQueryRequest {
  articleId?: number
  userId?: number
}

export interface ArticleLikeVO {
  id: number
  articleId: number
  ip?: string
  userId?: number
  createTime: string
}

// ========== 文章浏览模块 ==========
export interface ArticleViewAddRequest {
  articleId: number
  ip?: string
  userAgent?: string
}

export interface ArticleViewQueryRequest extends PageQueryRequest {
  articleId?: number
}

export interface ArticleViewVO {
  id: number
  articleId: number
  ip?: string
  userAgent?: string
  createTime: string
}

// ========== 文章标签关联 ==========
export interface ArticleTagAddRequest {
  articleId: number
  tagId: number
}

export interface ArticleTagQueryRequest extends PageQueryRequest {
  articleId?: number
  tagId?: number
}

export interface ArticleTagVO {
  id: number
  articleId: number
  tagId: number
  createTime: string
}

// ========== 评论模块 ==========
export interface CommentAddRequest {
  articleId: number
  parentId?: number
  nickname: string
  email?: string
  avatar?: string
  content: string
}

export interface CommentUpdateRequest {
  id: number
  status?: number
}

export interface CommentQueryRequest extends PageQueryRequest {
  articleId?: number
  status?: number
}

export interface CommentVO {
  id: number
  articleId: number
  parentId: number
  nickname?: string
  email?: string
  avatar?: string
  content?: string
  ip?: string
  userAgent?: string
  status: number
  createTime: string
}

// ========== 文件模块 ==========
export interface FileAddRequest {
  filename: string
  url: string
  size?: number
  type?: string
}

export interface FileUpdateRequest {
  id: number
  filename?: string
  url?: string
}

export interface FileQueryRequest extends PageQueryRequest {
  filename?: string
  type?: string
}

export interface FileVO {
  id: number
  filename?: string
  url?: string
  size?: number
  type?: string
  uploaderId?: number
  createTime: string
}

// ========== 配置模块 ==========
export interface ConfigAddRequest {
  configKey: string
  configValue?: string
  description?: string
}

export interface ConfigUpdateRequest {
  id: number
  configValue?: string
  description?: string
}

export interface ConfigQueryRequest extends PageQueryRequest {
  configKey?: string
}

export interface ConfigVO {
  id: number
  configKey: string
  configValue?: string
  description?: string
  createTime: string
  updateTime: string
}

// ========== 操作日志模块 ==========
export interface OperationLogAddRequest {
  operation: string
  method?: string
  params?: string
  ip?: string
  userId?: number
}

export interface OperationLogQueryRequest extends PageQueryRequest {
  userId?: number
  operation?: string
}

export interface OperationLogVO {
  id: number
  userId?: number
  operation?: string
  method?: string
  params?: string
  ip?: string
  createTime: string
}

// ========== 通用错误码 ==========
export enum ErrorCode {
  SUCCESS = 0,
  PARAMS_ERROR = 40000,
  NOT_LOGIN = 40100,
  NO_AUTH = 40101,
  PASSWORD_ERROR = 40103,
  ACCOUNT_DISABLED = 40104,
  ACCOUNT_OR_PASSWORD_ERROR = 40105,
  FORBIDDEN = 40300,
  NOT_FOUND = 40400,
  USER_NOT_FOUND = 40401,
  USER_EXISTS = 40402,
  SYSTEM_ERROR = 50000,
  OPERATION_FAILED = 50001,
}
