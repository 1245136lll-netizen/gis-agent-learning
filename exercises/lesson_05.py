"""第五课：在项目根目录执行 python -m exercises.lesson_05。"""

import json
from pathlib import Path

from exercises.lesson_04 import SUPPORTED_CATEGORIES, checked_search_nearby


REQUIRED_ARGUMENTS = ("center_lon", "center_lat", "radius_m", "category")

# 已提供：通用工具说明。真正的校验仍由 Python 函数执行。
SEARCH_NEARBY_TOOL = {
    "name": "search_nearby",
    "description": "按类别查询 WGS 84 中心点指定米制半径内的教学地点，按距离排序。",
    "parameters": {
        "type": "object",
        "properties": {
            "center_lon": {
                "type": "number",
                "minimum": -180,
                "maximum": 180,
                "description": "查询中心经度，WGS 84，单位为度",
            },
            "center_lat": {
                "type": "number",
                "minimum": -90,
                "maximum": 90,
                "description": "查询中心纬度，WGS 84，单位为度",
            },
            "radius_m": {
                "type": "number",
                "exclusiveMinimum": 0,
                "maximum": 100000,
                "description": "查询半径，单位为米",
            },
            "category": {
                "type": "string",
                "enum": list(SUPPORTED_CATEGORIES),
                "description": "地点类别",
            },
        },
        "required": list(REQUIRED_ARGUMENTS),
        "additionalProperties": False,
    },
}


def parse_tool_arguments(arguments):
    """待实现：检查参数字典的结构，返回新的四字段字典。

    arguments 必须为 dict，且必须、只能包含 REQUIRED_ARGUMENTS 中的键。
    缺少或多出字段、外层类型错误时抛出有说明的 ValueError。
    不修改输入，不自动转换字段值；本函数不检查字段值的类型与范围。
    字段值的校验交给 run_search_tool 调用的第四课入口。
    """
    # TODO 1：检查 arguments 是字典；不是则抛出 ValueError。
    # TODO 2：检查每个必要字段都存在；再检查没有其他字段。
    # TODO 3：创建新的字典，复制这四个字段并返回，不转换值。

    if not isinstance(arguments,dict):
        raise ValueError(f"arguments必须是字典")
    for key in REQUIRED_ARGUMENTS:
        if key not in arguments:
            raise ValueError(f"必须包含必要字段：{key}")
    for key in arguments:
        if key not in REQUIRED_ARGUMENTS:
            raise ValueError(f"不能包含其他字段：{key}")
    new_dict={}
    for key in REQUIRED_ARGUMENTS:
        new_dict[key]=arguments[key]

    return new_dict

def run_search_tool(features, arguments):
    """待实现：将查询包装为可序列化为 JSON 的成功或失败字典。

    先解析参数结构，再调用 checked_search_nearby。
    成功返回 {"ok": True, "query": 参数新字典, "count": 数量, "results": 结果列表}。
    只捕获上述步骤的 ValueError，返回：
    {"ok": False, "error": {"code": "INVALID_INPUT", "message": 非空错误说明}}。
    不打印、不修改输入、不四舍五入距离；其他异常继续向上传递。
    """
    # TODO 1：在 try 中调用 parse_tool_arguments。
    # TODO 2：使用解析得到的四个参数调用 checked_search_nearby。
    # TODO 3：构造成功字典；results 为空时仍然 ok=True、count=0。
    # TODO 4：except ValueError as error，将 str(error) 放进错误字典。
    try:
        new_dict=parse_tool_arguments(arguments)
        results = checked_search_nearby(features,new_dict["center_lon"],new_dict["center_lat"],new_dict["radius_m"],new_dict["category"])
        return {
                "ok":True,
                "query":new_dict,
                "count":len(results),
                "results":results
                }
    except ValueError as error:
        failed={
            "ok":False,
            "error":{
                "code":"INVALID_INPUT",
                "message":str(error)
            }
        }
        return failed

def main():
    project_dir = Path(__file__).resolve().parents[1]
    path = project_dir / "data" / "places.geojson"
    features = json.loads(path.read_text(encoding="utf-8"))["features"]
    cases = [
        ("合法查询", '{"center_lon":121.47,"center_lat":31.23,"radius_m":1000,"category":"hospital"}'),
        ("合法但无匹配", '{"center_lon":121.47,"center_lat":31.23,"radius_m":100,"category":"hospital"}'),
        ("缺少半径", '{"center_lon":121.47,"center_lat":31.23,"category":"hospital"}'),
        ("多余字段", '{"center_lon":121.47,"center_lat":31.23,"radius_m":1000,"category":"hospital","limit":5}'),
        ("负数半径", '{"center_lon":121.47,"center_lat":31.23,"radius_m":-100,"category":"hospital"}'),
        ("数字字符串", '{"center_lon":121.47,"center_lat":31.23,"radius_m":"1000","category":"hospital"}'),
    ]
    print("数据来源：教学合成数据，不代表真实地点")
    for label, request_text in cases:
        print(f"--- {label} ---")
        # 读取层先把 JSON 文本转换成字典；工具入口接收字典。
        arguments = json.loads(request_text)
        try:
            response = run_search_tool(features, arguments)
        except NotImplementedError as error:
            print(f"练习待完成：{error}")
            print("请先确认第四课通过检查，再完成第五课的两个函数。")
            return 1
        print(json.dumps(response, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
