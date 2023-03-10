import asyncio
import json
from functools import partial

from httpx import AsyncClient
from telegram import Bot
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.client import connect

from .models import DataModel
from .tools import conf, db, escaped_md, facemap, logger


class Qbot:
    def __init__(self, qq_ws: str, qq_http: str):
        """初始化bot参数

        Args:
            qq_ws (str): gocqhttp 的正向 ws 地址，形如 ws://ip:port
            qq_http (str): gocqhttp 的正向 http 地址，形如http://ip:port
        """
        self.ws, self.http = qq_ws, qq_http

    def __getattr__(self, name: str):
        """魔术方法，调用任意api"""
        return partial(self.call_gocq, name)

    @logger.catch
    async def call_gocq(self, method: str, **kwargs) -> dict:
        """调用 gocqhttp 的 http api

        Args:
            method (str): api终结点，参见 https://docs.go-cqhttp.org/api

        Returns:
            dict: api返回值
        """
        async with AsyncClient(base_url=self.http, timeout=10) as client:
            result = (await client.post(method, json=kwargs)).json()
            if result.get("retcode") == 0:
                return result
            logger.error(result)
            return {}

    @logger.catch
    async def on_message(self, message: str | bytes):
        """处理接受的消息

        Args:
            message (str | bytes): websocket client 接受到的数据
        """
        d = DataModel.parse_raw(message)
        if db.sent and d.post_type == "message_sent":
            logger.debug("Sent: {}", d.raw_message)
            db.sent = False
        elif d.message_type == "group" and (d.group_id in conf.forward.g):
            logger.info(f"<- Group {d.group_id}-{d.user_id}: {d.raw_message}")
            await self.forward_to_tg(conf.forward.g[d.group_id], d)
        elif d.message_type == "private" and (d.user_id in conf.forward.u):
            logger.info(f"<- User {d.user_id}: {d.raw_message}")
            await self.forward_to_tg(conf.forward.u[d.user_id], d)
        elif "recall" in d.notice_type and d.message_id in db.qq:  # type:ignore
            if not conf.anti_recall:
                await self.recall_msg(d.message_id)

    @logger.catch
    async def ws_client(self):
        """websocket client，连接 gocqhttp 的服务端"""
        async with connect(self.ws) as ws:
            if "meta_event_type" in json.loads(await ws.recv()):
                logger.success("Successful connection to '{}'", self.ws)
            async for message in ws:
                asyncio.create_task(self.on_message(message))

    @logger.catch
    async def run(self):
        """运行bot，接受并处理消息"""
        self.tg = Bot(token=conf.tg_token, base_url=conf.tg_api)
        await self.tg.initialize()
        while True:
            try:
                await self.ws_client()
            except (ConnectionClosedError, ConnectionRefusedError):
                logger.warning("Connection closed, retrying in 5 seconds...")
            await asyncio.sleep(5)

    @logger.catch
    async def forward_to_tg(self, chat_id: int, d: DataModel):
        """将消息转发到 telegram 群

        Args:
            chat_id (int): 消息所在群/用户对应的 telegram 群的 chai_id
            d (DataModel): 传入的消息模型
        """
        msg_id_tg = None
        if d.message and d.sender:
            user_name = escaped_md(d.sender.card or d.sender.nickname, extra=True)
            reply_id, text, img_list = await self.create_msg(d)
            if img_list:
                for img in img_list:
                    msg_id_tg = await self.send_to_tg(
                        chat_id=chat_id,
                        text=f"*{user_name}*: [⁣⁣⁣图片]({img})",
                        parse_mode="MarkdownV2",
                    )
            if text:
                msg_id_tg = await self.send_to_tg(
                    chat_id=chat_id,
                    reply_to_message_id=reply_id,
                    text=f"*{user_name}*:\n{escaped_md(text)}",
                    parse_mode="MarkdownV2",
                )
        elif d.file:
            size = escaped_md(f"{d.file.size/1048576:.2f}")
            file_name = escaped_md(d.file.name)
            text = f"大小: {size}MB\n文件: [{(file_name)}]({d.file.url})"
            msg_id_tg = await self.send_to_tg(
                chat_id=chat_id,
                text=text,
                parse_mode="MarkdownV2",
            )
        else:
            return
        if msg_id_tg and d.message_id:
            db.set((msg_id_tg, chat_id), d.message_id)

    @logger.catch
    async def create_msg(self, d: DataModel) -> tuple:
        """生成要发送的消息

        Args:
            d (DataModel): 传入的消息模型

        Returns:
            tuple: _description_
        """
        reply_id, text, img_list = None, "", []
        for msg in d.message:  # type:ignore
            match msg.type:
                case "at":
                    at = msg.data["qq"]
                    if at == "all":
                        at_name = "全体成员"
                    else:
                        at_info = (
                            await self.get_group_member_info(
                                group_id=d.group_id, user_id=at
                            )
                        ).get("data", {})
                        at_name = at_info.get("card") or at_info.get("nickname")
                    text = f"{text}@{at_name} "
                case "text":
                    text = f'{text}{msg.data["text"]} '
                case "face":
                    text = f'{text}{facemap[msg.data["id"]]} '
                case "image":
                    img_list.append(msg.data["url"])
                case "reply":
                    reply_id = db.get_tg_msgid(msg.data["id"])[0]
                case "video":
                    text = "[暂不支持视频消息]"
                case "forward":
                    text = "[暂不支持合并转发消息]"
                case "record":
                    text = "[暂不支持语音消息]"
                case _:
                    logger.warning(f"[不支持的消息]: {msg.type}")
        return reply_id, text, img_list

    @logger.catch
    async def send_to_tg(self, **kwargs):
        for _ in range(3):
            try:
                return (await self.tg.send_message(**kwargs)).message_id
            except Exception as e:
                logger.error("Retrying {} times... {}", _ + 1, repr(e))
                await asyncio.sleep(2)

    @logger.catch
    async def recall_msg(self, qq_msgid):
        msg_list = (await self.get_msg(message_id=qq_msgid))["data"]["message"]
        raw_message = " ".join([m["data"].get("text", "") for m in msg_list])
        logger.info(f"<- Delete msg {qq_msgid}: {raw_message}")
        tg_msgid, chat_id = db.qq[qq_msgid]
        await self.tg.delete_message(chat_id=chat_id, message_id=tg_msgid)
