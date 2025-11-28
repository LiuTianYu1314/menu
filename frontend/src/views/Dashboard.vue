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
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 主页内容 - 添加菜品功能 -->
      <div v-if="activePage === 'home'" class="page-content home-page">
        <h2>菜品管理</h2>
        <!-- 添加菜品表单 -->
        <div class="add-form-section">
          <h3>添加新菜品</h3>
          <div class="form-container">
            <div class="form-group">
              <label>菜品名称:</label>
              <input
                v-model="addForm.name"
                type="text"
                placeholder="请输入菜品名称"
                class="form-input"
              >
            </div>
            <div class="form-group">
              <label>价格:</label>
              <input
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
            >
              {{ uploading ? '上传中...' : '添加菜品' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 菜单内容 - 菜品展示 -->
      <div v-else-if="activePage === 'menu'" class="page-content menu-page">
        <h2>菜品展示</h2>
        <div class="menu-display-section">
          <div class="menu-display-header">
            <h3>今日菜单</h3>
            <div class="menu-stats">
              共 {{ deliciousData.length }} 道菜品
            </div>
          </div>

          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="deliciousData.length === 0" class="empty-state">
            <div class="empty-icon">🍽️</div>
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
                <div class="card-overlay">
                  <button class="quick-view-btn">快速查看</button>
                </div>
              </div>

              <div class="card-content">
                <div class="card-header">
                  <h4 class="dish-name">{{ item.name }}</h4>
                  <span class="dish-price">¥{{ item.price }}</span>
                </div>

                <div class="card-actions">
                  <button
                    class="action-btn favorite"
                    @click="handleFavorite(item)"
                  >
                    ♥
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 今日菜单内容 -->
      <div v-else-if="activePage === 'today'" class="page-content today-page">
        <h2>今日菜单</h2>
        <div class="today-menu-section">
          <div class="date-selector">
            <label>选择日期:</label>
            <input
              v-model="selectedDate"
              type="date"
              @change="handleDateChange"
              class="date-input"
            >
          </div>

          <div class="menu-display-header">
            <h3>{{ selectedDate }} 的菜单</h3>
            <div class="menu-stats">
              共 {{ todayMenuData.length }} 道菜品
            </div>
          </div>

          <div v-if="todayMenuData.length === 0" class="empty-state">
            <div class="empty-icon">📅</div>
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
                  <span class="dish-price">¥{{ item.price }}</span>
                </div>
                <div class="today-stats">
                  <span class="vote-count">点赞数: {{ item.vote_count || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部菜单栏 -->
      <div class="bottom-menu">
        <div class="menu-section" :class="{ active: activePage === 'menu' }">
          <button class="menu-button" @click="switchPage('menu')">菜单</button>
        </div>
        <div class="home-section" :class="{ active: activePage === 'home' }">
          <button class="home-button" @click="switchPage('home')">添加菜品</button>
        </div>
        <div class="today-section" :class="{ active: activePage === 'today' }">
          <button class="today-button" @click="switchPage('today')">今日菜单</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 原有的样式保持不变，添加以下新样式 */
.dashboard-container {
  width: 100vw;
  height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f8f9fa;
}

.page-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-content h2 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

/* 主页样式 */
.welcome-section {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.welcome-section h3 {
  color: #333;
  margin-bottom: 15px;
}

.welcome-section p {
  color: #666;
  line-height: 1.6;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-card h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  opacity: 0.9;
}

.stat-card .number {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

/* 底部菜单栏 */
.bottom-menu {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  display: flex;
  background-color: #f5f5f5;
  border-top: 1px solid #ddd;
  z-index: 1000;
}

.menu-section,
.home-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background-color 0.3s ease;
}

.menu-section {
  border-right: 1px solid #ddd;
}

.menu-section.active {
  background-color: #e3f2fd;
}

.home-section.active {
  background-color: #e8f5e8;
}

.menu-button,
.home-button {
  padding: 10px 20px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}

.menu-button:hover,
.home-button:hover {
  background-color: #0056b3;
}

.menu-section.active .menu-button,
.home-section.active .home-button {
  background-color: #28a745;
  transform: scale(1.05);
}

/* 添加菜品表单样式 */
.add-form-section {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.add-form-section h3 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: #007bff;
}

.file-upload-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.upload-btn:hover {
  background-color: #0056b3;
}

.file-name {
  color: #666;
  font-size: 14px;
}

.submit-btn {
  padding: 12px 24px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  background-color: #218838;
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

/* 菜品列表样式 */
.delicious-list-section {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.delicious-list-section h3 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.delicious-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.delicious-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.delicious-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.image-container {
  width: 100%;
  height: 150px;
  overflow: hidden;
}

.delicious-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delicious-info {
  padding: 15px;
  text-align: center;
}

.delicious-name {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
}

.delicious-price {
  margin: 0;
  color: #e74c3c;
  font-size: 18px;
  font-weight: bold;
}

/* 菜单展示样式 */
.menu-display-section {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.menu-stats {
  color: #666;
  font-size: 14px;
  background: #f8f9fa;
  padding: 6px 12px;
  border-radius: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}

.menu-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.menu-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.menu-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.menu-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.menu-card:hover .menu-image {
  transform: scale(1.05);
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.menu-card:hover .card-overlay {
  opacity: 1;
}

.quick-view-btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s ease;
}

.quick-view-btn:hover {
  background: #0056b3;
}

.card-content {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.dish-name {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  flex: 1;
}

.dish-price {
  color: #e74c3c;
  font-size: 20px;
  font-weight: bold;
  margin-left: 10px;
}

.card-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #f8f9fa;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 16px;
}

.action-btn:hover {
  background: #007bff;
  color: white;
  transform: scale(1.1);
}

.action-btn.favorite:hover {
  background: #e74c3c;
}

.action-btn.share:hover {
  background: #28a745;
}

.action-btn.cart:hover {
  background: #ffc107;
  color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .menu-cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .dish-price {
    margin-left: 0;
  }
}

.menu-display-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.menu-display-header h3 {
  color: #333;
  margin: 0;
  font-size: 24px;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f8f9fa;
  padding-bottom: 80px; /* 添加底部内边距，避免被底部菜单覆盖 */
}
/* 今日菜单样式 */
.today-menu-section {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.date-selector {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-selector label {
  font-weight: 500;
  color: #333;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.today-stats {
  margin-top: 10px;
  text-align: center;
}

.vote-count {
  color: #666;
  font-size: 14px;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 12px;
}

/* 底部菜单栏调整 */
.bottom-menu {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  display: flex;
  background-color: #f5f5f5;
  border-top: 1px solid #ddd;
  z-index: 1000;
}

.menu-section,
.home-section,
.today-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background-color 0.3s ease;
  border-right: 1px solid #ddd;
}

.today-section {
  border-right: none;
}

.menu-section.active {
  background-color: #e3f2fd;
}

.home-section.active {
  background-color: #e8f5e8;
}

.today-section.active {
  background-color: #fff3e0;
}

.menu-button,
.home-button,
.today-button {
  padding: 10px 20px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}

.menu-button:hover,
.home-button:hover,
.today-button:hover {
  background-color: #0056b3;
}

.menu-section.active .menu-button {
  background-color: #28a745;
  transform: scale(1.05);
}

.home-section.active .home-button {
  background-color: #28a745;
  transform: scale(1.05);
}

.today-section.active .today-button {
  background-color: #ff9800;
  transform: scale(1.05);
}
</style>
