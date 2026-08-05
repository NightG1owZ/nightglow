# -*- coding: utf-8 -*-
"""根据 FastAPI OpenAPI 规范生成接口文档 Markdown。运行后自动写入 接口文档说明.md"""
import json
from pathlib import Path

from app.main import app

spec = app.openapi()
SCHEMAS = spec.get("components", {}).get("schemas", {})

TAG_ORDER = [
    "健康检查", "用户管理", "分类管理", "标签管理", "文章管理",
    "文章标签关联", "文章点赞", "文章浏览", "评论管理", "文件管理",
    "网站配置", "操作日志",
]

# 公开接口（无需登录）；其余均需 session_id Cookie
PUBLIC = {
    ("POST", "/user/register"),
    ("POST", "/user/login"),
    ("POST", "/user/logout"),
    ("POST", "/article/list"),
    ("GET", "/article/{article_id}"),
    ("POST", "/article/like"),
    ("POST", "/article/like/cancel"),
    ("POST", "/comment/list"),
    ("GET", "/comment/{comment_id}"),
    ("POST", "/comment"),
    ("GET", "/config/key/{config_key}"),
    ("GET", "/health"),
    ("GET", "/"),
}
SKIP_PATHS = {"/docs", "/openapi.json", "/redoc", "/docs/oauth2-redirect"}

PY_TYPE_MAP = {
    "integer": "int", "number": "float", "string": "str",
    "boolean": "bool", "array": "array", "object": "object",
}


def ref_name(ref):
    return ref.split("/")[-1]


def resolve_schema(schema):
    """递归把 \$ref 解析为实际 schema dict"""
    if not schema:
        return {}
    if "$ref" in schema:
        name = ref_name(schema["$ref"])
        return resolve_schema(SCHEMAS.get(name, {}))
    if schema.get("type") == "array" and "items" in schema:
        return {"type": "array", "items": resolve_schema(schema["items"])}
    return schema


def field_type(prop):
    """从 property schema 生成类型字符串"""
    if "$ref" in prop:
        return ref_name(prop["$ref"])
    # pydantic v2: Optional[X] -> anyOf [{...}, {type:null}]
    for key in ("anyOf", "oneOf"):
        if key in prop:
            subs = [s for s in prop[key] if s.get("type") != "null"]
            if subs:
                return field_type(subs[0])
    t = prop.get("type")
    if t == "array":
        items = prop.get("items", {})
        if "$ref" in items:
            return f"array<{ref_name(items['$ref'])}>"
        return f"array<{items.get('type', 'any')}>"
    if t == "object":
        return "object"
    if t == "string" and prop.get("format") == "date-time":
        return "datetime"
    return PY_TYPE_MAP.get(t, t or "any")


def sample_value(prop, name=""):
    """根据 schema 生成示例值"""
    if "default" in prop and prop["default"] is not None:
        return prop["default"]
    if "example" in prop:
        return prop["example"]
    for key in ("anyOf", "oneOf"):
        if key in prop:
            subs = [s for s in prop[key] if s.get("type") != "null"]
            if subs:
                return sample_value(subs[0], name)
    if "$ref" in prop:
        s = resolve_schema(prop)
        return sample_object(s)
    t = prop.get("type")
    if t == "array":
        items = prop.get("items", {})
        if "$ref" in items:
            return [sample_object(resolve_schema(items))]
        return [sample_value(items)]
    if t == "object":
        return sample_object(prop)
    if t == "integer":
        return 1 if "id" in name.lower() else 0
    if t == "number":
        return 0
    if t == "boolean":
        return False
    if t == "string":
        if prop.get("format") == "date-time":
            return "2026-08-04T12:00:00"
        if name.lower().endswith("email"):
            return "user@example.com"
        if "url" in name.lower() or name in ("cover", "avatar"):
            return "https://example.com/x.png"
        if name in ("content",):
            return "示例内容"
        if name in ("title",):
            return "示例标题"
        if name in ("password",):
            return "12345678"
        return "string"
    return None


def sample_object(schema):
    schema = resolve_schema(schema)
    props = schema.get("properties", {})
    if not props:
        return {}
    obj = {}
    for name, p in props.items():
        obj[name] = sample_value(p, name)
    return obj


def body_schema_info(operation):
    """返回 (schema_name, resolved_schema) 或 (None, None)"""
    rb = operation.get("requestBody", {})
    content = rb.get("content", {}).get("application/json", {})
    schema = content.get("schema", {})
    if not schema:
        return None, None
    name = ref_name(schema["$ref"]) if "$ref" in schema else None
    return name, resolve_schema(schema)


