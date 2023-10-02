import hashlib
from datetime import datetime

from celery.signals import task_prerun, task_postrun, task_failure

from management.models import TaskRun, PeriodicTaskStatus, PeriodicTaskResult, Task


def get_fargs_dict(*args, **kwargs):
    return {'args': args, 'kwargs': kwargs}


def get_fargs_json_mds(fargs):
    return hashlib.md5(str(fargs).encode('utf-8')).hexdigest()


def publish_pre_run_task(sender):
    @task_prerun.connect(sender=sender)
    def trigger_cron_task_pre_run_notifier(signal=None, sender=None, task_id=None, task=None, args=None,
                                           **kwargs):
        task_run = TaskRun.objects.filter(task_uuid=task_id).first()
        if task_run:
            task_run.status = PeriodicTaskStatus.RUNNING
            task_run.started_at = datetime.utcnow()
            task_run.save()

    return trigger_cron_task_pre_run_notifier


def publish_post_run_task(sender):
    @task_postrun.connect(sender=sender)
    def trigger_cron_task_post_run_notifier(signal=None, sender=None, task_id=None, task=None, args=None,
                                            **kwargs):
        task_run = TaskRun.objects.filter(task_uuid=task_id).first()
        if task_run:
            task_run.status = PeriodicTaskStatus.COMPLETED
            task_run.completed_at = datetime.utcnow()
            task_run.save()

    return trigger_cron_task_post_run_notifier


def publish_failure_task(sender):
    @task_failure.connect(sender=sender)
    def trigger_cron_task_failure_notifier(signal=None, sender=None, task_id=None, task=None, args=None,
                                           **kwargs):
        task_run = TaskRun.objects.filter(task_uuid=task_id).first()
        if task_run:
            task_run.result = PeriodicTaskResult.FAILED
            task_run.save()

    return trigger_cron_task_failure_notifier


def get_or_create_task(task, *args, **kwargs):
    fargs = get_fargs_dict(*args, **kwargs)
    md5_farags = get_fargs_json_mds(fargs)
    saved_task, _ = Task.objects.get_or_create(task=task,
                                               md5_fargs=md5_farags,
                                               defaults={
                                                   'fargs': fargs,
                                               })

    return saved_task


def check_scheduled_or_running_task_run_for_task(saved_task):
    return TaskRun.objects.filter(task=saved_task).filter(
        status__in=[PeriodicTaskStatus.SCHEDULED, PeriodicTaskStatus.RUNNING]).count() > 0


def create_task_run(**kwargs):
    task_run = TaskRun.objects.create(**kwargs)
    return task_run
