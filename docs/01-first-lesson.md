# 第一课：从终端到 GeoJSON

本课目标：知道代码在哪里运行，读懂一份地理数据，用 Python 自己实现一个筛选函数。
不用安装 GIS 软件，不用大模型账号。遇到不懂的地方可以停下来逐项确认。

## 1. 认识终端和目录

终端是通过文字命令操作计算机的窗口。先按 [第 0 步](00-github-codespaces.md) 打开 GitHub Codespaces 并导入源码；以下命令输入那个浏览器编辑器里的终端。
GitHub 的普通仓库网页和 `github.dev` 编辑器不提供用于运行本课 Python 的集成终端。
以下 `bash` 代码块里的每一行都是一条命令，逐行输入后按回车。不要输入代码块外的说明文字。

```bash
pwd
ls
```

- `cd 路径`：切换到指定目录。
- `pwd`：显示当前目录。在 Codespaces 通常为 `/workspaces/gis-agent-learning`，以你的实际仓库目录为准。
- `ls`：列出当前目录里的文件，应能看到 `README.md`、`data`、`docs` 等。
- 以 `/` 开头的是绝对路径；例如 `data/places.geojson` 是相对于当前目录的路径。

## 2. 理解 Git 和分支

Git 记录文件内容的变化；仓库是保存代码和历史记录的目录；提交是一份可以追溯的版本记录。
分支是指向一系列提交的名字，方便在同一起点上推进不同工作。
GitHub 是托管 Git 仓库的网站，和云端的本地 Git 仓库是两个位置。

完成第 0 步后，你自己的 GitHub 仓库已有默认分支和 `learn/gis-agent-from-zero` 学习分支。

```bash
git branch --show-current
git status
git log --oneline -3
```

第一条应显示 `learn/gis-agent-from-zero`。`git status` 查看当前分支和未提交修改；`git log` 查看提交历史。
分支区分版本历史，不是另一台云主机。当前练习只在本项目目录中进行。

## 3. 认识 Python 和虚拟环境

Python 是编程语言；Python 解释器执行 `.py` 文件里的代码。
虚拟环境是项目专用的 Python 运行与依赖环境，避免不同项目的第三方包互相影响。

在项目根目录创建 `.venv` 并激活它。如果第 0 步已经创建，可以直接从激活命令继续：

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
python -c "print('你好，GIS')"
```

`source` 让当前终端使用这个环境；`python --version` 显示 Python 版本；`-c` 执行引号内的一小段 Python。
最后一条应输出 `你好，GIS`。新开终端后需要重新进入目录并激活。

如果将来换了环境、项目里没有 `.venv`，在项目目录先执行 `python3 -m venv .venv`。
`venv` 是 Python 自带的虚拟环境工具。输入 `deactivate` 可以退出激活状态。

## 4. 运行第一个项目示例

```bash
python examples/inspect_geojson.py
```

应看到：

```text
数据来源：教学合成数据，不代表真实地点
数据类型：FeatureCollection
要素数量：3
- 教学医院甲 | hospital | 经度=121.4737, 纬度=31.2304
- 教学公园 | park | 经度=121.4785, 纬度=31.2333
- 教学医院乙 | hospital | 经度=121.49, 纬度=31.24
```

现在打开项目文件 `examples/inspect_geojson.py`，将代码与输出对照阅读。
这里的“打开文件”指在编辑器里查看项目文件；不需要把整段 Python 粘贴到 Bash。

代码执行了五件事：找到数据路径；读取文本；把 JSON 解析成 Python 对象；取得要素列表；逐个打印。

| 写法 | 意思 |
| --- | --- |
| `import json` | 使用 Python 自带的 JSON 工具 |
| `Path(...)` | 用对象表示文件路径 |
| `read_text(encoding="utf-8")` | 读取文本，并指定支持中文的编码 |
| `json.loads(text)` | 把 JSON 文本解析为字典、列表等对象 |
| `collection["features"]` | 从字典取出 `features` 对应的值 |
| `len(features)` | 获取列表中元素的数量 |
| `for feature in features:` | 逐个处理列表里的要素 |
| `print(...)` | 将内容显示到终端 |
| `f"数量：{len(features)}"` | 把表达式的值嵌入文字 |

`def main():` 把操作组织成函数。末尾的 `if __name__ == "__main__":` 表示“直接运行这个文件时调用 main”；先理解用途，后面再深入模块机制。

## 5. 理解 GeoJSON

JSON 是一种文本数据格式。Python 解析后，`{}` 一般成为字典，`[]` 成为列表。
GeoJSON 在这个格式上约定了如何表示地理数据。

打开 `data/places.geojson`，先找这些层次：

```text
FeatureCollection（要素集合）
└── features（要素列表，共 3 个）
    └── Feature（单个要素）
        ├── id：稳定的标识
        ├── properties：名称、类别等普通属性
        └── geometry：形状和坐标
