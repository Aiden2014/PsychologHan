# Unity Mono 通用 TMP UI Hook 设计

## 目标

为 `localizing-unity-mono-games` skill 增加一套可复用的静态与动态 UI 文本汉化模式，覆盖 `New Game`、`Settings` 等序列化在场景或 prefab 中、不会经过游戏对白数据入口的 `TextMeshProUGUI`/`TextMeshPro` 文本。

默认方案采用“场景扫描 + TMP 生命周期入队 + 特定控制器补丁”的混合模式。所有运行时入口共用同一个严格匹配的 `UiTextDispatcher`。不 Hook `TMP_Text.text` setter，不进行每帧全局扫描，不修改未命中审核清单的组件。

## 参考结论

- ProdigalHan 优先 Hook 游戏数据/显示入口，适合对白和选项，但不覆盖序列化 TMP 菜单。
- RhellHan 使用 `TextMeshPro.Awake` 和 `TextMeshProUGUI.OnEnable` 补静态 UI，证明生命周期入口可以覆盖这类文本；其原文直查和逐项缺失日志不作为通用模板照搬。
- SeafrogHan 使用全局 `TMP_Text.text` setter 与责任链覆盖动态文本，适用于其 IL2CPP/资源 CRC 约束；该方案拦截范围和运行频率过大，不作为 Mono skill 默认实现。
- SuperLoneSurvivorHan 的 setter Hook 目标是游戏自定义 `UIText`，并以对象上下文限定，说明 setter 方案只有在目标是游戏类型且范围可证明时才适合。

## Hook 选择顺序

1. 游戏原生本地化、数据加载或接近显示的控制器方法。
2. 特定控制器的 `Refresh`、`UpdateVisuals`、`OnEnable` 等方法，并在原方法写完文本后调用统一分发器。
3. 对序列化或动态实例化的 TMP UI，使用本设计的场景扫描和 TMP 生命周期入队。
4. `TMP_Text.text` setter 仅作为项目明确证明不可替代的最后手段；不加入默认模板。

前三层可以并存，但同一条目只保留一个权威 translation key。任何查找或运行时异常都保留当前文本。

## 组件边界

### `UiTextDispatcher`

接受 `TMP_Text`，因此同时覆盖 `TextMeshProUGUI` 和世界空间 `TextMeshPro`。它负责：

- 构建运行时定位上下文；
- 按审核后的 locator 和翻译表匹配；
- 检查原文、译文和歧义；
- 仅在安全匹配时赋值；
- 在文本安全命中后调用 `FontManager.ApplyFor(component, locator)`，使 UI 和对白显示层复用同一字体策略；
- 在 Development audit 模式将缺口交给有界、去重、限速的 `MissingTextTracker`。

它不实现字体加载、不遍历场景、不注册 Harmony，也不维护游戏专用 key 规则。当前文本已经等于目标译文时仍可调用一次幂等的 `ApplyFor`，用于处理“译文已写入、字体尚未应用”的入口顺序。

### `UiTextSceneScanner`

订阅 `SceneManager.sceneLoaded`。场景加载后遍历该场景的 root objects，并以 `GetComponentsInChildren<TMP_Text>(true)` 收集 active 与 inactive 组件。扫描结果只入队，不立即在加载回调中改文本。

每个场景只执行一次完整扫描；不使用 `Update` 或周期性全局轮询。

### `UiTextLifecyclePatches`

先检查目标游戏实际携带的 `Unity.TextMeshPro.dll`，再以 Harmony Postfix Hook 该版本可验证的生命周期入口；优先选择 `TextMeshProUGUI.OnEnable` 和 `TextMeshPro.OnEnable`，旧版或特殊实现可以改用已验证的 `Awake`。同一 TMP 类型默认只选一个入口，除非运行时证据证明需要两者。补丁只做空值检查并把组件交给有界队列，不执行翻译查找，也不写日志。

队列在帧末统一处理，使同帧的 `Awake`、`OnEnable`、`Start` 有机会先完成赋值。按 Unity instance ID 去重；处理后立即释放引用，禁止无界积累。

### 游戏专用控制器补丁

如果游戏在场景加载或 OnEnable 之后继续覆盖某个标签，项目必须 Hook 已验证的游戏控制器刷新方法，并在 Postfix 中调用同一 `UiTextDispatcher`。如果该入口已经能拿到最终显示的 `TMP_Text`，它也由 dispatcher 触发字体应用；不要在多个补丁中各写一套字体选择逻辑。不得用每帧重写文本掩盖覆盖顺序问题。

