<script setup lang="ts">
import {ref, onMounted} from 'vue'
import axios from 'axios'
import {ElMessage, ElMessageBox} from 'element-plus'

// 当前活动页面 - 修改为默认显示菜单页面
const activePage = ref('menu')

// 菜品数据
const deliciousData = ref<any[]>([])
const loading = ref(false)

// 表单数据
const addForm = ref({
  name: '',
  price: '',
  src: ''
})

// 文件上传
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)

// 今日菜单相关
const todayMenuData = ref<any[]>([])
const selectedDate = ref(new Date().toISOString().split('T')[0]) // 默认今天

// 切换页面
const switchPage = (page: string) => {
  activePage.value = page
  if (page === 'today') {
    fetchTodayMenu()
  }
}

// 获取菜品数据
const fetchDeliciousData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/delicious-data/') // 去掉完整的 localhost:8000
    console.log('API返回数据:', response.data)
    deliciousData.value = response.data
  } catch (error) {
    console.error('获取菜品数据错误:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 处理点赞功能
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

    // 发送点赞请求到后端
    const response = await axios.post('/api/add-like/', { // 修改这里
      delicious_id: item.id,
      number: 1 // 每次点赞数量为1
    })

    if (response.data.success) {
      ElMessage.success('点亮成功！')
      // 可以在此处更新 deliciousData 中的点赞数 (如果需要实时反馈)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('点亮错误:', error)
      ElMessage.error('点亮失败')
    }
  }
}

// 获取今日菜单
const fetchTodayMenu = async () => {
  try {
    const response = await axios.get('/api/today-menu/', {
      params: {
        date: selectedDate.value
      }
    })
    todayMenuData.value = response.data
  } catch (error) {
    console.error('获取今日菜单错误:', error)
    ElMessage.error('获取今日菜单失败')
  }
}

// 处理日期变化
const handleDateChange = () => {
  fetchTodayMenu()
}

// 处理文件选择
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    if (!file.type.startsWith('image/')) {
      ElMessage.warning('请选择图片文件')
      return
    }

    const fileExtension = file.name.split('.').pop()
    const fileName = `${Date.now()}.${fileExtension}`
    addForm.value.src = fileName

    const formData = new FormData()
    formData.append('image', file)
    formData.append('filename', fileName)

    try {
      await axios.post('/api/upload-image/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      ElMessage.success('图片上传成功')
    } catch (error) {
      console.error('图片上传错误:', error)
      ElMessage.error('图片上传失败')
      addForm.value.src = ''
    }
  }
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 添加菜品
const handleAddDelicious = async () => {
  if (!addForm.value.name || !addForm.value.price) {
    ElMessage.warning('请填写菜品名称和价格')
    return
  }

  uploading.value = true
  try {
    // 如果没有上传图片，使用默认图片
    const imageSrc = addForm.value.src || 'desktop/neo1.jpg'

    const response = await axios.post('/add-delicious/', {
      name: addForm.value.name,
      price: parseFloat(addForm.value.price),
      src: imageSrc
    })

    if (response.data.success) {
      ElMessage.success('菜品添加成功')
      addForm.value = {name: '', price: '', src: ''}
      if (fileInput.value) {
        fileInput.value.value = ''
      }
      fetchDeliciousData()
    }
  } catch (error) {
    console.error('添加菜品错误:', error)
    ElMessage.error('添加菜品失败')
  } finally {
    uploading.value = false
  }
}

// 获取完整图片路径
const getImageUrl = (src: string) => {
  if (!src) {
    return '/desktop/neo1.jpg'
  }

  // 处理不同的图片路径格式
  if (src.startsWith('http')) {
    return src
  } else if (src.startsWith('/')) {
    return src
  } else if (src.startsWith('desktop/')) {
    return `/img/${src}`
  } else {
    return `/img/${src}`  // 所有图片都放在 /img/ 目录下
  }
}

// 改进图片错误处理
const handleImageError = (event: Event, fallbackSrc: string = '/desktop/neo1.jpg') => {
  const target = event.target as HTMLImageElement
  if (target.src !== fallbackSrc) {
    target.src = fallbackSrc
  }
}
// 页面加载时获取数据
onMounted(() => {
  fetchDeliciousData()
})
</script>

