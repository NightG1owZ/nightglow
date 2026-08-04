# 第一篇博客

```sql
USE personal_blog;


-- ============================================
-- 1. 插入分类
-- ============================================

INSERT INTO blog_category
(
    id,
    name,
    description,
    sort
)
VALUES
(
    1,
    'Java性能优化',
    'Java JVM、性能测试、系统优化相关技术文章',
    1
);



-- ============================================
-- 2. 插入标签
-- ============================================

INSERT INTO blog_tag
(
    id,
    name,
    color
)
VALUES
(1, 'JMH', '#FF5722'),
(2, 'Benchmark', '#2196F3'),
(3, 'JVM', '#4CAF50'),
(4, '性能测试', '#9C27B0'),
(5, 'Java', '#F44336');



-- ============================================
-- 3. 插入文章
-- ============================================

INSERT INTO blog_article
(
    id,
    title,
    summary,
    cover,
    content,
    category_id,
    author_id,
    status,
    is_top,
    is_original,
    view_count,
    like_count,
    comment_count,
    publish_time
)
VALUES
(
1,

'JMH 基准测试 Benchmark',

'本文介绍 OpenJDK 提供的微基准测试框架 JMH，通过 Hello World 示例以及压缩算法性能测试案例，深入了解 Benchmark 的使用方法和结果分析。',

'/upload/article/jmh-benchmark-cover.png',


'# JMH 基准测试 Benchmark


# 1 引言


今天，笔者为大家带来一款压力测试工具：JMH（Java Microbenchmark Harness） Benchmark。


JMH 是 OpenJDK 提供的微基准测试框架，主要用于测试 JVM 级别的方法执行性能。


聊到这，可能会有的疑问：

压力测试有 JMeter 不就够了吗？


关于这个问题：

它们解决的问题是不同的。


可以这样讲：

JMH 是实验室里的显微镜：

测试一个方法执行 1 万次到底需要多久，关注单个方法执行效率。


JMeter 是生产环境演练：

关注 1 万个用户同时访问接口，测试系统整体承载能力。


简单讲：

JMH 是拆开引擎，单独测活塞运转速度；

JMeter 是整车开上高速，测满载状态下整车最高时速。


两者场景并不冲突。


日常开发优化代码优先使用 JMH；

上线前容量评估使用 JMeter。


因此，除了对某个方法进行压力测试，在遇到需要评估某段代码、某个算法或某个第三方组件执行效率时，也可以考虑 Benchmark。


本文会通过 Hello World 级 Benchmark 示例，以及实际压缩算法性能对比案例，介绍 JMH 的使用方法。


# 2 特性


JMH 专为 JVM 性能测试设计，规避 JIT 编译、循环消除、无用代码裁剪等 JVM 优化带来的测试失真。


主要能力包括：


| 特性 | 说明 |
| --- | --- |
| Warmup 预热 | 正式测试前运行多轮代码，让 JVM 完成 JIT 优化 |
| Measurement 多轮测试 | 多轮采集数据减少误差 |
| Fork 独立进程 | 使用独立 JVM 运行测试 |
| Thread 多线程并发 | 支持模拟多线程调用 |
| Benchmark Mode | 支持吞吐量、平均耗时等指标 |
| Blackhole 黑洞 | 防止 JVM 删除无效代码 |
| JVM 参数隔离 | 支持不同 JVM 配置测试 |



# 3 实践


## 3.1 Maven 依赖


```xml
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>


<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-generator-annprocess</artifactId>
    <version>1.37</version>
    <scope>provided</scope>
</dependency>
```

# --- CUT THROUGH  ---

设计思路说明
1. 为什么文章内容使用 LONGTEXT？

博客正文通常是 Markdown：

例如：

# JMH 基准测试 Benchmark

## 1 引言

今天笔者介绍...

转换 HTML 后可能达到几十 KB，甚至包含代码块、图片引用，因此普通：

VARCHAR(5000)

明显不够。

2. 为什么标签单独拆表？

文章：

JMH Benchmark

可能拥有：

Java
性能优化
JVM
源码分析

标签：

Java

又可能属于：

100篇文章

所以是典型：

文章 N : M 标签

需要中间表：

blog_article_tag
3. 为什么点赞不用直接存在文章表？

很多简单博客会：

article.like_count

直接 +1。

但是无法解决：

同一个人刷新页面无限点赞

所以额外增加：

blog_article_like

保存行为记录。

4. 为什么增加浏览记录表？

因为：

view_count

只能告诉你：

这篇文章看了多少次

但是无法分析：

哪天访问最多？
哪个地区访问？
哪篇文章增长最快？

因此：

blog_article_view

负责数据分析。



