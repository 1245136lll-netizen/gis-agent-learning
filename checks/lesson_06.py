"""在项目根目录执行 python -m checks.lesson_06；不发送真实 API 请求。"""

from contextlib import redirect_stdout
import copy
import io
import json
import unittest
from unittest.mock import patch

from exercises.lesson_06 import (
    DEFAULT_QUESTION,
    SYSTEM_PROMPT,
    build_messages,
    extract_reply,
    load_offline_response,
    main as lesson_main,
)


def response_with_text(text):
    response = load_offline_response()
    response["choices"][0]["message"]["content"] = text
    return response


class MessageChecks(unittest.TestCase):
    def test_valid_message_structure(self):
        messages = build_messages("为什么使用米？")
        self.assertEqual(messages, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "为什么使用米？"},
        ])

    def test_invalid_question(self):
        for value in [None, 1, True, [], {}, "", " \n\t "]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as caught:
                    build_messages(value)
                self.assertTrue(str(caught.exception).strip())

    def test_question_whitespace(self):
        messages = build_messages(" \n 为什么使用米？ \t")
        self.assertEqual(messages[1]["content"], "为什么使用米？")

    def test_fresh_containers(self):
        first = build_messages("问题甲")
        second = build_messages("问题乙")
        self.assertIsNot(first, second)
        self.assertIsNot(first[0], second[0])
        self.assertIsNot(first[1], second[1])
        first[0]["content"] = "被修改"
        first.append({"role": "assistant", "content": "示例"})
        self.assertEqual(second, [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "问题乙"},
        ])


class ReplyChecks(unittest.TestCase):
    def assert_invalid_response(self, response):
        with self.assertRaises(ValueError) as caught:
            extract_reply(response)
        self.assertTrue(str(caught.exception).strip())

    def test_valid_reply(self):
        response = load_offline_response()
        self.assertEqual(extract_reply(response), response["choices"][0]["message"]["content"])

    def test_response_outer_type(self):
        for value in [None, [], "{}", 1, True]:
            with self.subTest(value=value):
                self.assert_invalid_response(value)

    def test_choices_structure(self):
        self.assert_invalid_response({})
        for value in [None, {}, "choices", [], [None], [1], [[]]]:
            with self.subTest(value=value):
                self.assert_invalid_response({"choices": value})

    def test_finish_reason(self):
        for value in [None, "length", "tool_calls", "content_filter", "", 1]:
            response = load_offline_response()
            response["choices"][0]["finish_reason"] = value
            with self.subTest(value=value):
                self.assert_invalid_response(response)
        response = load_offline_response()
        response["choices"][0].pop("finish_reason")
        self.assert_invalid_response(response)

    def test_message_structure(self):
        for value in [None, [], "message", 1]:
            response = load_offline_response()
            response["choices"][0]["message"] = value
            with self.subTest(value=value):
                self.assert_invalid_response(response)
        response = load_offline_response()
        response["choices"][0].pop("message")
        self.assert_invalid_response(response)

    def test_assistant_role(self):
        for value in [None, "user", "system", "Assistant", 1]:
            response = load_offline_response()
            response["choices"][0]["message"]["role"] = value
            with self.subTest(value=value):
                self.assert_invalid_response(response)

    def test_content_type_and_empty(self):
        for value in [None, 1, False, [], {}, "", " \n\t"]:
            with self.subTest(value=value):
                self.assert_invalid_response(response_with_text(value))
        response = load_offline_response()
        response["choices"][0]["message"].pop("content")
        self.assert_invalid_response(response)

    def test_trim_and_keep_text(self):
        self.assertEqual(extract_reply(response_with_text(" \n 米制距离 \t")), "米制距离")
        json_looking_text = '{"note": "这仍然是正文字符串"}'
        self.assertEqual(extract_reply(response_with_text(json_looking_text)), json_looking_text)

    def test_first_choice_and_extra_fields(self):
        response = response_with_text("第一个候选")
        second = copy.deepcopy(response["choices"][0])
        second["message"]["content"] = "第二个候选"
        response["choices"].append(second)
        response["extra"] = "允许额外字段"
        response["choices"][0]["message"]["reasoning_content"] = "额外的模型字段"
        self.assertEqual(extract_reply(response), "第一个候选")

    def test_response_unchanged(self):
        response = response_with_text("  正文  ")
        before = copy.deepcopy(response)
        self.assertEqual(extract_reply(response), "正文")
        self.assertEqual(response, before)

    def test_reasoning_is_not_final_reply(self):
        for reason in ("stop", "length"):
            response = response_with_text(None)
            response["choices"][0]["finish_reason"] = reason
            response["choices"][0]["message"]["reasoning_content"] = "教学占位：只有思考字段，没有回答正文"
            with self.subTest(reason=reason):
                self.assert_invalid_response(response)


class IntegrationChecks(unittest.TestCase):
    def test_json_round_trip(self):
        messages = build_messages(DEFAULT_QUESTION)
        decoded_messages = json.loads(json.dumps(messages, ensure_ascii=False, allow_nan=False))
        self.assertEqual(decoded_messages, messages)
        response = load_offline_response()
        decoded_response = json.loads(json.dumps(response, ensure_ascii=False, allow_nan=False))
        self.assertEqual(extract_reply(decoded_response), extract_reply(response))

    def test_offline_main_does_not_call_api(self):
        output = io.StringIO()
        with patch("exercises.lesson_06.call_model") as api, redirect_stdout(output):
            code = lesson_main([])
        self.assertEqual(code, 0)
        api.assert_not_called()
        self.assertIn("离线样例", output.getvalue())
        self.assertIn(extract_reply(load_offline_response()), output.getvalue())

    def test_live_main_with_mocked_api(self):
        output = io.StringIO()
        response = response_with_text("这是测试替身返回的回答")
        with patch("exercises.lesson_06.call_model", return_value=response) as api, redirect_stdout(output):
            code = lesson_main(["--live", "--question", "为什么校验参数？"])
        self.assertEqual(code, 0)
        api.assert_called_once_with(build_messages("为什么校验参数？"))
        self.assertIn("这是测试替身返回的回答", output.getvalue())

    def test_incomplete_live_reply_is_reported(self):
        response = load_offline_response()
        response["choices"][0]["finish_reason"] = "length"
        output = io.StringIO()
        with patch("exercises.lesson_06.call_model", return_value=response), redirect_stdout(output):
            code = lesson_main(["--live"])
        self.assertEqual(code, 1)
        self.assertIn("运行错误：", output.getvalue())


def main():
    try:
        build_messages(DEFAULT_QUESTION)
        extract_reply(load_offline_response())
    except NotImplementedError as error:
        print(f"练习待完成：{error}")
        return 1
    unittest.main(verbosity=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