```

本例的几何类型是 `Point`，即点。`coordinates` 是 `[经度, 纬度]`，不要颠倒。
坐标的单位是**度**，不是米。“读取坐标”还不等于“能正确计算距离”，下一阶段会专门学习。

先试着不运行代码，从文件内容找出：医院有几个？公园有几个？第一个点的经度是多少？

## 6. 完成练习前需要的 Python 语法

以下是阅读用的 Python 小例子。需要尝试时，可在编辑器中新建 `.py` 文件保存，再用 `python 文件路径` 运行。

**变量与列表**：`=` 把右侧的值赋给左侧的名字；列表按顺序保存多个值。

```python
numbers = [2, 5, 8]
selected = []
selected.append(5)
print(selected)  # 输出 [5]；append 是向列表末尾添加一个元素
```

**字典**：通过键找到值。

```python
place = {"name": "教学点", "category": "park"}
print(place["category"])  # 输出 park
```

**循环与条件**：`for` 遍历列表，`if` 只在条件成立时执行缩进内的代码。

```python
for number in numbers:
    if number > 4:
        print(number)
```

这段代码接着第一段的 `numbers` 使用，依次输出 5 和 8。Python 用缩进表示代码归属，建议每层使用 4 个空格。冒号和缩进不能省略。
`==` 表示“是否相等”，例如 `place["category"] == "park"`；它与赋值用的 `=` 不同。

**函数与返回值**：函数将一项工作起个名字，可接收参数，并通过 `return` 返回结果。

```python
def double(number):
    return number * 2

answer = double(3)
print(answer)  # 输出 6
```

`print` 是给人看输出；`return` 是将结果交给调用函数的代码。这次练习需要返回列表，不能只把名称打印出来。

## 7. 亲手实现筛选函数

打开 `exercises/lesson_01.py`，只修改 `select_by_category(features, category)` 的函数体。
删掉占位的 `raise NotImplementedError(...)`，写入你的实现，保存文件。
`NotImplementedError` 表示这项功能还未实现；初始文件故意保留这个占位。

函数约定：

- 输入 `features`：要素列表，每项都有 `feature["properties"]["category"]`。
- 输入 `category`：想查询的类别，比如 `"hospital"`。
- 返回值：一个新的列表，只包含类别完全相同的要素，顺序与原列表一致。
- 空输入或无匹配时：返回空列表 `[]`。
- 不删除或改动原来的要素；不用重新读文件；不要把查询类别写死。

思考顺序：先准备一个空的结果列表；逐个检查要素；匹配时添加完整要素；全部检查后返回列表。
如果只得到第一个匹配项，检查 `return` 是否写在了循环里面。

运行自己的练习：

```bash
python exercises/lesson_01.py
```

实现正确时应输出：

```text
医院数量：2
教学医院甲
教学医院乙
```

再运行自动检查：

```bash
python -m checks.lesson_01
```

`-m` 表示按模块名字运行 Python 程序，点号对应目录层级；请在项目根目录执行。
检查会验证医院、公园、无匹配、空输入、原数据不变、传入新数据这 6 种行为。全部通过时末尾会显示 `Ran 6 tests` 和 `OK`。
尚未实现时会提示“练习尚未实现”，这是待完成状态，不是环境坏了。

## 8. 记录并保存自己的第一份成果

在 `docs/progress.md` 写下你运行的命令、检查结果和仍不理解的地方。
如果只是照着提示写出来，也如实记录；下一步要尝试离开提示重新写一遍。

查看自己的改动：

```bash
git diff
git status
```

检查通过后，再提交。Git 提交需要作者名和邮箱。如果还没设置，可先用以下本地学习身份；它不会发邮件，只会写入提交记录。正式发布前可改为自己的名字与 GitHub 提交邮箱。

```bash
git config user.name "GIS Learner"
git config user.email "learner@example.invalid"
git add exercises/lesson_01.py docs/progress.md
git commit -m "feat: complete category filtering exercise"
```

`git config` 这里仅影响本仓库。`git add` 选择要记录的文件，`git commit` 保存一次版本。
本地提交不会自动上传到 GitHub。

## 常见问题

| 现象 | 先检查什么 |
| --- | --- |
| 找不到文件或 `.venv/bin/activate` | 是否已导入课程源码、`pwd` 是否为自己的项目目录、新环境是否已创建 `.venv` |
| Bash 报 Python 语法错误 | 是否把 Python 代码直接输入了终端；应保存为 `.py` 再运行 |
| `IndentationError` | 缩进是否统一；函数、循环和条件内的代码是否正确缩进 |
| 返回 `None` 或数量报错 | 是否遗漏 `return`；是否把 `print` 当成返回值 |
| 只筛出一个医院 | 是否在循环中提前 `return` |
| `No module named checks` | 是否在项目根目录运行了 `python -m checks.lesson_01` |

完成后，把运行结果和不懂的地方交给导师一起检查。下一课从“如何把经纬度变成正确的米制距离”开始。
