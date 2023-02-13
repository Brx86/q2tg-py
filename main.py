#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/02/06 21:25:32
@Author  :   Ayatale 
@Version :   1.1
@Contact :   ayatale@qq.com
@Github  :   https://github.com/brx86/
@Desc    :   None
"""

import asyncio

from utils import conf, logger, Qbot, Tbot


@logger.catch
async def main():
    qbot = Qbot(conf.qq_ws, conf.qq_http)
    tbot = Tbot(conf.tg_token, conf.tg_api)
    asyncio.create_task(tbot.start())
    await qbot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Exiting...")
