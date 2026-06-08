---
name: hfut-xuancheng-ppt-maker
description: Create or revise Hefei University of Technology Xuancheng Campus style classroom presentation decks from Chinese requests, screenshots, source PPTs, course topics, or memory notes. Use when the user asks for 合肥工业大学/合工大/宣城校区 PPT 制作, course reports, classroom presentations, 6-8 minute talks, HFUT red-white style templates, slide scripts, or adapting an old PPT into a polished lecture/report deck.
---

# 合肥工业大学宣城校区 PPT 制作

用于制作或改造合肥工业大学宣城校区风格的课堂汇报 PPT。目标是生成可直接演讲使用的 PPTX/演示文稿，而不是答辩模板堆砌或空泛美化。

## 快速流程

1. 读取用户给的题目、截图、原始 PPT、身份信息、课程要求和演讲时长。
2. 明确输出：默认做课堂演讲版 PPT；如果用户需要，另配逐页演讲稿或视频脚本。
3. 提炼主题结构，按 6-8 分钟控制在约 12-15 页；用户指定页数时优先服从。
4. 套用合工大/宣城校区风格：红白为主，金色点缀，保留校徽、校名、姓名、专业/班级等身份信息。
5. 联网补充资料和图片时，优先使用权威来源，图片必须与主题高度相关且不重复。
6. 制作 PPT 后必须渲染或截图检查每页：文字不压图、不溢出、不重叠，图片无明显重复痕迹。
7. 交付 PPT 文件，并简要说明页数、主题、是否附带演讲稿和检查结果。

详细规范见 [references/ppt-production-standard.md](references/ppt-production-standard.md)。

## 输入信息

优先从用户材料中提取：

- 姓名、学校、学院、专业、班级、学号或汇报人。
- 课程名称、章节、主题、老师要求或评分点。
- 原始 PPT、截图、网页链接、图片素材或模板。
- 演讲时长、页数要求、是否课堂汇报/答辩/小组展示。
- 是否需要联网检索资料和图片。

信息缺失但不影响制作时，使用占位符或合理默认值；不要为了姓名/班级等小字段阻塞整体制作。

## 制作原则

- 课堂汇报优先，不默认做毕业答辩风。
- 内容不能太少；每页应有明确讲述点。
- 图片和文字不能重叠，文字必须清晰可读。
- 不要多次使用同一张图片；同类图片也要避免明显重复。
- 图片优先选历史图片、地图、人物、文献截图、场景图、课程相关网页截图。
- 旧 PPT 改造时保留原始结构的有用部分，补足不足内容，统一版式。
- 首页必须体现学校/课程/主题/汇报人，不要只有装饰图。
- 结尾页可用“感谢聆听”“请批评指正”等合工大红色系收束。

## 工具选择

- 制作 `.pptx` 时优先使用可渲染检查的演示文稿工具或 Presentations 插件能力。
- 若用户指定 Canva、网页 PPT 或单 HTML PPT，可使用对应工具，但仍遵守本 Skill 的内容与视觉规范。
- 需要联网检索资料时，必须打开网页核对来源；优先学校官网、人民网、求是网、新华社、政府/机构官网、课程指定材料。
- 使用用户提供的模板或 logo 时，优先复用原始素材，不凭空改动校徽比例和校名。

## 质量检查

交付前必须检查：

- 页数是否符合演讲时长和用户要求。
- 所有页面是否无文字重叠、无裁切、无明显错位。
- 图片是否清晰、不重复、与主题相关。
- 标题层级是否统一，页脚/页码/校名是否一致。
- 内容是否适合课堂演讲，而不是答辩式“研究背景、意义、难点”空模板。
- 若生成演讲稿，逐页稿件总时长应匹配用户要求。

## 记忆来源

本 Skill 从用户提供的 `skill.pdf` 中提炼，重点保留其中关于合工大风格、课堂演讲版、资料补充、视觉排版和 Skill 化封装的可复用逻辑。
