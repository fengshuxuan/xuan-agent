from uuid import UUID

from sqlmodel import Session

from app.agent.runtime import AgentRuntime
from app.db.session import engine
from app.models import AgentSession, Job, JobStatus, utc_now


def run_chat_job(job_id: str, user_id: str, session_id: str, message: str) -> None:
    """Background chat job placeholder.

    MVP chat still runs synchronously. This function is ready for the next step:
    queueing long-running chat / file processing jobs through Redis + RQ.
    """
    with Session(engine) as db:
        job = db.get(Job, UUID(job_id))
        session_obj = db.get(AgentSession, UUID(session_id))
        if not job or not session_obj:
            return

        job.status = JobStatus.running
        job.progress = 10
        job.updated_at = utc_now()
        db.add(job)
        db.commit()

        try:
            runtime = AgentRuntime(db=db, user_id=UUID(user_id), session_obj=session_obj)
            result = runtime.run(message)
            job.status = JobStatus.succeeded
            job.progress = 100
            job.result_json = result.reply
        except Exception as exc:  # noqa: BLE001 - worker must persist failure
            job.status = JobStatus.failed
            job.error_message = str(exc)
        finally:
            job.updated_at = utc_now()
            db.add(job)
            db.commit()
