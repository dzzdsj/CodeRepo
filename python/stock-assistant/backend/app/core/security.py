"""Token 加解密：用于推送渠道 Token 的安全存储（P2 使用，P1 先建表占位）。"""

from __future__ import annotations

import base64
import os

from cryptography.fernet import Fernet

from app.core.config import settings


def _get_fernet() -> Fernet:
    """由 SECRET_KEY 派生 32 字节密钥并构造 Fernet。"""
    key = settings.secret_key.encode("utf-8")
    # 填充/截断到 32 字节
    key = (key.ljust(32, b"0"))[:32]
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


_fernet = _get_fernet()


def encrypt_token(plain: str) -> str:
    """加密 Token，返回密文字符串。空串原样返回。"""
    if not plain:
        return ""
    return _fernet.encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_token(cipher: str) -> str:
    """解密 Token。空串或无效返回空。"""
    if not cipher:
        return ""
    try:
        return _fernet.decrypt(cipher.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""


def generate_secret_key() -> str:
    """生成随机 32 字符密钥（供初始化 .env 使用）。"""
    return base64.urlsafe_b64encode(os.urandom(24)).decode("utf-8")[:32]