def response_data_schema(operation):
    """取 200 响应中 BaseResponse.data 的 schema"""
    resp = operation.get("responses", {}).get("200", {})
    content = resp.get("content", {}).get("application/json", {})
    schema = resolve_schema(content.get("schema", {}))
    props = schema.get("properties", {})
    data = props.get("data", {})
    return data  # 可能是 $ref / array / anyOf / 空


def unwrap_anyof(schema):
    """剥离 anyOf/oneOf 中的 null，返回真实类型 schema"""
    if not schema:
        return {}
    for key in ("anyOf", "oneOf"):
        if key in schema:
            subs = [s for s in schema[key] if s.get("type") != "null"]
            if subs:
                return subs[0]
            return schema[key][0]
    return schema


def params_table(operation):
    """路径/查询参数表 -> list[list] 对齐 headers"""
    params = operation.get("parameters", [])
    if not params:
        return None
    rows = []
    for p in params:
        s = resolve_schema(p.get("schema", {}))
        desc = p.get("description", "") or s.get("description", "") or ""
        rows.append([
            p["name"], p.get("in"), field_type(s),
            "是" if p.get("required") else "否", desc,
        ])
    return rows


def fields_table(schema):
    """请求体/响应体字段表 -> list[list] 对齐 headers"""
    schema = resolve_schema(schema)
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    rows = []
    for name, p in props.items():
        t = field_type(p)
        if p.get("type") == "array":
            items = p.get("items", {})
            t = f"array<{field_type(items)}>" if "$ref" not in items else f"array<{ref_name(items['$ref'])}>"
        desc = p.get("description", "") or p.get("title", "") or ""
        rows.append([
            name, t,
            "是" if name in required else "否",
            p.get("default", "—") if p.get("default") is not None else "—",
            desc,
        ])
    return rows


def md_table(headers, rows):
    if not rows:
        return ""
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(lines)


def auth_label(method, path):
    if (method, path) in PUBLIC:
        return "公开"
    return "需登录（Cookie: session_id）"


def method_emoji(m):
    return {"GET": "GET", "POST": "POST", "PUT": "PUT", "DELETE": "DELETE"}.get(m, m)


# 收集接口
endpoints = []
for path, methods in spec["paths"].items():
    if path in SKIP_PATHS:
        continue
    for method, op in methods.items():
        if method.upper() not in ("GET", "POST", "PUT", "DELETE"):
            continue
        tags = op.get("tags", ["其他"])
        endpoints.append((tags[0], method.upper(), path, op))

# 排序
def sort_key(e):
    tag, method, path, _ = e
    tag_idx = TAG_ORDER.index(tag) if tag in TAG_ORDER else 99
    method_idx = {"GET": 0, "POST": 1, "PUT": 2, "DELETE": 3}.get(method, 9)
    return (tag_idx, path, method_idx)

endpoints.sort(key=sort_key)

# 生成 Markdown
out = []
out.append("# 个人博客后端 接口文档\n")
out.append("> 本文档由 FastAPI OpenAPI 规范自动生成，与代码实现保持一致。\n")
out.append("- Base URL: `http://localhost:8101`")
out.append("- 所有响应统一结构 `BaseResponse<T>`：`{ code, data, message }`，`code=0` 表示成功。")
out.append("- 分页响应 `data` 为 `PageResponse<T>`：`{ records, total, current, pageSize }`。")
out.append("- 需登录的接口依赖 Cookie `session_id`（登录接口下发），缺失或过期返回 `40100 未登录`。")
out.append("- 请求体字段使用驼峰别名（如 `articleId`），与前端一致。\n")

out.append("## 通用错误码\n")
out.append("| code | 说明 |")
out.append("| --- | --- |")
out.append("| 0 | 成功 |")
out.append("| 40000 | 请求参数错误 |")
out.append("| 40100 | 未登录 |")
out.append("| 40101 | 无权限 |")
out.append("| 40103 | 密码错误 |")
out.append("| 40104 | 账号已被禁用 |")
out.append("| 40105 | 账号或密码错误 |")
out.append("| 40300 | 禁止访问 |")
out.append("| 40400 | 请求数据不存在 |")
out.append("| 40401 | 用户不存在 |")
out.append("| 40402 | 用户已存在 |")
out.append("| 50000 | 系统内部异常 |")
out.append("| 50001 | 操作失败（如重复点赞） |\n")

out.append("## 通用响应结构 BaseResponse\n")
out.append("```json")
out.append(json.dumps({"code": 0, "data": None, "message": "ok"}, ensure_ascii=False, indent=2))
out.append("```\n")

