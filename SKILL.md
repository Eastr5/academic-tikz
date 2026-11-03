---
name: academic-tikz
description: >-
  创建、编辑、编译并检查论文级 TikZ / PGFPlots 图像，保留可编辑的 .tex 源码，输出矢量 PDF 与 PNG 预览。
  覆盖因果图与机制示意、经济学与金融图示、研究流程与教学图、ML/深度学习架构、UML 与神经网络示意、
  CSV 数据图、物理/化学/生物/电路/数学学科示意图、多面板论文配图、Beamer 动画。
  触发词：画论文图、画架构图、画流程图、画示意图、技术路线图、因果图、TikZ 画图、论文配图、
  tikz diagram、latex figure、draw architecture diagram、make a figure for my paper。
  不适用于：纯统计数据的 Python 绘图（改用 python-data-figures）、位图工具
  （Photoshop/Figma/Canva）、快速草图、TikZ 语法问答。
---

> 首次安装见 [README.md](README.md) 与 [使用说明.md](使用说明.md)：把本目录放进所用工具的 skills 目录，再装一次 LaTeX 引擎（MiKTeX / BasicTeX / TeX Live）与 poppler。

# academic-tikz

把图当作交付物而不是代码片段：写源码 → 静态检查 → 编译 → 渲染 → 目视检查 → 修复 → 交付 `.tex` + `.pdf` + `.png`（数据图另附数据文件）。

## 资产路由

先判任务类型，再取对应资产。三套资产来自三个上游技能，合并后目录路径保持不变。

| 任务 | 入口 | 资产 |
|---|---|---|
| ML/深度学习架构、Transformer、CNN、GNN、UML、神经网络示意 | 模板优先 | `references/templates/`（187 个模板：165 个可直接编译，22 个 UML 片段需包进文档） |
| 物理、化学、生物、电路、数学学科示意图 | 按学科取 recipe | `references/physics-recipes.md`、`references/chemistry-recipes.md`、`references/biology-recipes.md`、`references/circuitikz-recipes.md`、`references/math-recipes.md`、`references/cs-recipes.md`、`references/diagram-recipes.md` |
| 因果 DAG、经济学/金融机制、供需与阈值曲线、研究流程、教学图 | 图族 + 通用模板 | `references/diagram_patterns.md`、`references/business_economics_patterns.md`、`templates/` |
| CSV 驱动的数据图（折线/散点/柱/直方/箱线/热图/等高/3D/对数） | recipe | `references/pgfplots-recipes.md`、`references/pgfplots-templates.md` |
| 多面板论文配图 (a)(b)(c)、插图、显著性标记、拟合与置信带 | 组图规范 | `references/figure-composition.md` |
| Beamer 动画、GIF/MP4 预览、帧序列 | 动画规范 | `references/animation_workflow.md`、`scripts/render_animation_preview.py` |
| 修订已有 .tex 图 | 编辑规范 | `references/editing-guide.md`、`references/critique_and_iteration.md` |
| 自由视觉润色（Inkscape/TikZiT） | SVG 分支 | `scripts/export_svg.sh`、`scripts/edit_svg.sh` |
| 编译、布局、标签报错 | 排错 | `references/tikz_gotchas.md`、`references/common-errors.md` |
| 含方程、曲线、均衡、阈值、博弈支付、几何依赖箭头 | 逻辑检查门 | `references/math_logic_checks.md` |
| 配色、字体、留白、幻灯片适配 | 视觉规范 | `references/style_guidelines.md`、`assets/preamble.tex`（内置色盲安全配色）；完整对比度审计走 python-data-figures |

## 统一工作流

1. **判类型**：对照上表确定图族与入口文件。同时确定呈现模式：`teaching`（讲义，允许解释框）、`research`（论文/会议，直接标注为主）、`compact`（多面板/受限版面，仅直接标注）。
2. **模板优先，不可跳过**：先在 `references/templates/` 中按关键词检索匹配模板，输出命中列表。零命中就放宽关键词。即使没有相似结构，也要从最接近的模板骨架起步，不从零生成。
   ```
   grep -l -i "<关键词>" references/templates/*.tex
   ```
   命中后按情况处理：完整匹配直接改标签与配色；部分匹配改标签、增删节点、调整坐标，必要时拼接 2 个以上模板；无相似结构仍沿用最接近的骨架。
