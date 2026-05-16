from app.database import async_session

async def get_db():
    '''
    Dependency function to provide a database session for each request.
    Uses an asynchronous context manager to ensure proper session management.
    '''
    async with async_session() as session:
        yield session