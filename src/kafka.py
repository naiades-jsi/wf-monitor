# imports
import logging
import json
from datetime import datetime
from kafka import KafkaConsumer
from kafka import TopicPartition
from kafka import OffsetAndMetadata

# project imports

# logging
logging.getLogger("kafka").setLevel(logging.CRITICAL)
LOGGER = logging.getLogger(__name__)

class KafkaCheck:
    """Checking InfluxDB for recent data."""

    def __init__(self, section, check) -> None:
        self.section = section
        self.check = check

    def run(self) -> None:
        LOGGER.info("  Queryjing topic for: %s", self.check["name"])

        # read the last message's timestamp
        self.consumer = KafkaConsumer(
            group_id = self.section["groupid"],
            bootstrap_servers = [ self.section["bootstrap_servers"]],
            value_deserializer = lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset ='latest',
            enable_auto_commit = False,
            consumer_timeout_ms = 2000)

        tp = TopicPartition(self.check["topic"], 0)
        assigned_topic = [tp]
        self.consumer.assign(assigned_topic)
        last_offset = self.consumer.position(tp)
        #options = {}
        #options[0] = OffsetAndMetadata(last_offset, tp)
        self.consumer.commit({
            tp: OffsetAndMetadata(last_offset - 1, None)
        })

        LOGGER.warning("  Last offset: %d", last_offset)

        # consumer.seek_to_beginning(topic_partition)
        ts = 0
        for message in self.consumer:
            try:
                ts = message.value["timestamp"]
            except Exception as e:
                LOGGER.error(e)
            # LOGGER.info("  %s key=%s value=%s" % (message.topic, message.key, message.value))
        self.consumer.close()

        self.check_last_ts(ts)


    def check_last_ts(self, ts: int) -> bool:
        try:
            # extracting difference from now
            ts = ts / 1000
            nowts = datetime.timestamp(datetime.now())
            diff_hrs = (nowts - ts) / 60 / 60

            # check timestamp of now
            if diff_hrs > self.check["error_diff"]:
                LOGGER.error("  Timestamp bigger then limit: %fh", diff_hrs)
            elif diff_hrs > self.check["alert_diff"]:
                LOGGER.warning("  Timestamp bigger than limit: %fh", diff_hrs)
            else:
                LOGGER.info("  Timestamp in the limits: %fh", diff_hrs)
        except Exception as e:
            LOGGER.error(f'  Time checking error: {e}')


