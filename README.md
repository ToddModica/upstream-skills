# Codex 上游 Skills Marketplace

这是一个公开的 Codex Git Marketplace，用于分发具有明确上游来源和可再分发许可证的科研、写作、文档、开发及图示设计工作流。每个已打包的第三方 Skill 保留原目录、脚本、参考资料、资源文件和许可证；版本与 commit SHA 记录在 `sources.json`。外部插件 Tavotto 与 Diagram Design 在市场清单中引用其官方分支，安装时获取完整上游插件。

## 许可证边界

仓库根目录的 MIT License 只适用于本仓库新增的包装脚本、清单、校验器和文档，不会改变第三方内容的许可证。

特别注意：Academic Research Skills 与其 Codex 版本使用 **CC-BY-NC-4.0**，要求署名并限制商业使用。其他已打包来源使用 MIT 或 Apache-2.0。完整归属见 `THIRD_PARTY_NOTICES.md`，每个 Skill 的锁定许可证位置见 `sources.json`。

Tavotto 通过其官方 `plugin-stable` 分支按需拉取，许可证为 **AGPL-3.0**；本仓库仅保存其插件来源引用，未重新分发 Tavotto 代码。使用和再分发 Tavotto 时应遵守其上游许可证。

## 上游 GitHub 来源

以下链接对应本公开 Marketplace 已打包的 Skill、插件和 MCP 桥接。锁定提交、分支、许可证与目标目录以 `sources.json` 为准。

