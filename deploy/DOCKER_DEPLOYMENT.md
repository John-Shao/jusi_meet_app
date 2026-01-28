# Docker 部署指南

本项目依赖于独立的 `jusi_infrastructure` 基础设施项目，该项目提供共享的 MySQL 和 Redis 服务。

## 前置条件

在启动登录服务之前，需要先启动基础设施服务。

### 启动基础设施项目

```bash
# 1. 进入基础设施项目目录（jusi_infrastructure 项目位于同级目录）
cd ../jusi_infrastructure

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库和 Redis 密码

# 3. 启动基础设施服务（MySQL 和 Redis）
docker-compose up -d

# 4. 检查服务状态
docker-compose ps

# 5. 查看日志确认服务正常
docker-compose logs -f
```

基础设施服务只需启动一次，可被多个业务服务共享使用。

---

## 部署登录服务

### 方案一：使用 Docker Compose（推荐）

确保基础设施服务已启动后，部署登录服务：

```bash
# 1. 返回登录服务项目目录
cd ../jusi_login_server

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置应用相关配置

# 3. 启动登录服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

**优点**：
- 多个服务共享 MySQL 和 Redis
- 节省资源
- 数据统一管理
- 服务可以独立启停
- 基础设施与业务代码解耦

---

### 方案二：传统部署方式（备用）

如果需要在项目内管理所有服务，可以使用传统方式：

```bash
# 使用包含所有服务的配置文件
docker-compose -f docker-compose.app.yml up -d
```

---

## 部署其他业务服务

其他业务服务也可以连接到同一个基础设施，只需在 `docker-compose.yml` 中配置相同的网络。

### 其他服务的配置示例

```yaml
version: '3.8'

services:
  your_service:
    build: .
    container_name: your_service_name
    environment:
      # 使用共享的数据库和缓存（通过容器名访问）
      DB_HOST: jusi_mysql
      DB_PORT: 3306
      DB_USER: jusi
      DB_PASSWORD: your_db_password
      DB_NAME: jusi_db
      REDIS_HOST: jusi_redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: your_redis_password
    ports:
      - "9000:9000"
    networks:
      - jusi_shared_network

networks:
  jusi_shared_network:
    external: true
    name: jusi_shared_network
```

启动其他服务：

```bash
cd /path/to/other/service
docker-compose up -d
```

---

## 服务架构

### 项目结构

```
workspace/
├── jusi_infrastructure/         # 基础设施项目（独立）
│   ├── docker-compose.yml       # MySQL + Redis
│   ├── .env                     # 基础设施配置
│   └── init-scripts/            # 数据库初始化脚本
│
├── jusi_login_server/          # 登录服务（本项目）
│   ├── docker-compose.yml      # 登录服务应用
│   └── .env                    # 应用配置
│
└── other_services/             # 其他业务服务
    ├── service_a/
    └── service_b/
```

### 共享基础设施架构

```
┌─────────────────────────────────────────────────────────────┐
│                jusi_shared_network                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  jusi_infrastructure/docker-compose.yml              │  │
│  │  ┌────────────────┐  ┌────────────────┐             │  │
│  │  │ MySQL          │  │ Redis          │             │  │
│  │  │ jusi_mysql     │  │ jusi_redis     │             │  │
│  │  │ Port: 3306     │  │ Port: 6379     │             │  │
│  │  └────────────────┘  └────────────────┘             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  jusi_login_server/docker-compose.yml                │  │
│  │  ┌────────────────────────────────────┐              │  │
│  │  │  Login Server                      │              │  │
│  │  │  Port: 8000                        │              │  │
│  │  └────────────────────────────────────┘              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Other Service 1                                     │  │
│  │  ┌────────────────────────────────────┐              │  │
│  │  │  API Server                        │              │  │
│  │  │  Port: 9000                        │              │  │
│  │  └────────────────────────────────────┘              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Other Service 2                                     │  │
│  │  ┌────────────────────────────────────┐              │  │
│  │  │  Message Server                    │              │  │
│  │  │  Port: 10000                       │              │  │
│  │  └────────────────────────────────────┘              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 常用命令

### 查看运行中的容器

```bash
docker ps
```

### 查看网络

