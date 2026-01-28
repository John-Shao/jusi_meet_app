# 数据库配置说明

## 概述

本项目已从内存字典存储（`users_db`）迁移到 MySQL 数据库存储。用户信息现在持久化存储在 `jusi_db.tb_user` 表中。

## 数据库表结构

表名：`tb_user`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 自增主键 |
| user_id | VARCHAR(64) | 用户ID，唯一索引 |
| user_name | VARCHAR(128) | 用户名 |
| phone | VARCHAR(20) | 手机号，可为空 |
| created_at | BIGINT | 创建时间戳（秒） |
| updated_at | BIGINT | 更新时间戳（秒） |
| is_active | TINYINT(1) | 是否激活：1-激活，0-停用 |

## 配置步骤

### 1. 创建数据库和表

执行 SQL 文件创建数据库和表：

```bash
# 本地部署mysql
mysql -u root -p < sql/create_tb_user.sql
# 使用容器部署mysql
mysql -h 172.17.0.1 -u jusi -p < init-scripts/create_tb_user.sql
```

或者手动在 MySQL 客户端执行：

```bash
mysql -u root -p
source sql/create_tb_user.sql
```

### 2. 配置数据库连接

在项目根目录创建或编辑 `.env` 文件，添加数据库连接信息：

```env
# MySQL数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=jusi_db
```

### 3. 安装依赖

安装新增的 `aiomysql` 依赖：

```bash
pip install -r requirements.txt
```

或单独安装：

```bash
pip install aiomysql==0.2.0
```

## 代码变更说明

### 新增文件

- `db.py` - 数据库操作模块，提供用户 CRUD 操作
- `sql/create_tb_user.sql` - 数据库表创建脚本

### 修改文件

1. **config.py** - 添加数据库连接配置项
2. **main.py** - 添加数据库生命周期管理（启动时初始化连接池，关闭时释放连接）
3. **login.py** - 将所有 `users_db` 字典操作替换为数据库操作
4. **requirements.txt** - 添加 `aiomysql` 依赖

### 数据库操作函数

`db.py` 模块提供以下异步函数：

- `create_user(user_info: UserInfo) -> bool` - 创建新用户
- `get_user_by_login_token(login_token: str) -> Optional[UserInfo]` - 根据登录令牌获取用户
- `update_user_name(login_token: str, user_name: str) -> bool` - 更新用户名
- `user_exists_by_login_token(login_token: str) -> bool` - 检查用户是否存在

## 启动应用

确保 MySQL 服务正在运行，并且已经创建了数据库和表，然后启动应用：

```bash
python main.py
```

应用启动时会自动：
1. 读取 `.env` 配置文件
2. 初始化数据库连接池
3. 记录日志："数据库连接池已初始化"

## 注意事项

1. 确保 MySQL 服务已启动
2. 确保数据库用户有足够的权限创建数据库和表
3. `.env` 文件中的数据库密码请妥善保管，不要提交到版本控制系统
4. 生产环境建议使用连接池配置优化（可在 `db.py` 中调整 `minsize` 和 `maxsize`）
5. 建议为数据库设置定期备份策略

## 故障排查

### 连接失败

如果出现数据库连接失败，请检查：

1. MySQL 服务是否运行：`systemctl status mysql` (Linux) 或查看服务管理器 (Windows)
2. `.env` 配置是否正确
3. 数据库用户权限是否足够
4. 防火墙是否允许连接

### 表不存在

如果提示表不存在，请确保已执行 SQL 脚本创建表：

```bash
mysql -u root -p jusi_db < sql/create_tb_user.sql
```
