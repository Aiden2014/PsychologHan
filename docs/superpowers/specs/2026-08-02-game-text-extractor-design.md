# Psycholog 游戏流程与文本提取器设计

## 目标

在 `scripts/` 下提供一个可重复运行的 Python 工具，读取 `Assembly-CSharp-decompiled/` 中的剧情代码以及 `resources/` 下的 Unity 导出 JSON/资源文件，生成适合 Paratranz 翻译的三列 CSV，同时生成不进入翻译平台的流程、场景、动画和音频参考索引。

## 范围

工具覆盖四类信息：

1. `GameManager.cs` 中的对白、旁白、选项、节点跳转、图片、动态背景、过场、音乐、环境音和音效调用。
2. C# 中明确赋给 UI 文本组件的字符串，以及 `MonoBehaviour` 导出的 `Text`/`TextMeshProUGUI` 文本。
3. Unity 导出的 `GameObject`、`AudioSource`、`AudioClip`、`Sprite`、`Texture2D`、`Animator`、`AnimatorController`、`AnimationClip`、`Transform` 和 `RectTransform` 之间的引用关系。
4. 无法确定的跨文件引用，写入单独报告而不是丢弃。

`TextAsset`、`ActionListAsset` 和其他 `ScriptableObject` 为可选输入；当前资源不存在时程序正常运行。

## 输出格式

所有 CSV 都使用 UTF-8 with BOM、无表头、三列：唯一键、原文或参考内容、译文/空列。

- `dialogue.csv`：对白与旁白。
- `choice.csv`：选项文字。
- `item.csv`：调查项、物品和 `sitItems` 运行时文本。
- `character_name.csv`：对白说话者名称、客户端标题名称和可识别的人物名。
- `client_info.csv`：客户端进度、信任度、治疗状态和资料页说明。
- `ending.csv`：死亡符文、结局说明和结算文字。
- `ui.csv`：界面文字。
- `flow_context.csv`：不用于翻译的剧情模块、对白顺序、选项分叉、节点跳转、图片、动画、音乐和音频上下文。
- `asset_index.csv`：资源类型、名称、来源文件、PathID 与导出文件路径。
- `unresolved_refs.csv`：无法唯一解析的 Unity 引用。

翻译 CSV 的键只使用稳定的节点、说话者、对象标识和行号，使用短的 `|||` 分隔格式，不再重复写入 CSV 分类名和来源文件名前缀；键超过 512 字符时直接报错而不静默截断。键中的字段按 CSV 类型固定位置解释：对白为“节点|||说话人|||行号”，选项为“来源节点|||选项 ID|||行号”，UI 为“来源文件|||PathID|||类型|||对象名”。`asset_index.csv` 是例外，保留完整资源类型、来源和 PathID。流程参考通过节点键关联，避免资源文件名变化导致 BepInEx Hook 键变化。

## 解析方式

### C# 扫描

不依赖完整 C# 编译器。工具使用忽略注释和字符串内部括号的调用扫描器，并按顶层逗号拆分参数，因此可以处理多行调用、字符串中的逗号和包含 `delegate` 的回调。

从 `GameManager.cs` 识别：

- `addMe`、`addSpeaker` 及角色包装方法：对白/旁白。
- `addOpt`、`warm`、`joking`、`analytical`、`stern`、`silent` 等：选项。
- `illustrate`、`animate`、`addCutscene`：视觉事件。
- `addMusic`、`addAmbience`、`playSoundEffect`：音频事件。
- `addChoice`、`addMap`、`addPac`、`applyTransition`：流程事件。

同时提取以下非节点文本：

- 角色包装方法中的显示名，例如 `VERA`、`DET. JACKSON`、`DR. BENNETT`。
- `GameState` 的 `trustComment*`、`treatmentComment*` 和 `rune*` 初始文本。
- `GameManager.updateProgressionMetricComments()` 和 `DeathRunes.cs` 中按条件选择的文本。
- `died`、`failed`、`fight` 中生成的系统文字。
- `sitItems[id].text = "固定文本" + 运行时表达式`，固定片段保留，运行时表达式替换为稳定占位符，并在参考字段中保留原始表达式。

默认不把 Adventure Creator 自身的编辑器说明、调试日志和资源类型说明当作玩家可见文本；只有带有实际游戏对象来源或明确游戏 UI 字段的值才进入翻译 CSV。

每条流程记录保留源文件行号、节点 ID、触发方式和原始调用摘要；回调中的音效会关联到外层对白或过场调用。`strToAudio()` 中明确存在的别名（例如 `subway -> subwayAmbience`）会继续解析到 AudioSource/AudioClip。

`GameManager` 中的 `storyAshley()`、`storyVera()` 等剧情方法会写入 `story_module`；其中的对白调用写入 `dialogue_edge`，保存目标节点；选项调用写入 `choice_edge`，保存选项 ID 和目标节点。模块内的源码行号用于保持定义顺序，目标节点用于表示线性跳转或分叉关系。游戏没有显式的“前期/中期/后期”字段，因此工具不擅自生成这类阶段标签。

纯下划线 UI 文本（例如 `__________`）视为布局或输入框占位线，不进入 `ui.csv`；含有实际可读字符的 UI 文本仍然提取。

### Unity 引用索引

每个 JSON 对象以 `(source_file, path_id)` 建立索引。`m_FileID=0` 优先在当前来源文件内解析；非零 `m_FileID` 使用来源文件映射、类型约束和唯一 PathID 候选解析。若候选仍不唯一，输出 unresolved report 并保留原始引用。

资源名解析同时使用 JSON 的 `m_Name` 和 UABEA 导出的文件名，图片/音频的实际导出路径只作为参考信息，不参与翻译键生成。音频字段会尝试按 `GameManager -> AudioSource -> AudioClip` 解析，图片事件会同时记录 Sprite JSON 及同名 PNG（若存在）。

## 错误处理

- 缺少可选资源目录时跳过并报告。
- JSON 损坏或无法解码时记录文件名和错误，继续处理其他文件。
- 同一键对应不同原文时保留第一条并报告冲突。
- `nothing` 音频哨兵和 `addPac/addMap` 的 `backgroundImage` 默认参数不视为缺失资源；其他找不到或无法唯一确定资源的引用写入 `unresolved_refs.csv`。
- 输出目录不存在时自动创建；每次运行覆盖本次生成的 CSV。

## 测试策略

使用 pytest 测试纯 Python 解析逻辑：C# 参数扫描、对白/选项提取、JSON PathID 索引解析、AudioSource→AudioClip 关联、Sprite→Texture2D 关联、三列 CSV 输出和 unresolved 报告。测试使用临时目录构造最小资源，不依赖完整游戏资源。

## 运行方式

默认从项目根目录推导输入和输出路径：

```text
python scripts/extract_game_text.py
```

同时支持显式指定项目根目录和输出目录，便于以后对不同 dump 版本重复运行。
