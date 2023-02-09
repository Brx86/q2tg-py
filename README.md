# Q2TG-py

QQ 群与 Telegram 群相互转发的桥接机器人，但 telegram 群里只有机器人和用户。受 [Clansty/Q2TG](https://github.com/Clansty/Q2TG) 启发。

## 如何部署

1. 环境配置：
python == 3.10
    ```bash
    python -m venv venv --upgrade-deps
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2. 运行一个 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases/latest) 实例，配置文件可参考 `bot/example_config.yml`
3. 参考 `example_config.toml` ，配置一个 `config.toml`
4. 开始运行
    ```bash
    python main.py
    ```

## 支持的消息类型

- [x] 文字（双向）
- [x] 图片（双向）
- [x] 图文混排消息（双向）
- [x] 回复（双平台原生回复）
- [x] 小表情（可显示为文字）
- [x] 大表情（双向）
  - [x] TG 中的动态 Sticker（目前仅发送缩略图）
- [x] 链接（双向）
- [ ] 文件（双向）
  - [x] QQ -> TG 获取下载地址
  - [ ] TG -> QQ 自动转发 20M 以下的小文件
- [ ] 视频（双向）
- [ ] 语音（双向）
- [ ] JSON/XML 卡片
- [ ] 转发多条消息记录
- [ ] TG 编辑消息（撤回再重发）
- [ ] 双向撤回消息
