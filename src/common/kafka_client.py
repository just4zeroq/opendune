"""
Kafka客户端封装
"""

import json
from typing import Any, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger(__name__)


class KafkaProducer:
    """Kafka生产者"""

    def __init__(self, bootstrap_servers: Optional[List[str]] = None):
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """启动生产者"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3,
            retry_backoff_ms=1000,
            enable_idempotence=True,
            compression_type='lz4',
        )
        await self.producer.start()
        logger.info("kafka_producer_started", servers=self.bootstrap_servers)

    async def stop(self):
        """停止生产者"""
        if self.producer:
            await self.producer.stop()
            logger.info("kafka_producer_stopped")

    async def send(self, topic: str, value: Dict[str, Any], key: Optional[str] = None):
        """发送消息"""
        if not self.producer:
            raise RuntimeError("Producer not started")

        try:
            await self.producer.send(topic, value=value, key=key)
            logger.debug("message_sent", topic=topic, key=key)
        except Exception as e:
            logger.error("send_message_failed", topic=topic, error=str(e))
            raise

    async def send_batch(self, topic: str, messages: List[Dict[str, Any]]):
        """批量发送消息"""
        for msg in messages:
            await self.send(topic, msg)


class KafkaConsumer:
    """Kafka消费者"""

    def __init__(
        self,
        topics: List[str],
        group_id: str,
        bootstrap_servers: Optional[List[str]] = None,
    ):
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.consumer: Optional[AIOKafkaConsumer] = None

    async def start(self):
        """启动消费者"""
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            max_poll_records=500,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
        )
        await self.consumer.start()
        logger.info("kafka_consumer_started", topics=self.topics, group_id=self.group_id)

    async def stop(self):
        """停止消费者"""
        if self.consumer:
            await self.consumer.stop()
            logger.info("kafka_consumer_stopped")

    async def consume(self, callback):
        """消费消息"""
        if not self.consumer:
            raise RuntimeError("Consumer not started")

        async for msg in self.consumer:
            try:
                await callback(msg)
                await self.consumer.commit()
            except Exception as e:
                logger.error("consume_message_failed", error=str(e), topic=msg.topic)
