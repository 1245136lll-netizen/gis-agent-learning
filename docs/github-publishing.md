# 在 GitHub 整理项目并发布版本

如果你按 [第 0 步](00-github-codespaces.md) 使用 Codespaces，课程开始时就已经有自己的 GitHub 仓库和学习分支。
本页用于开发过程中的提交、审阅与最终发布，不需要再新建第二个仓库或重复添加 `origin`。

## 1. 整理一份可复现的版本

确认 README 写明环境要求、安装步骤、运行示例和当前功能；记录实际验证过的依赖版本；运行项目检查。
本项目代码采用 MIT 许可证；教学合成数据也随项目以 MIT 提供。加入外部数据或代码时，另行记录其来源和许可证。
检查提交内容中没有 `.env`、密钥、虚拟环境和不准备公开的文件。`.gitignore` 只会忽略尚未跟踪的文件，发布前仍要检查实际内容。

## 2. 确认自己的远程仓库与分支

在自己的 Codespaces 项目目录执行：

```bash
git remote -v
git branch --show-current
git status
```

`origin` 是远程仓库的本地别名，应指向自己的 GitHub 学习仓库。当前分支应为 `learn/gis-agent-from-zero`。
这与助手最初准备课程的 `/workspace/gis-agent-learning` 是两份仓库；不会自动同步彼此的文件。

## 3. 提交并推送自己的改动

阅读本次修改，再保存版本：

```bash
git diff
git add .
git diff --cached
git commit -m "feat: describe the function completed in this change"
git push -u origin learn/gis-agent-from-zero
```

提交消息应替换为本次实际完成的功能描述。`git add .` 会选择当前目录下所有未忽略的修改，提交前用 `git diff --cached` 确认内容。
本地保存文件、Git 提交、推送到 GitHub 是三个步骤，只有推送后其他人才能从远程分支取得这些提交。
Codespaces 通常会配置当前账号的仓库认证；遇到权限错误时根据实际错误定位，不要把访问令牌写进 URL 或源码。

## 4. 用 PR 审阅自己的项目

在 GitHub 创建 Pull Request：目标分支选自己的默认分支（通常是 `main`），来源分支选 `learn/gis-agent-from-zero`。
写明解决的问题、使用方法与验证结果；阅读完整 diff（改动对比），确认没有误提交的文件。
理解并确认改动后，再合并；发布版本前应从最终提交重新验证。

## 5. 发布第一个版本

如果最初使用 Private 仓库，准备公开开源时，将仓库可见性改为 Public。
为可运行的版本创建 `v0.1.0` 发布，说明已实现功能、数据来源、安装方法和使用示例。
完成标准是“别人能按说明运行，你能独立解释和扩展”，而不是仅在 GitHub 上有一个仓库。

如果你选择本地开发而没有使用 Codespaces，需要先创建 GitHub 仓库、关联远程地址并配置认证，再推送；不要直接套用这里关于已有 `origin` 的假设。