### `FontManager`

字体加载、TMP fallback、组件级替换、材质和字形覆盖由 `FontManager` 独立负责。它读取唯一权威配置 `localization/font-map.json`，按源英文字体、材质、语义角色和可选 locator 覆盖选择中文字体。文本成功替换但显示方框或空白属于字体问题，不能通过重复翻译 Hook 修复。

`FontManager` 延迟加载并缓存 AssetBundle/TMP 字体，不在每个组件命中时重复读取磁盘。它必须能在 `TMP_FontAsset.ReadFontAssetDefinition` 发生之前或之后工作：definition Hook 可以用于尽早安装源字体级 fallback，但 `ApplyFor` 仍需按需确保映射已应用，不能只依赖某个生命周期时序。

对白、选项和 UI 的文本来源可以不同，但最终只要能定位到显示组件，就使用同一个 `FontManager`。上游对白补丁只负责文本；字体在控制器 Postfix、TMP 生命周期或已验证的显示入口应用。

## 字体风格映射

### 设计原则

不同英文源字体往往承担不同视觉角色，不能把所有中文统一塞进一个 fallback。正式项目应保留并审核“英文源字体 → 中文目标字体”的对应关系，例如正文、对白、菜单粗体、标题像素体、描边按钮和世界空间文字可以分别映射。

映射优先级从高到低为：

1. 精确 `scene + hierarchy path + component type + component index` 的 locator 覆盖；
2. 源 `TMP_FontAsset.name + material.name`；
3. 源 `TMP_FontAsset.name`；
4. 语义角色默认值，例如 `dialogue`、`menu`、`title`、`button`、`world-space`；
5. 全局安全 fallback。

上一级配置缺失时才落到下一级。多个同级规则命中、配置引用不存在或目标字体加载失败时，不猜测字体：保留组件当前 font/material，并在 audit 模式记录一次有界诊断。

### `fallback` 与 `replace`

- `fallback`：保留组件的英文源 `TMP_FontAsset`，让拉丁字符继续使用原字体，并把指定中文字体加入 fallback 链。中文 glyph 实际由 fallback 字体及其材质渲染，不能假设会继承源字体材质；适合对白、正文和允许中英文字体分别渲染的控件。
- `replace`：把组件的 font 指向预构建的中文 TMP 字体资产，并按配置应用配套材质。适合像素标题、特殊字重、描边按钮等 fallback 无法可靠保留视觉效果的场景。

源字体级 `fallback` 会修改共享 `TMP_FontAsset.fallbackFontAssetTable`，因此会自然作用于所有使用该源字体的 UI 和对白组件。locator 覆盖不得向共享源字体追加一个只供单组件使用的 fallback，否则会污染其它上下文；组件级覆盖必须使用 `replace`，或引用预构建且只分配给该组件的变体字体资产。

同一 fallback 不得重复插入。插件记录自己追加到每个源字体的确切目标资产；卸载时只移除这些仍然存在的追加项，不清空游戏原有 fallback。对于组件级替换，首次修改前记录组件原 font/material，并在释放时尽力恢复；不得销毁游戏自带字体资产。

### 配置契约

`localization/font-map.json` 是唯一权威字体映射。机器本地 TTF/OTF 路径、Unity 工程路径和构建缓存不得写入该文件；它们保存在被忽略的本地构建配置中。建议的最小结构为：

```json
{
  "schema_version": 1,
  "fonts": [
    {
      "id": "body-regular",
      "source_font": "Original Body SDF",
      "source_material": null,
      "target_bundle": "zh-body.bundle",
      "target_asset": "Chinese Body SDF",
      "mode": "fallback",
      "roles": ["dialogue", "body"],
      "material": {
        "strategy": "preserve-source",
        "face_dilate": 0.0,
        "outline_width": 0.0
      },
      "license": {
        "id": "OFL-1.1",
        "redistributable": true
      },
      "notes": "对白和正文"
    },
    {
      "id": "menu-bold",
      "source_font": "Original Menu Bold SDF",
      "source_material": "Original Menu Outline",
      "target_bundle": "zh-menu.bundle",
      "target_asset": "Chinese Menu Bold SDF",
      "mode": "replace",
      "roles": ["menu", "button"],
      "material": {
        "strategy": "mapped",
        "face_dilate": 0.1,
        "outline_width": 0.2
      },
      "license": {
        "id": "OFL-1.1",
        "redistributable": true
      },
      "notes": "主菜单与描边按钮"
    }
  ],
  "overrides": [
    {
      "locator_key": "main-menu|||Canvas/Buttons/NewGame|||TextMeshProUGUI|||0",
      "font_id": "menu-bold"
    }
  ],
  "defaults": {
    "dialogue": "body-regular",
    "menu": "menu-bold",
    "global": "body-regular"
  }
}
```

