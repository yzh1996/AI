#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密工具模块
使用 Fernet 对称加密来保护敏感信息（如数据库密码）
"""

import os
from cryptography.fernet import Fernet
from typing import Optional


class EncryptionManager:
    """加密管理器"""

    def __init__(self, key: Optional[bytes] = None):
        """
        初始化加密管理器

        Args:
            key: 加密密钥（bytes），如果为 None 则从环境变量读取
        """
        if key is None:
            # 从环境变量读取密钥
            key_str = os.environ.get('ENCRYPTION_KEY')
            if key_str:
                key = key_str.encode()
            else:
                # 如果环境变量不存在，生成新密钥并提示用户保存
                key = Fernet.generate_key()
                print(f"警告: 未找到 ENCRYPTION_KEY 环境变量，已生成新密钥")
                print(f"请将以下密钥保存到 .env 文件中:")
                print(f"ENCRYPTION_KEY={key.decode()}")

        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """
        加密字符串

        Args:
            plaintext: 明文字符串

        Returns:
            加密后的字符串（Base64 编码）
        """
        if not plaintext:
            return ""

        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        解密字符串

        Args:
            ciphertext: 加密后的字符串（Base64 编码）

        Returns:
            解密后的明文字符串
        """
        if not ciphertext:
            return ""

        try:
            decrypted_bytes = self.cipher.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")


def generate_key() -> str:
    """
    生成新的加密密钥

    Returns:
        Base64 编码的密钥字符串
    """
    key = Fernet.generate_key()
    return key.decode()


# 全局加密管理器实例
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """
    获取全局加密管理器实例（单例模式）

    Returns:
        EncryptionManager 实例
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_password(password: str) -> str:
    """
    加密密码的便捷函数

    Args:
        password: 明文密码

    Returns:
        加密后的密码
    """
    return get_encryption_manager().encrypt(password)


def decrypt_password(encrypted_password: str) -> str:
    """
    解密密码的便捷函数

    Args:
        encrypted_password: 加密后的密码

    Returns:
        明文密码
    """
    return get_encryption_manager().decrypt(encrypted_password)
