from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

__all__ = [
    "commit_session",
    "delete_session_record",
    "execute_session_query",
    "get_record_or_404"
]


async def commit_session(session: Session | AsyncSession):
    if isinstance(session, AsyncSession):
        await session.commit()

    else:
        session.commit()


async def delete_session_record(record, session):
    if isinstance(session, AsyncSession):
        await session.delete(record)

    else:
        session.delete(record)
    await commit_session(session)


async def execute_session_query(session: Session | AsyncSession, query):
    if isinstance(session, AsyncSession):
        return await session.execute(query)

    return session.execute(query)


def get_record_or_404(result):
    if not (record := result.scalar_one_or_none()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    return record
