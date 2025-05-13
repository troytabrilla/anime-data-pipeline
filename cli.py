import argparse
import json
import time

from kafka import KafkaConsumer


class KafkaCLI:
    def __init__(self, url=None, version=None, topics=None):
        if not url:
            raise ValueError("must provide url")
        if not version:
            raise ValueError("must provide version")
        if not topics:
            raise ValueError("must provide topics")

        self.url = url
        self.version = tuple(int(part) for part in version.split("."))
        self.topics = topics

    def __repr__(self):
        return f"{self.url} {self.version} {self.topics}"

    def consume(self):
        print(self)
        consumer = KafkaConsumer(
            bootstrap_servers=[self.url],
            value_deserializer=json.loads,
            api_version=self.version,
            consumer_timeout_ms=5000,
            auto_offset_reset="earliest",
            group_id=None,
        )

        consumer.subscribe(topics=self.topics)

        while not consumer.poll():
            print("waiting for messages")
            time.sleep(1)
            continue

        print("seeking to beginning")
        consumer.seek_to_beginning()

        print("processing messages")
        count = 0
        for msg in consumer:
            print(msg.value)
            count += 1

        print(f"processed {count} messages")
        print("closing")
        consumer.close()


parser = argparse.ArgumentParser("cli")
subparsers = parser.add_subparsers(dest="command", help="CLI commands", required=True)

kafka_parser = subparsers.add_parser("kafka", help="Run Kafka commands")
kafka_parser.add_argument(
    "sub_command", type=str, help="Kafka sub-commands", choices=["consume"]
)
kafka_parser.add_argument(
    "-u",
    "--url",
    metavar="url",
    type=str,
    default="localhost:9092",
    help="URL to Kafka bootstrap server",
)
kafka_parser.add_argument(
    "-v",
    "--version",
    metavar="version",
    type=str,
    default="4.0.0",
    help="Kafka API version",
)
kafka_parser.add_argument(
    "-t",
    "--topics",
    metavar="topics",
    type=str,
    action="append",
    default=["raw_user", "raw_media"],
    help="Kafka topics",
)

args = parser.parse_args()

if args.command == "kafka":
    kafka_cli = KafkaCLI(args.url, args.version, args.topics)
    if args.sub_command == "consume":
        kafka_cli.consume()
