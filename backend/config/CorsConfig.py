import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def _parse_origins(env_value: str | None) -> List[str]:
    """
    将环境变量中的逗号分隔字符串解析成 origin 列表
    """
    if not env_value:
        return []
    return [item.strip() for item in env_value.split(",") if item.strip()]


# 默认放行的本地开发源（Vite 默认 5173，preview 默认 4173）
_DEFAULT_DEV_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def get_allowed_origins() -> List[str]:
    """
    获取允许的跨域源列表，优先使用环境变量 CORS_ALLOW_ORIGINS（逗号分隔）
    未配置时使用默认开发源列表
    """
    custom = _parse_origins(os.getenv("CORS_ALLOW_ORIGINS"))
    if custom:
        return custom
    return _DEFAULT_DEV_ORIGINS


def register_cors(app: FastAPI) -> FastAPI:
    """
    在 FastAPI 应用上注册 CORS 中间件
    :param app: FastAPI 应用实例
    :return: 注册后的应用实例
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
