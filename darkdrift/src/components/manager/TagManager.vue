<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import AppPagination from '@/components/AppPagination.vue'
import { listTag, addTag, updateTag, deleteTag } from '@/api/tag'
import type { TagVO } from '@/types'

const tags = ref<TagVO[]>([])
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const toast = ref('')

const current = ref(1)
const pageSize = ref(20)
const total = ref(0)
const keyword = ref('')

// 新建表单
const addForm = reactive({
  name: '',
  color: '#4a90d9',
})
const addError = ref('')

// 编辑状态
const editingId = ref<number | null>(null)
const editForm = reactive({
  name: '',
  color: '#4a90d9',
})
const editError = ref('')

// 删除确认
const deletingId = ref<number | null>(null)

const PRESET_COLORS = [
  '#4a90d9',
  '#67c23a',
  '#e6a23c',
  '#f56c6c',
  '#909399',
  '#8e6ddc',
  '#13c2c2',
  '#eb2f96',
]

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => {
    toast.value = ''
  }, 2500)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await listTag({
      current: current.value,
      pageSize: pageSize.value,
      name: keyword.value || undefined,
      sortField: 'createTime',
      sortOrder: 'descend',
    })
    tags.value = res.records || []
    total.value = res.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function onSearch() {
  current.value = 1
  load()
}

function onPageChange(page: number) {
  current.value = page
  load()
}

function validateName(name: string): string {
  if (!name.trim()) return '标签名称不能为空'
  if (name.trim().length > 50) return '标签名称不能超过 50 个字符'
  return ''
}

async function handleAdd() {
  addError.value = validateName(addForm.name)
  if (addError.value) return
  submitting.value = true
  try {
    await addTag({
      name: addForm.name.trim(),
      color: addForm.color || undefined,
    })
    addForm.name = ''
    addForm.color = '#4a90d9'
    showToast('标签创建成功')
    await load()
  } catch (e: any) {
    addError.value = e?.message || '创建失败'
  } finally {
    submitting.value = false
  }
}

function startEdit(t: TagVO) {
  editingId.value = t.id
  editForm.name = t.name
  editForm.color = t.color || '#4a90d9'
  editError.value = ''
}

function cancelEdit() {
  editingId.value = null
  editError.value = ''
}

async function saveEdit(id: number) {
  editError.value = validateName(editForm.name)
  if (editError.value) return
  submitting.value = true
  try {
    await updateTag({
      id,
      name: editForm.name.trim(),
      color: editForm.color || undefined,
    })
    showToast('标签已更新')
    editingId.value = null
    await load()
  } catch (e: any) {
    editError.value = e?.message || '更新失败'
  } finally {
    submitting.value = false
  }
}

