-- 创建 jusi_db 数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS jusi_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE jusi_db;

-- 创建用户表 tb_user
CREATE TABLE IF NOT EXISTS tb_user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    user_id VARCHAR(64) NOT NULL UNIQUE COMMENT '用户ID',
    user_name VARCHAR(128) NOT NULL COMMENT '用户名',
    phone VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    created_at BIGINT NOT NULL COMMENT '创建时间戳（秒）',
    updated_at BIGINT NOT NULL COMMENT '更新时间戳（秒）',
    last_login_at BIGINT DEFAULT NULL COMMENT '最后登录时间戳（秒）',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否激活：1-激活，0-停用',
    INDEX idx_user_id (user_id),
    UNIQUE KEY uk_phone (phone),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';