current_tag = None
for tag, method, path, op in endpoints:
    if tag != current_tag:
        out.append(f"\n---\n\n## {tag}\n")
        current_tag = tag
    summary = (op.get("description") or op.get("summary") or op.get("operationId", "") or "").strip()
    out.append(f"### {method_emoji(method)} `{path}`\n")
    out.append(f"**功能描述**：{summary}  ")
    out.append(f"**鉴权**：{auth_label(method, path)}\n")

    # 请求头
    out.append("**请求头**：\n")
    out.append("| Header | 说明 | 必填 |")
    out.append("| --- | --- | --- |")
    if (method, path) in PUBLIC:
        out.append("| Content-Type | application/json | POST/PUT 必填 |")
    else:
        out.append("| Content-Type | application/json | POST/PUT 必填 |")
        out.append("| Cookie | session_id=登录下发的会话ID | 是 |")
    out.append("")

    # 路径/查询参数
    rows = params_table(op)
    if rows:
        out.append("**路径参数**：\n")
        out.append(md_table(["参数名", "位置", "类型", "必填", "说明"], rows))
        out.append("")

    # 请求体
    bname, bschema = body_schema_info(op)
    if bschema and bschema.get("properties"):
        out.append(f"**请求体**：`{bname}`\n")
        out.append(md_table(
            ["参数名", "类型", "必填", "默认值", "说明"],
            fields_table(bschema),
        ))
        out.append("\n**请求体示例**：\n")
        out.append("```json")
        out.append(json.dumps(sample_object(bschema), ensure_ascii=False, indent=2))
        out.append("```\n")

    # 响应
    data_schema = unwrap_anyof(response_data_schema(op))
    out.append("**响应数据结构**：\n")
    if data_schema and ("$ref" in data_schema or data_schema.get("type") == "array"):
        if data_schema.get("type") == "array":
            inner = data_schema.get("items", {})
            inner_name = ref_name(inner["$ref"]) if "$ref" in inner else field_type(inner)
            out.append(f"`BaseResponse<array<{inner_name}>>`，`data` 为数组：\n")
            inner_schema = resolve_schema(inner)
            out.append(md_table(["参数名", "类型", "必填", "默认值", "说明"], fields_table(inner_schema)))
            out.append("\n**响应示例**：\n")
            out.append("```json")
            out.append(json.dumps({"code": 0, "message": "ok", "data": [sample_object(inner_schema)]}, ensure_ascii=False, indent=2))
            out.append("```\n")
        else:
            dname = ref_name(data_schema["$ref"])
            resolved = resolve_schema(data_schema)
            # 检测 PageResponse<X>：含有 records 字段
            rec_prop = resolved.get("properties", {}).get("records", {})
            if "records" in resolved.get("properties", {}):
                rec_items = rec_prop.get("items", {})
                inner_name = ref_name(rec_items["$ref"]) if "$ref" in rec_items else field_type(rec_items)
                inner_schema = resolve_schema(rec_items)
                out.append(f"`BaseResponse<PageResponse<{inner_name}>>`，`data`（`PageResponse<{inner_name}>`）字段结构：\n")
                out.append(md_table(["参数名", "类型", "必填", "默认值", "说明"], fields_table(resolved)))
                out.append(f"\n其中 `records` 为 `array<{inner_name}>`，`{inner_name}` 字段结构：\n")
                out.append(md_table(["参数名", "类型", "必填", "默认值", "说明"], fields_table(inner_schema)))
                out.append("\n**响应示例**：\n")
                out.append("```json")
                sample = {
                    "code": 0, "message": "ok",
                    "data": {"records": [sample_object(inner_schema)], "total": 1, "current": 1, "pageSize": 10},
                }
                out.append(json.dumps(sample, ensure_ascii=False, indent=2))
                out.append("```\n")
            else:
                out.append(f"`BaseResponse<{dname}>`，`data` 字段结构：\n")
                out.append(md_table(["参数名", "类型", "必填", "默认值", "说明"], fields_table(resolved)))
                out.append("\n**响应示例**：\n")
                out.append("```json")
                out.append(json.dumps({"code": 0, "message": "ok", "data": sample_object(resolved)}, ensure_ascii=False, indent=2))
                out.append("```\n")
    else:
        out.append("`BaseResponse<T>`，`data` 为基本类型（int/bool/null）。\n")
        out.append("**响应示例**：\n")
        out.append("```json")
        out.append(json.dumps({"code": 0, "message": "成功", "data": 1}, ensure_ascii=False, indent=2))
        out.append("```\n")

    out.append("**响应状态码**：HTTP 200（业务结果见响应体 `code` 字段）\n")

content = "\n".join(out)
target = Path(__file__).parent / "接口文档说明.md"
target.write_text(content, encoding="utf-8")
print(f"WRITTEN: {target}  ({len(content)} chars, {len(endpoints)} endpoints)")
