"""独立示例：在项目根目录执行 python examples/messages_basics.py。"""

import json
from pathlib import Path


def main():
    messages = [
        {"role": "system", "content": "你是 GIS 编程学习助手，请用中文解释概念。"},
        {"role": "user", "content": "查询半径为什么用米表示？"},
    ]
    print("发送前的消息列表：")
    print(json.dumps(messages, ensure_ascii=False, indent=2))
    print("第一条消息的角色：", messages[0]["role"])
    print("第二条消息的内容：", messages[1]["content"])

    path = Path(__file__).resolve().parents[1] / "data" / "lesson_06_response.json"
    response_data = json.loads(path.read_text(encoding="utf-8"))
    print("\n以下读取预先编写的离线样例，没有调用模型：")
    print(json.dumps(response_data, ensure_ascii=False, indent=2))
    print("choices 的 Python 类型：", type(response_data["choices"]).__name__)
    print("第一个候选的结束原因：", response_data["choices"][0]["finish_reason"])
    print("message.content 的 Python 类型：", type(response_data["choices"][0]["message"]["content"]).__name__)
    print("本例 usage 中的 0 是占位数字，不是一次真实调用的用量。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
