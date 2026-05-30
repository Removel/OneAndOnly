import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.router.SessionRouter import session_router
from backend.router.ChatRouter import chat_router
from backend.exception.GlobalExceptionHandler import register_exception_handlers
from backend.config.DatabaseConfig import init_db
from backend.config.CorsConfig import register_cors

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")
    yield
    logger.info("应用关闭")


app = FastAPI(title="One and Only Backend API", version="1.0.0", lifespan=lifespan)

app = register_cors(app)

app.include_router(session_router)
app.include_router(chat_router)

app = register_exception_handlers(app)


@app.get("/")
async def root():
    logger.info("访问根路径 /")
    return {"message": "One and Only Backend API is running"}


@app.get("/health")
async def health_check():
    logger.info("健康检查 /health")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info("正在启动FastAPI应用...")
    uvicorn.run(app, host="0.0.0.0", port=8000)