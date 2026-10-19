# 第三课：查询附近地点，并按距离排序

本课把前两课组合起来：用第一课的 `select_by_category` 筛选类别，用第二课的 `distance_m` 计算距离，返回查询半径内的地点。
你将实现一个 `search_nearby` 函数，供后面的 GIS 工具和 Agent 调用。

## 1. 导入本课新增材料

从聊天下载 `gis-agent-lesson-03.zip`，拖入 Codespaces 项目根目录。在这个目录的终端逐行执行：

```bash
python3 -m zipfile -e gis-agent-lesson-03.zip .
source .venv/bin/activate
python examples/sort_results.py
```

本课沿用已安装的 pyproj，不需要新增第三方依赖。材料包只包含以下 5 个新增文件：

```text
docs/03-nearby-query.md
docs/course-outline.md
examples/sort_results.py
exercises/lesson_03.py
checks/lesson_03.py
```

第一、二课的代码和教学数据沿用你自己的文件。第三课文件一旦开始编辑，就直接继续编辑，不要再次解压覆盖同名文件。

## 2. 先明确输入与输出

函数接口为：

```python
search_nearby(features, center_lon, center_lat, radius_m, category)
```

| 参数 | 含义 | 示例 |
| --- | --- | --- |
| `features` | 由调用方传入的 GeoJSON 要素列表 | `collection["features"]` |
| `center_lon` | 查询中心经度 | `121.4700` |
| `center_lat` | 查询中心纬度 | `31.2300` |
| `radius_m` | 查询半径，单位为米 | `1000` |
| `category` | 查询类别 | `"hospital"` |

本课假设输入结构完整、坐标合法、半径为正数，ID 为字符串；第四课再处理错误数据和参数。

返回一个新的结果列表。每条结果是一个字典，包含以下字段：

```python
{
    "id": "poi-001",
    "name": "教学医院甲",
    "category": "hospital",
    "coordinates": [121.4737, 31.2304],
    "distance_m": 355.29287867499926,
}
```

`distance_m` 这个带引号的键是结果字段名；`distance_m(...)` 是第二课的函数调用。字典中的字符串键与函数名各有用途。
结果列表按距离从近到远排列；距离相同时，按字符串 ID 升序排列。
没有匹配项或输入为空时，返回空列表 `[]`。

## 3. 从其他文件导入自己的函数

第三课文件里已经准备了：

```python
from exercises.lesson_01 import select_by_category
from exercises.lesson_02 import distance_m
```

第一行表示：从 `exercises/lesson_01.py` 导入第一课写好的函数。
第二行同理，导入第二课的距离函数。这样可以在新功能中复用已有代码。

例如，在第三课函数中可以先得到候选要素：

```python
candidates = select_by_category(features, category)
```

导入函数时，前两课的示例 `main()` 不会自动执行，因为你保留了它们文件末尾的 `if __name__ == "__main__":` 判断。

第三课统一在项目根目录按模块运行：

```bash
python -m exercises.lesson_03
```

`-m` 让 Python 从项目根目录寻找对应模块，并支持上述跨文件导入。不要把这个命令改成直接运行文件路径。

## 4. 给每个匹配点创建结果字典

逐个处理候选要素时，先取出位置和属性：

```python
longitude, latitude = feature["geometry"]["coordinates"]
properties = feature["properties"]
```

再调用第二课的函数计算距离。输入顺序仍然是起点经度、起点纬度、终点经度、终点纬度。
将得到的距离保存在变量中，例如 `meters`。

判断规则是：

```python
meters <= radius_m
```

`<=` 表示“小于或等于”，因此位于半径边界上的点也要保留。
使用完整精度比较；`round(...)` 和格式化显示应放在计算、筛选和排序之后。

满足条件时，新建一个结果字典。例如：

```python
record = {
    "id": feature["id"],
    "name": properties["name"],
    "category": properties["category"],
    "coordinates": [longitude, latitude],
    "distance_m": meters,
}
```

然后把 `record` 添加到结果列表。这里新建字典和坐标列表，让查询结果独立组织；原始要素保持原样。
记得区分：`feature` 是原始要素，`record` 是附带距离的查询结果。

