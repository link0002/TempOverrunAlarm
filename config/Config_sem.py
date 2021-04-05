#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
# 本地运行：则是在测试环境运行（配置的）
# 部署运行：取决于部署的环境是测试、预生产、还是生产
configs = {
    "root_path": os.getenv("ROOT_PATH", os.getcwd()),
    "rabbitmq_config": {"username": os.getenv("USERNAME_RM", "jnc"),
                        "password": os.getenv("PASSWORD_RM", "juneng"),
                        "host": os.getenv("HOST_RM", "14.23.57.52"),
                        "port": os.getenv("PORT_RM", 5672),
                        "exchange_get": os.getenv("EXCHANGE", "exceedinfo.server.exchange"),
                        "exchange_send": os.getenv("EXCHANGE", "exceedinfo.server.exchange"),
                        "exchange_type": os.getenv("EXCHANGE_TYPE", "topic"),
                        "queue_name_get": os.getenv("QUEUE_NAME_GET", "exceedinfo.server.queue.input"),
                        "routing_key_get": os.getenv("ROUTING_KEY_GET", "exceedinput"),
                        "queue_name_send": os.getenv("QUEUE_NAME_SEND", "exceedinfo.server.queue.output"),
                        "routing_key_send": os.getenv("ROUTING_KEY_SEND", "exceedoutput")
                        }

        }
