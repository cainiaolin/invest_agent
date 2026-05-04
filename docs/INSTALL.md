# 投资智能体系统 - 安装和部署指南

## 系统要求

- Python 3.11+
- Node.js 18+ (用于前端)
- Tushare Pro API Token

## 快速开始

### 1. 获取Tushare Token

1. 访问 [Tushare Pro](https://tushare.pro/register)
2. 注册并登录
3. 进入用户中心 -> 接口TOKEN
4. 复制您的Token

### 2. 后端安装

#### 使用Poetry (推荐)

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 克隆项目
git clone <repository_url>
cd invest_agent_by_graph

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

#### 使用pip

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# Linux/macOS
export TUSHARE_TOKEN="your_token_here"
export DATABASE_URL="sqlite+aiosqlite:///./data/invest_agent.db"

# Windows (PowerShell)
$env:TUSHARE_TOKEN="your_token_here"
$env:DATABASE_URL="sqlite+aiosqlite:///./data/invest_agent.db"

# 或创建 .env 文件
echo "TUSHARE_TOKEN=your_token_here" > .env
```

### 4. 验证安装

```bash
# 检查配置
invest-agent config

# 查看版本
invest-agent version
```

## CLI使用

### 分析股票

```bash
# 基本分析
invest-agent analyze 600519

# 指定Agent
invest-agent analyze 600519 --agent buffet

# 投票模式
invest-agent analyze 600519 --mode vote --agents buffet,graham,fisher

# 辩论模式
invest-agent analyze 600519 --mode debate --agents all
```

### 智能选股

```bash
# 全市场扫描
invest-agent screen all --agents all --top 20

# 行业筛选
invest-agent screen industry:银行 --agents buffet,graham --top 10

# 指数成分股
invest-agent screen index:沪深300 --agents fisher,lynch --top 30
```

### 策略回测

```bash
# 基本回测
invest-agent backtest 600519 --agent buffet --start-date 2020-01-01 --end-date 2024-12-31

# 自定义资金
invest-agent backtest 600519 --agent lynch --capital 5000000 --start-date 2020-01-01 --end-date 2024-12-31

# 比较多个Agent
for agent in buffet graham fisher; do
  invest-agent backtest 600519 --agent $agent --start-date 2020-01-01 --end-date 2024-12-31
done
```

## Web API部署

### 开发模式

```bash
# 启动API服务器
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# 访问API文档
# http://localhost:8000/docs
```

### 生产模式

```bash
# 使用gunicorn (Linux)
pip install gunicorn uvicorn
gunicorn app.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## 前端部署

### 开发模式

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

### 生产构建

```bash
# 构建
npm run build

# 输出在 dist/ 目录
```

### 使用Nginx部署

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Docker部署

### 使用Docker Compose (推荐)

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 服务端口

- API: http://localhost:8000
- 前端: http://localhost:80
- API文档: http://localhost:8000/docs

## 故障排查

### 常见问题

**1. Tushare连接失败**
```
错误: 连接失败
解决: 检查Token是否正确，网络是否通畅
```

**2. 股票数据为空**
```
错误: 无数据返回
解决: 检查股票代码格式（6位数字），确认股票存在
```

**3. Agent执行失败**
```
错误: Agent分析失败
解决: 查看日志确认具体错误，可能是数据获取失败
```

**4. Docker启动失败**
```
错误: 容器启动失败
解决: 检查端口占用，确保Docker服务运行
```

### 日志查看

```bash
# CLI调试
invest-agent --log-level DEBUG analyze 600519

# API日志
tail -f logs/api.log

# Docker日志
docker-compose logs -f api
```

## 性能优化

### 数据缓存

```python
# 在config.py中配置
class Settings(BaseSettings):
    cache_ttl: int = 3600  # 缓存1小时
```

### 并发限制

```python
# 限制同时分析的股票数量
MAX_CONCURRENT_ANALYSES = 5
```

### 数据库优化

```bash
# 使用PostgreSQL替代SQLite
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/invest_agent"
```

## 安全建议

1. **不要提交Token到版本控制**
   ```bash
   # .gitignore
   .env
   *.key
   ```

2. **使用环境变量管理敏感信息**
   ```bash
   export TUSHARE_TOKEN="xxx"
   ```

3. **生产环境启用HTTPS**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

4. **限制API访问频率**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

## 更新升级

```bash
# 更新依赖
poetry update

# 或
pip install --upgrade -r requirements.txt

# 前端更新
cd frontend
npm update
```

## 卸载

```bash
# 停止Docker服务
docker-compose down -v

# 删除虚拟环境
rm -rf venv
# 或
poetry env remove --all

# 删除数据
rm -rf data/
rm -rf logs/
```

## 支持

- 文档: [项目Wiki]
- 问题: [GitHub Issues]
- 讨论: [GitHub Discussions]
