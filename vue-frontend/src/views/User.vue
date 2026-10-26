<template>
  <div class="account-settings-page">
    <el-card class="settings-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2 class="title">账号设置</h2>
          <span class="subtitle">管理你的个人资料和账号安全</span>
        </div>
      </template>

      <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-width="100px"
          label-position="top"
          class="settings-form"
      >
        <div class="form-layout">
          <!-- 左侧：头像区域 -->
          <div class="avatar-section">
            <div class="avatar-wrapper">
              <!-- 原生 img 标签，加载失败自动降级。注意这里去掉了模板里的 getAvatarUrl 计算 -->
              <img
                v-if="formData.avatar && !imgError"
                :src="formData.avatar"
                class="user-avatar-img"
                alt="头像"
                @error="handleImgError"
              />
              <!-- 兜底显示文字首字母 -->
              <div v-else class="user-avatar-text">
                {{ formData.name?.charAt(0) || '用' }}
              </div>

              <div class="avatar-upload-btn">
                <el-upload
                    action="#"
                    :show-file-list="false"
                    :auto-upload="false"
                    accept="image/*"
                    :before-upload="beforeAvatarUpload"
                    @change="handleAvatarChange"
                >
                  <el-button type="primary" circle :icon="Camera" size="small"/>
                </el-upload>
              </div>
            </div>
            <p class="avatar-tip">点击图标更换头像</p>
          </div>

          <!-- 右侧：表单区域 -->
          <div class="info-section">
            <el-row :gutter="24">
              <!-- 第一排：用户名 & 真实姓名 -->
              <el-col :xs="24" :sm="12">
                <el-form-item label="用户名 (Username)">
                  <el-input v-model="formData.username" disabled/>
                </el-form-item>
              </el-col>

              <el-col :xs="24" :sm="12">
                <el-form-item label="真实姓名" prop="name">
                  <el-input v-model="formData.name" placeholder="请输入真实姓名" clearable/>
                </el-form-item>
              </el-col>

              <!-- 第二排：电子邮箱 & 手机号码 (非必填) -->
              <el-col :xs="24" :sm="12">
                <el-form-item label="电子邮箱" prop="email">
                  <el-input v-model="formData.email" placeholder="请输入邮箱地址 (选填)" clearable/>
                </el-form-item>
              </el-col>

              <el-col :xs="24" :sm="12">
                <el-form-item label="手机号码" prop="phone">
                  <el-input v-model="formData.phone" placeholder="请输入手机号 (选填)" maxlength="11" clearable/>
                </el-form-item>
              </el-col>

              <!-- 第三排：账号角色 & 账号状态 -->
              <el-col :xs="24" :sm="12">
                <el-form-item label="账号角色">
                  <div class="readonly-tag">
                    <el-tag :type="roleTagType" effect="light" round>
                      {{ roleLabel }}
                    </el-tag>
                  </div>
                </el-form-item>
              </el-col>

              <el-col :xs="24" :sm="12">
                <el-form-item label="账号状态">
                  <div class="readonly-tag">
                    <el-tag :type="String(formData.status) === '1' ? 'success' : 'danger'" effect="plain" round>
                      <el-icon class="status-icon">
                        <CircleCheck v-if="String(formData.status) === '1'"/>
                        <CircleClose v-else/>
                      </el-icon>
                      {{ String(formData.status) === '1' ? '正常使用中' : '账号已禁用' }}
                    </el-tag>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <div class="form-actions">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">保存修改</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { Camera, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { getUserInfoApi, updateUserInfoApi } from '@/api/user'
import { uploadFileApi } from '@/api/file'
import { ref, reactive, onMounted, computed } from 'vue'
import { useUser } from '@/utils/user'
import { ElMessage } from 'element-plus'

const { updateUser } = useUser()
const loading = ref(false)
const submitting = ref(false)
const formRef = ref()
const imgError = ref(false) // 控制图片加载失败的降级状态

// 表单数据模型
const formData = reactive({
  id: '',
  username: '',
  name: '',
  role: '',
  email: '',
  phone: '',
  avatar: '',
  status: ''
})

