<template>
  <div class="root-container">
    <!-- 顶部按钮区域 -->
    <div class="header-buttons">
      <el-button
        type="primary"
        class="menu-btn"
        :class="{ active: currentView === 'user' }"
        @click="switchView('user')"
      >
        用户管理
      </el-button>
      <el-button
        type="success"
        class="menu-btn"
        :class="{ active: currentView === 'menu' }"
        @click="switchView('menu')"
      >
        菜单管理
      </el-button>
    </div>

    <!-- 用户管理界面 -->
    <div v-if="currentView === 'user'" class="view-container">
      <el-card class="table-card">
        <template #header>
          <div class="card-header">
            <span>用户账号</span>
            <div>
              <el-button type="primary" @click="fetchPswData">刷新数据</el-button>
              <el-button type="success" @click="showAddDialog = true">添加账号</el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="pswData"
          :style="{ width: '100%' }"
          v-loading="loading"
          empty-text="暂无数据"
        >
          <el-table-column prop="account" label="账号"></el-table-column>
          <el-table-column prop="password" label="密码"></el-table-column>
          <el-table-column prop="time" label="创建时间">
            <template #default="scope">
              {{ formatDateTime(scope.row.time) || 'N/A' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteUser(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <div class="stats">
        共 {{ pswData.length }} 条记录
      </div>
    </div>

    <!-- 菜单管理界面 -->
    <div v-if="currentView === 'menu'" class="view-container">
      <el-card class="table-card">
        <template #header>
          <div class="card-header">
            <span>菜单管理</span>
            <div>
              <el-button type="primary" @click="fetchMenuData">刷新数据</el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="menuData"
          :style="{ width: '100%' }"
          v-loading="menuLoading"
          empty-text="暂无数据"
        >
          <el-table-column prop="name" label="菜品名称"></el-table-column>
          <el-table-column prop="price" label="价格">
            <template #default="scope">
              ¥{{ scope.row.price }}
            </template>
          </el-table-column>
          <el-table-column prop="src" label="图片链接">
            <template #default="scope">
              <el-link type="primary" :href="scope.row.src" target="_blank">
                查看图片
              </el-link>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteMenu(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <div class="stats">
        共 {{ menuData.length }} 条记录
      </div>
    </div>

    <!-- 添加账号对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加账号"
      width="400px"
      :before-close="handleCloseDialog"
    >
      <el-form
        :model="addForm"
        :rules="formRules"
        ref="addFormRef"
        label-width="80px"
      >
        <el-form-item label="账号" prop="account">
          <el-input
            v-model="addForm.account"
            placeholder="请输入账号"
            clearable
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="addForm.password"
            type="password"
            placeholder="请输入密码"
            clearable
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button type="primary" @click="handleAddAccount" :loading="adding">
            {{ adding ? '添加中...' : '确认添加' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, reactive} from 'vue'
import axios from 'axios'
import {
  ElButton,
  ElCard,
  ElTable,
  ElTableColumn,
  ElMessage,
  ElMessageBox,
  ElForm,
  ElFormItem,
  ElInput,
  ElDialog,
  ElLink
} from 'element-plus'
import type {FormInstance, FormRules} from 'element-plus'

// 定义数据类型
interface PswRecord {
  id: number
  account: string
  password: string
  time?: string
}

interface MenuRecord {
  id: number
  name: string
  price: string
  src: string
}

interface AddForm {
  account: string
  password: string
}

// 响应式数据
const currentView = ref<'user' | 'menu'>('user')
const pswData = ref<PswRecord[]>([])
const menuData = ref<MenuRecord[]>([])
const loading = ref(false)
const menuLoading = ref(false)
const adding = ref(false)
const showAddDialog = ref(false)
const addFormRef = ref<FormInstance>()

const addForm = reactive<AddForm>({
  account: '',
  password: ''
})

// 切换视图
const switchView = (view: 'user' | 'menu') => {
  currentView.value = view
  if (view === 'user') {
    fetchPswData()
  } else {
    fetchMenuData()
  }
}

// 获取PSW数据库数据
const fetchPswData = async () => {
  loading.value = true
  try {
    const response = await axios.get('api/psw-data/')
    pswData.value = response.data
  } catch (error) {
    console.error('获取PSW数据错误:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 获取菜单数据
const fetchMenuData = async () => {
  menuLoading.value = true
  try {
    const response = await axios.get('/api/menu-data/')
    menuData.value = response.data
  } catch (error) {
    console.error('获取菜单数据错误:', error)
    ElMessage.error('获取菜单数据失败')
  } finally {
    menuLoading.value = false
  }
}

// 添加账号
const handleAddAccount = async () => {
  if (!addFormRef.value) return

  try {
    await addFormRef.value.validate()
  } catch (error) {
    ElMessage.warning('请完善表单信息')
    return
  }

  adding.value = true
  try {
    const response = await axios.post('/api/add-psw-account/', {
      account: addForm.account,
      password: addForm.password
    })

    if (response.data.success) {
      ElMessage.success('账号添加成功')
      handleCloseDialog()
      fetchPswData()
    }
  } catch (error) {
    console.error('添加账号错误:', error)
    ElMessage.error('添加账号失败')
  } finally {
    adding.value = false
  }
}

// 格式化日期时间
const formatDateTime = (dateTimeStr: string) => {
  if (!dateTimeStr) return 'N/A'

  try {
    const date = new Date(dateTimeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return 'N/A'
  }
}

// 表单验证规则
const formRules = reactive<FormRules>({
  account: [
    {required: true, message: '请输入账号', trigger: 'blur'},
    {min: 2, max: 20, message: '账号长度在 2 到 20 个字符', trigger: 'blur'}
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 2, max: 20, message: '密码长度至少 2 个字符', trigger: 'blur'}
  ]
})

// 删除用户账号
const handleDeleteUser = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个账号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/delete-psw-account/${id}/`)
    ElMessage.success('删除成功')
    fetchPswData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除账号错误:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 删除菜单
const handleDeleteMenu = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个菜单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/delete-menu/${id}/`)
    ElMessage.success('删除成功')
    fetchMenuData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除菜单错误:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 关闭对话框
const handleCloseDialog = () => {
  showAddDialog.value = false
  if (addFormRef.value) {
    addFormRef.value.resetFields()
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchPswData()
})
</script>

<style scoped>
.root-container {
  padding: 20px;
}

.header-buttons {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.menu-btn {
  padding: 12px 24px;
  font-size: 16px;
  transition: all 0.3s;
}

.menu-btn.active {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.table-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats {
  margin-top: 15px;
  text-align: right;
  color: #666;
  font-size: 14px;
}

.view-container {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
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