`id`、bundle 内 asset 名和 locator key 必须唯一。`source_material` 为可选精确限定；角色必须来自审核后的 locator 或游戏专用显示入口，用于未建立源字体映射时的受控回退，不得仅凭字号、对象名或字形外观自动推断。`material.strategy` 至少支持 `preserve-source` 与 `mapped`：前者不主动改写组件材质，但 fallback glyph 仍使用 fallback 字体自身材质；后者使用目标字体资产的审核材质并允许显式记录 Face Dilate、Outline 等参数。运行时不得自动猜测材质。

每个目标字体还要记录许可证和是否允许随补丁分发。`redistributable` 不是 `true` 时，发布构建不得打包对应字体；这属于发布阻断项，而不是警告。

### 字形覆盖与生成方式

正式发布字体默认覆盖所有已审核中文译文、运行时缺口清单中确认需要显示的字符，以及项目要求的中文标点和必要拉丁字符。只有在能够用各路线文本清单证明覆盖完整时才允许字符子集构建。TTF/OTF 到 TMP Font Asset/AssetBundle 的生成仍走受版本约束的 Unity Editor 构建器；运行时从 TTF 直接生成 TMP 字体不作为可靠默认方案。

现有单字体构建器可以按 `font-map.json` 逐项调用和校验，不要求先实现复杂的批量构建系统。人工仍负责选择字体、确认授权、在 Unity 中调整 atlas、字重、基线、行高、描边和材质视觉效果。

### 中英文字体对照报告

从 `font-map.json` 生成一个只读对照报告到被忽略的 `reports/`，而不是另建第二份手写映射。报告至少包含：

- 英文源 font/material 与中文目标 font/material；
- 使用上下文、locator 覆盖和最终优先级来源；
- `fallback` 或 `replace` 模式；
- 中英文示例字符串；
- 已审核译文的字形覆盖结果；
- 基线、行高、字重、Face Dilate、Outline 等人工检查项；
- 字体许可证、可分发状态和备注；
- 可选的运行时截图路径。

报告用于人工 review，不回写运行时配置。截图和机器路径不得成为发布所需输入。

## 定位与翻译数据

Paratranz 继续使用三列 `key, original, translation`。运行时定位信息单独保存在受审查的 `localization/ui-locators.json`，避免把机器或提取工具细节塞入译文主表。

每个 locator 至少包含：

- translation key；
- scene 名；
- hierarchy path；
- component type；
- 同一 GameObject 上该类型的 component index；
- 预期英文原文；
- 可选 GameObject 名称回退。

静态提取先在忽略提交的工作区生成候选 locator。能从资源关系恢复 scene/path 的候选可以进入人工审查；只有审核后的 locator 才进入 `localization/ui-locators.json`。不能解析运行时路径的条目标记为 unresolved，不伪造精确定位。

## 匹配规则

分发器按以下顺序匹配，前一层安全命中后停止：

1. `scene + hierarchy path + component type + component index + original` 精确匹配。
2. `GameObject name + component type + original`，但只在审核数据中唯一时启用。
3. category 范围内的 original-only 匹配，但只在原文对应唯一译文时启用。

匹配使用规范化副本处理 CRLF/LF 和可配置的首尾空白，实际回退仍保留组件收到的原始字符串。富文本标签、占位符和换行必须通过导入校验，运行时不擅自重排。

幂等规则：

- 当前文本等于目标译文：跳过；
- 当前文本等于预期原文：替换；
- 当前文本既不是原文也不是译文：保留并在 audit 模式记录 context mismatch；
- 多个 locator 或多个译文同时命中：视为歧义并保留原文。

## 过滤与错误处理

