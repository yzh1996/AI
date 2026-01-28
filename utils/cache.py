#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的内存缓存实现
"""

import time
from typing import Any, Optional, Dict, Callable
from functools import wraps


class SimpleCache:
    """简单的内存缓存类"""

    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}  # key -> (value, expire_time)

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        if key not in self._cache:
            return None

        value, expire_time = self._cache[key]

        # 检查是否过期
        if expire_time > 0 and time.time() > expire_time:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: int = 300):
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），0 表示永不过期
        """
        expire_time = time.time() + ttl if ttl > 0 else 0
        self._cache[key] = (value, expire_time)

    def delete(self, key: str):
        """
        删除缓存

        Args:
            key: 缓存键
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """清空所有缓存"""
        self._cache.clear()

    def cleanup(self):
        """清理过期的缓存项"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expire_time) in self._cache.items()
            if expire_time > 0 and current_time > expire_time
        ]
        for key in expired_keys:
            del self._cache[key]


# 全局缓存实例
_global_cache: Optional[SimpleCache] = None


def get_cache() -> SimpleCache:
    """
    获取全局缓存实例（单例模式）

    Returns:
        SimpleCache 实例
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = SimpleCache()
    return _global_cache


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    缓存装饰器

    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 缓存键前缀

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # 尝试从缓存获取
            cache = get_cache()
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
