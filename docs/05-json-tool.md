# 第五课：把 GIS 查询封装成有明确 JSON 输入输出的工具

前四课完成了读取、筛选、距离计算和输入校验。本课给这些函数增加一个统一入口：
接收参数字典，调用第四课的查询，返回格式稳定的成功或错误字典。
之后 Agent 就能通过这个入口请求真实的空间计算。

本课只使用 Python 标准库和前几课已有的 pyproj，不增加依赖，不需要模型账号或 API 密钥。
课程中的 GeoJSON 导出安排在第十课；本课的 JSON 返回值先用于程序间传递数据。

## 1. 导入材料并确认第四课已经完成

将聊天中的 `gis-agent-lesson-05.zip` 下载并上传到自己的 Codespaces 项目根目录。
项目路径沿用 `/workspaces/gis-agent-learning`，以自己的 `pwd` 为准。
在终端逐行执行：

```bash
pwd
git branch --show-current
python3 -m zipfile -e gis-agent-lesson-05.zip .
source .venv/bin/activate
python -m checks.lesson_04
python examples/json_basics.py
```

- `pwd` 确认当前是项目根目录。
- 分支应为 `learn/gis-agent-from-zero`。
- `zipfile -e` 将新材料解压到当前目录；末尾的 `.` 表示当前目录。
- `source` 激活你已有的虚拟环境。
- 第四课应显示 `Ran 16 tests` 和 `OK`；未通过时先修好原来的校验函数。
- 最后一条运行独立的 JSON 示例，可以在第五课练习尚未实现时阅读和运行。

压缩包只有 4 个新增文件：

```text
docs/05-json-tool.md
examples/json_basics.py
exercises/lesson_05.py
checks/lesson_05.py
```

它们沿用你现有的第一至第四课代码和原始数据。开始写第五课后，继续编辑同名文件，避免再次解压覆盖自己的实现。

## 2. 这里的工具是什么

本课的“工具”是一个有固定名字、用途、输入规则和返回格式的 Python 功能入口。
后续由模型生成查询参数，Python 执行 GIS 查询，并将结果交回模型组织回答。

```text
JSON 参数文本
    ↓ json.loads
Python 参数字典
    ↓ run_search_tool(features, arguments)
检查字段 → 第四课校验与查询 → 成功或错误字典
    ↓ json.dumps
JSON 结果文本
```

本课先手写参数模拟调用方。`features` 来自本地教学数据，由 Python 读取后传入，
不用调用方提供完整数据列表，也不让它选择任意数据文件。

## 3. JSON 文本与 Python 字典有什么区别

JSON 是一种数据交换格式。JSON 文本可以放进文件，也可以通过 API 传给另一个程序。
Python 字典是 Python 程序运行时使用的数据结构。

```python
import json

text = '{"radius_m": 1000, "category": "hospital"}'
arguments = json.loads(text)
print(arguments["radius_m"])

response_text = json.dumps(arguments, ensure_ascii=False, indent=2)
```

- `text` 是字符串，不能直接用 `text["radius_m"]` 取字段。
- `json.loads(text)` 将 JSON 文本解析为 Python 数据，本例得到字典。
- `json.dumps(arguments)` 将 Python 数据转为 JSON 字符串；它本身不写文件。
- `ensure_ascii=False` 让中文直接显示，`indent=2` 让文本缩进便于阅读。

常见对应关系：

