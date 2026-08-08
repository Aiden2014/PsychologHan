# Unity Mono 游戏汉化 Skill 设计

## 目标

创建个人 Codex skill `localizing-unity-mono-games`，用于为 Unity Mono 游戏建立可复现的中文本地化项目，并完成文本提取、剧情流程重建、Paratranz 协作、BepInEx 运行时补丁、字体与图片处理、人工游玩验收和发布验证。第一版不实现 IL2CPP；PsychologHan 是首个端到端验收样例，ProdigalHan 与 RhellHan 是 Mono 补丁主要参考，SuperLoneSurvivorHan 与 SeafrogHan 只用于借鉴通用项目结构和运行时漏文本记录方式。

## 总体架构

采用“通用管线 + 游戏适配器 + 人工验收”的分层结构：

1. 通用层定义目录、条目格式、Paratranz CSV 约束、QA、BepInEx 脚手架、运行时审计和发布门禁。
2. 游戏适配器由 Python 脚本实现，解析该游戏的 ILSpy 反编译代码、AssetStudio JSON 和特殊数据结构。
3. 人工层负责确认剧情顺序、人物语气、难以静态发现的运行时文本、影响流程的图片文字、字体和版面效果。

所有自动推断均保留来源与置信度；补丁运行时找不到译文时显示原文并记录缺口，不因汉化失败阻断游戏。

## 项目布局

推荐每个游戏使用以下布局：

```text
GameHan/
├─ .gitignore
├─ Directory.Build.props.example
├─ GameHan.csproj
├─ Plugin.cs
├─ TranslationManager.cs
├─ ResourceLoader.cs
├─ MissingTextTracker.cs
├─ FontManager.cs
├─ ImageAudit.cs
├─ ImageReplacer.cs
├─ localization/
│  ├─ project-profile.json
│  ├─ glossary.csv
│  ├─ translation-guide.md
│  ├─ qa-rules.json
│  ├─ characters/
│  └─ story/
├─ scripts/
│  ├─ extract_game_text.py
│  ├─ export_paratranz.py
│  ├─ import_paratranz.py
│  └─ validate_localization.py
├─ tests/
├─ resources/
│  ├─ managed/
│  ├─ decompiled/
│  ├─ assetstudio-json/
│  ├─ work/
│  ├─ fonts/
│  └─ runtime-audit/
└─ dist/
```

`.gitignore` 必须忽略整个 `resources/`、`dist/`、`bin/`、`obj/`、本机 `Directory.Build.props` 和 IDE 缓存。`localization/` 默认纳入版本控制，因为它只保存项目 profile、术语表、角色风格、剧情顺序、QA 规则等可公开协作资料；从游戏提取的原文语料、DLL、JSON dump、字体源文件、运行时日志与截图留在 `resources/`，不提交。项目若获得合法授权提交译文，再由用户显式调整规则。

## 发现与提取

先记录游戏版本、Unity 版本、Mono/位数、程序集和主要资源哈希。优先使用 `ilspycmd` 将 Managed 程序集反编译到 `resources/decompiled/`，使用 AssetStudio CLI 将主要资源批量导出为 JSON，并建立资源索引。已确认的 AssetStudio CLI 形式为：

```powershell
AssetStudio.CLI.exe <game-data-or-bundle> <output-dir> `
  --game Normal --export_type JSON --map_op Both --map_type JSON `
  --group_assets ByType
```

按以下优先级取得文本：

1. Python 解析结构化数据、ILSpy 代码和 AssetStudio JSON。
2. 为游戏编写小型、可测试的 Python 适配器，输出统一条目和剧情图。
3. UABEA/UABEA Next 用于人工核对、特殊序列化字段和资源修改。
4. BepInEx 运行时采集只负责补齐静态提取缺口，不应成为首要提取方法。

条目保留稳定 key、原文、类别、说话人、上下文、代码类型/方法/行号或资源文件/PathID/字段路径、剧情节点、占位符、富文本标签和提取器版本。生成的工作语料写入 `resources/work/entries.jsonl`，Paratranz 文件由脚本生成，不手工维护两套主数据。