3. **起手文件**：通用示意图用 `templates/standalone.tex`（Beamer 用 `templates/beamer_16x9.tex`）；出版级图用 `assets/standalone-template.tex` + `assets/preamble.tex`，保留文件顶部的 `TUNABLES` 块，便于后续手工调整。
4. **数据外置**：数据图的数值放外部 `data.csv`，改图优先改数据文件而不是改 TikZ。
5. **写短标签**：长解释放图外（caption、讲稿、QA 记录、回复正文）。默认不把 caption 式散文渲进图内。
6. **编译**：默认 XeLaTeX，两次编译，禁用 shell escape（宏包自动安装由本地 TeX 发行版决定）。
   ```bash
   python3 scripts/compile_render.py figure.tex            # 编译 + 渲染 PNG
   bash scripts/compile.sh figure.tex                      # 只要裁边 PDF（TIKZ_ENGINE 换引擎）
   ```
   需要其他引擎用 `--engine pdflatex`（或 `TIKZ_ENGINE=pdflatex bash scripts/compile.sh figure.tex`）；两个入口都固定编译两遍并传 `-no-shell-escape`。SVG 导出走 `scripts/export_svg.sh`；已存在输出默认拒绝覆盖，确认是本轮修订后再覆盖。
7. **检查**：编译前跑静态检查；编译后跑渲染视觉检查。两者可按需选一套。
   ```bash
   python3 scripts/check_tikz_safety.py figure.tex
   python3 scripts/compile_render.py figure.tex --visual-check --visual-mode research
   python3 references/quality_inspect.py output.tex output.pdf
   ```
   `quality_inspect.py` 汇总 15 项检查，不修改文件。正常时全部是 WARN，逐项判断：模板原本就带的 WARN 属于设计意图，跳过；适配编辑后新出现的 WARN 属于缺陷，修掉。任一检查器无法运行时它会打印 `FAILED SENSORS` 并以退出码 2 结束——此时结论不完整，不能当作通过。
8. **目视检查**：实际打开渲染出的 PNG，看文字重叠、标签裁切、空白输出、文字拥挤、版面适配、箭头语义、模型逻辑。自动检查不能替代这一步。
9. **修复循环**：读准报错或 QA 结果，只改最小源区域，重跑失败的那一项检查，从当前源码继续而不是重写整张图。同类失败连续两次后，改走简化、拆分或重设计。普通单图首渲染后只做一轮聚焦修复；除非有严重缺陷（重叠、裁切、不可读、空白、语义错误、版面明显失配）才继续。
10. **交付**：`.tex` + `.pdf` + `.png`（数据图另附数据文件）。批量任务附 contact sheet 与简短 QA 记录。动画另附帧预览。

## 质量红线

- 输出矢量 PDF，不只交付位图；保留 `.tex` 源码与真实数据来源。
- 无文字重叠、无标签/箭头/图例裁切、无空白渲染。
- 色盲安全配色（Okabe–Ito、viridis），已写入 `assets/preamble.tex`；不硬编码原始红绿，不用 `jet`。
- 按目标版面定尺寸：单栏 89 mm、双栏 183 mm，正文 7–9 pt。每个坐标轴标注单位；误差棒注明 SD/SE/CI；多面板编号 (a)(b)(c)；数学标签用 LaTeX 渲染以与正文一致。
- 箭头必须表达真实语义（因果、时序、逻辑、变换、诊断、反馈）。一张图只讲一件事；机制加系数、模型加诊断这类双诉求默认拆成配对图。
- 数学、曲线、均衡、统计量、阈值、博弈支付、几何依赖图必须核对代数与比较静态。缺少精确方程或数据时，在 QA 记录里标为 `schematic`，不做看起来精确的数值暗示。
- 编辑已有图：默认改 `.tex` / `.csv` 后重编译，有源码就不重画。视觉修复从最小改动开始，不顺手重排无关元素。
- SVG 分支：`export_svg.sh` 会写出 `figure.svg.frozen` 标记，此后 SVG 是权威源、`.tex` 是冻结存档。**不得再用旧 `.tex` 覆盖用户的 SVG 编辑**，并始终告知当前处于哪个分支。`edit_svg.sh` 启动本地 Method Draw 编辑器，`Ctrl/Cmd+S` 写回同一文件。
- 动画：先明确什么在变、为何动画优于静态图。每个运动元素都要有意义，不为装饰而动。交付交互式 PDF 与可检查的帧预览；平滑过渡显著增加渲染时间时，先询问走快速分步预览还是慢速平滑渲染。
- 迭代与 critique：使用版本化文件名（`figure_v01.png`、`contact_sheet_v02.png`），只把确认接受的版本复制成最终文件名，避免浏览器或聊天缓存显示旧渲染。

