"""
微信公众号平台适配器
"""

import hashlib
import hmac
import time
from pathlib import Path
from typing import Optional

import httpx

from .base import ImageUploadResult, Platform, PublishRequest, PublishResult


class WeChatPlatform(Platform):
    """微信公众号平台"""

    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._client = httpx.AsyncClient(timeout=30.0)

    @property
    def name(self) -> str:
        return "wechat"

    @property
    def display_name(self) -> str:
        return "微信公众号"

    def is_configured(self) -> bool:
        return bool(self.app_id and self.app_secret)

    async def _get_access_token(self) -> str:
        """获取 access_token"""
        # 检查缓存是否有效
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        url = f"{self.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
        }

        resp = await self._client.get(url, params=params)
        data = resp.json()

        if "errcode" in data:
            raise RuntimeError(f"获取 access_token 失败: {data.get('errmsg')}")

        self._access_token = data["access_token"]
        # 提前 5 分钟过期
        self._token_expires_at = time.time() + data["expires_in"] - 300

        return self._access_token

    async def validate_credentials(self) -> bool:
        """验证凭证是否有效"""
        try:
            await self._get_access_token()
            return True
        except Exception:
            return False

    async def upload_image(self, image_path: str) -> ImageUploadResult:
        """上传图片到微信素材库"""
        token = await self._get_access_token()

        # 判断是 URL 还是本地文件
        if image_path.startswith(("http://", "https://")):
            # 下载远程图片
            resp = await self._client.get(image_path)
            image_data = resp.content
            filename = image_path.split("/")[-1].split("?")[0]
        else:
            # 读取本地文件
            path = Path(image_path)
            if not path.exists():
                return ImageUploadResult(
                    success=False, message=f"图片文件不存在: {image_path}"
                )
            image_data = path.read_bytes()
            filename = path.name

        # 上传到微信
        url = f"{self.BASE_URL}/material/add_material"
        params = {"access_token": token, "type": "image"}

        files = {"media": (filename, image_data, "image/jpeg")}
        resp = await self._client.post(url, params=params, files=files)
        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            return ImageUploadResult(
                success=False, message=f"上传失败: {data.get('errmsg')}"
            )

        return ImageUploadResult(
            success=True, url=data.get("url"), media_id=data.get("media_id")
        )

    async def publish(self, request: PublishRequest) -> PublishResult:
        """发布文章到微信草稿箱"""
        try:
            token = await self._get_access_token()

            # 上传封面图片（必须有封面）
            thumb_media_id = None
            if request.cover:
                result = await self.upload_image(request.cover)
                if result.success and result.media_id:
                    thumb_media_id = result.media_id
                else:
                    return PublishResult(
                        success=False,
                        platform=self.name,
                        message=f"封面上传失败: {result.message}",
                    )
            else:
                # 没有封面时，生成默认封面
                thumb_media_id = await self._upload_default_cover(token)
                if not thumb_media_id:
                    return PublishResult(
                        success=False,
                        platform=self.name,
                        message="默认封面上传失败",
                    )

            # 创建草稿
            url = f"{self.BASE_URL}/draft/add"
            params = {"access_token": token}

            articles = [
                {
                    "title": request.title,
                    "author": request.author or "",
                    "digest": request.digest or "",
                    "content": request.content,
                    "content_source_url": request.source_url or "",
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0,
                }
            ]

            payload = {"articles": articles}

            resp = await self._client.post(url, params=params, json=payload)
            data = resp.json()

            if "errcode" in data and data["errcode"] != 0:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    message=f"创建草稿失败: {data.get('errmsg')}",
                )

            media_id = data["media_id"]

            return PublishResult(
                success=True,
                platform=self.name,
                media_id=media_id,
                draft_url=f"https://mp.weixin.qq.com",
                message="草稿创建成功",
            )

        except Exception as e:
            return PublishResult(
                success=False, platform=self.name, message=f"发布失败: {str(e)}"
            )

    async def _upload_default_cover(self, token: str) -> Optional[str]:
        """生成并上传默认封面图片"""
        try:
            import io

            from PIL import Image, ImageDraw, ImageFont

            # 创建一个简单的渐变封面
            width, height = 900, 500
            img = Image.new("RGB", (width, height), color="#4A90D9")

            # 添加一些装饰
            draw = ImageDraw.Draw(img)

            # 绘制渐变效果
            for i in range(height):
                r = int(74 + (i / height) * 30)
                g = int(144 - (i / height) * 50)
                b = int(217 - (i / height) * 30)
                draw.line([(0, i), (width, i)], fill=(r, g, b))

            # 保存到内存
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            image_data = buffer.getvalue()

            # 上传到微信
            url = f"{self.BASE_URL}/material/add_material"
            params = {"access_token": token, "type": "image"}

            files = {"media": ("cover.jpg", image_data, "image/jpeg")}
            resp = await self._client.post(url, params=params, files=files)
            data = resp.json()

            if "media_id" in data:
                return data["media_id"]
            return None

        except Exception:
            return None

    async def close(self) -> None:
        """关闭客户端连接"""
        await self._client.aclose()