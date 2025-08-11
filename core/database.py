from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from core.settings import get_settings

settings = get_settings()

engine: AsyncEngine = None
AsyncSessionLocal: sessionmaker = None

def init_db():
    global engine, AsyncSessionLocal
    
    # 创建异步数据库连接
    if not engine:
        engine = create_async_engine(settings.scheduler_mysqldb_url,
                                    echo=True,
                                    pool_recycle=3600,        # 回收连接时间
                                    pool_pre_ping=True,       # 检查连接可用性
                                    pool_size=3,
                                    max_overflow=10)
    
    # 创建数据库会话
    if not AsyncSessionLocal:
        AsyncSessionLocal = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

# 依赖项：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables():
    '''
    加载 app.models.* 下的所有 model 文件 初始化数据库
    '''
    import models
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)