import json
import logging
import threading
import datetime

import jsonschema
from kafka import KafkaConsumer, TopicPartition

import services
from config import config
from utilities import resource as resource_util

logger = logging.getLogger()


class Consumer(threading.Thread):
    """ Kafka consumer for fo-live cloud events """

    def __init__(self):
        """ Initialize the consumer """
        super(Consumer, self).__init__(daemon=True)
        self.last_event_processed = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.consumer = KafkaConsumer(
            group_id=config.kafka.consume_group_id,
            client_id=config.kafka.consume_client_id,
            bootstrap_servers=config.kafka.brokers
        )
        logger.debug(f'[Consumer] kafka config: {self.consumer.config}')


    def run(self):
        """ Control loop that spins up or down the video instances based on the received events """

        # explicitly assign partition to consumer
        partition = TopicPartition(config.kafka.consume_topic, 0)
        self.consumer.assign([partition])

        # dummy poll
        self.consumer.poll()

        # go to end of the stream so we don't process messages during the time frame the consumer was down
        self.consumer.seek_to_end()

        # iterate over each message as they are consumed
        for message in self.consumer:

            # exit run loop if stop event was set
            if self.stop_event.is_set():
                logger.info('[Consumer] Stopping kafka consumer!')
                break

            # parse and validate the message, ignore if not invalid
            cloudevent = self.parse_and_validate(message.value)
            if cloudevent is None:
                continue

            # process the cloudevent
            self.process(message.timestamp, cloudevent)

            # cache the current time. the main loop will kill all video instances if this is too old
            self.last_event_processed = datetime.datetime.utcnow()

        # close the kafka consumer connection on exit
        self.consumer.close()


    def stop(self):
        """ Stops the kafka consumer and scheduler """
        self.stop_event.set()


    def parse_and_validate(self, value):
        """ validate the message and deserialize the value """
        try:
            cloudevent = json.loads(value.decode('utf-8'))
            jsonschema.validate(instance=cloudevent, schema=config.schemas.cloudevent)

            if cloudevent['context']['type'] == 'aquavid.subscription.event':
                jsonschema.validate(instance=cloudevent['data'], schema=config.schemas.aquavid_subscription_event)
                return cloudevent

            else:
                logger.debug(f'[Consumer] Received unknown event type: {cloudevent}')
            
        except:
            logger.exception(f'[Consumer] Failed to parse or validate message: {value}')


    def process(self, timestamp, cloudevent):
        """
        Process the cloudevent if it is current (not old)
        """
        try:
            # ignore old messages that come through for whatever reason (greater than 5 seconds).
            elasped = datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(timestamp / 1000)
            if elasped >= datetime.timedelta(seconds=5):
                logger.warn(f'[Consumer] Discarding old event: {cloudevent}')
                return

            # invoke the appropriate handler for the event
            if cloudevent['context']['type'] == 'aquavid.subscription.event':
                self.handle_subscription_event(cloudevent)

        except:
            logger.exception(f'[Consumer] Failed to process event: {cloudevent}')


    def handle_subscription_event(self, cloudevent):
        """
        Handler for fo-live room events.
        """
        camera_name = cloudevent['data']['camera']
        sub_type = cloudevent['data']['type']
        subscriber_count = cloudevent['data']['subscribers']

        # create the camera resource if a user has subscribed to the room
        if sub_type == 'subscribe':
            logger.info(f"[Consumer] (event {cloudevent['context']['id']}) Creating resource '{camera_name}'")
            resource_util.create_resource(camera_name)

        # mark the camera resource for deletion if no users are subscribed to the room
        elif sub_type == 'unsubscribe' and subscriber_count == 0:
            logger.info(f"[Consumer] (event {cloudevent['context']['id']}) Marking resource '{camera_name}' for deletion")
            resource_util.mark_resource_for_deletion(camera_name)