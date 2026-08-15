import { getWechatConfig } from '@/api/user'

const WECHAT_AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/qrconnect'

/**
 * 发起微信扫码登录：跳转到微信授权页，授权后回调到 /wechat/callback
 * @param redirect 登录成功后回跳的站内路径（默认首页）
 */
export async function startWechatLogin(redirect?: string) {
  const cfg = await getWechatConfig()
  if (!cfg?.enabled || !cfg.appId) {
    throw new Error('微信登录未配置，请使用账号密码登录')
  }
  const redirectUri = `${window.location.origin}/wechat/callback`
  const state = redirect && redirect.startsWith('/') ? redirect : '/'
  const params = new URLSearchParams({
    appid: cfg.appId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: 'snsapi_login',
    state,
  })
  window.location.href = `${WECHAT_AUTHORIZE_URL}?${params.toString()}#wechat_redirect`
}
