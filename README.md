# academic-tikz

论文级 TikZ / PGFPlots 图像的统一技能。2026-10-29 由三个功能重叠的 TikZ 技能合并而成，目的是消除多个名字互相抢触发的问题，同时不丢任何资产。

## 合并来源

| 原技能 | 上游仓库 | 并入的内容 |
|---|---|---|
| tikz-diagrams | Patrick-Healy/tikz-diagrams-skill | 编译、渲染、视觉 QA 与动画脚本；因果 DAG、经济学/金融图族；Beamer 与通用模板；回归 fixtures |
| tikz-figure-skill | haiyichen001/tikz-figure-skill | 187 个已验证模板；15 项检查器；碰撞检测与布局参考 |
| tikz-scientific-figures | PM-Shawn/tikz-scientific-figures | PGFPlots 与六个学科 recipes；出版级 preamble；SVG 导出与 Method Draw 可视化编辑 |

三个上游技能都下载于 2026-10-19。

## 目录结构

```
academic-tikz/
  SKILL.md              统一入口：资产路由、工作流、质量红线、命令速查
  scripts/              编译、检查、渲染、动画、SVG 编辑脚本
  references/           规范文档 + 检查器脚本
    templates/          187 个模板（ML/UML/物理/化学/神经网络）
  templates/            通用画布骨架（standalone、Beamer、经济学示意）
  assets/               出版级 preamble、standalone 模板、Method Draw 编辑器
  tests/                回归 fixtures
  agents/               两份上游 agent 配置（内容不同，分别改名保留）
```

`README-templates.md` 与 `README-recipes.md` 是两份上游 README 的原样保留；`使用说明.md` 来自 tikz-scientific-figures。

## 改名与去重

内容不同的同名文件已改名保留：`README.md` 两份、`agents/openai.yaml` 两份。内容完全相同的文件只留一份。业务资产（模板、recipes、脚本）彼此不重名，路径保持原样。

## 安装

1. 把整个 `academic-tikz/` 目录放进所用 AI 工具的 skills 目录（如 Claude Code 的 `~/.claude/skills/`），重启对话。
2. 装一次绘图引擎：LaTeX（MiKTeX / BasicTeX / TeX Live）与 poppler，各系统命令见 [使用说明.md](使用说明.md)。
3. 环境自检：`bash scripts/check_env.sh`，或 `python3 scripts/check-env.py`。

## 分工

纯统计数据的 Python 绘图（Matplotlib / Seaborn / Plotly）、数据诚信审查、期刊导出规范与配色无障碍审计仍由 `python-data-figures` 技能负责。本技能负责 LaTeX 原生的示意、架构、机制与矢量出版图。
