#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

configs = {
    "root_path": os.getenv("ROOT_PATH", os.getcwd()),
    "rabbitmq_config": {"username": os.getenv("USERNAME_RM", "jnc"),
                        "password": os.getenv("PASSWORD_RM", "juneng"),
                        "host": os.getenv("HOST_RM", "14.23.57.52"),
                        "port": os.getenv("PORT_RM", 5672),
                        "exchange_get": os.getenv("EXCHANGE", "sem.server.exchange"),
                        "exchange_send": os.getenv("EXCHANGE", "sem.server.exchange"),
                        "exchange_type": os.getenv("EXCHANGE_TYPE", "topic"),
                        "queue_name_get": os.getenv("QUEUE_NAME_GET", "lyq_test"),
                        "routing_key_get": os.getenv("ROUTING_KEY_GET", "lyq_test"),
                        "queue_name_send": os.getenv("QUEUE_NAME_SEND", "lyq_test_return"),
                        "routing_key_send": os.getenv("ROUTING_KEY_SEND", "lyq_test_return")
                        },
    "redis_config": {"redis_host": os.getenv("REDIS_HOST", "14.23.57.52"),
                     "redis_port": os.getenv("REDIS_PORT", 3682),
                     "redis_pass": os.getenv("REDIS_PASS", "huidian")
                     }
        }
