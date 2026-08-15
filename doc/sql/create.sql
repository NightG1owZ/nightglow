-- ============================================
-- Personal Blog Database
-- MySQL 8.0
-- ============================================


CREATE DATABASE IF NOT EXISTS NIGHTGLOW
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE NIGHTGLOW;


-- ============================================
-- 1. 用户表
-- 管理后台登录用户，支持账号密码与微信扫码登录
-- ============================================

CREATE TABLE blog_user (
    id                      BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username                VARCHAR(50) COMMENT '用户名(账号密码登录使用，微信扫码注册用户可为空)',
    PASSWORD                VARCHAR(255) COMMENT '密码密文(账号密码登录使用，微信扫码注册用户可为空)',
    nickname                VARCHAR(50) COMMENT '昵称',
    avatar                  VARCHAR(500) COMMENT '头像地址',
    email                   VARCHAR(100) COMMENT '邮箱',
    openid                  VARCHAR(64) COMMENT '微信唯一标识openid',
    unionid                 VARCHAR(64) COMMENT '微信开放平台unionid(同一开放平台下唯一)',
    wechat_nickname         VARCHAR(100) COMMENT '微信昵称',
    wechat_avatar           VARCHAR(500) COMMENT '微信头像',
    wechat_login_status     TINYINT DEFAULT 0 COMMENT '微信扫码登录状态 1已登录 0未登录',
    last_wechat_login_time  DATETIME COMMENT '微信最后登录时间',
    STATUS                  TINYINT DEFAULT 1 COMMENT '状态 1正常 0禁用',
    last_login_time         DATETIME COMMENT '最后登录时间',
    create_time             DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time             DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_openid (openid),
    UNIQUE KEY uk_unionid (unionid)
) COMMENT='博客用户表(支持账号密码与微信扫码登录)';


-- ============================================
-- 2. 文章分类表
-- ============================================

CREATE TABLE blog_category (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    NAME                VARCHAR(50) NOT NULL COMMENT '分类名称',
    DESCRIPTION         VARCHAR(255) COMMENT '分类描述',
    sort                INT DEFAULT 0 COMMENT '排序',
    article_count       INT DEFAULT 0 COMMENT '文章数量',
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_category_name (NAME)
) COMMENT='文章分类表';


-- ============================================
-- 3. 标签表
-- 支持父子层级，树形展示
-- ============================================

CREATE TABLE blog_tag (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    NAME                VARCHAR(50) NOT NULL COMMENT '标签名称',
    color               VARCHAR(20) COMMENT '标签颜色',
    parent_id           BIGINT DEFAULT 0 COMMENT '父标签ID，0表示顶级标签',
    level               TINYINT DEFAULT 1 COMMENT '标签层级深度，1为顶级标签',
    article_count       INT DEFAULT 0 COMMENT '文章数量',
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_tag_name (NAME),
    KEY idx_parent_id (parent_id)
) COMMENT='文章标签表(支持父子层级树形展示)';


-- ============================================
-- 4. 文章表
-- 核心业务表
-- ============================================

CREATE TABLE blog_article (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    title               VARCHAR(200) NOT NULL COMMENT '文章标题',
    summary             VARCHAR(500) COMMENT '文章摘要',
    cover               VARCHAR(500) COMMENT '封面图片',
    content             LONGTEXT NOT NULL COMMENT 'Markdown正文内容',
    category_id         BIGINT COMMENT '分类ID',
    author_id           BIGINT COMMENT '作者ID',
    STATUS              TINYINT DEFAULT 0 COMMENT '状态 0草稿 1发布 2下架',
    is_top              TINYINT DEFAULT 0 COMMENT '是否置顶',
    is_original         TINYINT DEFAULT 1 COMMENT '是否原创',
    view_count          INT DEFAULT 0 COMMENT '浏览次数',
    like_count          INT DEFAULT 0 COMMENT '点赞数量',
    comment_count       INT DEFAULT 0 COMMENT '评论数量',
    publish_time        DATETIME COMMENT '发布时间',
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FULLTEXT KEY ft_article_content (title, content),
    KEY idx_category (category_id),
    KEY idx_author (author_id),
    KEY idx_status (STATUS),
    KEY idx_publish_time (publish_time)
) COMMENT='博客文章表';


-- ============================================
-- 5. 文章标签关联表
-- 多对多关系
-- ============================================

CREATE TABLE blog_article_tag (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    article_id          BIGINT NOT NULL COMMENT '文章ID',
    tag_id              BIGINT NOT NULL COMMENT '标签ID',
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_article_tag (article_id, tag_id)
) COMMENT='文章标签关联表';


-- ============================================
-- 6. 评论表
-- 支持评论回复
-- ============================================

CREATE TABLE blog_comment (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    article_id          BIGINT NOT NULL COMMENT '文章ID',
    parent_id           BIGINT DEFAULT 0 COMMENT '父评论ID',
    nickname            VARCHAR(50) COMMENT '评论昵称',
    email               VARCHAR(100) COMMENT '邮箱',
    avatar              VARCHAR(500) COMMENT '头像',
    content             VARCHAR(1000) COMMENT '评论内容',
    ip                  VARCHAR(50) COMMENT 'IP地址',
    user_agent          VARCHAR(500) COMMENT '浏览器信息',
    STATUS              TINYINT DEFAULT 1 COMMENT '状态 1显示 0隐藏',
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_article (article_id),
    KEY idx_parent (parent_id)
) COMMENT='文章评论表';


-- ============================================
-- 7. 点赞记录表
-- 防止重复点赞
-- ============================================

CREATE TABLE blog_article_like (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    article_id          BIGINT NOT NULL,
    ip                  VARCHAR(50) COMMENT '访问IP',
    user_id             BIGINT COMMENT '登录用户ID',
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_article_ip (article_id, ip)
) COMMENT='文章点赞记录表';


-- ============================================
-- 8. 浏览记录表
-- 用于统计PV
-- ============================================

CREATE TABLE blog_article_view (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    article_id          BIGINT NOT NULL,
    ip                  VARCHAR(50),
    user_agent          VARCHAR(500),
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_article (article_id),
    KEY idx_time (create_time)
) COMMENT='文章访问记录表';


-- ============================================
-- 9. 文件资源表
-- 图片、附件等
-- ============================================

CREATE TABLE blog_file (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    filename            VARCHAR(255) COMMENT '文件名称',
    url                 VARCHAR(500) COMMENT '访问地址',
    size                BIGINT COMMENT '文件大小',
    TYPE                VARCHAR(50) COMMENT '文件类型',
    uploader_id         BIGINT COMMENT '上传用户',
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='博客文件资源表';


-- ============================================
-- 10. 网站配置表
-- 如标题、头像、简介
-- ============================================

CREATE TABLE blog_config (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_key          VARCHAR(100) NOT NULL,
    config_value        TEXT,
    DESCRIPTION         VARCHAR(255),
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_key (config_key)
) COMMENT='网站配置表';


-- ============================================
-- 11. 操作日志
-- 后台行为审计
-- ============================================

CREATE TABLE blog_operation_log (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id             BIGINT,
    operation           VARCHAR(100) COMMENT '操作名称',
    method              VARCHAR(200) COMMENT '请求方法',
    params              TEXT COMMENT '参数',
    ip                  VARCHAR(50),
    create_time         DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='后台操作日志表';

