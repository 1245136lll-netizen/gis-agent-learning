# 第四课：校验数据与参数，清楚地处理输入错误

本课接收已经解析好的 GeoJSON `features` 列表，检查其结构和查询参数，再调用第三课查询。
你将实现 `validate_query`、`validate_features` 两个函数，学习 `isinstance`、`raise ValueError`、`try/except` 与字典的 `get`。
本课沿用前三课代码和 pyproj，不增加第三方依赖。

## 1. 获取新增材料并运行独立示例

把聊天中的 `gis-agent-lesson-04.zip` 上传到 Codespaces 项目根目录，逐行执行：

```bash
python3 -m zipfile -e gis-agent-lesson-04.zip .
source .venv/bin/activate
python examples/validation_basics.py
```

压缩包只有 4 个新增文件：

```text
docs/04-validation.md
examples/validation_basics.py
exercises/lesson_04.py
checks/lesson_04.py
```

前三课的答案和原始数据沿用你自己的文件。本课文件开始编辑后，直接继续编辑，避免重复解压覆盖同名文件。
独立示例会让 `1000` 通过，并说明为什么拒绝 `0`、`-10`、字符串 `"1000"` 和布尔值 `True`。

## 2. 区分无匹配结果与输入错误

| 情况 | 行为 |
| --- | --- |
| 合法坐标、半径 100 米，但没有医院 | 正常返回 `[]` |
| 合法查询，数据列表为空 | 正常返回 `[]` |
| 半径为负数、经度为 200 或必要字段缺失 | 抛出有具体说明的 `ValueError` |

如果把错误也返回为 `[]`，调用方就无法分清“没有医院”和“输入有问题”。
校验函数负责报告问题；调用它的界面或程序负责捕获错误并向用户解释。
校验成功时返回 `None`，表示检查完成；不需要返回 `True`。

## 3. 先检查类型，再检查数值

`isinstance` 判断一个值是否属于指定类型：

```python
isinstance(1000, (int, float))    # True：整数或浮点数
isinstance("1000", (int, float))  # False：这是字符串
isinstance({}, dict)             # True：字典
isinstance([], list)             # True：列表
```

Python 中 `bool` 是 `int` 的子类，因此 `isinstance(True, int)` 也是 `True`。
但布尔值不适合作为本项目的坐标和半径，所以数字检查要先排除 `bool`。

本课已提供 `require_number(value, field_name)`，检查有限的 Python 整数、浮点数，并拒绝布尔值、数字字符串和非有限浮点数。
`math.isfinite` 用于判断浮点数是否有限：`float("nan")` 表示非数值，`float("inf")` 表示无穷大，这些值不能进入地理计算。
`field_name` 用于在报错里指出字段，例如 `radius_m`。

## 4. 用 raise 报告错误，用 try/except 处理错误

在半径已经通过数字类型检查之后，可以这样检查范围：

```python
if radius_m <= 0:
    raise ValueError("radius_m 必须大于 0")
```

`raise` 抛出异常，并中止当前函数的正常执行；后面的计算不会继续，异常交给调用方。
本项目统一将不符合输入约定的情况报告为 `ValueError`，并附上可读说明。

调用方可以处理这个错误：

```python
try:
    validate_query(center_lon, center_lat, radius_m, category)
    print("参数校验通过")
except ValueError as error:
    print(f"输入错误：{error}")
```

`try` 中的语句依次执行；发生 `ValueError` 时，转到对应的 `except`。
`as error` 把异常对象交给变量 `error`，可以打印它的说明。
这与第三课占位函数的 `NotImplementedError` 不同：后者表示你还没实现功能，前者表示输入违反约定。

## 5. 查询参数的规则

实现 `validate_query(center_lon, center_lat, radius_m, category)`，遵循：

| 参数 | 规则 |
| --- | --- |
| `center_lon` | 有限数值，-180 到 180，包含边界 |
| `center_lat` | 有限数值，-90 到 90，包含边界 |
| `radius_m` | 有限数值，大于 0 且不超过 100000 米 |
| `category` | 字符串，且为 `"hospital"` 或 `"park"` |

半径上限和开放的查询类别是本项目第一版的应用约定，不是所有 GIS 程序的统一要求。
第三课的通用查询函数仍然保留；第四课新增的入口只开放上述类别，不自动转换数字字符串、大小写或空格。

你已经有两个可复用的辅助函数：

```python
validate_coordinates([center_lon, center_lat], "查询中心")
require_number(radius_m, "radius_m")
```

