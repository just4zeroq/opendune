# OpenDune 数据采集平台

.PHONY: help install dev-up dev-down test lint format type-check build clean

# 默认目标
help:
	@echo "OpenDune 可用命令:"
	@echo "  make install         - 安装依赖"
	@echo "  make dev-up          - 启动开发环境"
	@echo "  make dev-down        - 停止开发环境"
	@echo "  make test            - 运行测试"
	@echo "  make test-coverage   - 运行测试并生成覆盖率报告"
	@echo "  make lint            - 代码检查"
	@echo "  make format          - 代码格式化"
	@echo "  make type-check      - 类型检查"
	@echo "  make build           - 构建Docker镜像"
	@echo "  make clean           - 清理环境"
	@echo "  make logs            - 查看日志 (SERVICE=<service_name>)"
	@echo "  make init-db         - 初始化数据库"
	@echo "  make start-collector - 启动数据采集器"
	@echo "  make start-api       - 启动API服务"

# 安装依赖
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# 开发环境
dev-up:
	docker-compose up -d
	@echo "等待服务启动..."
	@sleep 10
	@echo "开发环境已启动"
	@echo "- Kafka UI: http://localhost:8080"
	@echo "- Grafana: http://localhost:3000"
	@echo "- API Docs: http://localhost:8000/docs"

dev-down:
	docker-compose down

dev-down-clean:
	docker-compose down -v

# 测试
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

# 代码质量
lint:
	flake8 src/ tests/ --max-line-length=100
	pylint src/ --max-line-length=100 --disable=R,C

format:
	black src/ tests/ --line-length=100
	isort src/ tests/ --profile black

type-check:
	mypy src/ --ignore-missing-imports

# 构建
build:
	docker-compose build

# 日志
logs:
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose logs -f; \
	else \
		docker-compose logs -f $(SERVICE); \
	fi

# 数据库
init-db:
	python scripts/init_db.py

# 启动服务
start-collector:
	python scripts/start_collector.py

start-api:
	python scripts/start_api.py

# 清理
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# 前端 (Vue)
frontend-install:
	cd src/data_visualization/web && npm install

frontend-dev:
	cd src/data_visualization/web && npm run dev

frontend-build:
	cd src/data_visualization/web && npm run build
