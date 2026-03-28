"""测试完整的创建草稿和发布流程"""
import asyncio
import os
from multi_writing_skills.platforms import ZhihuPlatform
from multi_writing_skills.platforms.base import PublishRequest

async def test_full_flow():
    cookie = os.environ.get("ZHIHU_COOKIE", "")
    if not cookie:
        print("未找到 ZHIHU_COOKIE")
        return

    platform = ZhihuPlatform(cookie=cookie)

    # 1. 创建草稿
    request = PublishRequest(
        title="自动化测试文章标题",
        content="<p>这是自动化测试的内容</p>",
        digest="这是摘要",
    )

    draft_result = await platform.create_draft(request)
    print(f"创建草稿: {draft_result}")

    if draft_result.success and draft_result.media_id:
        # 2. 发布草稿
        publish_result = await platform.publish_draft(
            draft_id=draft_result.media_id,
            title=request.title,
            content=request.content,
        )
        print(f"发布结果: {publish_result}")

    await platform.close()

if __name__ == "__main__":
    asyncio.run(test_full_flow())