from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine
from contextlib import asynccontextmanager, contextmanager
from apscheduler_db.core.settings import get_settings

engine: AsyncEngine = None
engine_sync: Engine = None
AsyncSessionLocal: sessionmaker = None
SessionLocal: sessionmaker = None

def init_db():
    
    settings = get_settings()

    global engine, AsyncSessionLocal, engine_sync, SessionLocal

    # 创建异步数据库连接
    if not engine:
        engine = create_async_engine(settings.scheduler_mysqldb_url,
                                    echo=False,
                                    pool_recycle=3600,        # 回收连接时间
                                    pool_pre_ping=True,       # 检查连接可用性
                                    pool_size=3,
                                    max_overflow=10)
    if not engine_sync:    
        engine_sync = create_engine(settings.scheduler_mysqldb_url.replace("+asyncmy", "+pymysql"),
                                    echo=False,
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
    
    if not SessionLocal:
        SessionLocal = sessionmaker(
            bind=engine_sync,
            class_=Session,
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
    import apscheduler_db.models
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@contextmanager
def get_db_session_sync():
    with SessionLocal() as session:
        yield session