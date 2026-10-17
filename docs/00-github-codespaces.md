# 第 0 步：只用 GitHub 和浏览器，建立自己的操作入口

你不需要额外购买云服务器。GitHub Codespaces 会为你提供开发环境，在浏览器中编辑代码和运行终端命令。

先区分三个东西：

| 你打开的页面 | 用途 |
| --- | --- |
| GitHub 仓库网页 | 保存代码、查看版本、编辑和提交文件 |
| `github.dev` 编辑器（例如在仓库里按 `.` 打开） | 在浏览器编辑文件，没有本课所需的 Python 运行环境或集成终端 |
| GitHub Codespaces | 编辑器 + 运行环境 + 终端，可以运行 Python、安装依赖和使用 Git |

依据：[GitHub 官方的两种编辑器对比](https://docs.github.com/zh/codespaces/the-githubdev-web-based-editor)。

助手之前准备文件的 `/workspace/gis-agent-learning` 属于助手工作环境，不是你登录 GitHub 就能直接进入的目录。之前准备的分支也还没有上传到你的 GitHub。以下步骤建立的是你自己可以亲手操作的环境。

## 1. 创建专用学习仓库

登录自己的 GitHub，打开 [新建仓库页面](https://github.com/new)。

1. Owner 选择自己的账号。
2. Repository name 填写 `gis-agent-learning`。
3. 选择可见性：可以先 Private 学习，准备发布开源版本时再改 Public。
4. 将 Add README / README 设置为开启，让仓库有初始提交。
5. 点击 Create repository。

这里需要初始化 README，才能从已有分支启动 Codespaces。暂时不用额外选择许可证和 `.gitignore`，后面会导入课程中的文件。
如果这个名称已被自己使用，选一个新名字，并按实际仓库名操作。

依据：[GitHub 仓库快速入门](https://docs.github.com/zh/repositories/creating-and-managing-repositories/quickstart-for-repositories)。

## 2. 在 GitHub 网页创建学习分支

在新仓库首页，点击文件列表上方显示当前分支名的下拉菜单（通常是 `main`）。
输入 `learn/gis-agent-from-zero`，选择创建这个新分支的选项。
确认页面当前分支显示为 `learn/gis-agent-from-zero`。

这是在你自己的 GitHub 仓库中建立的分支，区别于助手备课仓库里的同名分支。

## 3. 打开 Codespaces

仍在学习分支页面，点击绿色 Code 按钮 → Codespaces 选项卡 → 创建 codespace 的按钮。
若需要选择配置，可以使用 New with options / 新建并配置选项，确认分支，并在可选时选择 2 核机器；默认开发环境即可。
创建页面会显示费用归属。确认后点击 Create codespace，等待浏览器打开 VS Code 编辑器。

如果之前改过默认编辑器，选择在浏览器打开该 codespace 即可。左侧应能看到项目文件，中央是代码编辑区。

依据：[GitHub 官方创建步骤](https://docs.github.com/zh/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository?tool=webui)。

## 4. 找到终端，验证自己能运行 Python

在浏览器编辑器的菜单中选择 Terminal → New Terminal，或 View → Terminal。
如果菜单折叠在左上角，先展开菜单。终端一般出现在页面下方。

逐行输入以下命令，每行输入后按回车：

```bash
pwd
python3 --version
python3 -c "print('你好，GIS')"
```

第一条显示项目目录，通常在 `/workspaces/` 下；第二条显示 Python 版本；最后一条输出 `你好，GIS`。
这一步成功，就说明你已经在亲手操作云端开发环境，不必再另找一台云端计算机。

依据：[VS Code 终端使用说明](https://code.visualstudio.com/docs/terminal/getting-started)。

## 5. 导入已经准备好的课程材料

先完成上一步；新建仓库此时只有初始化 README，还没有 `examples` 等课程文件。
在聊天中下载 `gis-agent-learning-starter.zip` 源码包，保持 ZIP 文件形式。
将 ZIP 从电脑拖到 Codespaces 左侧的文件资源管理器中，放在项目根目录，让它与初始化 README 位于同一层；不要拖到中央编辑区或 README 文件内部。

确认终端 `ls` 能看到 ZIP 和 README，且 `git branch --show-current` 为学习分支。
仅在这个新建的专用学习仓库中执行以下导入，它会用课程 README 替换初始化 README：

```bash
git branch --show-current
python3 -m zipfile -e gis-agent-learning-starter.zip .
python3 -m venv .venv
source .venv/bin/activate
python examples/inspect_geojson.py
```

`zipfile -e` 是 Python 自带的解压命令，最后的 `.` 表示当前目录。
源码包直接包含 `README.md`、`data/`、`examples/` 等，不包含外层项目目录，不需要再次进入子文件夹。
源码包也不包含 `.git`、虚拟环境或密钥；它传递课程文件，不改变你仓库已有的 Git 历史。

示例应输出 `要素数量：3`，以及教学医院甲、教学公园、教学医院乙。
练习函数保持待实现状态；以后运行检查时提示待实现属于正常现象。

文件拖入资源管理器的能力参见 [VS Code 官方文件上传说明](https://code.visualstudio.com/updates/v1_46#_filefolder-upload)。

## 6. 保存到自己的 GitHub 学习分支

在终端逐行执行：

```bash
git status
git add README.md LICENSE .gitignore docs data examples exercises checks outputs
git commit -m "chore: import GIS agent learning materials"
git push -u origin learn/gis-agent-from-zero
```

`git add` 选择课程文件，`commit` 保存版本，`push` 上传分支。Codespaces 通常已配置当前 GitHub 账号的仓库认证。
如果出现权限或作者配置问题，保留错误信息再定位，不要把密钥或令牌粘贴进聊天。
ZIP 和 `.venv` 已列入忽略规则，不会作为课程源码提交。

回到 GitHub 仓库网页，切换到学习分支，确认能看到 `docs`、`examples`、`data` 等目录。
现在可以继续 [第一课](01-first-lesson.md)。

## 7. 每次结束与下次继续

- 保存并提交、推送自己要保留的代码。关闭浏览器标签页不会立即停止运行中的 Codespaces。
- 到 [我的 Codespaces](https://github.com/codespaces)，点击对应环境右侧的 `...` → Stop codespace。
- 下次仍从该页面打开已有环境，在项目目录执行 `source .venv/bin/activate` 继续，不用反复新建。

个人账户含每月免费计算和存储配额，具体剩余额度以账户页面为准；停止后不再消耗计算时间，但保留环境仍占用存储。
参见 [官方计费说明](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) 和 [停止与恢复步骤](https://docs.github.com/zh/codespaces/developing-in-a-codespace/stopping-and-starting-a-codespace)。

## 如果创建不了 Codespaces

先记录报错和提示：可能涉及个人额度、账户类型或组织策略。可以改用自己电脑上的 Python 和 VS Code，再把代码提交到 GitHub；不必为了学习项目先购买云服务器。
尚未导入课程文件时，不要运行 `python examples/inspect_geojson.py`，因为那个文件还不存在。
