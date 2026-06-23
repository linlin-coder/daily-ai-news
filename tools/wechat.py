#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""微信公众号 API 客户端"""

import json
import os
import time
from urllib.request import urlopen, Request
from urllib.error import URLError


class WeChatAPI:
    def __init__(self, appid=None, appsecret=None):
        if appid is None or appsecret is None:
            # 从环境变量读取
            appid = os.environ.get("WECHAT_APPID", "")
            appsecret = os.environ.get("WECHAT_APPSECRET", "")

        if not appid or not appsecret:
            raise ValueError("Missing WECHAT_APPID or WECHAT_APPSECRET in environment")

        self.appid = appid
        self.appsecret = appsecret
        self.access_token = None
        self.token_time = 0

    def get_access_token(self):
        """获取 access_token（2小时有效）"""
        now = time.time()
        if self.access_token and (now - self.token_time) < 7000:
            return self.access_token

        url = (
            f"https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
        )
        req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if "access_token" in data:
            self.access_token = data["access_token"]
            self.token_time = now
            return self.access_token
        else:
            errcode = data.get("errcode", "unknown")
            errmsg = data.get("errmsg", "unknown")
            raise RuntimeError(f"WeChat token error {errcode}: {errmsg}")

    def upload_thumb_media(self, image_path):
        """上传永久封面图片"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=thumb"

        with open(image_path, "rb") as f:
            file_data = f.read()

        # 构建 multipart/form-data
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="media"; filename="thumb.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

        req = Request(url, data=body, headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "DailyAINews/1.0",
        })
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if "media_id" in data:
            return data["media_id"]
        else:
            print(f"[wechat] Thumb upload failed: {data}")
            return None

    def upload_image_media(self, image_path):
        """上传文章内图片，返回可用于正文的 URL"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"

        with open(image_path, "rb") as f:
            file_data = f.read()

        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="media"; filename="chart.png"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

        req = Request(url, data=body, headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "DailyAINews/1.0",
        })
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if "url" in data:
            return data["url"]
        else:
            print(f"[wechat] Image upload failed: {data}")
            return None

    def create_draft(self, title, author, digest, content, thumb_media_id=""):
        """创建草稿（不发布）"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

        payload = {
            "articles": [{
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "content_source_url": "",
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 0,
            }]
        }

        data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = Request(url, data=data_bytes, headers={
            "Content-Type": "application/json",
            "User-Agent": "DailyAINews/1.0",
        })
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if "media_id" in data:
            return data["media_id"]
        else:
            raise RuntimeError(f"Draft creation failed: {data}")

    def publish_draft(self, media_id):
        """发布草稿（自动发布到公众号）"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"

        payload = {"media_id": media_id}
        data_bytes = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data_bytes, headers={
            "Content-Type": "application/json",
            "User-Agent": "DailyAINews/1.0",
        })
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("errcode") == 0:
            return data.get("publish_id", "")
        else:
            raise RuntimeError(f"Publish failed: {data}")

    def create_and_publish(self, title, author, digest, content):
        """创建草稿并发布"""
        media_id = self.create_draft(title, author, digest, content)
        try:
            publish_id = self.publish_draft(media_id)
            return media_id, publish_id
        except Exception as e:
            print(f"[wechat] Publish failed, draft created: {media_id}")
            return media_id, None


if __name__ == "__main__":
    # 测试获取 access_token
    from config import load_env
    load_env()

    wx = WeChatAPI()
    try:
        token = wx.get_access_token()
        print(f"[wechat] Access token: {token[:20]}...")
    except Exception as e:
        print(f"[wechat] Error: {e}")
