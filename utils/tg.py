import asyncio
from time import time

from telegram import Bot, Message, Update
from telegram.ext import Updater

from .qq import Qbot
from .tools import Msg, conf, db, logger


class Tbot:
    def __init__(
        self,
        bot_token: str,
        base_url: str = "https://api.telegram.org/bot",
    ):
        """初始化bot参数

        Args:
            bot_token (str): 桥接 bot 的token
            base_url (str, optional): telegram 的 api 地址，默认为 https://api.telegram.org/bot
        """
        self.bot_token, self.base_url = bot_token, base_url

    @logger.catch
    async def on_message(self, bot: Bot, m: Message):
        """处理接受的消息

        Args:
            bot (Bot): 当前活动的 bot
            m (Message): 传入的消息模型
        """
        if m.text == "/chatid":
            logger.warning("Telegram: Get ID: {}", m.chat_id)
            await bot.send_message(
                m.chat_id,
                f"`{m.chat_id}`",
                parse_mode="MarkdownV2",
            )
        elif m.chat_id in conf.forward.g:
            logger.info("T->Qg | {}", m.text)
            await self.forward_to_qq(m, group_id=conf.forward.g[m.chat_id])
        elif m.chat_id in conf.forward.u:
            logger.info("T->Qu | {}", m.text)
            await self.forward_to_qq(m, user_id=conf.forward.u[m.chat_id])

    @logger.catch
    async def start(self):
        """运行bot，接受并处理消息"""
        self.qq = Qbot(conf.qq_ws, conf.qq_http)
        try:
            async with Bot(token=self.bot_token, base_url=self.base_url) as bot:
                self.bot = bot
                async with (updater := Updater(bot, asyncio.Queue())):
                    q = await updater.start_polling(timeout=20, read_timeout=5)
                    while True:
                        update: Update = await q.get()
                        if update.message and update.message.chat_id in conf.forward.a:
                            await self.on_message(bot, update.message)
        except RuntimeError:
            await updater.stop()  # type:ignore

    @logger.catch
    async def forward_to_qq(
        self,
        m: Message,
        user_id: int | None = None,
        group_id: int | None = None,
    ):
        """将消息转发到 qq

        Args:
            m (Message): 传入的消息模型
            user_id (int | None, optional): 要发送的用户id，默认为 None
            group_id (int | None, optional): 要发送的群id，默认为 None
        """
        msg_list = []
        if m.reply_to_message:
            reply_id = db.get_qq_msgid((m.reply_to_message.message_id, m.chat_id))
            msg_list.append(Msg.reply(reply_id))
        if m.text:
            msg_list.append(Msg.text(m.text))
        elif m.sticker:
            if m.sticker.is_animated or m.sticker.is_video:
                image_url = await self.cache_file_url(m.sticker.thumb.file_id)
            else:
                image_url = await self.cache_file_url(m.sticker.file_id)
            msg_list.append(Msg.image(image_url))
        elif m.photo:
            image_url = await self.cache_file_url(m.photo[-1].file_id)
            msg_list.append(Msg.image(image_url))
        elif m.document:
            if "image/" in m.document.mime_type:
                image_url = await self.cache_file_url(m.document.file_id)
                msg_list.append(Msg.image(image_url))
            elif "video/" in m.document.mime_type:
                video_url = await self.cache_file_url(m.document.file_id)
                msg_list.append(Msg.video(video_url))
        if m.caption:
            msg_list.append(Msg.text(m.caption))
        logger.debug("Send: {} -> {}", m, msg_list)
        db.sent_time = int(time())
        msg_id_qq: int = (
            (
                await self.qq.send_msg(
                    message=msg_list,
                    user_id=user_id,
                    group_id=group_id,
                )
            )
            .get("data", {})
            .get("message_id", 0)
        )
        db.set((m.message_id, m.chat_id), msg_id_qq)

    @logger.catch
    async def cache_file_url(self, file_id: str, reverse=True) -> str:
        """获取文件url，同时查询已获取的文件

        Args:
            file_id (str): telegram 的文件 id
            reverse (bool, optional): 是否使用自定义的 base_url ，默认为 True

        Returns:
            str: 文件地址
        """
        if file_id not in db.file_cache:
            photo_url = (await self.bot.get_file(file_id)).file_path
            reverse_url = self.base_url[:-3] + photo_url[25:]
            db.file_cache[file_id] = (photo_url, reverse_url)
        return db.file_cache[file_id][reverse]
