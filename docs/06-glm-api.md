# 第六课：第五课答疑，以及用 GLM-5.3-Flash API 发送消息、读取回答

本课按你确认的“智谱开放平台 BigModel，GLM-5.3-Flash”准备。
目标：看懂一次模型请求的过程，亲手组织消息、提取回答，再用自己的智谱标准模型 API 完成一次真实调用。
Agent 的 GIS 工具调用循环安排在第七课。

本版的配置入口为 `GLM_API_KEY`、`GLM_BASE_URL`、`GLM_MODEL`，默认模型 ID 为 `glm-5.3-flash`。
第 5 节提供保留现有练习函数的升级方法；第五课答疑仍在下面第 1 节。

## 1. 先逐条解释你第五课的回答

本节依据你在学习分支 [第五课讲义末尾](https://github.com/1245136lll-netizen/gis-agent-learning/blob/learn/gis-agent-from-zero/docs/05-json-tool.md) 填写的五条回答。
我也读取了你推送的第一至第五课代码，并在备课环境运行第五课检查，18 项全部通过。
下面重点补齐“代码已经能运行，但为什么这样设计还不清楚”的部分。

### 1.1 JSON 文本、Python 字典、loads 和 dumps

你回答的主要方向正确：JSON 用于表示和交换数据，字典是 Python 的数据结构。
再精确区分两个词：JSON 是格式，JSON 文本是按这个格式写出的文字。

```python
text = '{"radius_m": 1000}'   # str：一段 JSON 文本
data = {"radius_m": 1000}     # dict：一个 Python 字典
```

看起来相似，但前者不能直接使用 `text["radius_m"]` 取值。

- `json.loads(text)`：解析 JSON 文本，得到 Python 数据。
- `json.dumps(data)`：将 Python 数据编码成 JSON 文本。

`loads` 的结果也可能是列表、数字、布尔值或 `None`，取决于原始 JSON；并非总是字典。
`dumps` 只返回字符串，不会自动保存文件，也不会自动发送网络请求。
本课的 SDK 会负责网络传输以及传输时的 JSON 编解码。

### 1.2 缺少 radius_m 与没有匹配医院

这道题你理解正确。可以进一步从“是否执行了一个合法查询”来判断：

| 情况 | 发生了什么 | 工具返回 |
| --- | --- | --- |
| 缺少 `radius_m` | 查询条件不完整，无法按约定执行 | `ok=False`，说明缺少字段 |
| 半径为 100 米，没有医院 | 查询条件、数据均合法，计算后没有匹配 | `ok=True`、`count=0`、`results=[]` |

注意，`if results:` 检查的是列表是否非空。它不能用来判断查询有没有出错。
正常查询既可能得到非空列表，也可能得到空列表；输入错误由校验与异常报告。

### 1.3 工具说明已有范围，为什么 Python 仍需校验

你写的是“工具虽然提供了范围，但是没有进行相应的错误处理”。这里需要补充：
**工具说明是在描述规则；Python 校验函数负责执行这些规则。**

例如，写出一个字典：

```python
rules = {"minimum": 0}
radius_m = -100
```

上面两行本身不会产生异常。Python 没有因为看到 `minimum` 就自动检查 `radius_m`。
必须有代码读取规则并执行判断，或者调用校验库，规则才会生效。
第五课中实际执行检查的就是你写的参数解析函数和第四课校验函数。

模型服务或框架可能对部分 Schema 做检查；你的程序仍需负责项目自己的数值范围、允许类别和实际数据质量。
因此，关键不只是“出现错误后如何处理”，还包括“真正检查输入，发现问题后阻止计算”。

### 1.4 第四课抛出异常，第五课为什么转换成字典

你回答“这个我没理解”。我们沿着一次负半径请求，把执行顺序走一遍。

```text
run_search_tool 收到 radius_m=-100
    ↓
parse_tool_arguments：四个字段齐全，结构检查通过
    ↓
checked_search_nearby 调用 validate_query
    ↓
validate_query 发现半径为负，raise ValueError(...)
    ↓
checked_search_nearby 的后续数据检查、距离计算都不再执行
    ↓
异常沿调用关系返回，进入 run_search_tool 的 except ValueError
    ↓
工具入口返回 {"ok": False, "error": {...}}
    ↓
最外层将这个字典显示出来，或编码成 JSON 交给调用方
```

这里有两个职责：

- 内部校验函数负责发现问题，并用异常中止无效计算。
- 工具入口负责把这个预期的输入错误转换成调用方约定的返回格式。

看一个缩小后的独立例子：

```python
def validate_radius(radius_m):
    if radius_m <= 0:
        raise ValueError("半径必须大于 0")

def radius_tool(radius_m):
    try:
        validate_radius(radius_m)
        return {"ok": True}
    except ValueError as error:
        return {"ok": False, "message": str(error)}

print(radius_tool(-100))
```

输出 `{'ok': False, 'message': '半径必须大于 0'}`。
异常已经阻止了无效操作；入口再把问题变成了调用方能读取的数据。
`str(error)` 取出异常说明。异常对象本身不能直接作为普通 JSON 数据发送。

这与“校验函数捕获异常后只打印，然后继续查询”不同：本例明确返回失败，调用方能够识别并停止正常结果处理。
只捕获约定的输入错误 `ValueError`；`NameError`、`TypeError` 等程序错误应暴露出来，供开发者修复。
之后接模型服务时，你也会遇到类似的职责划分：SDK 报告请求失败，最外层决定怎样向用户说明。

### 1.5 为什么调用方只提供查询参数，数据由项目加载

你提到“减轻调用方工作量”，这是一个实际好处。
需要修正的是：“四个参数能够决定数据是否符合标准”把两种校验混在了一起。

| 对象 | 代表什么 | 对应检查 |
| --- | --- | --- |
| 经度、纬度、半径、类别 | 本次想查哪里、查多远、查什么 | `validate_query` |
| `features` 中的地点、坐标、属性 | 可供查询的事实数据 | `validate_features` |

四个参数描述查询需求，不能单独证明地点数据正确。
半径为 1000 米很合法，但地点缺少 `properties`，数据仍然不合法。

数据也可以长期固定。例如，你现在的三个教学点保持不变，第一次查医院、第二次查公园，只需改变查询条件。
因此，“数据不固定、数值不一样”并不是由项目加载数据的根本原因。

由项目加载数据，可以统一决定数据来源、版本、坐标约定和可访问范围；调用方专注于表达查询需求。
后续 Agent 请求查询，仍应由你的 GIS 函数使用已知数据计算距离和数量，再把计算结果交给模型解释。

## 2. 第六课的 API、SDK 和模型分别是什么

- 模型：生成回答的程序，本课使用 GLM-5.3-Flash。
- API：让你的 Python 程序通过网络请求模型服务的接口。
- SDK：帮助 Python 组织请求、发送请求和读取响应的客户端库。
- API Key：服务用来识别调用身份和权限的凭据。
- Base URL：请求发往哪个服务地址。
- Model ID：在这个服务上选择哪个模型。

你已选择智谱开放平台，可以在自己的 Codespaces 中配置调用。
本课使用 BigModel 的标准模型 API：`https://open.bigmodel.cn/api/paas/v4`。
标准模型 API 与 Coding Plan 专用入口有不同用途；本课按标准模型 API 配置和计费。

智谱支持 OpenAI 兼容的 Chat Completions 接口，所以这里使用 `openai` Python SDK。
实际请求发往 BigModel，使用智谱 API Key 与 GLM 模型；无需 OpenAI 账号。
模型名与思考模式已对照 [智谱模型说明](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash) 核对，
请求结构见 [官方 Chat Completion API](https://docs.bigmodel.cn/api-reference/模型-api/对话补全)。

## 3. 消息是一个“字典组成的列表”

```python
messages = [
    {"role": "system", "content": "你是 GIS 学习助手，请用中文解释概念。"},
    {"role": "user", "content": "为什么查询半径用米表示？"},
]
```

| 字段或值 | 含义 |
| --- | --- |
| `messages` | 按对话顺序排列的消息列表 |
| `role` | 这条消息的角色 |
| `system` | 应用设定的任务、回答方式与约束 |
| `user` | 用户本次的问题 |
| `assistant` | 模型给出的回复，后续也可作为历史消息传回 |
| `content` | 本课中为消息正文字符串 |

`"system"`、`"user"` 是角色名称的字符串值，类型都是 `str`。
判断角色要比较值，例如 `role == "assistant"`。

取值时，列表先用数字下标，字典再用字段名：

```python
messages[0]             # 第一条消息，是字典
messages[0]["role"]     # "system"
messages[1]["content"]  # 用户问题
```

本课只发送一轮问题。Chat Completions 的多轮上下文需要由应用把相关历史消息一起传入；本课暂不实现历史管理。
系统消息可以指导模型，但提示词不能替代 GIS 实际计算和程序校验。

## 4. 模型响应：外层是数据结构，正文仍然是字符串

一次普通文本响应的简化结构如下：

```json
{
  "id": "chatcmpl-example",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "半径用米表示，便于表达实际地面距离。"
      }
    }
  ]
}
```

响应经解析后，最外层是 Python 字典，`choices` 是列表，`message` 是字典，`content` 是字符串。
本课只取第一个候选；确认各层结构合法后，读取路径是：

```python
response_data["choices"][0]["message"]["content"]
```

不要把整个响应字典当成模型回答，也不要把正文自动当成 JSON 再解析。
例如正文是 `"半径用米表示……"`，这就是普通文本。
即使正文看起来像 `'{"count": 1}'`，它此时仍是字符串；只有应用明确需要结构化正文时，才另外解析、校验它。

GLM 的响应还可能包含 `message.reasoning_content`。本课提取最终回答时只读取 `message.content`，
不能在正文为空时改用思考字段冒充回答。离线样例中的该字段是人工编写的占位文字。

`finish_reason` 告诉你回答为什么结束：

| 值 | 本课如何处理 |
| --- | --- |
| `stop` | 检查消息角色与非空正文，然后接受文本回答 |
| `length` | 生成被长度限制截断，报告未得到完整回答 |
| `tool_calls` | 模型请求执行工具，第七课再处理这个分支 |
| 缺失或其他值 | 报告不符合本课文本回答约定 |

`stop` 表示本轮生成按接口规则结束，不表示回答中的所有事实已经被 GIS 工具验证。
本课用模型解释概念；具体地点和距离仍应来自工具计算。

## 5. 获取本课材料，先运行独立示例

将聊天中的 `gis-agent-lesson-06-glm.zip` 上传到自己 Codespaces 的项目根目录。
逐行执行：

```bash
cd /workspaces/gis-agent-learning
python3 -m zipfile -e gis-agent-lesson-06-glm.zip .
python3 scripts/upgrade_lesson_06_glm.py
source .venv/bin/activate
python -m checks.lesson_05
python examples/messages_basics.py
```

解压会放入升级脚本和 `.lesson06-glm-update/` 材料目录；运行脚本后安装以下六个课程文件：

```text
docs/06-glm-api.md
examples/messages_basics.py
exercises/lesson_06.py
checks/lesson_06.py
data/lesson_06_response.json
requirements-lesson-06.txt
```

如果已有 `exercises/lesson_06.py`，脚本会保留你的 `build_messages`、`extract_reply`、`SYSTEM_PROMPT` 和 `DEFAULT_QUESTION`，
更新课程提供的客户端与显示代码。原文件保存在 `.lesson06-glm-backups/` 下，路径会打印出来。
现有代码存在语法错误时，脚本会停止，先修复语法再升级，不会用空白练习覆盖它。
重复运行不会重置已写的函数。除上述四部分外，自行改写的辅助代码可从完整备份核对、迁移。
脚本会在旧讲义顶部添加新版入口，保留其余原文与学习笔记；当前配置和学习入口以本篇 `docs/06-glm-api.md` 为准。

独立示例会打印消息列表和一个预先编写的响应，帮助你观察类型与层级，不需要安装 SDK 或配置 Key。
样例文件中的模型名、响应 ID 和用量数字是教学占位内容，不能作为真实调用记录。

## 6. 练习一：build_messages

在 `exercises/lesson_06.py` 中实现 `build_messages(user_text)`：

1. 检查用户问题为字符串，且 `strip()` 后不为空；不符合则抛出有说明的 `ValueError`。
2. 创建系统消息，使用文件已提供的 `SYSTEM_PROMPT`。
3. 创建用户消息，使用去掉首尾空白的用户问题。
4. 按系统消息、用户消息的顺序放进一个新列表并返回。

每次调用都创建新的列表与字典。返回的是 Python 列表，不是 JSON 字符串。
这里复习第五课的字典与列表组合，不需要写任何网络代码。

## 7. 练习二：extract_reply

实现 `extract_reply(response_data)`，按从外到内的顺序检查：

1. 最外层为字典。
2. `choices` 为非空列表。
3. 第一个候选为字典，`finish_reason == "stop"`。
4. 候选中的 `message` 为字典，`role == "assistant"`。
5. `content` 为非空白字符串。
6. 返回 `content.strip()`，只去掉首尾空白，不修改传入的响应。

允许额外字段。发现任何不符合约定的内容，都抛出有说明的 `ValueError`。
`choices=[]` 表示没有可读取的候选，本课应报告错误；它与第五课“合法查询没有医院”的 `results=[]` 含义不同。
同样是空列表，具体含义取决于字段的约定。

使用 `.get()` 前先检查当前对象是字典；读取 `[0]` 前先确认列表非空。
这正是第四课“先检查结构，再读取下一层”的复习。

## 8. 完成离线练习与检查

```bash
python -m exercises.lesson_06
python -m checks.lesson_06
```

第一条默认读取离线样例，并明确打印“没有调用模型”。更改问题不会改变固定样例的回答。
第二条有 19 项检查，覆盖消息结构、空输入、新对象、响应层级、结束原因、文本内容、JSON 往返，以及离线模式不调用 API。
新增检查确认：响应只有 `reasoning_content`、缺少最终正文时，不能把它当成有效回答。
检查中模拟真实入口的部分使用测试替身，也不会发送真实请求。

初始占位代码会提示待实现；完成后应显示 `Ran 19 tests` 和 `OK`。
两个函数都通过后，再配置真实调用。`-m` 后使用点号模块名，不写 `.py`。

## 9. 配置智谱开放平台标准模型 API

先安装本课 SDK：

```bash
python -m pip install -r requirements-lesson-06.txt
```

本课备课测试的 SDK 版本为 `openai==3.35.1`，要求 Python 3.10 或更新版本；课程使用的 Python 3.12 满足要求。
`python -m pip` 使用当前虚拟环境的 Python 安装依赖。

### 9.1 保存 API Key

在 GitHub 仓库的 Settings → Secrets and variables → Codespaces 中添加仓库机密：

- 名称：`GLM_API_KEY`
- 值：你在智谱 BigModel 控制台创建的、具有标准模型 API 权限的 API Key

让该机密对学习仓库可用，停止并重新启动当前 Codespace 后打开终端、重新激活虚拟环境。
机密由 Codespaces 作为环境变量提供，不需要写入 Python 源码或课程文档。
Key 不要发到聊天中，也不要提交进 Git。
界面步骤与生效方式见 [GitHub 官方说明](https://docs.github.com/zh/codespaces/managing-codespaces-for-your-organization/managing-development-environment-secrets-for-your-repository-or-organization)。

只检查是否存在，不打印实际值：

```bash
python -c "import os; print('API Key 已配置：', bool(os.getenv('GLM_API_KEY')))"
```

显示 `True` 只说明变量有值，不代表 Key 的模型权限和额度已经通过验证。
凭据在 [智谱控制台](https://bigmodel.cn/) 管理。新连接函数只读取 `GLM_` 配置，不会把旧平台的凭据发给智谱。

### 9.2 配置 Base URL 和模型

本课标准模型 API 的 Base URL 为：

```text
https://open.bigmodel.cn/api/paas/v4
```

代码已提供默认值。也可以在终端明确设置：

```bash
export GLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
export GLM_MODEL="glm-5.3-flash"
```

`export` 让当前终端启动的 Python 程序能够读取这个变量；只在这个终端设置的值，需要在新终端重新设置，或放进 Codespaces 配置。
本课代码通过 `os.getenv()` 读取这些设置。
Base URL 填到 `/api/paas/v4` 为止，SDK 会继续拼接 `/chat/completions`。
不要把完整请求路径再填入 Base URL，也不要填原来百炼的地址。

模型 ID 是 `glm-5.3-flash`，大小写、连字符按这个值填写，并以自己账号的可用模型与权限为准。
本版连接函数名为 `call_model`，避免模型切换后函数名仍指向旧模型。

## 10. 阅读已提供的真实请求函数

`call_model(messages)` 已提供。它的核心流程是：

```python
with OpenAI(api_key=api_key, base_url=base_url, timeout=60.0, max_retries=0) as client:
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False,
        max_tokens=4096,
        reasoning_effort="low",
        extra_body={"thinking": {"type": "enabled"}},
    )

response_data = completion.model_dump(mode="json")
```

- `OpenAI(...)` 创建兼容接口客户端，地址和凭据来自你的智谱设置。
- `chat.completions.create(...)` 发起模型请求。
- `stream=False` 表示等待本次回答后一次性读取，先不学习分块拼接。
- `max_tokens=4096` 为本次生成设置额度，模型不一定用完；发生截断时，仍要识别 `finish_reason="length"`。
- GLM-5.3-Flash 的思考模式只能开启，因此这里使用 `thinking.type="enabled"`。
- `reasoning_effort="low"` 选择轻量推理，它仍然会思考；更复杂任务可按官方文档选择 `high` 或 `max`。
- `extra_body` 将智谱扩展字段加入请求；旧版关闭思考的字段已移除。
- `timeout=60.0` 设置请求超时；`max_retries=0` 关闭 SDK 自动重试，便于观察一次请求。
- SDK 返回一个响应对象，`.model_dump(mode="json")` 将它转换成 JSON 兼容的 Python 字典，再交给你的 `extract_reply`。

完整流程是：

```text
用户问题字符串
  → build_messages：Python 消息列表
  → SDK 编码为请求 JSON，发送到智谱
  → GLM 生成回答，服务返回响应 JSON
  → SDK 响应对象 → Python 响应字典
  → extract_reply：模型正文字符串
```

这一步是发送和读取模型消息，还没有执行你第五课的 GIS 工具。
第七课会让模型生成工具调用参数，再由 Python 执行工具并回传结果。

GLM-5.3-Flash 的思考开关与千问不同，不能只换模型名而照搬原来的请求参数。
如果正文为空、只有思考字段，或结束原因为 `length`，应检查生成额度、推理强度和请求状态，不能改为返回思考字段来绕过检查。
相关约定见 [官方模型说明](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash) 和 [核心参数](https://docs.bigmodel.cn/cn/guide/start/concept-param)。

## 11. 进行一次真实调用

配置就绪后执行：

```bash
python -m exercises.lesson_06 --live
```

`--live` 是本课程序提供的命令行选项，开启真实网络请求。
这次会使用自己的标准模型 API 权限和额度，按照智谱实际计费规则结算；离线练习没有模型调用费用。
程序会显示回答正文、响应 ID、请求 ID、模型和用量。记录这些信息即可，不记录 Key。

换一个问题再调用时可以使用：

```bash
python -m exercises.lesson_06 --live --question "为什么不能把经纬度的差直接当成米制距离？"
```

每次运行只进行一次请求。模型回答文字可能不同，检查时关注能否正确提取正文以及解释是否合理。

## 12. 遇到错误时检查哪一层

| 表现 | 先检查 |
| --- | --- |
| `练习待完成` | 两个 TODO 函数是否实现并保存 |
| 提示没有 `GLM_API_KEY` | 是否创建了智谱对应的 Codespaces 机密、终端是否已重启 |
| 提示 Base URL 不符合标准 API | 是否填成旧平台地址、完整请求路径或 Coding Plan 专用路径 |
| 提示安装依赖 | 是否激活 `.venv` 并安装本课 requirements |
| HTTP 400 | 请求参数、所选模型与参数支持情况 |
| HTTP 401 或 403 | Key 是否有效，是否有标准模型 API 与所选模型的权限 |
| HTTP 404 | 模型 ID 与接口地址 |
| HTTP 429 | 限流、额度或配额；对照智谱错误信息 |
| 连接失败或超时 | 当前网络、接口地址和服务状态 |
| `finish_reason` 不是 `stop` | 响应属于截断或其他分支，按本课约定报告未得到完整文本 |

这些是排查方向，具体原因以智谱控制台与 [官方接口文档](https://docs.bigmodel.cn/api-reference/模型-api/对话补全) 为准。
程序错误如字段拼写错误仍要修代码，不能通过捕获所有异常把它们伪装成正常回答。
重试策略和失败恢复会在第八课展开。

## 13. 完成标准与自己的回答

- [√] 我能解释 JSON 文本、Python 字典和 SDK 响应对象各是什么。
- [√] 我能追踪负半径怎样从第四课异常变成第五课错误字典。
- [√] 我能区分查询参数校验与地点数据校验。
- [√] 我实现了两个函数，第六课 19 项检查通过。
- [√] 我能解释 system、user、assistant 三个角色。
- [√] 我知道 `choices[0]` 与 `message.content` 的取值层级。
- [√] 我用自己的智谱标准模型 API 完成至少一次 `--live` 调用，并记录模型和响应 ID。

真实调用记录：

- 日期：2026.10.21
- 模型 ID：glm-5.3-flash
- 响应 ID：202610212332480914ce6a311e4eeb
- 我的提问：为什么不能把经纬度的差直接当成米制距离？
- 正文与结束状态是否符合预期：是
- 遇到的问题与排查过程：1.在判断列表非空时使用了strip()函数，结果报错显示list无该函数，我就想到该函数大概率是str的函数，list直接用not判断是否为空即可；
                       2.第一次新建消息时，把一条单独消息理解为了列表，最终全部添加到总消息中时，变成了列表嵌套，语法存在问题，不符合原始定义。

请在本节下面用自己的话回答：

1. `messages`、单条消息和 `content` 分别是什么 Python 类型？答：messages是列表、单条消息是字典、content是字符串。
2. 为什么安装了 `openai` 库，却仍然是在调用 GLM？ 答：openai库的作用是Python 消息列表编码成请求数据；根据接口地址和 API Key 发送网络请求；接收模型响应，并转换成方便读取的对象；通过异常报告超时、连接失败等问题，他并不是大模型本身，他是一个调用GLM的工具。
3. API 返回 JSON，为什么 `message.content` 仍可能只是普通文字？答：message.content是SDK响应对象的提取格式，获取的是message的content字符串，与字典取同字符串含义相同，因此也可以是普通文字。
4. `finish_reason="length"` 与第五课的合法空结果为什么要区别处理？答：因为该结果表示文本被截断了，属于数据输出异常的一种情况，而第五课是合法的匹配结果为空。
5. 用负半径这个例子，解释 `raise`、`except`、`return` 各发生在哪里。答：raise是在判断半径是否合法的函数中如果不合法则发生raise，except则是在入口前检查负半径不符合规则，return则会给出对应错误问题的合适语法进入工具调用。
6. 模型给出一组医院名称，为什么还不能据此认为 GIS 查询已经执行？答：因为需要查看输入的数据以及问题是否符合需求，而且也要看是否调用了GIS查询的工具。

## 14. 提交本课成果

通过检查后，逐行执行：

```bash
git diff
git add .gitignore docs/06-glm-api.md examples/messages_basics.py exercises/lesson_06.py checks/lesson_06.py data/lesson_06_response.json requirements-lesson-06.txt
git diff --cached --stat
git commit -m "feat: adapt model API lesson to GLM-5.3-Flash"
git push
```

`git diff` 进入分页时按 `q` 退出。提交列表中不包含 ZIP、虚拟环境或 API Key。
如果课程总览和旧讲义已更新，可另外提交 `docs/course-outline.md`、`docs/06-qwen-api.md`。
升级脚本与当前课程文件可一并保存：`git add scripts/upgrade_lesson_06_glm.py`。
在另一个环境重新运行升级脚本时，需要先解压同一升级包，提供 `.lesson06-glm-update/` 材料。

本课材料在备课环境中验证离线行为和 SDK 请求构造；没有使用你的 Key 发起真实调用。
离线检查通过不等于真实账号调用已经成功，真实调用以你自己完成并记录的结果为准。

参考资料核对日期：2026-10-20。

- [GLM-5.3-Flash 官方模型说明](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash)
- [智谱 Chat Completion API](https://docs.bigmodel.cn/api-reference/模型-api/对话补全)
- [智谱核心参数](https://docs.bigmodel.cn/cn/guide/start/concept-param)
- [OpenAI Python SDK 官方仓库](https://github.com/openai/openai-python)
- [本课使用的 SDK 版本](https://pypi.org/project/openai/3.35.1/)
