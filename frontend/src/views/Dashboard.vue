<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 当前活动页面 - 默认显示添加页面 (home)
const activePage = ref('home')

// 菜品数据
const deliciousData = ref<any[]>([])
const loading = ref(false)

// 表单数据
const addForm = ref({
  name: '',
  price: '',
  src: ''
})

// 图片预览地址
const imagePreview = ref('')
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)

// 今日菜单相关
const todayMenuData = ref<any[]>([])
const selectedDate = ref(new Date().toISOString().split('T')[0])

// 切换页面
const switchPage = (page: string) => {
  activePage.value = page
  if (page === 'today') {
    fetchTodayMenu()
  } else if (page === 'menu') {
    fetchDeliciousData()
  }
}

// 获取全部菜品
const fetchDeliciousData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/delicious-data/')
    deliciousData.value = response.data
  } catch (error) {
    console.error('获取菜品数据错误:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 点赞/选择功能
const handleFavorite = async (item: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要吃香喷喷的 ${item.name} 吗！`,
      '确认点亮',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await axios.post('/api/add-like/', {
      delicious_id: item.id,
      number: 1
    })

    if (response.data.success) {
      ElMessage.success('点亮成功！')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('点亮失败')
    }
  }
}

// 获取今日菜单
const fetchTodayMenu = async () => {
  try {
    const response = await axios.get('/api/today-menu/', {
      params: { date: selectedDate.value }
    })
    todayMenuData.value = response.data
  } catch (error) {
    ElMessage.error('获取今日菜单失败')
  }
}

// 处理图片选择与预览
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    if (!file.type.startsWith('image/')) {
      ElMessage.warning('请选择图片文件')
      return
    }

    // 创建本地预览 URL
    imagePreview.value = URL.createObjectURL(file)

    const fileExtension = file.name.split('.').pop()
    const fileName = `${Date.now()}.${fileExtension}`
    addForm.value.src = fileName

    const formData = new FormData()
    formData.append('image', file)
    formData.append('filename', fileName)

    try {
      await axios.post('/api/upload-image/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ElMessage.success('图片上传成功')
    } catch (error) {
      ElMessage.error('图片上传失败')
      addForm.value.src = ''
      imagePreview.value = ''
    }
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

// 提交新菜品
const handleAddDelicious = async () => {
  if (!addForm.value.name || !addForm.value.price) {
    ElMessage.warning('请填写菜品名称和价格')
    return
  }

  uploading.value = true
  try {
    const imageSrc = addForm.value.src || 'desktop/neo1.jpg'

    const response = await axios.post('/api/add-delicious/', {
      name: addForm.value.name,
      price: parseFloat(addForm.value.price),
      src: imageSrc
    })

    if (response.data.success) {
      ElMessage.success('🎉 菜品添加成功！')
      // 重置表单
      addForm.value = { name: '', price: '', src: '' }
      imagePreview.value = ''
      if (fileInput.value) fileInput.value.value = ''
    }
  } catch (error) {
    ElMessage.error('添加失败，请重试')
  } finally {
    uploading.value = false
  }
}

const getImageUrl = (src: string) => {
  if (!src) return '/desktop/neo1.jpg'
  if (src.startsWith('http') || src.startsWith('/')) return src
  return `/img/${src}`
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/desktop/neo1.jpg'
}

onMounted(() => {
  fetchDeliciousData()
})
</script>

<template>
  <div class="dashboard-container">
    <div class="main-content">

      <div v-if="activePage === 'home'" class="page-content home-page">
        <div class="page-header">
          <h2>✨ 新增美味</h2>
          <p class="subtitle">录入新菜品，丰富你的美食库</p>
        </div>

        <div class="add-form-container">
          <div class="upload-preview-card" @click="triggerFileInput">
            <div v-if="imagePreview" class="preview-wrapper">
              <img :src="imagePreview" class="preview-img" />
              <div class="change-overlay">更换图片</div>
            </div>
            <div v-else class="upload-placeholder">
              <div class="upload-icon">📸</div>
              <span>点击上传菜品图片</span>
              <p class="upload-hint">支持 jpg, png 格式</p>
            </div>
            <input ref="fileInput" type="file" accept="image/*" @change="handleFileSelect" style="display: none">
          </div>

          <div class="form-fields-card">
            <div class="form-group">
              <label>菜品名称</label>
              <div class="input-wrapper">
                <span class="input-icon">🍜</span>
                <input v-model="addForm.name" type="text" placeholder="例如：宫保鸡丁" class="nice-input">
              </div>
            </div>

            <div class="form-group">
              <label>售卖价格 (元)</label>
              <div class="input-wrapper">
                <span class="input-icon">💰</span>
                <input v-model="addForm.price" type="number" step="0.01" placeholder="0.00" class="nice-input">
              </div>
            </div>

            <div class="form-info">
              <p>💡 小贴士：好名字和美图更有吸引力哦！</p>
            </div>

            <button @click="handleAddDelicious" :disabled="uploading" class="glow-submit-btn">
              <span v-if="!uploading">🚀 确认发布菜品</span>
              <span v-else>正在努力上传...</span>
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="activePage === 'menu'" class="page-content menu-page">
        <div class="page-header">
          <h2>🍽️ 菜单展示</h2>
        </div>
        <div class="menu-display-section">
          <div class="menu-display-header">
            <h3>全部菜品</h3>
            <div class="menu-stats">共 {{ deliciousData.length }} 道菜品</div>
          </div>

          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="deliciousData.length === 0" class="empty-state">
            <div class="empty-icon">😔</div>
            <p>暂无菜品，请先去添加吧</p>
          </div>
          <div v-else class="menu-cards-grid">
            <div v-for="item in deliciousData" :key="item.id" class="menu-card">
              <div class="card-image">
                <img :src="getImageUrl(item.src)" :alt="item.name" class="menu-image" @error="handleImageError">
              </div>
              <div class="card-content">
                <div class="card-header">
                  <h4 class="dish-name">{{ item.name }}</h4>
                </div>
                <div class="card-actions">
                  <span class="dish-price">¥{{ item.price }}</span>
                  <button class="action-btn favorite" @click="handleFavorite(item)">❤️</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activePage === 'today'" class="page-content today-page">
        <div class="page-header">
          <h2>📅 今日精选</h2>
        </div>
        <div class="today-menu-section">
          <div class="date-selector">
            <label>选择日期:</label>
            <input v-model="selectedDate" type="date" @change="fetchTodayMenu" class="date-input">
          </div>

          <div v-if="todayMenuData.length === 0" class="empty-state">
            <div class="empty-icon">🤔</div>
            <p>该日期暂无数据</p>
          </div>
          <div v-else class="menu-cards-grid">
            <div v-for="item in todayMenuData" :key="item.id" class="menu-card">
              <div class="card-image">
                <img :src="getImageUrl(item.src)" class="menu-image" @error="handleImageError">
              </div>
              <div class="card-content">
                <h4 class="dish-name">{{ item.name }}</h4>
                <div class="card-actions today-card-actions">
                  <span class="dish-price">¥{{ item.price }}</span>
                  <span class="vote-count">👍 {{ item.vote_count || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <div class="bottom-menu">
      <div class="nav-item" :class="{ active: activePage === 'menu' }" @click="switchPage('menu')">
        <i class="icon">🍜</i>
        <span>菜单</span>
      </div>
      <div class="nav-item" :class="{ active: activePage === 'today' }" @click="switchPage('today')">
        <i class="icon">🗓️</i>
        <span>今日</span>
      </div>
      <div class="nav-item" :class="{ active: activePage === 'home' }" @click="switchPage('home')">
        <i class="icon">📝</i>
        <span>添加</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 基础变量 */
:root {
  --primary: #007bff;
  --success: #28a745;
  --bg-light: #f8f9fc;
  --text-dark: #2d3436;
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dashboard-container {
  width: 100vw;
  min-height: 100vh;
  background-color: #f4f7f6;
  font-family: 'PingFang SC', sans-serif;
}

.main-content {
  padding: 20px;
  padding-bottom: 90px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header h2 {
  font-size: 26px;
  color: var(--text-dark);
  margin-bottom: 8px;
}

.subtitle {
  color: #636e72;
  font-size: 14px;
  margin-bottom: 25px;
}

/* 添加页面布局 */
.add-form-container {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 30px;
  animation: fadeIn 0.5s ease;
}

/* 图片预览上传卡片 */
.upload-preview-card {
  aspect-ratio: 1/1;
  background: white;
  border: 2px dashed #dcdfe6;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: var(--shadow);
}

.upload-preview-card:hover {
  border-color: #409eff;
  background: #f0f7ff;
}

.upload-placeholder {
  text-align: center;
  color: #909399;
}

.upload-icon { font-size: 50px; margin-bottom: 10px; }
.upload-hint { font-size: 12px; margin-top: 5px; opacity: 0.7; }

.preview-wrapper { position: relative; width: 100%; height: 100%; }
.preview-img { width: 100%; height: 100%; object-fit: cover; }
.change-overlay {
  position: absolute; bottom: 0; width: 100%; padding: 8px;
  background: rgba(0,0,0,0.6); color: white; text-align: center; font-size: 13px;
}

/* 表单填报卡片 */
.form-fields-card {
  background: white;
  padding: 30px;
  border-radius: 20px;
  box-shadow: var(--shadow);
}

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 8px; color: #333; }

.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 12px; font-size: 18px; }

.nice-input {
  width: 100%; padding: 12px 12px 12px 42px;
  border: 1px solid #e0e0e0; border-radius: 12px;
  font-size: 16px; background: #fbfbfb; transition: all 0.3s;
}

.nice-input:focus {
  outline: none; border-color: #409eff; background: white;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.1);
}

.form-info {
  margin: 20px 0; padding: 12px; background: #fff9db;
  border-left: 4px solid #fcc419; border-radius: 4px; font-size: 13px; color: #856404;
}

.glow-submit-btn {
  width: 100%; padding: 16px; border: none; border-radius: 12px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white; font-size: 18px; font-weight: bold; cursor: pointer;
  transition: all 0.3s; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.glow-submit-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4); }
.glow-submit-btn:disabled { background: #ccc; box-shadow: none; cursor: not-allowed; }

/* 菜单展示通用样式 */
.menu-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.menu-card {
  background: white; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: transform 0.3s;
}
.menu-card:hover { transform: translateY(-5px); }
.card-image { height: 180px; width: 100%; }
.menu-image { width: 100%; height: 100%; object-fit: cover; }
.card-content { padding: 15px; }
.dish-name { margin: 0 0 10px; font-size: 18px; }
.card-actions { display: flex; justify-content: space-between; align-items: center; }
.dish-price { font-size: 20px; font-weight: bold; color: #e74c3c; }
.action-btn.favorite {
  border: none; background: #ff7675; color: white;
  width: 36px; height: 36px; border-radius: 50%; cursor: pointer;
}

/* 底部导航 */
.bottom-menu {
  position: fixed; bottom: 0; left: 0; width: 100%; height: 70px;
  background: white; display: flex; border-top: 1px solid #eee;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05); z-index: 100;
}

.nav-item {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; cursor: pointer;
  color: #95a5a6; transition: all 0.3s;
}

.nav-item .icon { font-size: 24px; margin-bottom: 2px; }
.nav-item span { font-size: 12px; }

.nav-item.active { color: #409eff; font-weight: bold; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 手机端适配 */
@media (max-width: 600px) {
  .add-form-container { grid-template-columns: 1fr; }
  .upload-preview-card { max-width: 200px; margin: 0 auto; }
  .menu-cards-grid { grid-template-columns: 1fr 1fr; }
  .dish-name { font-size: 14px; }
  .dish-price { font-size: 16px; }
}
</style>
