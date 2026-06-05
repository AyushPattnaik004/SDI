import time
import sys
import os
from consumers.base import ProcessModel
from consumers.main import queue_manager
from consumers.bls_main import BLS
from consumers.bls_main_flow import BLSFLOW
from consumers.bls_main_both import BLSBOTH
from consumers.bls_conversational import BLSConversational
from consumers.bls_conversational_modified import BLSConversationalModified

from core.main import QUEUE_CONSUMER_DETAILS
FLOW_TYPE = "conversation_modified"
REFRESH_TIME = 5
if __name__ == '__main__':
    queue_process: dict[str, ProcessModel] = {}

    try:
        for consumer in QUEUE_CONSUMER_DETAILS:
            print(consumer.name)
            if consumer.name=="bls":
                if FLOW_TYPE == "flow":
                    queue_process[consumer.name]= ProcessModel(
                        consumer_model=BLSFLOW,
                        min_process_summon= consumer.min_process_summon,
                        queue_name=consumer.name
                    )
                elif FLOW_TYPE == "both":
                    queue_process[consumer.name]= ProcessModel(
                        consumer_model=BLSBOTH,
                        min_process_summon= consumer.min_process_summon,
                        queue_name=consumer.name
                    )
                elif FLOW_TYPE == "conversation":
                    queue_process[consumer.name]= ProcessModel(
                        consumer_model=BLSConversational,
                        min_process_summon= consumer.min_process_summon,
                        queue_name=consumer.name
                    )
                elif FLOW_TYPE == "conversation_modified":
                    queue_process[consumer.name]= ProcessModel(
                        consumer_model=BLSConversationalModified,
                        min_process_summon= consumer.min_process_summon,
                        queue_name=consumer.name
                    )
                else:
                    queue_process[consumer.name]= ProcessModel(
                        consumer_model=BLS,
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