```bash
docker network ls
docker network inspect jusi_shared_network
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker logs -f jusi_login_server
docker logs -f jusi_mysql
docker logs -f jusi_redis
```

### 进入容器

```bash
# 进入 MySQL 容器
docker exec -it jusi_mysql mysql -ujusi -p

# 进入 Redis 容器
docker exec -it jusi_redis redis-cli

# 进入应用容器
docker exec -it jusi_login_server /bin/bash
```

### 停止和清理

```bash
# 停止登录服务（保留数据）
cd jusi_login_server
docker-compose down

# 停止基础设施服务（保留数据）
cd ../jusi_infrastructure
docker-compose down

# 停止基础设施服务并删除数据卷（慎用！会清除所有数据）
cd ../jusi_infrastructure
docker-compose down -v
```

### 重启服务

```bash
# 重启登录服务
cd jusi_login_server
docker-compose restart login_server

# 重新构建并启动登录服务
docker-compose up -d --build

# 重启基础设施服务
cd ../jusi_infrastructure
docker-compose restart mysql
docker-compose restart redis
```

---

## 数据持久化

数据由基础设施项目管理，存储在 Docker 卷中：

- `jusi_infrastructure_mysql_data`: MySQL 数据库文件
- `jusi_infrastructure_redis_data`: Redis 持久化数据

查看卷：

```bash
docker volume ls
docker volume inspect jusi_infrastructure_mysql_data
docker volume inspect jusi_infrastructure_redis_data
```

备份数据：

```bash
# 备份 MySQL 数据库
docker exec jusi_mysql mysqldump -u root -p jusi_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复 MySQL 数据库
docker exec -i jusi_mysql mysql -u root -p jusi_db < backup.sql
```

---

## 网络配置

### 容器之间的通信

在同一个 Docker 网络中，容器可以通过**容器名**互相访问：

- MySQL 主机名: `jusi_mysql`
- Redis 主机名: `jusi_redis`

### 端口映射

- 应用服务: `http://localhost:8000`
- MySQL: `localhost:3306`
- Redis: `localhost:6379`

---

## 故障排查

### 检查容器健康状态

```bash
docker ps
# 查看 STATUS 列中的 health 状态
```

### 检查服务依赖

```bash
# 确保 MySQL 和 Redis 已启动
docker ps | grep jusi_mysql
docker ps | grep jusi_redis
```

### 网络连接问题

```bash
# 测试容器之间的网络连接
docker exec -it jusi_login_server ping jusi_mysql
docker exec -it jusi_login_server ping jusi_redis
```

### 查看详细错误

```bash
docker-compose logs --tail=100 login_server
```

---

## 生产环境建议

1. **使用 secrets 管理敏感信息**，而不是 `.env` 文件
2. **限制 CORS 配置**，不要使用 `allow_origins=["*"]`
3. **设置资源限制**（CPU、内存）
4. **配置备份策略**（数据库定期备份）
5. **使用反向代理**（Nginx/Traefik）处理 HTTPS
6. **启用日志收集**（ELK Stack、Loki 等）
7. **监控和告警**（Prometheus + Grafana）

---

## 环境变量

### 基础设施项目环境变量

在 `jusi_infrastructure` 项目中配置：

```bash
cd ../jusi_infrastructure
cp .env.example .env
```

主要配置项：
- `DB_ROOT_PASSWORD`: MySQL root 密码
- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `DB_NAME`: 数据库名称
- `REDIS_PASSWORD`: Redis 密码（可选）

### 登录服务环境变量

在 `jusi_login_server` 项目中配置：

```bash
cd jusi_login_server
cp .env.example .env
```

主要配置项：
- `VOLC_AK`, `VOLC_SK`: 火山引擎密钥
- `RTC_APP_ID`, `RTC_APP_KEY`: RTC 配置
- `SMS_ACCOUNT`, `SMS_TEMPLATE_ID`: 短信服务配置
- `DB_PASSWORD`: 数据库密码（需与基础设施项目保持一致）
- `REDIS_PASSWORD`: Redis 密码（需与基础设施项目保持一致）

**注意**：
- Docker 部署时，`DB_HOST` 和 `REDIS_HOST` 会在 `docker-compose.yml` 中自动设置为容器名
- 本地开发时，使用 `localhost` 作为主机名