- Academic Research：[`academic-paper`、`academic-paper-reviewer`、`academic-pipeline`、`deep-research`](https://github.com/Imbad0202/academic-research-skills)；[`academic-research-suite`](https://github.com/Imbad0202/academic-research-skills-codex)。
- Nature：[`nature-*` 九个工作流](https://github.com/Yuan1z0825/nature-skills)。
- 专利与 SciPilot：[`patent-disclosure-skill`](https://github.com/handsomestWei/patent-disclosure-skill)；[`scipilot-cite-skill`](https://github.com/Haojae/scipilot-cite-skill)、[`scipilot-figure-skill`](https://github.com/Haojae/scipilot-figure-skill)、[`scipilot-writing-skill`](https://github.com/Haojae/scipilot-writing-skill)。
- 写作：[`humanizer`](https://github.com/blader/humanizer)、[`humanizer-zh`](https://github.com/op7418/Humanizer-zh)、[`shuorenhua`](https://github.com/MrGeDiao/shuorenhua)、[`stop-slop`](https://github.com/hardikpandya/stop-slop)、[`anti-defensive-writing`（中文）与 `anti-defensive-writing-en`（英文）](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill)。
- 开发与文档：[`bilibili-page-reader`、`powershell-safe-invocation`](https://github.com/Misaka-Mikoto-Tech/agent-skills)、[`design-taste-frontend`](https://github.com/Leonxlnx/taste-skill)、[`ppt-master`](https://github.com/hugohe3/ppt-master)、[`grilling`](https://github.com/mattpocock/skills)。
- 插件与 MCP：[`ponytail`](https://github.com/DietrichGebert/ponytail)、[`watermarks-remover`](https://github.com/guillaumemeyer/watermarks-remover)、[`no-negative-echo`](https://github.com/LB623/no-negative-echo)、[`itasca-mcp`](https://github.com/yusong652/itasca-mcp)、[`Tavotto`](https://github.com/Tavotto/Tavotto)。Tavotto 的插件来源固定为上游 `plugin-stable` 发布分支。
- CAD 运行时：专利工具的 STEP/SVG 处理使用 [`CadQuery`](https://github.com/CadQuery/cadquery)。
- 图示设计：[`Diagram Design`](https://github.com/cathrynlavery/diagram-design)，MIT 许可证，独立插件归入 `Creativity`，来源为官方 `main` 分支。

`imagegen`、`openai-docs`、`skill-creator`、`skill-installer`、`doc` 与 `pdf` 由 Codex 运行时提供；当前 `sources.json` 不含其可公开锁定的 GitHub 上游地址。

## 快速安装

需要 Codex CLI 和 Git：

```powershell
git clone https://github.com/ToddModica/upstream-skills.git
Set-Location .\upstream-skills
pwsh -NoLogo -NoProfile -File .\scripts\Initialize-Marketplace.ps1
```

也可以直接注册 Git Marketplace 并按需安装：

```powershell
codex plugin marketplace add https://github.com/ToddModica/upstream-skills.git --ref main
codex plugin add research-toolkit@research-toolkit-marketplace
codex plugin add writing-toolkit@research-toolkit-marketplace
codex plugin add codex-utility-toolkit@research-toolkit-marketplace
codex plugin add ponytail@research-toolkit-marketplace
codex plugin add watermarks-remover@research-toolkit-marketplace
codex plugin add no-negative-echo@research-toolkit-marketplace
codex plugin add tavotto@research-toolkit-marketplace
codex plugin add diagram-design@research-toolkit-marketplace
```

安装后新建 Codex 任务，使 Skills、Hooks 和 MCP 工具加载。

## 插件与 Skills

### research-toolkit

- Academic Research：`deep-research`、`academic-paper`、`academic-paper-reviewer`、`academic-pipeline`、`academic-research-suite`
- 中国专利：`patent-disclosure-skill` 及其申请、检索、解读、审查答复和专利地图工作流
- Nature：`nature-academic-search`、`nature-citation`、`nature-data`、`nature-figure`、`nature-paper2ppt`、`nature-polishing`、`nature-reader`、`nature-response`、`nature-writing`
- SciPilot：`scipilot-cite-skill`、`scipilot-figure-skill`、`scipilot-writing-skill`
- ITASCA MCP：通过 `uvx itasca-mcp` 启动；桥接文件位于 `plugins/research-toolkit/assets/itasca-mcp-addon.py`

### writing-toolkit

- `humanizer`
- `humanizer-zh`
- `shuorenhua`
- `stop-slop`
- `anti-defensive-writing`（中文）
- `anti-defensive-writing-en`（英文）

可显式调用 `$anti-defensive-writing` 或 `$anti-defensive-writing-en`。撰写或修改论文摘要、引言、结论、实验叙事、论文压缩及审稿回复时，也会按 Skill 描述自动匹配；建议里要求围绕真实贡献组织叙事，并保留与核心主张相关的结果和限制。

### codex-utility-toolkit

- `bilibili-page-reader`
- `design-taste-frontend`
- `doc`
- `grilling`
- `imagegen`
- `openai-docs`
- `pdf`
- `powershell-safe-invocation`
- `ppt-master`
- `skill-creator`
- `skill-installer`

### ponytail

完整保留上游插件的 Skills、Hooks、资源、测试和版本：`ponytail`、`ponytail-review`、`ponytail-audit`、`ponytail-debt`、`ponytail-gain`、`ponytail-help`。

### no-negative-echo

保留上游 Skill 与生命周期 Hooks，用于在任务启动、恢复、压缩和子代理启动时加载最终交付面检查规则。首次启用 Hooks 时应通过 `/hooks` 审查并信任。

### watermarks-remover

面向用户拥有或获授权处理的内容，检测并清理不可见 Unicode、C2PA、EXIF、XMP 和常见文档容器元数据。Skill 连接本机回环地址上的原生 Python 服务；核心路径要求 Python 3.10+，ExifTool 与 QPDF 可增强文件处理能力。

启动与检查：

```powershell
git clone https://github.com/guillaumemeyer/watermarks-remover.git "$env:USERPROFILE\watermarks-remover-service"
python "$env:USERPROFILE\watermarks-remover-service\service\scripts\server.py" --host 127.0.0.1 --port 8765
curl.exe -s http://127.0.0.1:8765/health
```

插件内 `Start-Service.ps1` 支持按需隐藏启动，使用结束后保持运行。远程服务地址和鉴权通过本机环境变量配置。

### Tavotto

Tavotto 用于在不改动 Matplotlib 源脚本的前提下，交互编辑、预检并导出科研图。公开市场条目代理其官方 `plugin-stable` 分支，包含 `tavotto-figure` Skill 与本地 MCP 服务。安装插件后，还需安装引擎：

```powershell
py -3 -m pip install --user pipx
py -3 -m pipx install "tavotto[worker]"
tavotto codex install
tavotto codex doctor
```

Windows 上每次 Tavotto 插件升级后都应再运行一次 `tavotto codex install`，以校正 MCP 使用的 Python 启动器。只安装 Tavotto 桌面版时可交接图形到桌面窗口；若要在 Codex 内使用 Tavotto MCP 画布与导出工具，仍需安装上述 `tavotto[worker]` 引擎。完成安装后必须新建 Codex 任务。

### Diagram Design（Creativity）

Diagram Design 适用于架构图、流程图、时序图、数据流图、层次图和已有图的重新排版，输出 HTML、SVG 或 PNG。市场直接引用 Cathryn Lavery / LittleMight 的官方仓库；上游插件保留作者信息、MIT 许可证、第三方许可说明与完整模板、参考资料及脚本。此市场条目由本市场维护。

HTML 预览只需现代浏览器；图源解析、SVG 导出和自检使用 Python 标准库。PNG 导出需要 Python Playwright 与 Chromium：

```powershell
python -m pip install playwright
python -m playwright install chromium
```

安装后新建 Codex 任务，直接描述任务即可按 Skill 描述自动匹配，例如：“把这个系统画成架构图，采用默认配色，输出 HTML 和 PNG。”也可以输入 `@diagram-design` 或 `$diagram-design` 明确选择插件或 Skill。首次使用时可选择默认风格、网站配色或已有品牌资料；在请求中写明“采用默认配色”即可给出该选择。

适合的任务包括结构和流程说明、汇报插图及 draw.io / Mermaid / Excalidraw 图源重绘。论文数据图仍应按数据、统计与期刊要求选择科研绘图工作流。模板默认从 Google Fonts 加载字体，离线时使用系统回退字体；按网站提取品牌时才需要访问用户指定的网站。详见[上游隐私说明](https://github.com/cathrynlavery/diagram-design/blob/main/PRIVACY.md)。

GitHub Actions 会自动刷新 `sources.json` 中的上游提交记录。已安装插件需刷新本机市场和插件后，在新任务中加载：

```powershell
codex plugin marketplace upgrade research-toolkit-marketplace
codex plugin add diagram-design@research-toolkit-marketplace
```

## 主要本机依赖

### PPT Master

完整 Skill、脚本、模板和 `requirements.txt` 随插件分发。首次使用前，在已安装的 Skill 目录运行：

```powershell
python -m pip install -r .\requirements.txt
```

它可能按任务启动本机预览服务、访问用户指定网页、调用外部转换程序或可选图像服务。只处理可信输入，并把可选服务凭据保存在本机环境变量或私有配置中。

### 专利工具

Markdown 主流程无需额外 Python 包。按需安装：

| 功能 | 依赖 |
|---|---|
| Word/PPT、公式与交付文件 | `requirements.txt` |
| 国知局检索 | `tools/requirements-cnipa.txt` 与 Playwright Chromium |
| PDF 专利解读 | `tools/patent_reader/requirements.txt` |
| Mermaid 图片 | Node.js 与 `tools/` 内 npm 依赖 |

涉及浏览器运行时下载或写入 Obsidian 库时，应先确认目标路径和数据范围。

### Hooks

Ponytail 与 No Negative Echo 的生命周期 Hooks 需要 PATH 中可用的 Node.js。初始化和更新脚本会检查运行时。

## 更新

在仓库目录运行：

```powershell
git pull --ff-only
pwsh -NoLogo -NoProfile -File .\scripts\Update-Marketplace.ps1
```

也可以直接刷新：

```powershell
codex plugin marketplace upgrade research-toolkit-marketplace
codex plugin add research-toolkit@research-toolkit-marketplace
codex plugin add writing-toolkit@research-toolkit-marketplace
codex plugin add codex-utility-toolkit@research-toolkit-marketplace
codex plugin add ponytail@research-toolkit-marketplace
codex plugin add watermarks-remover@research-toolkit-marketplace
codex plugin add no-negative-echo@research-toolkit-marketplace
codex plugin add tavotto@research-toolkit-marketplace
```

更新后新建 Codex 任务。

## 自动同步

`.github/workflows/sync-sources.yml` 每天北京时间 01:47 检查上游，也支持手动触发。流程会：

1. 更新 `sources.json` 中的上游 commit SHA；
2. 只复制已确认可再分发的 Skill、插件或指定子目录；
3. 保留许可证并拒绝越界路径、符号链接和凭据类文件；
4. 更新发生内容变化的插件补丁版本；
5. 校验 Marketplace、全部插件清单、SKILL.md、MCP 配置和来源锁；
6. 只在全部校验通过且内容发生变化时提交。

## 卸载

```powershell
codex plugin remove research-toolkit@research-toolkit-marketplace
codex plugin remove writing-toolkit@research-toolkit-marketplace
codex plugin remove codex-utility-toolkit@research-toolkit-marketplace
codex plugin remove ponytail@research-toolkit-marketplace
codex plugin remove watermarks-remover@research-toolkit-marketplace
codex plugin remove no-negative-echo@research-toolkit-marketplace
codex plugin remove tavotto@research-toolkit-marketplace
codex plugin marketplace remove research-toolkit-marketplace
```

## 版本回退

把 Marketplace 固定到已知提交：

```powershell
codex plugin marketplace remove research-toolkit-marketplace
codex plugin marketplace add https://github.com/ToddModica/upstream-skills.git --ref <commit-sha>
codex plugin add research-toolkit@research-toolkit-marketplace
```

恢复最新版本时重新注册 `--ref main`，再运行更新脚本。

## 多设备部署

公开上游 Skills 只需提供：

```text
https://github.com/ToddModica/upstream-skills
```

每台设备分别安装必要运行时，并在本机配置 API Key、Token、Cookie 或其他凭据。这些值不进入 Marketplace 仓库。

## ZCode

ZCode 可使用根目录 `.zcode-plugin/marketplace.json`，Codex 使用 `.agents/plugins/marketplace.json`；两份清单指向相同 `plugins/` 内容。

## 维护者校验

```powershell
python .\scripts\update_sources.py
python .\scripts\sync_sources.py --remote
python .\scripts\validate_catalog.py
python .\tests\test_generate_sources.py
```

上游许可证与来源锁的详细状态见 `sources.json` 和 `THIRD_PARTY_NOTICES.md`。
