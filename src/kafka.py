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
        LOGGER.info("  Querying topic: %s", self.check["topic"])

        # read the last message's timestamp
        self.consumer = KafkaConsumer(
            group_id = self.section["groupid"],
            bootstrap_servers = [ self.section["bootstrap_servers"]],
            value_deserializer = lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset ='latest',
            enable_auto_commit = False,
            consumer_timeout_ms = 2000)

        # assign to a topic
        tp = TopicPartition(self.check["topic"], 0)
        assigned_topic = [tp]
        self.consumer.assign(assigned_topic)

        # hack for obtaining last position
        self.consumer.seek_to_end(tp)
        last_offset = self.consumer.position(tp)
        try:
            next_offset = last_offset - 3
            if next_offset < 0:
                next_offset = 0
            self.consumer.seek(tp, next_offset)
            new_offset = self.consumer.position(tp)
        except AssertionError as e:
            LOGGER.error(f"Topic {self.check['topic']} is empty. {e}")

        LOGGER.info("  Last offset: %d", last_offset)

        # consumer.seek_to_beginning(topic_partition)
        ts = -1
        t_value = ""
        wa_value = ""

        for message in self.consumer:
            # LOGGER.info(message)
            try:
                ts = message.value["timestamp"]
                if self.section["subtype"] == "prediction-watering":
                    t_value = message.value["T"]
                    wa_value = message.value["WA"]
                # LOGGER.info(message.value)
            except Exception as e:
                LOGGER.error(e)
            # LOGGER.info("  %s key=%s value=%s" % (message.topic, message.key, message.value))
        self.consumer.close()

        if (t_value == -1):
            LOGGER.warning("  No watering time was given!")

        if (wa_value == -1):
            LOGGER.warning("  No watering amount was given!")

        if (wa_value == 0.0):
            LOGGER.warning("  Watering amount was 0.0!")
        if (ts != -1):
            self.check_last_ts(ts)
        else:
            LOGGER.error("No message in consumer!")


    def check_last_ts(self, ts: int) -> bool:
        try:
            # extracting difference from now
            if self.section["subtype"] == "fusion":
                ts = ts / 1000
            if "time" in self.section:
                if self.section["time"] == "nano":
                    ts = ts / 1000
                if self.section["time"] == "pico":
                    ts = ts / 1000000
            nowts = datetime.timestamp(datetime.now())
            diff_hrs = (nowts - ts) / 60 / 60

            # LOGGER.info("TS: %d, NOWTS: %d", ts, nowts)

            # check timestamp of now
            if diff_hrs > self.check["error_diff"]:
                LOGGER.error("  Timestamp bigger than limit: %.2fh", diff_hrs)
            elif diff_hrs > self.check["alert_diff"]:
                LOGGER.warning("  Timestamp bigger than limit: %.2fh", diff_hrs)
            else:
                LOGGER.info("  Timestamp in the limits: %.2fh", diff_hrs)
        except Exception as e:
            LOGGER.error(f'  Time checking error: {e}')
