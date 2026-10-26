<template>
  <div class="register-container">
    <!-- 左侧：品牌展示区 -->
    <div class="register-left">
      <div class="brand-info">
        <div class="brand-logo">🐾</div>
        <h1>暖爪</h1>
        <p>加入我们，给毛孩子一个家</p>
        <div class="slogan">领养代替购买，让爱回家 🏡</div>
      </div>

      <!-- 装饰背景 -->
      <div class="floating-emoji emoji-1">🐶</div>
      <div class="floating-emoji emoji-2">🐱</div>
      <div class="floating-emoji emoji-3">🐾</div>
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
    </div>

    <!-- 右侧：注册表单区 -->
    <div class="register-right">
      <div class="register-form-wrapper">
        <div class="form-header">
          <h2>创建账号 ✨</h2>
          <p>只需几秒钟，开启你的领养之旅</p>
        </div>

        <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="register-form"
            size="large"
            @keyup.enter="handleRegister"
        >
          <!-- 用户名 -->
          <el-form-item prop="username">
            <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名（3-20个字符）"
                :prefix-icon="User"
                clearable
            />
          </el-form-item>

          <!-- 密码 -->
          <el-form-item prop="password">
            <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="设置密码（6-20位）"
                :prefix-icon="Lock"
                show-password
            />
          </el-form-item>

          <!-- 注册按钮 -->
          <el-form-item>
            <el-button
                type="primary"
                class="submit-btn"
                :loading="loadingValue"
                @click="handleRegister"
            >
              注 册
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 底部跳转登录 -->
        <div class="form-footer">
          <span>已有账号？</span>
          <router-link style="color: var(--el-color-primary)" to="/login">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive} from 'vue'
import {useRouter} from 'vue-router'
import {User, Lock} from '@element-plus/icons-vue'
import {ElMessage} from 'element-plus'
import {registerApi} from "@/api/register.js";

const router = useRouter()
const registerFormRef = ref(null)
const loadingValue = ref(false)

// 表单数据
const registerForm = reactive({
  username: '',
  password: '',
})

// 校验规则
const registerRules = {
  username: [
    {required: true, message: '请输入用户名', trigger: 'blur'},
    {min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur'},
  ],
  password: [
    {required: true, message: '请设置密码', trigger: 'blur'},
    {min: 6, max: 20, message: '密码长度为 6 到 20 位', trigger: 'blur'},
  ],
}

// 注册提交
const handleRegister = () => {
  if (!registerFormRef.value) return

  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loadingValue.value = true
      try {
        // 加上 await，等待请求返回真实数据
        const res = await registerApi(registerForm)

        if (res.code === 200) {
          ElMessage.success('注册成功')
          await router.push('/login')
        } else {
          // 这里改用 res.msg 或者 res.message，取决于你后端的字段
          ElMessage.error(res.message || '注册失败')
        }
      } catch (error) {
        console.error(error)
        ElMessage.error('网络请求失败，请稍后重试') // 增加异常提示
      } finally {
        loadingValue.value = false // 统一在这里关闭 loading
      }
    }
  })
}

</script>

<style scoped>
/* =========================================================
 * 基础布局
 * =======================================================*/
.register-container {
  display: flex;
  height: 100vh;
  height: 100dvh;
  background-color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* =========================================================
 * 左侧：品牌展示区
 * =======================================================*/
.register-left {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  color: #fff;
  overflow: hidden;
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
  letter-spacing: 2px;
}

.slogan {
  display: inline-block;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  font-size: 14px;
  backdrop-filter: blur(4px);
}

/* 装饰性圆圈 */
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

/* 漂浮的宠物 emoji */
.floating-emoji {
  position: absolute;
  font-size: 40px;
  opacity: 0.4;
  filter: blur(1px);
  animation: float 6s ease-in-out infinite;
}

.emoji-1 {
  top: 20%;
  left: 15%;
  animation-delay: 0s;
}

.emoji-2 {
  bottom: 25%;
  right: 20%;
  font-size: 50px;
  animation-delay: 2s;
}

.emoji-3 {
  top: 30%;
  right: 25%;
  font-size: 30px;
  animation-delay: 4s;
}

/* =========================================================
 * 右侧：注册表单区
 * =======================================================*/
.register-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
  padding: 40px;
}

.register-form-wrapper {
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

/* 注册按钮 */
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
  margin-top: 10px;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 107, 74, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 底部跳转登录 */
.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #8892a0;
}

.to-login-link {
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

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

/* =========================================================
 * 响应式适配
 * =======================================================*/
@media (max-width: 992px) {
  .register-left {
    flex: 0 0 45%;
  }

  .brand-info h1 {
    font-size: 28px;
  }
}

@media (max-width: 768px) {
  .register-left {
    display: none;
  }

  .register-right {
    padding: 20px;
    background: linear-gradient(180deg, #fff9f6 0%, #ffffff 100%);
  }

  .register-form-wrapper {
    background: #ffffff;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  }
}
</style>