// 保存初始数据快照
let initialFormData = {}

// 角色文本映射
const roleLabel = computed(() => {
  const map = { admin: '管理员', student: '学生', user: '普通用户' }
  return map[formData.role] || '未知角色'
})

// 角色标签颜色映射
const roleTagType = computed(() => {
  const map = { admin: 'danger', student: 'warning', user: 'primary' }
  return map[formData.role] || 'info'
})

// 表单校验规则（邮箱和手机号非必填，但校验格式）
const rules = reactive({
  name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
})

// 图片加载失败时的兜底逻辑
const handleImgError = () => {
  console.warn('图片加载失败，已降级显示文字。请检查图片路径:', formData.avatar)
  imgError.value = true
}

// 上传前校验
const beforeAvatarUpload = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!imageTypes.includes(file.type)) {
    ElMessage.error('只能上传 JPG/PNG/GIF/WEBP 格式的图片')
    return false
  }
  if (file.size / 1024 / 1024 > 2) {
    ElMessage.error('上传图片大小不能超过 2MB')
    return false
  }
  return true
}

// 处理头像选择与上传
const handleAvatarChange = async (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  if (!beforeAvatarUpload(file)) return

  // 1. 本地预览
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.avatar = e.target.result
    imgError.value = false // 🔴 关键：重置错误状态，允许显示新图
  }
  reader.readAsDataURL(file)

  // 2. 上传服务器
  try {
    const res = await uploadFileApi(file)

    if (res.code === 200 && res.data?.url) {
      // 🔴 关键：在赋值时处理 URL，加上时间戳防止浏览器死读 304 缓存
      let finalUrl = res.data.url
      if (!finalUrl.startsWith('http') && !finalUrl.startsWith('/')) {
        finalUrl = '/' + finalUrl
      }
      const timestamp = new Date().getTime()
      finalUrl = finalUrl.includes('?') ? `${finalUrl}&t=${timestamp}` : `${finalUrl}?t=${timestamp}`

      formData.avatar = finalUrl
      imgError.value = false // 🔴 确保状态无误
      ElMessage.success('头像上传成功')
    } else {
      ElMessage.warning('上传成功，但未获取到有效URL，已保留本地预览')
    }
  } catch (error) {
    console.error('头像上传接口报错:', error)
    ElMessage.error('头像上传失败，但已保留本地预览')
  }
}