## 剧情流程重建

从新游戏入口、章节/场景加载器、对话控制器、任务状态机、存档字段、旗标和结局条件开始，静态分析调用关系与数据引用。将对白、选择、事件、场景跳转、状态变化和结局建成有向图；边记录条件、目标和来源证据。

每项推断标记：

- `confirmed`：代码或资源存在直接稳定引用。
- `probable`：多条静态证据一致，但未运行验证。
- `hypothesis`：名称或邻近关系推测，必须人工确认。
- `runtime-confirmed`：已通过日志或存档路线验证。

PsychologHan 的 `story*` 方法、`dialogue_edge` 和 `choice_edge` 输出作为首个验收例；随后用运行时节点进入、选择、旗标、场景切换日志校正静态图。最终在 `localization/story/` 保存章节顺序、分支条件、角色关系、结局条件和人工覆盖清单，但不保存大段原文。

## Profile、术语与 Paratranz

每个游戏维护机器可读的 `project-profile.json` 和供译者使用的 `translation-guide.md`。Profile 记录游戏/Unity/TMP/BepInEx 版本、源目录约定、提取适配器、Paratranz CSV 列、补丁入口、字体策略、图片策略和 QA 门禁。

角色 profile 记录身份、关系、口癖、语气、称谓、禁用表达、路线阶段变化和少量例句。术语表记录源词、标准译名、领域、说明、允许变体和禁用译法。译文必须保持格式化占位符、TMP/UGUI 富文本标签、转义、换行语义和动态变量。相同原文在不同上下文允许使用不同稳定 key。

Paratranz 导出按剧情、UI、选项、物品、系统、图片等模块拆分。导入时校验 key、占位符、标签、空译文、意外原文回退和 CSV 编码；人工确认后才进入补丁资源。

## Mono BepInEx 补丁

Mono 游戏默认使用 BepInEx 5 的稳定版 Mono Windows x64 包，从官方 GitHub Releases 下载最新合适的 zip，解压到游戏可执行文件所在根目录。若目标实际为 32 位则改用 x86。首次启动仅验证 BepInEx 成功生成目录与日志，再部署插件。BepInEx 6 edge/pre-release 主要留给较新的 Unity IL2CPP 项目，第一版 skill 不处理。

补丁以游戏原生本地化或数据加载入口为优先，其次是特定控制器和显示组件，最后才是受控的原文查表兜底。避免无条件全局替换所有 `Text.text`/`TMP_Text.text`。推荐组件：

- `Plugin`：配置、兼容性检查、Harmony 注册和日志。
- `TranslationManager`/`ResourceLoader`：加载 CSV/JSON，标准化换行并查找稳定 key。
- 游戏专用 patcher：钩住真正的数据/显示入口。
- `MissingTextTracker`：开发模式记录未命中原文、对象路径、场景、调用上下文和次数。
- `FontManager`：UGUI/TMP 字体加载、fallback 与材质兼容修复。
- `ImageAudit`/`ImageReplacer`：图片资源定位与替换。

补丁项目通过本机 `Directory.Build.props` 或环境配置引用游戏 DLL，不提交游戏程序集。生成 `dist/` 时只包含 BepInEx 插件 DLL、译文、允许分发的字体/AssetBundle、配置和版本清单。

## 运行时缺口与人工验收

静态提取后仍必须人工带补丁游玩。开发审计模式对未命中文本去重、限流并记录：原文、规范化值、组件类型、场景、GameObject 层级、稳定 ID、首次/最后出现时间、次数和可选调用栈。人工将日志与截图、存档、复现步骤合并回提取适配器或补丁，不直接把所有日志原文当成正式语料。

验收路线覆盖主菜单、新游戏、存读档、设置、关键剧情、所有选择分支、失败路线和结局。检查漏译、错译、称谓、占位符、富文本、打字机效果、方框字、截断、溢出、换行、不同分辨率以及禁用补丁后的原版行为。P0/P1 必须清零才可发布。

