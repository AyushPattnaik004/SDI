import time, os, sys
from pika import BlockingConnection, ConnectionParameters
from .base import ProcessModel, ConsumerModel

from core.main import QUEUE_CONSUMER_DETAILS
import traceback

def queue_manager(queue_process: dict[str, ProcessModel]):
    channel = BlockingConnection(
        ConnectionParameters(host='localhost')).channel()
    try:
        for consumer_detail in QUEUE_CONSUMER_DETAILS:

            result = channel.queue_declare(
                queue=consumer_detail.name, durable=True).method

            # initial summon queue and we should delete consumers as
            queue_to_summon = 2
            queue_to_del = 0 if (result.consumer_count == 0 or result.consumer_count <= consumer_detail.min_process_summon) else (
                result.consumer_count - consumer_detail.min_process_summon)
            
            if result.message_count != 0:
                queue_to_summon = (result.message_count // consumer_detail.threshold_number) * 2
                queue_to_del = consumer_detail.threshold_number // result.message_count

            if result.message_count >= consumer_detail.threshold_number:
                # we can increase it progressively also!
                queue_process[consumer_detail.name
                              ].increase_consumer_instances(queue_to_summon)
            else:
                queue_process[consumer_detail.name
                              ].decrease_consumer_instances(queue_to_del)

    except Exception as e:
        print('queue manager error', e)
        traceback.print_exc()

