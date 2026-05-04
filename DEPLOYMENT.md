# 部署指南

## Docker 部署

本项目提供完整的 Docker 部署方案，包括生产环境和开发环境配置。

### 快速开始

#### 1. 环境准备

确保已安装：
- Docker (20.10+)
- Docker Compose (2.0+)

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入必要的配置
# TUSHARE_TOKEN=your_token_here
# LLM_API_KEY=your_api_key_here
```

#### 3. 启动服务

**生产环境：**
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

**开发环境（热重载）：**
```bash
# 使用开发配置启动
docker-compose -f docker-compose.dev.yml up

# 或后台运行
docker-compose -f docker-compose.dev.yml up -d
```

### 服务架构

生产环境包含以下服务：

1. **api** (端口 8000): FastAPI 后端服务
2. **frontend** (端口 8501): Streamlit 前端界面
3. **db** (端口 5432): PostgreSQL 数据库
4. **redis** (端口 6379): Redis 缓存
5. **nginx** (端口 80/443): 反向代理

### 常用命令

```bash
# 停止所有服务
docker-compose down

# 停止并清理数据卷
docker-compose down -v

# 重新构建镜像
docker-compose build

# 重启特定服务
docker-compose restart api

# 查看服务日志
docker-compose logs -f api

# 进入容器调试
docker-compose exec api bash
```

### 使用 Makefile 简化操作

```bash
# 安装依赖（非 Docker）
make install

# Docker 构建
make docker-build

# Docker 启动
make docker-up      # 生产环境
make docker-dev     # 开发环境

# Docker 停止
make docker-down

# 查看日志
make docker-logs

# 清理 Docker 资源
make docker-clean
```

## 本地开发部署

### 1. 安装依赖

**Linux/Mac:**
```bash
bash install_deps.sh
```

**Windows:**
```powershell
# PowerShell
powershell -ExecutionPolicy Bypass -File install_deps.ps1
```

**手动安装:**
```bash
# 安装 Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env
```

### 3. 运行应用

**CLI 模式：**
```bash
poetry run invest-agent analyze 000001.SZ
```

**Web API 模式：**
```bash
poetry run uvicorn app.api.main:app --reload
```

**前端模式：**
```bash
poetry run streamlit run app/frontend/app.py
```

## 健康检查

### API 健康检查

```bash
# 检查 API 状态
curl http://localhost:8000/health

# 检查 API 文档
open http://localhost:8000/docs
```

### 容器健康检查

```bash
# 查看容器健康状态
docker-compose ps

# 查看健康检查日志
docker-compose logs api | grep health
```

## 故障排查

### 常见问题

1. **端口被占用**
   ```bash
   # 修改 docker-compose.yml 中的端口映射
   ports:
     - "8001:8000"  # 将主机端口改为 8001
   ```

2. **权限问题**
   ```bash
   # 确保 .env 文件权限正确
   chmod 644 .env
   ```

3. **依赖安装失败**
   ```bash
   # 清理缓存重新构建
   docker-compose build --no-cache
   ```

4. **数据库连接问题**
   ```bash
   # 检查数据库服务状态
   docker-compose logs db

   # 重新创建数据库
   docker-compose down -v
   docker-compose up -d db
   ```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs -f api

# 查看最近 100 行日志
docker-compose logs --tail=100 api
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看特定容器资源
docker stats invest-agent-api
```

## 生产环境建议

1. **安全性**
   - 使用强密码和密钥
   - 启用 HTTPS（配置 nginx SSL）
   - 定期更新依赖

2. **性能**
   - 配置 Redis 缓存
   - 使用 PostgreSQL 而非 SQLite
   - 启用 nginx 压缩

3. **监控**
   - 配置日志聚合
   - 设置告警规则
   - 定期备份数据

4. **扩展**
   - 使用 Docker Swarm 或 Kubernetes
   - 配置负载均衡
   - 实现服务发现

## 环境变量参考

完整的环境变量列表参见 `.env.example` 文件：

```env
# Tushare 数据源
TUSHARE_TOKEN=your_token

# LLM 配置
LLM_API_KEY=your_api_key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/invest.db
DB_USER=investuser
DB_PASSWORD=investpass
DB_NAME=investdb

# 日志
LOG_LEVEL=INFO
```

## 支持

如遇问题，请查看：
- 项目文档: `docs/`
- 日志文件: `logs/`
- GitHub Issues