第一行检查坐标结构、类型与范围；第二行检查半径是否为合适的数字。
调用辅助函数之后，还需要检查半径范围，以及类别的类型和允许值。
允许的类别已经保存在 `SUPPORTED_CATEGORIES` 中，可使用 `in` 或 `not in` 判断成员关系。

## 6. 在读取字段前检查数据结构

第一课中，`feature["category"]` 报错是因为取值层级不对；本课还要处理字段真的缺失的情况。

比较两个取值方式：

```python
feature["properties"]      # 缺少键时抛出 KeyError
feature.get("properties")  # 缺少键时默认返回 None
```

`get` 不会自动搜索内部层级，只是让你有机会检查缺失值并给出更具体的错误。
使用 `get` 前，仍然要确认当前对象是字典。

例如，在已经确认 `feature` 为字典后：

```python
properties = feature.get("properties")
if not isinstance(properties, dict):
    raise ValueError("properties 必须是字典")
```

再检查里面的字段，而不是直接继续读取下一层。
非空字符串检查可以分为两步：确认 `isinstance(value, str)`，再确认 `value.strip()` 不为空。
`strip()` 去掉字符串两端的空白，帮助识别 `"   "` 这样的空白输入；检查时不用修改原数据。

## 7. 实现要素列表校验

实现 `validate_features(features)`，按顺序检查：

1. `features` 必须为列表，允许空列表 `[]`。
2. 每项必须为字典，`type` 必须是 `"Feature"`。
3. `id` 必须是非空字符串。
4. `properties` 必须为字典，其中 `name`、`category` 都是非空字符串。
5. `geometry` 必须为字典，`type` 必须是 `"Point"`。
6. `geometry` 中的 `coordinates` 交给已提供的 `validate_coordinates` 检查。

这个辅助函数要求二维 `[经度, 纬度]` 列表，两个值都必须是合法范围内的有限数字。
本课采用本项目的二维 Point 数据约定，并不是完整的通用 GeoJSON 校验器；额外字段允许存在，不要求你检查 ID 唯一性。
文件读取、JSON 文本语法错误属于读取层，后续再处理。

校验全部要素，任意一项错误就抛出异常；即使那一项的类别不匹配本次查询，也需要报告问题。
校验过程只检查，不删除坏数据、不改坐标、不修改名称。

如果希望错误提示带上要素下标，可以使用：

```python
for index, feature in enumerate(features):
    # index 是从 0 开始的下标，feature 是对应的要素。
    ...
```

例如错误说明可以是 `features[1].geometry.coordinates 经度越界`。

## 8. 通过新入口复用第三课查询

练习文件已经提供以下流程：

```python
def checked_search_nearby(features, center_lon, center_lat, radius_m, category):
    validate_query(center_lon, center_lat, radius_m, category)
    validate_features(features)
    return search_nearby(features, center_lon, center_lat, radius_m, category)
```

只要前两步发现问题并抛出异常，第三步就不会执行。
这个入口不把错误变成空列表；错误一直传给最外层的 `try/except`，由那里显示。

## 9. 练习、检查与保存

在 `exercises/lesson_04.py` 中，先完成 `validate_query`，再完成 `validate_features`。
其他辅助函数和包装入口已经提供。用自己的代码替换两个占位的 `raise NotImplementedError(...)`。

完成后，在项目根目录按点号模块名运行：

```bash
python -m exercises.lesson_04
python -m checks.lesson_04
```

练习会演示 4 个情况：合法查询返回 1 个结果；合法小半径查询返回 0 个结果；负半径和缺少 `properties` 的数据分别显示输入错误。
错误说明可使用你自己的措辞，但应指出具体字段和原因。

本课有 16 项检查，覆盖参数范围、类型、非有限数、缺失字段、坐标结构，以及“错误输入不启动查询”和“原数据保持不变”。
全部通过时末尾显示 `Ran 16 tests` 和 `OK`。初始状态会提示尚未完成的函数。

检查通过后提交本课的 4 个文件：

```bash
git diff
git add docs/04-validation.md examples/validation_basics.py exercises/lesson_04.py checks/lesson_04.py
git diff --cached --stat
git commit -m "feat: complete input validation lesson"
git push
```

`git diff` 进入分页时按 `q` 退出。上面的文件清单不包含 ZIP 和虚拟环境。

完成后，你应能解释：`return []` 与 `raise ValueError` 的区别、检查类型的先后顺序，以及为什么只有校验通过后才能进入空间查询。
第五课会把这个有明确输入和错误行为的查询入口，封装成可供 Agent 调用的 GIS 工具。
