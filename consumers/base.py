import asyncio
import time, os, sys
import multiprocessing

from datetime import datetime
from pika import BlockingConnection, ConnectionParameters
from pika.spec import Basic, BasicProperties
from pika.channel import Channel
from typing import TypeVar

class ConsumerModel:

    def __init__(self, queue: str, prefetch_count: int = 1) -> None:
        self.connection = BlockingConnection(ConnectionParameters('localhost'))
        self.queue_name = queue
        self.channel = self.connection.channel()
        self.prefetch_count = prefetch_count

        self.channel.queue_declare(self.queue_name, durable=True)

        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback)

        self.channel.start_consuming()

    def callback(self, ch: Channel, method: Basic.Deliver, properties: BasicProperties, data: bytes):
        try:

            print(f"data arrived on queue {self.queue_name} and data is: {data}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            print(f'error in handle message on {self.queue_name}')

        finally:
            pass


ConsumerBase = TypeVar("ConsumerBase", bound=ConsumerModel)
class ProcessModel:

    def __init__(self, consumer_model: ConsumerBase, queue_name: str, min_process_summon: int = 1) -> None:
        self.queue_name = queue_name
        self.min_process_summon = min_process_summon
        self.consumers = consumer_model

        self.process: list[multiprocessing.Process] = []
        self.increase_consumer_instances(self.min_process_summon)

    def increase_consumer_instances(self, no_of: int = 1):
        procs_list = []

        for _ in range(no_of):
            try:
                # change this or handle that create with param 
                p = multiprocessing.Process(target=self.consumers, args=(self.queue_name, ))
                p.start()
                print(f' [+] {self.queue_name} -> {p.pid}')
                procs_list.append(p)
            except:
                print(f'[x] {self.queue_name} xxxxxx')

        self.process.extend(procs_list)

    def decrease_consumer_instances(self, no_of: int = 1):
        done = 0
        while len(self.process) > self.min_process_summon:
            if done == no_of:
                break
            try:
                p = self.process.pop(0)
                p.terminate()
                print(f' [-] {self.queue_name} -> {p.pid}')
            except:
                print(f'[x] {self.queue_name} xxxxxx')
            finally:
                done += 1
    
    def kill_all(self):

        for p in self.process:
            try:
                p.kill()
            except:
                try:
                    while p.is_alive():
                        p.terminate()
                except: 
                    pass