## 5. 学会按字段排序

先阅读已运行的 `examples/sort_results.py`。它使用手工设定的距离，专门演示排序；这些距离不来自真实空间计算。

示例中：

```python
ordered = sorted(records, key=distance_and_id)
```

`sorted` 返回一个排好序的新列表，保留原列表顺序。`key` 指定“按什么排序”。
`distance_and_id` 是一个函数，返回每条记录的排序依据：

```python
def distance_and_id(record):
    return (record["distance_m"], record["id"])
```

这个括号里的两个值组成元组。比较时先看第一个值；第一个值相同，再看第二个值。
于是先比距离，再比 ID。

`key=distance_and_id` 传入的是函数本身，`sorted` 会对各条记录调用它。这里不写成 `distance_and_id()`。

在练习文件中，已经给你准备了对应的 `result_sort_key`。收集完结果后，可以用它排序：

```python
ordered = sorted(results, key=result_sort_key)
```

最后返回排序后的列表。`return` 应在整个遍历结束之后执行。

## 6. 你来实现主函数

打开 `exercises/lesson_03.py`，修改 `search_nearby` 函数体，移除占位的 `raise NotImplementedError(...)`。

按这个顺序组织代码：

1. 调用第一课函数，得到指定类别的候选点。
2. 创建空的结果列表。
3. 遍历候选点，取出坐标，调用第二课函数计算距离。
4. 距离小于或等于半径时，创建并添加结果字典。
5. 全部处理完后，排序并返回结果列表。

先用自己的话讲清楚这五步，再动手写。你只需复用已有计算函数，不需要重写前两课的逻辑。

运行：

```bash
python -m exercises.lesson_03
```

默认数据应输出：

```text
数据来源：教学合成数据，不代表真实地点
查询类别：hospital；半径：1000 米
匹配数量：1
poi-001 | 教学医院甲 | 355.3 米
```

分别尝试修改 `main()` 中的 `radius_m` 和 `category`：

| 类别 | 半径 | 预期结果 |
| --- | --- | --- |
| hospital | 1000 米 | 医院甲，355.3 米 |
| hospital | 3000 米 | 医院甲、医院乙，按距离排列 |
| park | 1000 米 | 教学公园，888.6 米 |
| hospital | 100 米 | 空结果 |

练习完可将默认值恢复为 `1000` 和 `"hospital"`。

## 7. 运行检查并保存成果

```bash
python -m checks.lesson_03
```

本课有 8 项检查，覆盖类别与半径、排序、空结果、边界与精度、同距离的 ID 顺序、原数据不变、新输入以及输出字段。
全部通过时末尾显示 `Ran 8 tests` 和 `OK`。初始骨架会提示练习尚待完成，按提示找到对应函数继续实现。

检查通过后，阅读并提交自己的改动：

```bash
git diff
git add docs/03-nearby-query.md docs/course-outline.md examples/sort_results.py exercises/lesson_03.py checks/lesson_03.py
git diff --cached --stat
git commit -m "feat: complete nearby place search lesson"
git push
```

`git diff` 如进入分页界面，按 `q` 退出。这份文件清单包含本课源码与讲义，不包含 ZIP 和虚拟环境。

## 常见问题

| 现象 | 检查方向 |
| --- | --- |
| `No module named exercises` | 是否在项目根目录用 `python -m exercises.lesson_03` 运行 |
| 报第一课或第二课尚未实现 | 是否保存了前两课的答案，且函数名与导入名称一致 |
| 结果里混入公园 | 是否先按传入的 `category` 筛选 |
| 有些本应保留的点被排除 | 是否把经纬度颠倒、比较前四舍五入，或把 `<=` 写成 `<` |
| 只返回第一个匹配点 | `return` 是否放进了循环或条件块内部 |
| 排序后得到 `None` | `list.sort()` 返回 `None`；本课可直接使用返回新列表的 `sorted(...)` |

完成后，你应该能解释五个参数和五个结果字段，并且独立修改类别、半径或查询中心。
下一课将处理错误输入，包括缺少字段、坐标越界和不合法的半径。