## 图片文字与定位

图片按影响排序：

- P0：不翻译会阻断流程或导致关键选择错误，必须处理。
- P1：教程、主线线索、关键地图/菜单等重要信息，必须处理。
- P2：支线或低频氛围信息，有时间再处理。
- P3：装饰性、远景、品牌或无需翻译内容，默认跳过。

P 图第一版由人工完成。skill 生成静态图片索引，并提供 BepInEx 图片审计设计：按热键抓取当前可见 `Image`、`RawImage`、`SpriteRenderer` 及材质纹理，记录场景、层级、资源名、类型、尺寸、sprite rect、材质和实例 ID，可选截图与屏幕框选。Python 再用资源名、尺寸、PathID、sprite rect 和像素哈希把运行日志关联回 AssetStudio 索引。无法准确命中时显示调试覆盖层，由人工选择候选。替换时优先加载本地化 AssetBundle 或在特定对象上换 `Texture2D`/`Sprite`；SpriteAtlas、动画帧、视频和动态材质单独验收。

## TMP 字体策略

字体采用三层选择：

1. `unity-bundle`（默认）：skill 提供 Unity Editor batchmode 包装器和 Editor 脚本。用户指定接近游戏版本的 Unity Editor 与 TTF/OTF；脚本收集审校译文字符、创建 TMP FontAsset、设置静态/动态、多图集、fallback 和材质，构建 Windows AssetBundle并输出字符覆盖清单。
2. `runtime-ttf`（实验）：先用 ILSpy 检查目标 `Unity.TextMeshPro.dll` 是否存在接受字体文件路径的 `TMP_FontAsset.CreateFontAsset` 重载。存在时通过反射从补丁旁 TTF 创建动态字体；不存在或测试失败立即回退，不假定所有 TMP 版本支持。
3. `manual-unity`（兜底）：自动构建不兼容时，输出精确 Unity/TMP 版本、字符集、图集参数、bundle 名和插件期望路径，由人工在 Unity 中制作。

运行时验证必须检查全部必需字符、fallback 链、首次生成卡顿、多图集内存、TMP 材质/描边/Face Dilate、字号、行高和字体许可证。AssetStudio/UABEA 用于读写已有资源，不视作跨版本可靠的 TMP FontAsset 生成器。

## Skill 资源

skill 包含：

```text
localizing-unity-mono-games/
├─ SKILL.md
├─ agents/openai.yaml
├─ references/
│  ├─ project-layout.md
│  ├─ extraction-and-story-flow.md
│  ├─ paratranz-and-profiles.md
│  ├─ bepinex-mono-patch.md
│  ├─ runtime-qa-and-images.md
│  └─ tmp-fonts.md
├─ scripts/
│  ├─ scaffold_project.py
│  ├─ collect_font_characters.py
│  ├─ build_tmp_font_bundle.py
│  └─ validate_project.py
└─ assets/
   ├─ project-template/
   └─ tmp-font-builder/
```

SKILL.md 只保存决策顺序、硬性门禁和引用导航。详细参数、模板和兼容性说明进入 references；可重复且容易出错的机械步骤进入脚本或 assets。

## 验证

1. 使用不加载 skill 的基线场景记录常见遗漏，再用完成后的 skill 重跑相同场景。
2. 对 Python 脚本执行单元/临时目录测试和 `--help` 冒烟测试。
3. 运行 skill-creator 的 `quick_validate.py`，验证 frontmatter、命名和目录结构。
4. 用 PsychologHan 做前向测试：识别现有 ILSpy/AssetStudio 产物、说明现有 CSV/Python 的生成链、生成兼容的项目建议，并正确选择 Mono BepInEx 5、运行时缺口、图片和 TMP 策略。
5. 个人技能目录部署后从实际路径再次运行校验，并确认 `agents/openai.yaml` 与 SKILL.md 一致。
