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
    tbot = Tbot(conf.tg_token, conf.tg_api)
    qbot = Qbot(conf.qq_ws, conf.qq_http)
    loop = asyncio.get_event_loop()
    loop.create_task(tbot.run())
    loop.create_task(qbot.run())
    while True:
        try:
            cmd = await loop.run_in_executor(None, input, ">")
            match cmd:
                case "h" | "help":
                    logger.warning("Commands: help, config, exit")
                case "c" | "config":
                    logger.warning(conf)
                case "q" | "quit" | "exit":
                    raise EOFError
        except (KeyboardInterrupt, EOFError):
            logger.warning("Exiting...")
            return


if __name__ == "__main__":
    asyncio.run(main())
