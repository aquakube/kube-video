from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from config import config
from services.consumer import Consumer
from services.reconcile import reconcile

consumer = None
scheduler = None


def start():
    """ start all services """
    global consumer
    global scheduler

    # start the scheduler
    scheduler = BackgroundScheduler()
    scheduler.start()

    # start the consumer
    consumer = Consumer()
    consumer.start()

    # add a secondary job store
    # this is done so the consumers deletion timers are in a separate job store
    scheduler.add_jobstore(
        MemoryJobStore(),
        alias='secondary'
    )

    # schedule the renconiliation job
    scheduler.add_job(
        reconcile,
        trigger='interval',
        id='reconcile',
        name='Resource Reconciliation',
        seconds=config.event.reconciliation_interval,
        jobstore='secondary'
    )


def stop():
    """ stops the consumer service """
    if consumer:
        consumer.stop()
    if scheduler:
        scheduler.shutdown()