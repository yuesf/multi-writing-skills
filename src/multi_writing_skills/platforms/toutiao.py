"""
今日头条平台适配器
"""

import json
import re
import time
from pathlib import Path
from typing import Optional

import httpx

from .base import ImageUploadResult, Platform, PublishRequest, PublishResult


class ToutiaoPlatform(Platform):
    """今日头条平台"""

    BASE_URL = "https://mp.toutiao.com/mp_v3"

    def __init__(self, cookie: str) -> None:
        self.cookie = cookie
        self._client = httpx.AsyncClient(timeout=30.0)

    @property
    def name(self) -> str:
        return "toutiao"

    @property
    def display_name(self) -> str:
        return "今日头条"

    def is_configured(self) -> bool:
        return bool(self.cookie)

    def _get_headers(self) -> dict[str, str]:
        """获取请求头"""
        return {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://mp.toutiao.com/",
        }

    async def validate_credentials(self) -> bool:
        """验证凭证是否有效"""
        try:
            url = f"{self.BASE_URL}/user/info"
            resp = await self._client.get(url, headers=self._get_headers())
            data = resp.json()
            return data.get("ret") == "success"
        except Exception:
            return False

    async def upload_image(self, image_path: str) -> ImageUploadResult:
        """上传图片到头条图床"""
        try:
            # 判断是 URL 还是本地文件
            if image_path.startswith(("http://", "https://")):
                resp = await self._client.get(image_path)
                image_data = resp.content
                filename = image_path.split("/")[-1].split("?")[0]
            else:
                path = Path(image_path)
                if not path.exists():
                    return ImageUploadResult(
                        success=False, message=f"图片文件不存在: {image_path}"
                    )
                image_data = path.read_bytes()
                filename = path.name

            # 头条图片上传
            url = f"{self.BASE_URL}/image/upload"
            headers = self._get_headers()
            del headers["Content-Type"]  # multipart 上传需要删除这个

            files = {"image": (filename, image_data, "image/jpeg")}
            resp = await self._client.post(url, headers=headers, files=files)
            data = resp.json()

            if data.get("ret") == "success" and "url" in data.get("data", {}):
                return ImageUploadResult(
                    success=True,
                    url=data["data"]["url"],
                    message="上传成功",
                )

            return ImageUploadResult(
                success=False, message=f"上传失败: {data.get('msg', '未知错误')}"
            )

        except Exception as e:
            return ImageUploadResult(success=False, message=f"上传异常: {str(e)}")

    async def publish(self, request: PublishRequest) -> PublishResult:
        """发布文章到今日头条"""
        try:
            # 如果有封面图片，先上传
            cover_url = None
            if request.cover:
                result = await self.upload_image(request.cover)
                if result.success and result.url:
                    cover_url = result.url

            # 构建文章数据
            url = f"{self.BASE_URL}/article/create"
            headers = self._get_headers()

            payload = {
                "title": request.title,
                "content": request.content,
                "cover_url": cover_url or "",
                "abstract": request.digest or "",
                "source_url": request.source_url or "",
                "tag": ",".join(request.tags) if request.tags else "",
            }

            resp = await self._client.post(url, headers=headers, json=payload)
            data = resp.json()

            if data.get("ret") == "success":
                article_id = data.get("data", {}).get("article_id")
                article_url = f"https://www.toutiao.com/article/{article_id}"

                return PublishResult(
                    success=True,
                    platform=self.name,
                    article_url=article_url,
                    message="发布成功",
                )

            return PublishResult(
                success=False,
                platform=self.name,
                message=f"发布失败: {data.get('msg', '未知错误')}",
            )

        except Exception as e:
            return PublishResult(
                success=False, platform=self.name, message=f"发布异常: {str(e)}"
            )

    async def close(self) -> None:
        """关闭客户端连接"""
        await self._client.aclose()