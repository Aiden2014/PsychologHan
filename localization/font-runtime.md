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

字体源文件来自项目现有的 `resources/fonts`；其再分发许可尚未由项目独立确认。验证器会把 fallback、Typewriter 映射字体和 GochiHand 手写映射字体生成子集后复制到 dist，并在 `package-manifest.json` 中记录字体 hash。

## 发布时的字体子集化

构建发布包前，验证器会从 `resources/work/approved-translations/**/*.csv` 的全部字段，以及主补丁 C# 源文件中的字符串/字符字面量收集字符，写入忽略目录下的 `resources/work/font-characters.txt`。三个映射字体都会根据同一份字符集生成 TTF 子集后再复制到：

```text
dist/BepInEx/plugins/PsychologHan/fonts/
```

首次执行发布校验前安装字体子集化依赖：

```powershell
python -m pip install fonttools
python scripts/validate_localization.py `
  --project-root . `
  --translations resources/work/approved-translations `
  --profile localization/project-profile.json `
  --dist dist
```

`package-manifest.json` 的 `font_coverage` 会记录字符文件 hash、补丁源文件、每个字体的源/目标大小和源字体缺失字符。缺失字符不会被伪造为字形；发布前应结合运行时字体 fallback 和人工路线检查这些记录。

如果字体文件缺失或运行时创建失败，插件会保留原字体行为并记录警告；这不会阻塞游戏启动。