| JSON | Python |
| --- | --- |
| object | `dict` |
| array | `list` |
| string | `str` |
| number | `int` 或 `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

JSON 中的字段名与字符串要用双引号，不支持注释和末尾多余逗号。
JSON 文本最外层也可能是数组或数字，所以 `json.loads` 成功不等于参数结构正确。
例如解析 `[]` 得到列表，而我们的工具要求字典。

无法解析的 JSON 文本会抛出 `json.JSONDecodeError`，由读取文本的那一层处理。
本课两个待实现函数接收已经解析好的 Python 数据，不承担 JSON 文本解析工作。

## 4. 输入规则：四个字段必须齐全

合法参数示例：

```json
{
  "center_lon": 121.47,
  "center_lat": 31.23,
  "radius_m": 1000,
  "category": "hospital"
}
```

| 字段 | 规则 |
| --- | --- |
| `center_lon` | 有限数值，-180 到 180，单位为度 |
| `center_lat` | 有限数值，-90 到 90，单位为度 |
| `radius_m` | 有限数值，`0 < radius_m <= 100000`，单位为米 |
| `category` | 字符串，`hospital` 或 `park` |

四个字段缺一不可，也不接受额外字段。例如误写 `radius` 或增加 `limit`，应报告输入错误。
这样能及时发现调用方的拼写或参数约定错误。
类型和数值规则继续沿用第四课：不把 `"1000"` 自动转为数字，也不把 `True` 当半径。

## 5. 输出规则：成功、空结果和错误

成功时返回 Python 字典，序列化后的结构如下：

```json
{
  "ok": true,
  "query": {
    "center_lon": 121.47,
    "center_lat": 31.23,
    "radius_m": 1000,
    "category": "hospital"
  },
  "count": 1,
  "results": [
    {
      "id": "poi-001",
      "name": "教学医院甲",
      "category": "hospital",
      "coordinates": [121.4737, 31.2304],
      "distance_m": 355.29287867499926
    }
  ]
}
```

`query` 保存本次查询条件；`count` 是结果条数，应等于 `len(results)`。
保留第三课结果中的字段、距离精度和排序；要显示一位小数时再格式化。

合法查询没有匹配地点时，仍然是 `ok: true`，但 `count: 0`、`results: []`，并保留 `query`。

输入错误时返回：

```json
{
  "ok": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "查询半径必须大于 0，且不超过 100000 米"
  }
}
```

错误说明使用你自己的措辞也可以，但必须为非空字符串。
失败字典只有 `ok`、`error`；不能把失败伪装成一个空的成功结果。

## 6. 第一个练习：解析参数结构

打开 `exercises/lesson_05.py`，实现 `parse_tool_arguments(arguments)`：

1. 确认最外层是字典，否则抛出 `ValueError`。
2. 遍历 `REQUIRED_ARGUMENTS`，检查每个必要字段都存在。
3. 遍历输入字典的键，检查没有其他字段。
4. 创建一个新的字典，复制这四个字段并返回。

这里先使用循环写清楚，不要求使用字典推导式。
对字典写 `for key in arguments`，得到的是键，不是值。

```python
settings = {"mode": "demo"}
"mode" in settings       # True：检查键是否存在
"limit" not in settings  # True：该键不存在
```

本函数只检查字段的存在和名称；字段值的类型、范围由后面的第四课入口检查。
不要在这里转换数字、修改输入或提前进行距离计算。
使用 `return arguments` 会返回同一个对象，不符合“返回新字典”的要求。

## 7. 第二个练习：调用查询并包装结果

实现 `run_search_tool(features, arguments)`：

1. 在 `try` 内调用 `parse_tool_arguments`，得到参数新字典。
2. 依次取出四个参数，调用已经导入的 `checked_search_nearby`。
3. 根据查询列表构造并返回成功字典。
4. 用 `except ValueError as error` 捕获参数结构、参数值或要素数据的校验错误，返回错误字典。

第四课函数的调用形式仍然是：

```python
checked_search_nearby(features, center_lon, center_lat, radius_m, category)
```

这里的四个参数应该从解析后的字典中读取，不要写死为演示值。
`str(error)` 将异常的说明转成字符串；不要把异常对象本身放进返回字典，JSON 无法直接表示它。

### 为什么这里可以捕获错误并返回？

第四课的校验函数需要用 `raise ValueError` 中止无效查询；第五课仍然保持这个行为。
新的工具入口处在调用方与内部函数之间，负责将预期的输入错误转换成稳定的返回格式。
调用方看到 `ok: false` 就知道发生错误，而不是继续把它当成成功查询。

只捕获 `ValueError`。拼写错误导致的 `AttributeError`、错误调用导致的 `TypeError`，
以及尚未完成练习的 `NotImplementedError` 应继续向上传递，让开发者看见并修复。
两个待实现函数都不调用 `print`；最外层 `main()` 负责显示结果。

## 8. 认识已提供的工具说明

`SEARCH_NEARBY_TOOL` 已提供名字、用途和参数说明，不需要你从零填写。
其中 `parameters` 使用 JSON Schema 的常见字段描述输入形状：

| 字段 | 含义 |
| --- | --- |
| `type: "object"` | 最外层应是对象，对应 Python 字典 |
| `properties` | 各个参数的名称、类型和说明 |
| `minimum` / `maximum` | 包含边界的最小值与最大值 |
| `exclusiveMinimum: 0` | 必须大于 0，不包含 0 |
| `enum` | 允许使用的取值 |
| `required` | 必须提供的字段名列表 |
| `additionalProperties: false` | 不接受额外字段 |

这份说明给调用方看，不会自动执行 Python 校验。
真正执行时仍需你的参数解析函数和第四课校验函数。
不同模型服务对工具定义的外层格式有不同要求，接 API 时再按官方接口适配。

## 9. 运行与检查

保留练习中的工具说明、导入和 `main()`，只实现两个待完成函数。
完成后在项目根目录运行：

```bash
python -m exercises.lesson_05
python -m checks.lesson_05
```

第一条会显示 6 次模拟工具调用：

| 情况 | 预期结果 |
| --- | --- |
| 1000 米内查询医院 | `ok: true`，`count: 1` |
| 100 米内查询医院 | `ok: true`，`count: 0` |
| 缺少半径 | `ok: false`，错误代码 `INVALID_INPUT` |
| 多余字段 `limit` | 同上 |
| 负数半径 | 同上 |
| 半径为字符串 `"1000"` | 同上 |

`main()` 已使用 `json.dumps(..., ensure_ascii=False, indent=2, allow_nan=False)` 显示结果。
`allow_nan=False` 会拒绝将非有限浮点数编码为非标准 JSON 值；有限性仍需第四课函数主动检查。

第二条执行 18 项检查，覆盖字段缺失和多出、正常与空查询、无效值、错误数据、原输入不被修改、
距离精度、JSON 往返转换，以及“输入错误不计算”和“程序错误继续抛出”。
初始占位代码会提示待完成；全部实现后应显示 `Ran 18 tests` 和 `OK`。
使用点号模块名 `checks.lesson_05`，不要写 `checks/lesson_05`。

## 10. 保存与完成标准

通过检查后，按顺序执行：

```bash
git diff
git add docs/05-json-tool.md examples/json_basics.py exercises/lesson_05.py checks/lesson_05.py
git diff --cached --stat
git commit -m "feat: wrap GIS query as a JSON tool"
git push
```

`git diff` 如果进入分页界面，按 `q` 返回终端。提交清单不包含 ZIP 和虚拟环境。

用自己的话回答以下问题，再进入第六课：

- JSON 文本和 Python 字典各是什么？`loads`、`dumps` 分别做什么？答：JSON文本是一种表示数据的格式，能够进行交换和和保存数据；而python字典是python语言的一种数据结构，由键值对来存储和表示。‘loads’是将JSON转换为python中的数据格式，dumps是将python数据转换为JSON文本格式。
- 为什么缺少 `radius_m` 与没有匹配医院是两种不同情况？答：缺少radiu_m属于数据缺失，是一种参数错误格式，其本身在该例子中不合法；而没有匹配医院是指检索中没有对应的对象与之匹配，其本身语法和参数均符合正常规范。
- 为什么工具说明里写了范围，Python 仍然要检查？答：我个人认为工具虽然提供了范围，但是没有进行相应的错误处理，python检查要保证错误输入不会直接进行系统。
- 为什么第四课抛出错误，而第五课工具入口将输入错误转换成字典？答：这个我没理解
- 为什么调用方只提供四个查询参数，而数据由项目自己加载？答：提供的四个查询参数是本项目的核心参数，这四个参数能够决定数据是否符合标准与需求。数据本身并不固定，且数值都不一样，因此交由项目自身加载，既减轻了调用方的工作量也保证最重要的查询参数起作用。

第六课会学习大模型 API、消息和返回结果；第七课再把本课工具接入 Agent 工具调用循环。
