# GIS Agent Learning

从零开始，自己写出一个能调用 GIS 工具的自然语言空间分析助手。

你可以把它想成这样的程序：

> 输入：“查询经度 121.4700、纬度 31.2300 周围 1 公里内的医院。”
>
> 程序识别查询条件，调用距离计算和筛选工具，返回候选医院、距离、数据来源与 GeoJSON 结果。

这是**最终目标**。目前仓库包含学习路线、可运行的入门示例、合成数据和第一课练习；自然语言 Agent 尚未实现。

## 从哪里开始

1. 先阅读 [第 0 步：用 GitHub Codespaces 开始](docs/00-github-codespaces.md)，建立自己能操作的开发环境并导入源码。
2. 阅读 [第一课：从终端到 GeoJSON](docs/01-first-lesson.md)，按顺序亲手操作。
3. 运行示例，理解数据结构。
4. 完成 `exercises/lesson_01.py` 中的一个函数，然后运行检查。
5. 用自己的话记录理解与问题，带着结果进入下一课。

在已导入源码的 Codespaces 终端中，确认当前目录里有本 README、`data`、`examples` 等文件后，逐行执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python examples/inspect_geojson.py
```

每个新环境都要创建自己的 `.venv`；源码包不会包含虚拟环境。
第一课只用 Python 标准库，不需要安装第三方包或配置大模型密钥。

## 学习材料

| 文件 | 用途 |
| --- | --- |
| [GitHub Codespaces 入门](docs/00-github-codespaces.md) | 从 GitHub 网页创建自己的分支、打开终端、导入学习材料 |
| [课程路线](docs/roadmap.md) | 每个阶段要学什么、做什么、怎样算完成 |
| [第一课](docs/01-first-lesson.md) | 终端、Git、Python 与 GeoJSON 的逐步讲解 |
| [项目设计](docs/project-design.md) | 最终行为、模块划分、GIS 与 Agent 的分工 |
| [学习记录](docs/progress.md) | 记录你亲手完成的内容和卡住的问题 |
| [GitHub 发布指南](docs/github-publishing.md) | 完成项目后创建远程仓库与发布版本 |

## 仓库结构

```text
gis-agent-learning/
├── data/                     # 教学合成数据和数据说明
├── examples/                 # 已完成、可阅读的示例
├── exercises/                # 由你实现的练习
├── checks/                   # 练习验收工具
├── docs/                     # 教程、设计与学习记录
├── outputs/                  # 将来生成的分析结果，Git 忽略其中内容
└── LICENSE                   # MIT 开源许可证
```

约定学习分支为 `learn/gis-agent-from-zero`，默认分支保存起点。助手最初在 `/workspace/gis-agent-learning` 准备了本地仓库和分支，尚未替你创建或上传 GitHub 仓库。按第 0 步操作后，你会在自己的 GitHub 仓库和 Codespaces 中拥有课程文件。源码包传递文件内容，不传递助手仓库的 Git 历史。

## 学习方式

每次推进一个可验证的小目标：先理解输入输出，再自己实现，运行检查，最后解释代码。卡住时先缩小问题、看错误提示、请求提示；需要完整解答时也可以明确提出。

教程中的终端命令适用于 Codespaces 的 Bash 环境。Codespaces 项目路径通常位于 `/workspaces/` 下，以自己的 `pwd` 输出为准。不要将 Python 代码直接粘贴到 Bash；代码写入 `.py` 文件后，用 `python 文件路径` 运行。
