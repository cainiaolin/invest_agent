<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <el-icon><TrendCharts /></el-icon>
          投资智能体系统
        </h1>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          router
        >
          <el-menu-item index="/analyze">
            <el-icon><Aim /></el-icon>
            <span>个股分析</span>
          </el-menu-item>
          <el-menu-item index="/screen">
            <el-icon><Search /></el-icon>
            <span>智能选股</span>
          </el-menu-item>
          <el-menu-item index="/backtest">
            <el-icon><DataAnalysis /></el-icon>
            <span>策略回测</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { TrendCharts, Aim, Search, DataAnalysis } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-container {
  height: 100vh;
  background: #f5f7fa;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  margin: 0 40px 0 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-main {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
</style>
