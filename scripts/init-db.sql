-- ============================================================
-- Vision - MySQL 8 Initialization Script
-- ============================================================

CREATE DATABASE IF NOT EXISTS vision CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vision;

-- --------------------------------------------------------
-- Users (managed primarily by OpenWebUI, but we link to them)
-- --------------------------------------------------------
-- We might not need this if OpenWebUI handles all user auth and we just use user_id from token
-- But good for audit logs and custom features
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- Documents Metadata
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    storage_path VARCHAR(512) NOT NULL, -- MinIO path
    status ENUM('queued', 'processing', 'indexed', 'failed') DEFAULT 'queued',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- --------------------------------------------------------
-- Document Chunks (for relational tracking)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS chunks (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    chunk_index INT NOT NULL,
    text_content MEDIUMTEXT NOT NULL,
    qdrant_id VARCHAR(36), -- Link to vector DB
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_document_id (document_id)
);

-- --------------------------------------------------------
-- Audit Logs
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    details JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_action (user_id, action)
);
