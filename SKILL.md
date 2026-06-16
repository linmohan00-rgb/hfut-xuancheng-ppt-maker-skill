---
name: hfut-xuancheng-ppt-maker
description: Create, revise, or restyle editable Hefei University of Technology and Xuancheng Campus PPTX decks by selecting exactly three complementary templates from the bundled HFUT template bank, extracting suitable source slides, and fusing them into one coherent visual system. Use for 合肥工业大学/合工大/宣城校区 PPT 制作, 课堂汇报, 课程展示, 论文答辩, 项目汇报, 研究报告, old-PPT redesign, seasonal campus decks, speaker notes, or requests to combine several HFUT templates without producing a visibly stitched deck.
---

# 合工大三模板融合 PPT 制作

制作可编辑、可直接演讲的合肥工业大学或宣城校区风格 PPTX。每次新建或大改 PPT 时，先从内置模板库选择三套互补模板，再按“一个视觉锚点 + 两个版式供体”的规则融合。

## 必须遵守

- 使用内置模板真实抽页，不凭空仿制合工大校徽、校名或模板装饰。
- 每个任务选择恰好三套模板，但不平均混用。建议视觉影响比例为 `60% / 25% / 15%`。
- 最终 PPT 只能有一套字体、色彩、页眉页脚、标题、页码和校徽规则。
- 主模板决定视觉系统；另外两套只提供构图、信息图、图表、图片裁切或季节气质。
- 未提供汇报人、姓名、班级、专业、学号、学院或日期时，相关字段必须留空或删除；不得默认代入任何个人姓名、历史姓名、`软件工程` 或其他假定身份信息。
- 不交付仍含“输入标题”“单击此处”等模板占位文字的页面。
- 不把不同模板的页眉、页脚、校徽版本和颜色原样并列保留。
- 必须渲染并检查全部页面后再交付。

详细融合规则见 [references/fusion-protocol.md](references/fusion-protocol.md)，模板风格说明见 [references/template-catalog.md](references/template-catalog.md)。

## 工作目录

将中间文件放在当前线程的演示文稿工作区：

```text
outputs/<thread-id>/presentations/<task-slug>/
  template-selection.json
  fusion-starter.pptx
  source-notes.txt
  claim-spine.txt
  design-system.txt
  preview/
  qa/
  output/
```

只把最终 PPTX、用户明确要求的讲稿或视频放入 `output/`。

## 制作流程

### 1. 读取需求

优先提取：

- 主题、课程、受众、演讲时长、页数和汇报类型。
- 姓名、学院、专业、班级、学号、小组和日期。
- 用户提供的原 PPT、截图、资料、图片和评分要求。
- 是否偏好简洁、沉稳、深色、数据型、校园摄影、秋季或冬季。

身份信息缺失但不影响制作时，清空对应字段或删除该信息行，不为姓名、班级等小字段阻塞整体制作。默认课堂汇报为 12-15 页、6-8 分钟。

### 2. 选择三套模板

先运行选择器：

```powershell
python scripts/select_templates.py `
  --brief "<主题、场景、受众、风格、时长的合并描述>" `
  --slides <页数> `
  --sections <章节数> `
  --output "<工作区>\template-selection.json"
```

选择器输出：

- `visual_anchor`：统一全稿品牌、字体、色彩和页面框架。
- `layout_donor`：提供章节页、流程、对比或复杂图文构图。
- `accent_donor`：提供数据图、摄影裁切、季节氛围或强调页。
- `slide_plan`：每张输出页对应的模板资产页和原始页码。

必须查看三套模板的联系表：

```text
assets/previews/<template-id>.png
```

如果某套模板与内容明显冲突，使用 `--exclude id1,id2` 重选；用户明确指定风格时可使用 `--include id1`。

### 3. 生成融合起始稿

在 Windows 且安装 PowerPoint 时运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_fusion_starter.ps1 `
  -Plan "<工作区>\template-selection.json" `
  -Output "<工作区>\fusion-starter.pptx"
```

此脚本按计划从三套模板复制真实、可编辑的源页面，并保留来源追踪。脚本只生成起始稿，不代表格式融合已经完成。

没有 PowerPoint COM 时，读取 `template-selection.json`，用 Presentations 插件分别导入对应模板资产并复制计划中的源页；不得改成空白页重画。

### 4. 写叙事骨架

在编辑页面前写 `claim-spine.txt`：

- 一句话主题。
- 受众和演讲目标。
- 每页的结论式标题。
- 每页唯一的主要证据对象：图片、图表、表格、流程、时间线或对比。
- 数据与图片来源。

课堂汇报不机械套用“研究背景、研究意义、研究方法”。根据课程主题改写章节；只有论文或研究答辩才使用研究结构。

### 5. 锁定融合设计系统

从 `visual_anchor` 提取并写入 `design-system.txt`：

- 页面比例和安全边距。
- 校徽、校名、页眉、页脚、页码位置。
- 标题、正文、数字和注释字体。
- 主红、深色中性、浅色中性、辅助强调色。
- 图片裁切、圆角、描边和阴影规则。
- 图表、表格、流程图和章节页语法。

将另外两套模板的颜色和字体映射到主模板语义色与字体，不直接保留供体模板的独立视觉系统。

### 6. 编辑真实模板页

将 `fusion-starter.pptx` 作为 template-following 源稿，用 Presentations 插件导入后编辑复制页：

- 保留供体页面的构图骨架、对齐、留白和对象关系。
- 替换全部示例文字、图片、图表和数据。
- 删除供体模板重复的校徽、页眉、页脚和无关装饰。
- 将非主模板页面的标题、正文、颜色、线条、按钮和页码统一到主模板。
- 只在现有模板页无法承载内容时换用计划中的另一张源页，不从空白页仿造模板。

若用户提供旧 PPT，将旧 PPT 作为内容来源，不让旧稿的混乱格式覆盖融合设计系统。

### 7. 内容与素材

- 联网补充资料时优先学校官网、政府和权威机构、课程指定资料、论文原文。
- 不虚构数据、引文、获奖信息、校史事实或人物身份。
- 不虚构汇报人、班级、专业、学院、学号或日期；只有用户材料明确给出时才填写。
- 同一图片只使用一次；相似校园图避免连续重复。
- 校徽、校名和官方标识只使用模板内或用户提供的真实资产。
- 图片做背景时添加足够遮罩，确保文字对比度。

### 8. 全量 QA

导出前必须：

1. 渲染每一页和整稿联系表。
2. 检查文字溢出、重叠、断行、裁切、低对比度和图片变形。
3. 检查三套模板已经融合为一套字体、主色、校徽、标题和页脚规则。
4. 检查没有模板示例文案、二维码、测试数据、陌生姓名或供体模板残留。
5. 检查汇报人、姓名、班级、专业、学院、学号和日期没有默认值；未知字段为空或已删除。
6. 检查连续三页不使用完全相同的宏观构图。
7. 检查所有图表与标题结论一致，数据有来源且单位统一。
8. 检查演讲时长、页数和逐页讲稿相匹配。

运行模板库验证：

```powershell
python scripts/validate_template_bank.py
```

## 讲稿

用户要求讲稿时按页生成，不照读页面文字。7-8 分钟中文讲稿通常约 1200-1800 字，并与最终页码完全对应。

## 交付

交付：

- 相关主题命名的最终 `.pptx`。
- 用户要求时附逐页讲稿或视频脚本。
- 简短说明页数、选中的三套模板、融合主模板和 QA 结果。

不要把选择 JSON、预览图、临时脚本或联系表当作最终交付物，除非用户明确要求。
