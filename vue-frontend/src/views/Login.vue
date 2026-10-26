<template>
  <div class="login-container">
    <!-- 左侧：品牌展示区 -->
    <div class="login-left">
      <div class="brand-info">
        <div class="brand-logo">🐾</div>
        <h1>暖爪</h1>
        <p>智能宠物领养平台</p>
        <div class="slogan">领养代替购买，让爱回家 🏡</div>
      </div>

      <!-- 装饰背景 -->
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>

    <!-- 右侧：登录表单区 -->
    <div class="login-right">
      <div class="login-form-wrapper">
        <div class="form-header">
          <h2>欢迎回来 👋</h2>
          <p>请登录你的账号，继续寻找你的毛孩子</p>
        </div>

        <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            size="large"
            @keyup.enter="handleLogin"
        >
          <!-- 账号输入框 -->
          <el-form-item prop="username">
            <el-input
                v-model="loginForm.username"
                placeholder="请输入账号或手机号"
                :prefix-icon="User"
                clearable
            />
          </el-form-item>

          <!-- 密码输入框 -->
          <el-form-item prop="password">
            <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
                clearable
            />
          </el-form-item>

          <!-- 辅助功能 -->
          <div class="form-options">
            <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
            <el-link type="primary" underline="never" class="forgot-pwd">忘记密码？</el-link>
          </div>

          <!-- 登录按钮 -->
          <el-form-item>
            <el-button
                type="primary"
                class="submit-btn"
                :loading="loadingValue"
                @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>还没有账号？</span>
          <router-link style="color: var(--el-color-primary)" to="/register">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { loginApi } from "@/api/login.js"
// 1. 补上缺失的导入
import { useUser } from '@/utils/user'

const router = useRouter()
const { saveLoginData } = useUser() // 2. 解构出保存方法

const loginFormRef = ref(null)
const loadingValue = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false,
})

const loginRules = {
  username: [
    { required: true, message: '请输入账号或手机号', trigger: 'blur' },
    { min: 3, max: 20, message: '账号长度应在 3 到 20 个字符之间', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  // 3. 先进行前端表单校验
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loadingValue.value = true
      try {
        const res = await loginApi(loginForm)
        if (res.code === 200) {
          saveLoginData(res.data)
          ElMessage.success('登录成功')
          router.push('/manager/home')
        } else {
          ElMessage.error(res.message || '账号或密码错误')
        }
      } catch (error) {
        // 网络异常处理（通常 axios 拦截器会处理，这里留个底）
        console.error(error)
      } finally {
        // 4. 使用 finally，无论成功失败都会关闭 loading
        loadingValue.value = false
      }
    } else {
      ElMessage.warning('请检查表单填写是否完整')
    }
  })
}
</script>

<style scoped>
/* =========================================================
 * 基础布局
 * =======================================================*/
.login-container {
  display: flex;
  height: 100vh;
  height: 100dvh;
  background-color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* =========================================================
 * 左侧：品牌展示区
 * =======================================================*/
.login-left {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  color: #fff;
  overflow: hidden;
  /* 在大屏幕下占据 55% 宽度 */
  flex: 0 0 55%;
}

.brand-info {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 0 40px;
  animation: fadeIn 0.8s ease;
}

.brand-logo {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: grid;
  place-items: center;
  font-size: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.brand-info h1 {
  font-size: 36px;
  margin: 0 0 10px;
  letter-spacing: 2px;
  font-weight: 700;
}

.brand-info p {
  font-size: 16px;
  margin: 0 0 30px;
  opacity: 0.9;
  letter-spacing: 4px;
}

.slogan {
  display: inline-block;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  font-size: 14px;
  backdrop-filter: blur(4px);
}

/* 背景装饰圆圈 */
.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  right: -50px;
  background: rgba(255, 255, 255, 0.12);
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  left: 10%;
  background: rgba(255, 255, 255, 0.05);
}

/* =========================================================
 * 右侧：登录表单区
 * =======================================================*/
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
  padding: 40px;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
  animation: slideUp 0.6s ease;
}

.form-header {
  margin-bottom: 30px;
}

.form-header h2 {
  font-size: 28px;
  color: #1f2937;
  margin: 0 0 10px;
}

.form-header p {
  font-size: 14px;
  color: #8892a0;
  margin: 0;
}

/* 覆写 Element Plus 输入框样式 */
:deep(.el-input__wrapper) {
  padding: 8px 15px;
  border-radius: 12px;
  background-color: #f4f6fa;
  box-shadow: none;
  border: 1px solid transparent;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:hover) {
  background-color: #eef1f7;
}

:deep(.el-input__wrapper.is-focus) {
  background-color: #ffffff;
  border-color: #ff7a59;
  box-shadow: 0 0 0 3px rgba(255, 122, 89, 0.15);
}

:deep(.el-input__inner) {
  color: #1f2937;
  font-size: 14px;
}

:deep(.el-input__prefix-inner) {
  color: #8892a0;
}

/* 辅助功能区 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  margin-top: -10px;
}

:deep(.el-checkbox__label) {
  color: #4b5563;
  font-size: 14px;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #ff7a59;
  border-color: #ff7a59;
}

.forgot-pwd {
  font-size: 14px;
}

/* 登录按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #ff8f6b, #ff6b4a);
  border: none;
  box-shadow: 0 6px 16px rgba(255, 107, 74, 0.3);
  transition: all 0.2s;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 107, 74, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 底部跳转 */
.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #8892a0;
}

.form-footer .el-link {
  font-size: 14px;
  font-weight: 600;
  margin-left: 4px;
}

/* =========================================================
 * 动画
 * =======================================================*/
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* =========================================================
 * 响应式适配
 * =======================================================*/
@media (max-width: 992px) {
  .login-left {
    flex: 0 0 45%;
  }

  .brand-info h1 {
    font-size: 28px;
  }
}

@media (max-width: 768px) {
  /* 小屏幕隐藏左侧品牌区，表单占满全屏 */
  .login-left {
    display: none;
  }

  .login-right {
    padding: 20px;
    background: linear-gradient(180deg, #fff9f6 0%, #ffffff 100%);
  }

  .login-form-wrapper {
    background: #ffffff;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  }
}
</style>