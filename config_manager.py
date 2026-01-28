#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置管理模块
支持多数据库配置的创建、读取、更新、删除和加密存储
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import pymysql
from utils.encryption import encrypt_password, decrypt_password


class ConfigManager:
    """数据库配置管理器"""

    def __init__(self, config_file: str = "db_configs.json"):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self._configs: Dict[str, Dict] = {}
        self._load_configs()

    def _load_configs(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._configs = {cfg['id']: cfg for cfg in data.get('configs', [])}
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self._configs = {}
        else:
            self._configs = {}

    def _save_configs(self):
        """保存配置到文件"""
        try:
            data = {
                'version': '1.0',
                'configs': list(self._configs.values())
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"保存配置文件失败: {e}")

    def create_config(self, name: str, driver: str, host: str, port: int,
                     database: str, user: str, password: str,
                     catalog: Optional[str] = None) -> Dict:
        """
        创建新配置

        Args:
            name: 配置名称
            driver: 数据库驱动类型 (mysql, postgresql, starrocks)
            host: 主机地址
            port: 端口号
            database: 数据库名
            user: 用户名
            password: 密码（明文，将被加密存储）
            catalog: 目录名（可选，用于 Trino/Presto）

        Returns:
            创建的配置字典
        """
        config_id = str(uuid.uuid4())
        encrypted_password = encrypt_password(password)

        config = {
            'id': config_id,
            'name': name,
            'driver': driver,
            'host': host,
            'port': port,
            'database': database,
            'catalog': catalog,
            'user': user,
            'password': encrypted_password,
            'created_at': datetime.now().isoformat(),
            'last_used': None
        }

        self._configs[config_id] = config
        self._save_configs()
        return config

    def get_config(self, config_id: str) -> Optional[Dict]:
        """
        获取配置（不含明文密码）

        Args:
            config_id: 配置ID

        Returns:
            配置字典，如果不存在则返回 None
        """
        config = self._configs.get(config_id)
        if config:
            # 返回副本，隐藏密码
            config_copy = config.copy()
            config_copy['password'] = '******'
            return config_copy
        return None

    def get_config_with_password(self, config_id: str) -> Optional[Dict]:
        """
        获取配置（含解密后的明文密码）

        Args:
            config_id: 配置ID

        Returns:
            配置字典，如果不存在则返回 None
        """
        config = self._configs.get(config_id)
        if config:
            config_copy = config.copy()
            config_copy['password'] = decrypt_password(config['password'])
            return config_copy
        return None

    def list_configs(self) -> List[Dict]:
        """
        列出所有配置（不含密码）

        Returns:
            配置列表
        """
        configs = []
        for config in self._configs.values():
            config_copy = config.copy()
            config_copy['password'] = '******'
            configs.append(config_copy)
        return configs

    def update_config(self, config_id: str, **kwargs) -> Optional[Dict]:
        """
        更新配置

        Args:
            config_id: 配置ID
            **kwargs: 要更新的字段

        Returns:
            更新后的配置，如果不存在则返回 None
        """
        if config_id not in self._configs:
            return None

        config = self._configs[config_id]

        # 更新允许的字段
        allowed_fields = ['name', 'driver', 'host', 'port', 'database', 'catalog', 'user']
        for field in allowed_fields:
            if field in kwargs:
                config[field] = kwargs[field]

        # 如果更新密码，需要加密
        if 'password' in kwargs and kwargs['password']:
            config['password'] = encrypt_password(kwargs['password'])

        self._save_configs()
        return self.get_config(config_id)

    def delete_config(self, config_id: str) -> bool:
        """
        删除配置

        Args:
            config_id: 配置ID

        Returns:
            是否删除成功
        """
        if config_id in self._configs:
            del self._configs[config_id]
            self._save_configs()
            return True
        return False

    def update_last_used(self, config_id: str):
        """
        更新配置的最后使用时间

        Args:
            config_id: 配置ID
        """
        if config_id in self._configs:
            self._configs[config_id]['last_used'] = datetime.now().isoformat()
            self._save_configs()

    def test_connection(self, config_id: str) -> tuple[bool, str]:
        """
        测试数据库连接

        Args:
            config_id: 配置ID

        Returns:
            (是否成功, 消息)
        """
        config = self.get_config_with_password(config_id)
        if not config:
            return False, "配置不存在"

        try:
            # 目前只支持 MySQL/StarRocks（使用 PyMySQL）
            if config['driver'] in ['mysql', 'starrocks']:
                conn = pymysql.connect(
                    host=config['host'],
                    port=config['port'],
                    user=config['user'],
                    password=config['password'],
                    database=config['database'],
                    connect_timeout=5
                )
                conn.close()
                return True, "连接成功"
            else:
                return False, f"暂不支持 {config['driver']} 数据库类型"
        except Exception as e:
            return False, f"连接失败: {str(e)}"


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    获取全局配置管理器实例（单例模式）

    Returns:
        ConfigManager 实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
