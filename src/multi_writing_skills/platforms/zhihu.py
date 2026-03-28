"""
知乎平台适配器
"""

import json
import re
import time
from pathlib import Path
from typing import Optional

import httpx

from .base import ImageUploadResult, Platform, PublishRequest, PublishResult


class ZhihuPlatform(Platform):
    """知乎平台"""

    BASE_URL = "https://www.zhihu.com/api/v4"
    WEB_URL = "https://zhuanlan.zhihu.com"

    def __init__(self, cookie: str) -> None:
        self.cookie = cookie
        self._client = httpx.AsyncClient(timeout=30.0)
        self._x_zse_96: Optional[str] = None
        self._x_xsrf_token: Optional[str] = None

    @property
    def name(self) -> str:
        return "zhihu"

    @property
    def display_name(self) -> str:
        return "知乎"

    def is_configured(self) -> bool:
        return bool(self.cookie)

    def _parse_xsrf_token(self) -> Optional[str]:
        """从 Cookie 中解析 x_xsrf_token"""
        # 尝试 x_xsrf_token 和 _xsrf 两种格式
        match = re.search(r"x_xsrf_token=([^;]+)", self.cookie)
        if not match:
            match = re.search(r"_xsrf=([^;]+)", self.cookie)
        if match:
            return match.group(1)
        return None

    def _get_headers(self, api_version: str = "v4") -> dict[str, str]:
        """获取请求头"""
        xsrf = self._parse_xsrf_token() or ""
        if api_version == "v3":
            # v3 API 需要的请求头
            return {
                "Cookie": self.cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "Referer": "https://www.zhihu.com/composer",
                "X-Xsrftoken": xsrf,
                "Origin": "https://www.zhihu.com",
            }
        return {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "x-xsrf-token": xsrf,
            "x-zse-83": "403_3.0",
        }

    def _get_headers_for_zhuanlan(self) -> dict[str, str]:
        """获取知乎专栏请求头"""
        xsrf = self._parse_xsrf_token() or ""
        return {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://zhuanlan.zhihu.com/",
            "Origin": "https://zhuanlan.zhihu.com",
            "X-Xsrftoken": xsrf,
        }

    def _get_headers_for_publish(self) -> dict[str, str]:
        """获取发布文章请求头"""
        xsrf = self._parse_xsrf_token() or ""
        return {
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.zhihu.com/",
            "Origin": "https://www.zhihu.com",
            "X-Xsrftoken": xsrf,
        }

    async def validate_credentials(self) -> bool:
        """验证凭证是否有效"""
        try:
            url = "https://www.zhihu.com/api/v4/me"
            resp = await self._client.get(url, headers=self._get_headers())
            data = resp.json()
            return "id" in data
        except Exception:
            return False

    async def upload_image(self, image_path: str) -> ImageUploadResult:
        """上传图片到知乎图床"""
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

            # 知乎图片上传
            url = f"{self.BASE_URL}/images"
            headers = self._get_headers()
            headers["Content-Type"] = "image/jpeg"

            params = {"image_source": "bubian_m", "image_name": filename}

            resp = await self._client.post(
                url, headers=headers, params=params, content=image_data
            )
            data = resp.json()

            if "upload_url" in data:
                # 获取上传结果
                upload_resp = await self._client.put(
                    data["upload_url"],
                    content=image_data,
                    headers={"Content-Type": "image/jpeg"},
                )
                if upload_resp.status_code == 200:
                    return ImageUploadResult(
                        success=True,
                        url=data.get("original_src", ""),
                        message="上传成功",
                    )

            if "src" in data or "original_src" in data:
                return ImageUploadResult(
                    success=True,
                    url=data.get("src") or data.get("original_src", ""),
                    message="上传成功",
                )

            return ImageUploadResult(
                success=False, message=f"上传失败: {data.get('message', '未知错误')}"
            )

        except Exception as e:
            return ImageUploadResult(success=False, message=f"上传异常: {str(e)}")

    async def publish(self, request: PublishRequest) -> PublishResult:
        """发布文章到知乎专栏"""
        try:
            # 如果有封面图片，先上传
            cover_image_id = None
            if request.cover:
                result = await self.upload_image(request.cover)
                if result.success and result.url:
                    cover_image_id = result.url

            # 构建文章数据
            url = f"{self.BASE_URL}/articles"
            headers = self._get_headers()

            payload = {
                "title": request.title,
                "content": request.content,
                "excerpt": request.digest or "",
                "source_url": request.source_url or "",
                "can_comment": True,
                "image_url": cover_image_id or "",
                "disclaimer_type": 0,
                "disclaimer_status": "disclaimer_none",
            }

            # 如果指定了专栏
            if request.column_id:
                payload["column_id"] = request.column_id

            resp = await self._client.post(url, headers=headers, json=payload)
            data = resp.json()

            if "id" in data:
                article_id = data["id"]
                article_url = f"https://zhuanlan.zhihu.com/p/{article_id}"

                return PublishResult(
                    success=True,
                    platform=self.name,
                    article_url=article_url,
                    message="发布成功",
                )

            if "error" in data:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    message=f"发布失败: {data['error'].get('message', '未知错误')}",
                )

            return PublishResult(
                success=False, platform=self.name, message=f"发布失败: {data}"
            )

        except Exception as e:
            return PublishResult(
                success=False, platform=self.name, message=f"发布异常: {str(e)}"
            )

    async def create_draft(self, request: PublishRequest) -> PublishResult:
        """创建文章草稿到知乎"""
        try:
            # 如果有封面图片，先上传
            cover_image_id = None
            if request.cover:
                result = await self.upload_image(request.cover)
                if result.success and result.url:
                    cover_image_id = result.url

            # 使用专栏 API 创建草稿
            url = "https://zhuanlan.zhihu.com/api/articles/drafts"
            headers = self._get_headers_for_zhuanlan()

            # 构建草稿数据
            payload = {
                "title": request.title,
                "content": request.content,
                "excerpt": request.digest or "",
                "image_url": cover_image_id or "",
            }

            resp = await self._client.post(url, headers=headers, json=payload)
            data = resp.json()

            if "id" in data:
                draft_id = data["id"]
                # 草稿没有公开 URL，返回内部 ID
                return PublishResult(
                    success=True,
                    platform=self.name,
                    media_id=str(draft_id),
                    title=request.title,
                    message=f"草稿创建成功，ID: {draft_id}",
                )

            if "error" in data:
                return PublishResult(
                    success=False,
                    platform=self.name,
                    message=f"创建草稿失败: {data['error'].get('message', '未知错误')}",
                )

            return PublishResult(
                success=False, platform=self.name, message=f"创建草稿失败: {data}"
            )

        except Exception as e:
            return PublishResult(
                success=False, platform=self.name, message=f"创建草稿异常: {str(e)}"
            )

    async def publish_draft(
        self,
        draft_id: str,
        title: str = "",
        content: str = "",
        comment_permission: str = "anyone",
    ) -> PublishResult:
        """发布知乎草稿"""
        try:
            import uuid
            import time

            url = "https://www.zhihu.com/api/v4/content/publish"
            headers = self._get_headers_for_publish()

            # 构建发布请求
            trace_id = f"{int(time.time() * 1000)},{uuid.uuid4()}"

            pc_business_params = {
                "commentPermission": comment_permission,
                "disclaimer_type": "none",
                "disclaimer_status": "close",
                "table_of_contents_enabled": False,
                "content": content,
                "title": title,
                "commercial_report_info": {"commercial_types": []},
                "commercial_zhitask_bind_info": None,
                "canReward": False,
            }

            import json

            publish_payload = {
                "action": "article",
                "data": {
                    "publish": {"traceId": trace_id},
                    "extra_info": {
                        "publisher": "pc",
                        "pc_business_params": json.dumps(pc_business_params),
                    },
                    "draft": {
                        "disabled": 1,
                        "id": draft_id,
                        "isPublished": False,
                    },
                    "commentsPermission": {"comment_permission": comment_permission},
                    "creationStatement": {
                        "disclaimer_type": "none",
                        "disclaimer_status": "close",
                    },
                    "contentsTables": {"table_of_contents_enabled": False},
                    "commercialReportInfo": {"isReport": 0},
                    "appreciate": {"can_reward": False, "tagline": ""},
                    "hybridInfo": {},
                    "hybrid": {"html": content, "textLength": len(content)},
                    "title": {"title": title},
                },
            }

            resp = await self._client.post(url, headers=headers, json=publish_payload)
            data = resp.json()

            if data.get("code") == 0 or "success" in data.get("message", "").lower():
                # 解析返回的文章 ID
                result_data = data.get("data", {}).get("result", "{}")
                if isinstance(result_data, str):
                    import json

                    result_data = json.loads(result_data)
                article_id = result_data.get("publish", {}).get("id", draft_id)
                article_url = f"https://zhuanlan.zhihu.com/p/{article_id}"
                return PublishResult(
                    success=True,
                    platform=self.name,
                    article_url=article_url,
                    media_id=article_id,
                    message=f"发布成功: {article_url}",
                )

            return PublishResult(
                success=False,
                platform=self.name,
                message=f"发布草稿失败: {data.get('message', str(data))}",
            )

        except Exception as e:
            return PublishResult(
                success=False, platform=self.name, message=f"发布草稿异常: {str(e)}"
            )

    async def get_columns(self) -> list[dict]:
        """获取用户的专栏列表"""
        try:
            # 先获取用户信息
            me_resp = await self._client.get(
                "https://www.zhihu.com/api/v4/me", headers=self._get_headers()
            )
            me_data = me_resp.json()

            if "url_token" not in me_data:
                return []

            # 获取专栏列表
            url = f"{self.BASE_URL}/people/{me_data['url_token']}/columns"
            resp = await self._client.get(url, headers=self._get_headers())
            data = resp.json()

            if "data" in data:
                return [{"id": c["id"], "title": c["title"]} for c in data["data"]]
            return []

        except Exception:
            return []

    async def close(self) -> None:
        """关闭客户端连接"""
        await self._client.aclose()