async function confirmDelete() {
  if (deletingId.value === null) return
  const id = deletingId.value
  submitting.value = true
  try {
    await deleteTag(id)
    showToast('标签已删除')
    deletingId.value = null
    // 删除后若当前页空了，回到上一页
    if (tags.value.length <= 1 && current.value > 1) {
      current.value -= 1
    }
    await load()
  } catch (e: any) {
    error.value = e?.message || '删除失败'
    deletingId.value = null
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="tag-manager">
    <div v-if="toast" class="toast toast-success">✅ {{ toast }}</div>
    <div v-if="error" class="banner banner-error mb-16">⚠️ {{ error }}</div>

    <!-- 新建标签 -->
    <div class="card mb-24">
      <h3 class="section-title">➕ 新建标签</h3>
      <div class="add-row">
        <input
          v-model="addForm.name"
          class="form-input"
          placeholder="输入标签名称"
          maxlength="50"
          @keyup.enter="handleAdd"
        />
        <div class="color-picker">
          <button
            v-for="c in PRESET_COLORS"
            :key="c"
            type="button"
            class="color-dot"
            :class="{ active: addForm.color === c }"
            :style="{ background: c }"
            :title="c"
            @click="addForm.color = c"
          />
          <input v-model="addForm.color" type="color" class="color-native" />
        </div>
        <button class="btn btn-primary" :disabled="submitting" @click="handleAdd">
          {{ submitting ? '提交中...' : '创建' }}
        </button>
      </div>
      <div v-if="addError" class="form-error">{{ addError }}</div>
    </div>

    <!-- 搜索 -->
    <div class="card mb-24">
      <div class="flex gap-12 flex-wrap items-center">
        <div class="form-item flex-1" style="margin-bottom: 0; min-width: 200px">
          <input
            v-model="keyword"
            class="form-input"
            placeholder="按名称搜索标签..."
            @keyup.enter="onSearch"
          />
        </div>
        <button class="btn btn-primary" :disabled="loading" @click="onSearch">搜索</button>
      </div>
    </div>

    <!-- 标签列表 -->
    <div class="card">
      <div class="flex justify-between items-center mb-16">
        <h3 class="section-title">🏷️ 标签列表 ({{ total }})</h3>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="tags.length === 0" class="empty">暂无标签</div>

      <div v-else class="tag-table">
        <div class="tag-row tag-row-header">
          <div class="col-name">名称</div>
          <div class="col-color">颜色</div>
          <div class="col-count">文章数</div>
          <div class="col-time">创建时间</div>
          <div class="col-actions">操作</div>
        </div>
        <div v-for="t in tags" :key="t.id" class="tag-row">
          <template v-if="editingId === t.id">
            <div class="col-name">
              <input v-model="editForm.name" class="form-input" maxlength="50" />
              <div v-if="editError" class="form-error">{{ editError }}</div>
            </div>
            <div class="col-color">
              <div class="color-picker small">
                <button
                  v-for="c in PRESET_COLORS"
                  :key="c"
                  type="button"
                  class="color-dot"
                  :class="{ active: editForm.color === c }"
                  :style="{ background: c }"
                  @click="editForm.color = c"
                />
                <input v-model="editForm.color" type="color" class="color-native" />
              </div>
            </div>
            <div class="col-count">{{ t.article_count }}</div>
            <div class="col-time">—</div>
            <div class="col-actions">
              <button
                class="btn btn-primary btn-sm"
                :disabled="submitting"
                @click="saveEdit(t.id)"
              >
                保存
              </button>
              <button class="btn btn-outline btn-sm" :disabled="submitting" @click="cancelEdit">
                取消
              </button>
            </div>
          </template>
          <template v-else>
            <div class="col-name">
              <span
                class="tag-chip"
                :style="{
                  background: `${t.color || '#4a90d9'}22`,
                  color: t.color || '#4a90d9',
                  borderColor: `${t.color || '#4a90d9'}66`,
                }"
              >
                #{{ t.name }}
              </span>
            </div>
            <div class="col-color">
              <span class="color-block" :style="{ background: t.color || '#4a90d9' }"></span>
              <span class="color-text">{{ t.color || '默认' }}</span>
            </div>
            <div class="col-count">{{ t.article_count }}</div>
            <div class="col-time">{{ t.createTime?.slice(0, 10) || '—' }}</div>
            <div class="col-actions">
              <button class="btn btn-outline btn-sm" @click="startEdit(t)">编辑</button>
              <button class="btn btn-danger btn-sm" @click="deletingId = t.id">删除</button>
            </div>
          </template>
        </div>
      </div>

      <AppPagination
        :current="current"
        :page-size="pageSize"
        :total="total"
        @change="onPageChange"
      />
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="deletingId !== null" class="modal-mask" @click.self="deletingId = null">
      <div class="modal card">
        <h3 class="modal-title">确认删除</h3>
        <p class="modal-body">
          确认删除该标签吗？删除后与文章的关联将解除，此操作不可撤销。
        </p>
        <div class="modal-actions">
          <button class="btn btn-outline" :disabled="submitting" @click="deletingId = null">
            取消
          </button>
          <button class="btn btn-danger" :disabled="submitting" @click="confirmDelete">
            {{ submitting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.add-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.add-row .form-input {
  flex: 1;
  min-width: 180px;
}

.color-picker {
  display: flex;
  align-items: center;
  gap: 6px;
}

.color-picker.small .color-dot {
  width: 18px;
  height: 18px;
}

.color-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition:
    transform 0.15s ease,
    border-color 0.15s ease;
}

.color-dot:hover {
  transform: scale(1.1);
}

.color-dot.active {
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px var(--bg-card);
}

.color-native {
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid var(--border-base);
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
}

.loading,
.empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.tag-table {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tag-row {
  display: grid;
  grid-template-columns: 1.5fr 1.2fr 0.6fr 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 12px 8px;
  border-bottom: 1px solid var(--border-lighter);
  font-size: 13px;
}

.tag-row:last-child {
  border-bottom: none;
}

.tag-row-header {
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-subtle);
  border-radius: 6px;
  padding: 10px 8px;
}

.tag-chip {
  display: inline-block;
  padding: 3px 12px;
  border: 1px solid;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 500;
}

.color-block {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 6px;
  vertical-align: middle;
  border: 1px solid var(--border-light);
}

.color-text {
  font-size: 12px;
  color: var(--text-tertiary);
}

.col-actions {
  display: flex;
  gap: 8px;
}

.banner-error {
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.toast {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 200;
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 14px;
  box-shadow: var(--shadow-hover);
  animation: toast-in 0.25s ease;
}

.toast-success {
  background: var(--success);
  color: #fff;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
  padding: 16px;
}

.modal {
  width: 100%;
  max-width: 420px;
  padding: 24px;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.modal-body {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .tag-row {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .tag-row-header {
    display: none;
  }

  .col-name::before {
    content: '名称: ';
    font-weight: 600;
    color: var(--text-tertiary);
  }

  .col-color::before {
    content: '颜色: ';
    font-weight: 600;
    color: var(--text-tertiary);
  }

  .col-count::before {
    content: '文章数: ';
    font-weight: 600;
    color: var(--text-tertiary);
  }

  .col-time {
    grid-column: span 2;
  }

  .col-actions {
    grid-column: span 2;
  }
}
</style>