// 加载用户信息
const loadUserInfo = async () => {
  loading.value = true
  imgError.value = false // 🔴 重置错误状态
  try {
    const res = await getUserInfoApi()
    if (res.code === 200) {
      let finalUrl = res.data.avatar || ''
      // 如果是网络地址，加上时间戳
      if (finalUrl && !finalUrl.startsWith('data:image')) {
        if (!finalUrl.startsWith('http') && !finalUrl.startsWith('/')) {
          finalUrl = '/' + finalUrl
        }
        const timestamp = new Date().getTime()
        finalUrl = finalUrl.includes('?') ? `${finalUrl}&t=${timestamp}` : `${finalUrl}?t=${timestamp}`
      }

      // 合并数据
      Object.assign(formData, res.data, { avatar: finalUrl })
      // 保存初始快照
      initialFormData = JSON.parse(JSON.stringify(formData))
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  imgError.value = false
  Object.assign(formData, JSON.parse(JSON.stringify(initialFormData)))
  ElMessage.info('已恢复至初始状态')
}

// 提交修改
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    // 剥离时间戳，防止把 ?t=xxx 存入数据库
    const payload = JSON.parse(JSON.stringify(formData))
    if (payload.avatar && payload.avatar.includes('?t=')) {
      payload.avatar = payload.avatar.split('?t=')[0]
    }

    const res = await updateUserInfoApi(payload)

    if (res.code === 200 || res.code === undefined) {
      ElMessage.success('个人信息更新成功')

      try {
        updateUser(res.data || payload)
      } catch (err) {
        console.error('更新本地全局用户状态失败:', err)
      }

      // 更新快照
      initialFormData = JSON.parse(JSON.stringify(formData))
    } else {
      ElMessage.error(res.message || '更新失败')
    }
  } catch (error) {
    console.error('真实的网络请求异常:', error)
    ElMessage.error(error.message || '网络请求异常，请稍后重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.account-settings-page {
  max-width: 960px;
  margin: 0 auto;
  animation: fade-in 0.3s ease;
}

.settings-card {
  border-radius: var(--radius-lg, 12px);
  border: 1px solid var(--border, #eaedf3);
  background-color: var(--bg-card, #ffffff);
}

.card-header {
  padding: 8px 0;
}

.card-header .title {
  margin: 0;
  font-size: 18px;
  color: var(--text-main, #1f2937);
  font-weight: 600;
}

.card-header .subtitle {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: var(--text-sub, #8892a0);
}

/* 布局 */
.form-layout {
  display: flex;
  gap: 40px;
  margin-bottom: 32px;
}

/* 左侧头像 */
.avatar-section {
  flex: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 160px;
}

.avatar-wrapper {
  position: relative;
  margin-bottom: 12px;
  /* 确保外层有宽高，不会被内层撑开变形 */
  width: 120px;
  height: 120px;
}

/* 原生图片样式，绝对居中裁切 */
.user-avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--bg-page, #f6f7fb);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background-color: var(--brand-weak, #fff1ec);
  display: block;
}

/* 默认文字样式 */
.user-avatar-text {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 500;
  background: var(--brand-weak, #fff1ec);
  color: var(--brand, #ff7a59);
  border: 3px solid var(--bg-page, #f6f7fb);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.avatar-upload-btn {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: var(--bg-card, #fff);
  border-radius: 50%;
  padding: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-upload-btn :deep(.el-button) {
  --el-button-bg-color: var(--brand, #ff7a59);
  --el-button-border-color: var(--brand, #ff7a59);
  --el-button-hover-bg-color: var(--brand-dark, #ef5b3a);
  --el-button-hover-border-color: var(--brand-dark, #ef5b3a);
}

.avatar-tip {
  font-size: 12px;
  color: var(--text-sub, #8892a0);
  text-align: center;
  margin: 0;
}

/* 右侧表单 */
.info-section {
  flex: 1;
  min-width: 0;
}

.readonly-tag {
  display: flex;
  align-items: center;
  height: 32px;
}

.status-icon {
  vertical-align: middle;
  margin-right: 4px;
}

:deep(.el-form-item__label) {
  color: var(--text-main, #1f2937);
  font-weight: 500;
  padding-bottom: 4px;
}

:deep(.el-input__wrapper) {
  border-radius: var(--radius-md, 10px);
  box-shadow: 0 0 0 1px var(--border, #eaedf3) inset;
  background-color: var(--bg-page, #f6f7fb);
  transition: all 0.2s;
}

:deep(.el-input__wrapper.is-focus) {
  background-color: var(--bg-card, #fff);
  box-shadow: 0 0 0 1px var(--brand, #ff7a59) inset;
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: var(--bg-page, #f6f7fb);
  box-shadow: none;
  opacity: 0.7;
}

/* 底部按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid var(--border, #eaedf3);
}

.form-actions :deep(.el-button--primary) {
  background-color: var(--brand, #ff7a59);
  border-color: var(--brand, #ff7a59);
  border-radius: var(--radius-md, 10px);
}

.form-actions :deep(.el-button--primary:hover) {
  background-color: var(--brand-dark, #ef5b3a);
  border-color: var(--brand-dark, #ef5b3a);
}

.form-actions :deep(.el-button) {
  border-radius: var(--radius-md, 10px);
}

/* 响应式 */
@media (max-width: 768px) {
  .form-layout {
    flex-direction: column;
    align-items: center;
    gap: 24px;
  }

  .avatar-section {
    width: 100%;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .form-actions :deep(.el-button) {
    width: 100%;
    margin-left: 0;
    margin-top: 8px;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>