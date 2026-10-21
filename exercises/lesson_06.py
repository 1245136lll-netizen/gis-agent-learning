"""第六课：python -m exercises.lesson_06；--live 才发送真实 GLM API 请求。"""

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit


SYSTEM_PROMPT = (
    "你是 GIS 编程学习助手，请用中文、面向初学者解释概念，回答尽量控制在 150 字以内。"
    "涉及具体地点、距离和数量时，要以项目实际工具结果为依据。"
    "本轮只解释概念；尚未执行 GIS 工具时，不编造地点或查询结果。"
)
DEFAULT_QUESTION = "在 GIS 查询中，为什么半径要用米表示？"
DEFAULT_MODEL = "glm-5.3-flash"
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"


def build_messages(user_text):
    """待实现：把用户问题组织成 system、user 两条消息组成的新列表。

    user_text 必须是非空字符串，排除空白字符串；否则抛出 ValueError。
    返回 [{"role": "system", "content": SYSTEM_PROMPT},
          {"role": "user", "content": 去掉首尾空白的用户问题}]。
    每次调用创建新的列表和字典；不发起网络请求，不返回 JSON 字符串。
    """
    # TODO 1：检查 user_text 是字符串，且 strip() 后非空。
    # TODO 2：创建两条消息，按 system、user 的顺序放进新列表并返回。
    if not isinstance(user_text,str) or not user_text.strip():
        raise ValueError(f"user_text必须是非空字符串")
    message1 = {
        "role": "system", 
        "content": SYSTEM_PROMPT
        }
    message2 = {
        "role": "user",
        "content": user_text.strip()
    }
    message = [message1,message2]
    return message


def extract_reply(response_data):
    """待实现：从已解析的 Chat Completions 响应字典提取完整文本回答。

    response_data 必须是字典；choices 必须是非空列表。
    只读取第一个候选：候选必须是字典，finish_reason 必须为 "stop"。
    候选的 message 必须是字典，role 为 "assistant"，content 为非空字符串。
    返回 content.strip()；额外字段允许存在，不修改输入。
    任一检查失败都抛出有说明的 ValueError，不以空字符串表示错误。
    本课处理非流式的纯文本回答，工具调用响应留到第七课处理。
    """
    # TODO 1：检查 response_data 和 choices 的类型及是否为空。
    # TODO 2：取 choices[0]，检查其类型与 finish_reason。
    # TODO 3：逐层检查 message、role、content，再返回整理后的正文。
    if not isinstance(response_data,dict):
        raise ValueError(f"response_data必须是字典")
    choices=response_data.get("choices")
    if not isinstance(choices,list) or not choices:
        raise ValueError(f"choices必须为非空列表")
    if not isinstance(choices[0],dict):
        raise ValueError(f"候选必须为字典")
    finish_reason = choices[0].get("finish_reason")
    if not finish_reason == "stop":
        raise ValueError(f"该字段必须为stop")
    message = choices[0].get("message")
    if not isinstance(message,dict):
        raise ValueError(f"message必须为字典")
    if not message.get("role") == "assistant":
        raise ValueError(f"role必须为assistant")
    if not isinstance(message.get("content"),str) or not message.get("content").strip():
        raise ValueError(f"content必须为非空字符串")
    return message.get("content").strip()


def load_offline_response():
    """已提供：读取教学样例，不需要 SDK、网络或 API Key。"""
    path = Path(__file__).resolve().parents[1] / "data" / "lesson_06_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


def call_model(messages):
    """已提供：用智谱标准模型 API 发送一次非流式 GLM 请求。"""
    api_key = os.getenv("GLM_API_KEY", "").strip()
    base_url = os.getenv("GLM_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
    model = os.getenv("GLM_MODEL", DEFAULT_MODEL).strip()
    if not api_key:
        raise ValueError("请先配置智谱的 GLM_API_KEY；不带 --live 可做离线练习")
    url = urlsplit(base_url)
    if (
        url.scheme != "https"
        or not url.hostname
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
        or url.path != "/api/paas/v4"
    ):
        raise ValueError("GLM_BASE_URL 应使用标准模型 API，例如 https://open.bigmodel.cn/api/paas/v4")
    if not model:
        raise ValueError("GLM_MODEL 必须是非空的模型 ID")

    # 延迟导入：离线练习只需要标准库。
    try:
        from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
    except ImportError as error:
        raise ValueError("请先执行 python -m pip install -r requirements-lesson-06.txt") from error

    try:
        with OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0,
            max_retries=0,
        ) as client:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                max_tokens=4096,
                reasoning_effort="low",
                extra_body={"thinking": {"type": "enabled"}},
            )
    except APITimeoutError as error:
        raise RuntimeError("GLM 请求超时，请检查网络或稍后重新运行") from error
    except APIConnectionError as error:
        raise RuntimeError("无法连接智谱，请检查网络和 GLM_BASE_URL") from error
    except APIStatusError as error:
        raise RuntimeError(
            f"智谱返回 HTTP {error.status_code}；请按讲义检查 Key、模型权限、请求参数和额度"
        ) from error

    # SDK 返回对象，这一步将它变成练习函数需要的 Python 字典。
    return completion.model_dump(mode="json")


def main(argv=None):
    parser = argparse.ArgumentParser(description="第六课：GLM API、消息和文本回答")
    parser.add_argument("--live", action="store_true", help="向智谱发送一次真实请求，按服务商规则计费")
    parser.add_argument("--question", default=DEFAULT_QUESTION, help="要解释的 GIS 问题")
    args = parser.parse_args(argv)
    try:
        messages = build_messages(args.question)
        print("本次请求消息：")
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        if args.live:
            print("模式：真实智谱 GLM API 请求")
            response_data = call_model(messages)
        else:
            print("模式：离线样例，回答预先编写，没有调用模型")
            response_data = load_offline_response()
            print("离线回答对应默认教学问题，更改问题不会改变样例回答。")
        reply = extract_reply(response_data)
        print("回答正文：")
        print(reply)
        if args.live:
            print("响应 ID：", response_data.get("id", "未提供"))
            print("请求 ID：", response_data.get("request_id", "未提供"))
            print("模型：", response_data.get("model", "未提供"))
            print("用量：", json.dumps(response_data.get("usage"), ensure_ascii=False))
    except NotImplementedError as error:
        print(f"练习待完成：{error}")
        return 1
    except (ValueError, RuntimeError) as error:
        print(f"运行错误：{error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