默认跳过空文本、纯数字/符号、分辨率、输入框编辑值以及明确标记为动态计数器的条目。已经含中文不自动等于“已正确翻译”；只有等于该 key 的目标译文才按幂等命中处理。

Production 模式对未注册组件静默返回。Development audit 模式可以记录可见且疑似可翻译的未命中文本，但必须复用现有的去重、容量上限和时间窗口限速，并包含 scene、hierarchy path、object name、component type/index、original 和触发原因。

场景扫描、生命周期队列或单条翻译抛出异常时，捕获到组件边界，保留当前文本并记录一次有界诊断；不得阻断场景加载或 UI 激活。

## 模板与 skill 更新范围

- 在 BepInEx Mono 参考中加入 UI Hook 选择顺序、混合模式和禁止 setter 默认化的说明。
- 增加可适配的 `UiTextDispatcher.cs`、`UiTextSceneScanner.cs` 与 `UiTextLifecyclePatches.cs.example` 模板。
- 增加独立 `FontManager.cs.example`，展示映射优先级、fallback/replace、缓存、幂等和恢复边界。
- 增加 `localization/ui-locators.json` 示例及其最小 schema 说明。
- 增加 `localization/font-map.json` 示例与 schema 校验；脚手架只生成这一份权威字体映射。
- 更新 `Plugin.cs` 模板，展示初始化/释放场景订阅和帧末队列，而不硬编码游戏类型。
- 扩展 TMP 字体构建/校验脚本，使其能逐项读取字体映射，并增加由该映射生成 `reports/font-map.html` 或 Markdown 对照报告的脚本。
- 更新脚手架与技能测试，使上述模板随新项目生成。
- 保持游戏专用 controller patches 位于项目自己的 `GamePatches.cs`，不塞入通用 dispatcher。

## 验证

自动验证包括：

- locator 精确、唯一回退、歧义和 context mismatch；
- 已译文本幂等、缺失译文保留原文；
- inactive 组件进入场景扫描；
- 所选 TMP 生命周期方法确实存在于目标 DLL，且运行时能够命中；
- 生命周期队列按 instance ID 去重并在处理后清空；
- 模板不存在 `HarmonyPatch(typeof(TMP_Text), nameof(TMP_Text.text), MethodType.Setter)`；
- Production 未命中静默，Development 诊断有界；
- 字体规则遵循 locator、font+material、font、role、global 的固定优先级，同级歧义保留原状态；
- `fallback` 与 `replace` 作用域正确，locator 覆盖不会污染共享源字体；
- fallback 重复调用不重复插入，组件重复调用不丢失首次原始 font/material；
- bundle/asset 缺失时保留当前字体，卸载只撤销插件自己的变更；
- 每个可分发目标字体覆盖全部审核译文字符，许可证不允许分发时阻止发布打包；
- 字体对照报告完全由 `font-map.json` 生成，不存在第二份权威映射；
- skill 脚手架包含新模板且 `quick_validate.py` 通过。

前向测试要求新的 Codex 实例面对“菜单 New Game/Settings 不经过游戏数据入口”时选择混合 UI 模式，而不是只修改对白入口或安装全局 setter Hook。

人工运行验收至少覆盖：

- 初始主菜单的 `New Game`、`Settings`；
- 初始 inactive、打开后才激活的设置面板；
- 场景加载后动态实例化的 TMP 标签；
- 被游戏控制器再次刷新的标签；
- 相同英文在两个上下文具有不同译文；
- 未注册动态数字、输入值和富文本；
- 禁用或移除插件后恢复原版行为；
- 对白、正文、菜单、标题、描边按钮和世界空间文字按各自英文源字体选中预期中文字体；
- locator 字体覆盖只影响指定组件，不改变共享对白/正文 fallback；
- 中文字体的字形覆盖、基线、行高、字重、材质、换行、截断和不同分辨率布局；
- 发布包中的每个字体都有可核验且允许分发的许可证记录。

## 非目标

- 不为 IL2CPP 生成 interop 或 IDA 工作流。
- 不自动翻译未进入审核表的任意英文。
- 不通过每帧扫描或全局 setter 追求百分之百运行时覆盖。
- 不把字体实现、图片汉化或游戏专用业务规则合并进 UI dispatcher；dispatcher 只调用独立字体接口。
- 不在运行时把任意 TTF/OTF 自动转换成 TMP Font Asset，也不自动决定审美上的字体配对。
