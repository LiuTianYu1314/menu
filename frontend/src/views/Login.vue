<!-- src/views/Login.vue -->
<template>
  <div class="login-container">
    <!-- 背景图片 -->
    <div class="background-image"></div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="card-header">
        <h2>用户登录</h2>
        <p>欢迎回来，请登录您的账户</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <div class="input-group">
            <span class="input-icon">
              <i class="icon-user">👤</i>
            </span>
            <input
              type="text"
              v-model="loginForm.account"
              required
              placeholder="请输入账号"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-group">
          <div class="input-group">
            <span class="input-icon">
              <i class="icon-lock">🔒</i>
            </span>
            <input
              type="password"
              v-model="loginForm.password"
              required
              placeholder="请输入密码"
              class="form-input"
            />
          </div>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="login-btn"
          :class="{ 'loading': loading }"
        >
          <span v-if="!loading">登录</span>
          <span v-else class="loading-spinner">
            <div class="spinner"></div>
            登录中...
          </span>
        </button>
        <div v-if="errorMessage" class="error-message">
          <i class="error-icon">⚠️</i>
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          <i class="success-icon">✅</i>
          {{ successMessage }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      loginForm: {
        account: '',
        password: ''
      },
      rememberMe: false,
      loading: false,
      errorMessage: '',
      successMessage: ''
    }
  },
  mounted() {
    const savedAccount = localStorage.getItem('rememberedAccount')
    if (savedAccount) {
      this.loginForm.account = savedAccount
      this.rememberMe = true
    }
  },
  methods: {
    async handleLogin() {
      if (!this.loginForm.account.trim()) {
        this.errorMessage = '请输入账号'
        return
      }

      if (!this.loginForm.password) {
        this.errorMessage = '请输入密码'
        return
      }

      this.loading = true
      this.errorMessage = ''
      this.successMessage = ''

      try {
        if (this.rememberMe) {
          localStorage.setItem('rememberedAccount', this.loginForm.account)
        } else {
          localStorage.removeItem('rememberedAccount')
        }

        const response = await axios.post('/api/login/', this.loginForm)

        if (response.data.success) {
          this.successMessage = '登录成功！'

          localStorage.setItem('token', response.data.token)
          localStorage.setItem('user', JSON.stringify(response.data.user))

          setTimeout(() => {
            if (this.loginForm.account === 'root' && this.loginForm.password === 'root') {
              this.router.push('/root')
            } else {
              this.router.push('/dashboard')
            }
          }, 1000)
        } else {
          this.errorMessage = response.data.message || '登录失败'
        }
      } catch (error) {
        if (error.response) {
          this.errorMessage = error.response.data.message || '登录失败，请检查账号密码'
        } else if (error.request) {
          this.errorMessage = '网络连接失败，请检查网络设置'
        } else {
          this.errorMessage = '发生未知错误，请稍后重试'
        }
        console.error('登录错误:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 背景图片样式 */
.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/desktop/001.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -1;
}

/* 登录卡片样式 */
.login-card {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow:
    0 15px 35px rgba(0, 0, 0, 0.1),
    0 5px 15px rgba(0, 0, 0, 0.07);
  width: 100%;
  max-width: 420px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.8rem;
  font-weight: 600;
}

.card-header p {
  color: #7f8c8d;
  font-size: 0.95rem;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  z-index: 2;
  font-size: 1.1rem;
}

.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 1rem;
  background: #fff;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  transform: translateY(-1px);
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #555;
}

.remember-me input {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.3s ease;
}

.remember-me input:checked + .checkmark {
  background-color: #3498db;
  border-color: #3498db;
}

.remember-me input:checked + .checkmark::after {
  content: '✓';
  color: white;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
}

.forgot-password {
  color: #3498db;
  text-decoration: none;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #2980b9;
  text-decoration: underline;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 7px 14px rgba(102, 126, 234, 0.3);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 注册链接 */
.register-link {
  text-align: center;
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.register-link a {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

/* 消息提示 */
.error-message,
.success-message {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.error-message {
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.success-message {
  background-color: #efe;
  color: #363;
  border: 1px solid #cfc;
}

/* 社交登录 */
.social-login {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.divider {
  text-align: center;
  margin-bottom: 1rem;
  position: relative;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #eee;
  z-index: 1;
}

.divider span {
  background: rgba(255, 255, 255, 0.95);
  padding: 0 1rem;
  position: relative;
  z-index: 2;
}

.social-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.social-btn {
  width: 50px;
  height: 50px;
  border: 2px solid #e9ecef;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.social-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.social-btn.wechat:hover {
  border-color: #09bb07;
  background: #09bb07;
  color: white;
}

.social-btn.qq:hover {
  border-color: #12b7f5;
  background: #12b7f5;
  color: white;
}

.social-btn.weibo:hover {
  border-color: #e6162d;
  background: #e6162d;
  color: white;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    margin: 1rem;
    padding: 2rem 1.5rem;
  }

  .card-header h2 {
    font-size: 1.5rem;
  }
}
</style>
