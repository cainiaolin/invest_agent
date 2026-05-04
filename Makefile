.PHONY: help install deps lint test build docker-build docker-up docker-down docker-logs clean

# 默认目标
help:
	@echo "投资智能 Agent - 常用命令"
	@echo ""
	@echo "依赖管理:"
	@echo "  make install     - 安装项目依赖"
	@echo "  make deps        - 更新依赖锁文件"
	@echo ""
	@echo "代码质量:"
	@echo "  make lint        - 运行代码检查 (ruff + mypy)"
	@echo "  make test        - 运行测试"
	@echo "  make format      - 格式化代码 (black)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    - 构建 Docker 镜像"
	@echo "  make docker-up       - 启动服务 (生产环境)"
	@echo "  make docker-dev      - 启动服务 (开发环境)"
	@echo "  make docker-down     - 停止服务"
	@echo "  make docker-logs     - 查看服务日志"
	@echo "  make docker-clean    - 清理 Docker 资源"
	@echo ""
	@echo "其他:"
	@echo "  make clean        - 清理临时文件"
	@echo "  make build        - 构建项目"

# 依赖安装
install:
	@echo "安装项目依赖..."
	poetry install

deps:
	@echo "更新依赖锁文件..."
	poetry lock
	poetry install

# 代码质量检查
lint:
	@echo "运行 ruff 检查..."
	poetry run ruff check app/
	@echo "运行 mypy 类型检查..."
	poetry run mypy app/

test:
	@echo "运行测试..."
	poetry run pytest tests/ -v

format:
	@echo "格式化代码..."
	poetry run black app/
	poetry run ruff check --fix app/

# Docker 命令
docker-build:
	@echo "构建 Docker 镜像..."
	docker-compose build

docker-up:
	@echo "启动服务 (生产环境)..."
	docker-compose up -d

docker-dev:
	@echo "启动服务 (开发环境)..."
	docker-compose -f docker-compose.dev.yml up

docker-down:
	@echo "停止服务..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	@echo "清理 Docker 资源..."
	docker-compose down -v
	docker system prune -f

# 清理
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/

# 构建
build:
	@echo "构建项目..."
	poetry build
