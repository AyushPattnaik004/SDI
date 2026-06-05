import time
import sys
import os
from consumers.base import ProcessModel
from consumers.main import queue_manager
from consumers.sdi_trainee import SDI

from core.main import QUEUE_CONSUMER_DETAILS
FLOW_TYPE = "conversation_modified"
REFRESH_TIME = 5
if __name__ == '__main__':
    queue_process: dict[str, ProcessModel] = {}

    try:
        for consumer in QUEUE_CONSUMER_DETAILS:
            print(consumer.name)
            if consumer.name=="sdi":
                queue_process[consumer.name]= ProcessModel(
                    consumer_model=SDI,
                    min_process_summon= consumer.min_process_summon,
                    queue_name=consumer.name
                )
            

        while True:
            queue_manager(queue_process)
            
            time.sleep(REFRESH_TIME)

    except KeyboardInterrupt:
        print("error")
        try:
            # print('killing')
            for q in queue_process:
                queue_process[q].kill_all()
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    except:
        pass
