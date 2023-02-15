# Q2TG-py

QQ 群与 Telegram 群相互转发的桥接机器人，适合tg重度用户单独使用。受 [Clansty/Q2TG](https://github.com/Clansty/Q2TG) 启发。

## 如何部署

1. 环境配置：python == 3.10

    如果python版本已经是3.10，建议使用 venv
    ```bash
    python -m venv venv --upgrade-deps
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    如果系统默认python版本非3.10，建议使用 conda
    ```bash
    conda create -n q2tg python=3.10 -y
    conda activate q2tg
    pip install -r requirements.txt
    ```

2. 运行一个 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases/latest) 实例，配置文件可参考 `bot/example_config.yml`，注意启用 http 和正向 ws 通信
3. 参考 `example_config.toml` ，填写 `config.toml` （如果不知道群的 ID，可以先不配置转发匹配，直接运行 bot，在需要查询 ID 的 TG 群里发送 /chatid 指令即可获得 ID）
4. 开始运行
    ```bash
    python main.py
    ```
    输入 Ctrl-D 或 `q` 回车退出

## 支持的消息类型

- [x] 群聊
- [x] 好友私聊
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
  - [x] TG -> QQ 转发图片文件
  - [ ] TG -> QQ 自动转发 20M 以下的小文件
- [ ] 视频（双向）
- [ ] 语音（双向）
- [ ] JSON/XML 卡片
- [ ] 双向转发消息记录
  - [ ] TG 转发单条消息，QQ 显示消息来源
  - [ ] QQ 合并转发，TG 展开消息记录
- [x] TG 编辑消息，QQ 撤回并重发
- [ ] 双向撤回消息
  - [ ] QQ 撤回消息，TG 显示删除线
  - [x] TG 删除消息，QQ 撤回（因bot无法接收删除事件，目前实现方式为编辑消息内容为 `/rm` ）
- [ ] 快速+1功能

## 其他大饼
- [x] 做成类似 oicq-http 的可交互 cli（初步）
- [ ] 所有私聊转发到同一个群
- [ ] 动图与 Sticker 转码发送
- [ ] 解析 Bilibili 分享卡片
- [ ] 同时连接多个 go-cqhttp 实现多账号统一收发
- [ ] 更详细的 readme 或 wiki，完整的一套教程
- [ ] 打个docker，一键运行
- [ ] 加入参数指定配置文件运行
- [ ] 待补充

## Bug列表
- [x] 发送 telegram 消息失败时触发 TelegramError
- [x] 查询不到历史消息时触发 KeyError
- [x] 部分特殊字符不会被 escape
- [x] telegram 编辑重发的消息可能被转发回来
- [x] telegram 发送的图片消息可能被转发回来
- [x] 用户名里的链接可能被识别为网址，触发自动预览
- [x] 转发失败时触发 UnboundLocalError
- [ ] 待补充

## 效果展示
![图1](https://user-images.githubusercontent.com/44391900/217712338-68e5da98-a2ba-4ab3-829a-709dddf03e7b.jpg)

## 我的状态
![图片](https://user-images.githubusercontent.com/44391900/217711971-7fc9d25e-2c7d-4f9a-bbe9-b48bba2b65d8.png)