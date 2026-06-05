
class ConsumerQueueDetailsModel:

    def __init__(self, name: str, min_process_summon: int, threshold_number: int) -> None:
        self.name = name
        self.min_process_summon = min_process_summon
        self.threshold_number = threshold_number


QUEUE_CONSUMER_DETAILS: list[ConsumerQueueDetailsModel] = [
    ConsumerQueueDetailsModel(name= "sdi",min_process_summon= 10,threshold_number= 5)
]
