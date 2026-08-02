# TMP 中文字体运行时方案

当前 Psycholog 版本的 TMP 资源没有中文字形，因此中文会显示为方框。插件现在会在启动时读取插件目录下的：

```text
BepInEx/plugins/fonts/南西油墨宋.ttf
```

插件优先读取你现有的 `BepInEx/plugins/fonts/南西油墨宋.ttf`，也接受插件目录内的 `fonts/南西油墨宋.ttf`。然后使用目标游戏的 TMP 3.0 API 创建动态 `TMP_FontAsset`，加入 `TMP_Settings.fallbackFontAssets`。这是针对当前 Unity 2021.3 Mono 版本验证过的局部 fallback，不修改游戏原字体、不拦截全局 `.text` 赋值。

## 已配置的字体映射

根据 AssetStudio 导出和运行时扫描结果，插件还会创建三个受控的 TMP 字体映射：

| 游戏原字体标识 | 映射字体 |
| --- | --- |
| TMP `faceInfo.familyName` 为 `Adler` | `fonts/南西油墨宋.ttf`（复用全局 fallback asset） |
| TMP 资源名以 `Typewriter_standard` 开头 | `fonts/朝華打字機.ttf` |
| TMP 资源名以 `GochiHand-Regular` 开头 | `fonts/JasonHandwriting1-Regular.ttf` |

映射在主菜单、设置/读档屏幕、剧情屏幕和客户端信息组件上应用；其他未验证的 TMP 对象保留原字体并继续使用中文 fallback。若映射字体缺失或创建失败，则保留原字体行为，不阻止游戏启动。

验证过的接口：

- `UnityEngine.Font(string name)`：从文件路径加载字体；
- `TMP_FontAsset.CreateFontAsset(Font, int, int, GlyphRenderMode, int, int, AtlasPopulationMode, bool)`；
- 目标程序集中的 `UnityEngine.TextCoreFontEngineModule.dll` 和 `UnityEngine.TextCoreTextEngineModule.dll`。

字体源文件来自项目现有的 `resources/fonts`；其再分发许可尚未由项目独立确认。验证器会把 fallback、Typewriter 映射字体和 GochiHand 手写映射字体复制到 dist，并在 `package-manifest.json` 中记录字体 hash。

如果字体文件缺失或运行时创建失败，插件会保留原字体行为并记录警告；这不会阻塞游戏启动。