<template>
  <div class="dashboard-container">
    <div class="main-content">
      <div v-if="activePage === 'menu'" class="page-content menu-page">
        <h2>🍽️ 菜单展示</h2>
        <div class="menu-display-section">
          <div class="menu-display-header">
            <h3>全部菜品</h3>
            <div class="menu-stats">
              共 {{ deliciousData.length }} 道菜品
            </div>
          </div>

          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="deliciousData.length === 0" class="empty-state">
            <div class="empty-icon">😔</div>
            <p>暂无菜品，请先添加菜品</p>
          </div>
          <div v-else class="menu-cards-grid">
            <div
              v-for="item in deliciousData"
              :key="item.id"
              class="menu-card"
            >
              <div class="card-image">
                <img
                  :src="getImageUrl(item.src)"
                  :alt="item.name"
                  class="menu-image"
                  @error="handleImageError"
                >
                </div>

              <div class="card-content">
                <div class="card-header">
                  <h4 class="dish-name">{{ item.name }}</h4>
                </div>

                <div class="card-actions">
                  <span class="dish-price">¥{{ item.price }}</span>
                  <button
                    class="action-btn favorite"
                    @click="handleFavorite(item)"
                    aria-label="点赞"
                  >
                    ❤️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activePage === 'today'" class="page-content today-page">
        <h2>📅 今日菜单</h2>
        <div class="today-menu-section">
          <div class="date-selector">
            <label for="date-input">选择日期:</label>
            <input
              id="date-input"
              v-model="selectedDate"
              type="date"
              @change="handleDateChange"
              class="date-input"
            >
          </div>

          <div class="menu-display-header">
            <h3>{{ selectedDate }} 的精选</h3>
            <div class="menu-stats">
              共 {{ todayMenuData.length }} 道菜品
            </div>
          </div>

          <div v-if="todayMenuData.length === 0" class="empty-state">
            <div class="empty-icon">🤔</div>
            <p>该日期暂无菜单数据</p>
          </div>
          <div v-else class="menu-cards-grid">
            <div
              v-for="item in todayMenuData"
              :key="item.id"
              class="menu-card"
            >
              <div class="card-image">
                <img
                  :src="getImageUrl(item.src)"
                  :alt="item.name"
                  class="menu-image"
                  @error="handleImageError"
                >
              </div>
              <div class="card-content">
                <div class="card-header">
                  <h4 class="dish-name">{{ item.name }}</h4>
                </div>
                <div class="card-actions today-card-actions">
                  <span class="dish-price">¥{{ item.price }}</span>
                  <span class="vote-count">👍 {{ item.vote_count || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activePage === 'home'" class="page-content home-page">
        <h2>➕ 菜品录入</h2>
        <div class="add-form-section">
          <h3>添加新菜品</h3>
          <div class="form-container">
            <div class="form-group">
              <label for="dish-name">菜品名称:</label>
              <input
                id="dish-name"
                v-model="addForm.name"
                type="text"
                placeholder="请输入菜品名称"
                class="form-input"
              >
            </div>
            <div class="form-group">
              <label for="dish-price">价格:</label>
              <input
                id="dish-price"
                v-model="addForm.price"
                type="number"
                step="0.01"
                placeholder="请输入价格"
                class="form-input"
              >
            </div>
            <div class="form-group">
              <label>菜品图片:</label>
              <div class="file-upload-section">
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  @change="handleFileSelect"
                  style="display: none"
                >
                <button
                  @click="triggerFileInput"
                  class="upload-btn"
                  type="button"
                >
                  选择图片
                </button>
                <span class="file-name">{{ addForm.src || '未选择文件' }}</span>
              </div>
            </div>
            <button
              @click="handleAddDelicious"
              :disabled="uploading"
              class="submit-btn"
              type="button"
            >
              {{ uploading ? '上传中...' : '确认添加菜品' }}
            </button>
          </div>
        </div>
      </div>


    </div>
    <div class="bottom-menu">
        <div class="menu-section" :class="{ active: activePage === 'menu' }">
          <button class="menu-button" @click="switchPage('menu')">
            <i class="icon-menu"></i> 菜单
          </button>
        </div>
        <div class="today-section" :class="{ active: activePage === 'today' }">
          <button class="today-button" @click="switchPage('today')">
            <i class="icon-today"></i> 今日
          </button>
        </div>
        <div class="home-section" :class="{ active: activePage === 'home' }">
          <button class="home-button" @click="switchPage('home')">
            <i class="icon-add"></i> 添加
          </button>
        </div>
      </div>
  </div>
</template>

<style scoped>
/* =========================================================================
   1. CSS 变量 (Variables) - 定义颜色、字体、阴影等，方便统一管理和修改
   ========================================================================= */
:root {
  /* 颜色 */
  --color-primary: #007bff; /* 蓝色 - 主要操作 */
  --color-success: #28a745; /* 绿色 - 成功/确认 */
  --color-warning: #ff9800; /* 橙色 - 今日菜单 */
  --color-danger: #dc3545; /* 红色 - 点赞 */
  --color-background-light: #f4f6f9; /* 浅背景色 */
  --color-background-white: #ffffff; /* 白色背景 */
  --color-text-dark: #343a40; /* 深文本 */
  --color-text-secondary: #6c757d; /* 次要文本 */
  --color-border: #e9ecef; /* 边框色 */

  /* 阴影 */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 25px rgba(0, 0, 0, 0.15);

  /* 字体 */
  --font-family-sans: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* =========================================================================
   2. 全局容器和布局 (Global/Layout)
   ========================================================================= */
.dashboard-container {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background-light); /* 统一背景色 */
  font-family: var(--font-family-sans);
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  padding-bottom: 80px; /* 为底部导航栏留出空间 */
}

.page-content {
  max-width: 1000px;
  margin: 0 auto;
}

.page-content h2 {
  color: var(--color-text-dark);
  margin-bottom: 25px;
  padding-bottom: 10px;
  font-size: 28px;
  font-weight: 700;
  border-bottom: 3px solid var(--color-border);
}

/* =========================================================================
   3. 菜品卡片 (Menu/Delicious Card)
   ========================================================================= */
.menu-display-section,
.add-form-section,
.today-menu-section {
  background: var(--color-background-white);
  padding: 30px;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  margin-bottom: 30px;
}

.menu-display-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--color-border);
}

