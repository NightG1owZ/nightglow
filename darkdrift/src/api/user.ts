import { get, post, put, del } from '@/utils/request'
import type {
  UserLoginRequest,
  UserRegisterRequest,
  WechatLoginRequest,
  WechatConfigVO,
  UserAddRequest,
  UserUpdateRequest,
  UserQueryRequest,
  UserVO,
  LoginUserVO,
  PageResponse,
  BatchDeleteRequest,
} from '@/types'

// 登录
export function login(data: UserLoginRequest) {
  return post<LoginUserVO>('/user/login', data)
}

// 注册
export function register(data: UserRegisterRequest) {
  return post<number>('/user/register', data)
}

// 退出登录
export function logout() {
  return post<number>('/user/logout')
}

// 获取微信登录配置
export function getWechatConfig() {
  return get<WechatConfigVO>('/user/wechat/config')
}

// 微信扫码登录
export function wechatLogin(data: WechatLoginRequest) {
  return post<LoginUserVO>('/user/wechat/login', data)
}

// 获取当前登录用户
export function getCurrentUser() {
  return get<LoginUserVO>('/user/current')
}

// 分页查询用户
export function listUser(data: UserQueryRequest) {
  return post<PageResponse<UserVO>>('/user/list', data)
}

// 查询单个用户
export function getUser(userId: number) {
  return get<UserVO>(`/user/${userId}`)
}

// 新增用户
export function addUser(data: UserAddRequest) {
  return post<number>('/user', data)
}

// 更新用户
export function updateUser(data: UserUpdateRequest) {
  return put<number>('/user', data)
}

// 删除用户
export function deleteUser(userId: number) {
  return del<number>(`/user/${userId}`)
}

// 批量删除用户
export function batchDeleteUser(data: BatchDeleteRequest) {
  return post<number>('/user/batch/delete', data)
}