## 命令速查

设 `SKILL_DIR` 为本技能目录。以下命令在技能根目录下执行，路径相对技能根；Windows 上 `python3` 换成 `python`。

| 用途 | 命令 |
|---|---|
| 静态安全检查 | `python3 scripts/check_tikz_safety.py figure.tex` |
| 编译 + 渲染 + 视觉 QA | `python3 scripts/compile_render.py figure.tex --visual-check --visual-mode research` |
| 图上标签压线细查 | 加 `--text-plot-overlap`，可用 `--plot-label-regex` 指定标签文本 |
| 检查已有 PDF | `python3 scripts/check_tikz_visual.py figure.pdf --mode teaching --report qa.json` |
| 15 项布局检查 | `python3 references/quality_inspect.py output.tex output.pdf` |
| 批量 contact sheet | `python3 scripts/make_contact_sheet.py path/to/pngs --output sheet.png --show-qa` |
| 受控图序列 | `python3 scripts/render_tikz_series.py series_manifest.json` |
| 动画帧预览 | `python3 scripts/render_animation_preview.py frames.pdf --fps 8 --key-frames 1,10,20` |
| 环境自检 | `python3 scripts/check-env.py` 或 `bash scripts/check_env.sh` |
| 编译/预览/导出 SVG | `bash scripts/compile.sh figure.tex`、`bash scripts/preview.sh figure.pdf`、`bash scripts/export_svg.sh figure.tex` |
| SVG 可视化编辑 | `bash scripts/edit_svg.sh figure.svg` |

## 完成标准

- `.tex` 源码存在；静态检查通过，或例外已记录。
- PDF 编译成功，PNG 渲染非空。
- 渲染视觉 QA 通过，或警告已逐项目视确认。
- 标签落在绘图区内时，文字压线细查已通过或已人工检查。
- 目视检查无严重重叠、裁切、版面失配。
- critique 门有明确结论：`keep` / `simplify` / `split` / `reject`。
- 数学、曲线、模型、估计量、阈值、博弈、几何依赖图：逻辑审查已标注为 `exact` / `schematic` / `needs_source` / `failed`。
- 动画：帧序列已通过帧页、GIF/MP4 预览或 contact sheet 检查，不只看首帧。
- 批量：contact sheet 已生成并检查。
- 回复用户时给出实际检查过的、本轮新渲染的版本化文件，不依赖被覆盖的固定文件名或浏览器缓存。

## 引用索引

按需读取，不要一次性全加载：

- 通用规范：`references/style_guidelines.md`、`references/tikz-coding-rules.md`、`references/design-philosophy.md`、`references/visual-patterns.md`
- 图族与领域模板：`references/diagram_patterns.md`、`references/business_economics_patterns.md`、`references/layout-patterns.md`
- 几何与碰撞：`references/collision-detection.md`、`references/geometry-math.md`、`references/graphdrawing-guide.md`
- 迭代与回归：`references/critique_and_iteration.md`、`references/clean_room_handoff_tests.md`、`references/example_corpus.md`
- 学科 recipes：`references/*-recipes.md`
- 组图与编辑：`references/figure-composition.md`、`references/editing-guide.md`
- 排错：`references/tikz_gotchas.md`、`references/common-errors.md`
- 上游说明：`README-templates.md`、`README-recipes.md`、`使用说明.md`

## 分工边界

纯统计数据的 Python 绘图（Matplotlib / Seaborn / Plotly）、数据诚信审查、期刊导出规范与无障碍配色审计走 `python-data-figures` 技能。本技能负责 LaTeX 原生的示意、架构、机制与矢量出版图。若用户要的是"用 TikZ 画由数据驱动的图"，仍归本技能。