.menu-display-header h3 {
  color: var(--color-text-dark);
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.menu-stats {
  color: var(--color-text-secondary);
  font-size: 14px;
  background: var(--color-background-light);
  padding: 6px 12px;
  border-radius: 20px;
}

.menu-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.menu-card {
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background: var(--color-background-white);
}

.menu-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.card-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background-color: #eee;
}

.menu-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.menu-card:hover .menu-image {
  transform: scale(1.03);
}

.card-content {
  padding: 15px 20px;
}

.card-header {
  margin-bottom: 10px;
}

.dish-name {
  margin: 0;
  color: var(--color-text-dark);
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dish-price {
  color: var(--color-danger); /* 价格使用显眼的红色 */
  font-size: 22px;
  font-weight: 800;
}

.action-btn.favorite {
  width: 40px;
  height: 40px;
  background: var(--color-danger);
  color: white;
  transition: all 0.3s ease;
  font-size: 18px;
  border: none;
  border-radius: 50%;
  box-shadow: 0 2px 5px rgba(220, 53, 69, 0.4);
}

.action-btn.favorite:hover {
  background: #c82333;
  transform: scale(1.1);
  box-shadow: 0 4px 10px rgba(220, 53, 69, 0.6);
}

/* 今日菜单卡片动作 */
.today-card-actions {
  justify-content: space-between;
}

.vote-count {
  color: var(--color-text-dark);
  font-size: 15px;
  font-weight: 600;
  background: var(--color-background-light);
  padding: 6px 12px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* =========================================================================
   4. 添加菜品表单 (Add Dish Form)
   ========================================================================= */
.add-form-section h3 {
  color: var(--color-primary);
  margin-bottom: 25px;
  font-size: 20px;
  font-weight: 600;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group label {
  font-weight: 600;
  color: var(--color-text-dark);
  margin-bottom: 5px;
}

.form-input {
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.upload-btn {
  padding: 10px 18px;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease, transform 0.1s;
}

.upload-btn:hover {
  background-color: #0056b3;
}

.upload-btn:active {
  transform: scale(0.98);
}

.file-name {
  color: var(--color-text-secondary);
  font-size: 14px;
  flex-shrink: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.submit-btn {
  padding: 14px 24px;
  background-color: var(--color-success);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  margin-top: 15px;
  transition: background-color 0.3s ease, transform 0.1s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #218838;
}

.submit-btn:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}

/* =========================================================================
   5. 今日菜单 (Today Menu)
   ========================================================================= */
.date-selector {
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
}

.date-selector label {
  font-weight: 600;
  color: var(--color-text-dark);
  font-size: 16px;
}

.date-input {
  padding: 10px 15px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 16px;
  background-color: var(--color-background-light);
}

/* =========================================================================
   6. 底部导航栏 (Bottom Menu)
   ========================================================================= */
.bottom-menu {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 65px; /* 稍微增高 */
  display: flex;
  background-color: var(--color-background-white);
  border-top: 1px solid var(--color-border);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 1000;
}

.menu-section,
.home-section,
.today-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.menu-button,
.home-button,
.today-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 5px 10px;
  border: none;
  background-color: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 12px; /* 字体小一点 */
  font-weight: 500;
  transition: color 0.3s ease;
}

/* 底部导航栏活动状态 */
.menu-section.active .menu-button {
  color: var(--color-primary);
}

.today-section.active .today-button {
  color: var(--color-warning);
}

.home-section.active .home-button {
  color: var(--color-success);
}

/* 模拟图标 - 实际项目中推荐使用 Icon 库 */
.menu-button i, .today-button i, .home-button i {
  font-style: normal;
  font-size: 24px; /* 图标大一点 */
}
/* 替换为 Emoji 图标 */
.icon-menu::before { content: '🍜'; }
.icon-today::before { content: '🗓️'; }
.icon-add::before { content: '📝'; }

/* =========================================================================
   7. 辅助样式 (Utility/Empty State)
   ========================================================================= */
.loading, .empty-state {
  text-align: center;
  padding: 50px 20px;
  color: var(--color-text-secondary);
  font-size: 16px;
}
.empty-icon {
  font-size: 56px;
  margin-bottom: 10px;
}

/* 响应式调整 */
@media (max-width: 600px) {
  .menu-cards-grid {
    grid-template-columns: 1fr; /* 移动端改为单列 */
  }
  .main-content {
    padding: 15px;
    padding-bottom: 80px;
  }
  .page-content h2 {
    font-size: 24px;
    margin-bottom: 15px;
  }
}
</style>
