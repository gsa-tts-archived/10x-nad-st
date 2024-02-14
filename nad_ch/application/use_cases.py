import os
from typing import List
from nad_ch.application.dtos import DownloadResult
from nad_ch.application.interfaces import ApplicationContext
from nad_ch.application.view_models import (
    get_view_model,
    DataProducerViewModel,
    DataSubmissionViewModel,
)
from nad_ch.domain.entities import DataProducer, DataSubmission


def add_data_producer(
    ctx: ApplicationContext, producer_name: str
) -> DataProducerViewModel:
    if not producer_name:
        ctx.logger.error("Producer name required")
        return

    matching_producer = ctx.producers.get_by_name(producer_name)
    if matching_producer:
        ctx.logger.error("Producer name must be unique")
        return

    producer = DataProducer(producer_name)
    saved_producer = ctx.producers.add(producer)
    ctx.logger.info("Producer added")

    return get_view_model(saved_producer)


def list_data_producers(ctx: ApplicationContext) -> List[DataProducerViewModel]:
    producers = ctx.producers.get_all()
    ctx.logger.info("Data Producer Names:")
    for p in producers:
        ctx.logger.info(p.name)

    return get_view_model(producers)


def ingest_data_submission(
    ctx: ApplicationContext, file_path: str, producer_name: str
) -> DataSubmissionViewModel:
    if not file_path:
        ctx.logger.error("File path required")
        return

    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() not in [".zip", ".csv"]:
        ctx.logger.error("Invalid file format. Only ZIP or CSV files are accepted.")
        return

    producer = ctx.producers.get_by_name(producer_name)
    if not producer:
        ctx.logger.error("Producer with that name does not exist")
        return

    try:
        filename = DataSubmission.generate_filename(file_path, producer)
        ctx.storage.upload(file_path, filename)

        submission = DataSubmission(filename, producer)
        saved_submission = ctx.submissions.add(submission)
        ctx.logger.info(f"Submission added: {saved_submission.filename}")

        return get_view_model(saved_submission)
    except Exception as e:
        ctx.storage.delete(filename)
        ctx.logger.error(f"Failed to process submission: {e}")


def get_data_submission(
    ctx: ApplicationContext, submission_id: int
) -> DataSubmissionViewModel:
    submission = ctx.submissions.get_by_id(submission_id)

    if submission is None:
        return None

    return get_view_model(submission)


def list_data_submissions_by_producer(
    ctx: ApplicationContext, producer_name: str
) -> List[DataSubmissionViewModel]:
    producer = ctx.producers.get_by_name(producer_name)
    if not producer:
        ctx.logger.error("Producer with that name does not exist")
        return

    submissions = ctx.submissions.get_by_producer(producer)
    ctx.logger.info(f"Data submissions for {producer.name}")
    for s in submissions:
        ctx.logger.info(f"{s.producer.name}: {s.filename}")

    return get_view_model(submissions)


def validate_data_submission(ctx: ApplicationContext, filename: str):
    submission = ctx.submissions.get_by_filename(filename)
    if not submission:
        ctx.logger.error("Data submission with that filename does not exist")
        return

    download_result: DownloadResult = ctx.storage.download_temp(filename)
    if not download_result:
        ctx.logger.error("Data extration error")
        return

    report = ctx.task_queue.run_load_and_validate(
        ctx.submissions, submission.id, download_result.extracted_dir
    )

    ctx.logger.info(f"Total number of features: {report.overview.feature_count}")

    ctx.storage.cleanup_temp_dir(download_result.temp_dir)
