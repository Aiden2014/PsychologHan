# TMP 中文字体运行时方案

当前 Psycholog 版本的 TMP 资源没有中文字形，因此中文会显示为方框。插件现在会在启动时读取插件目录下的：

```text
BepInEx/plugins/PsychologHan/fonts/NotoSansSC-VF.ttf
```

然后使用目标游戏的 TMP 3.0 API 创建动态 `TMP_FontAsset`，加入 `TMP_Settings.fallbackFontAssets`。这是针对当前 Unity 2021.3 Mono 版本验证过的局部 fallback，不修改游戏原字体、不拦截全局 `.text` 赋值。

验证过的接口：

- `UnityEngine.Font(string name)`：从文件路径加载字体；
- `TMP_FontAsset.CreateFontAsset(Font, int, int, GlyphRenderMode, int, int, AtlasPopulationMode, bool)`；
- 目标程序集中的 `UnityEngine.TextCoreFontEngineModule.dll` 和 `UnityEngine.TextCoreTextEngineModule.dll`。

字体源文件为 Noto Sans SC Variable Font，按 SIL Open Font License 1.1 使用；分发时保留其上游许可证。验证器会把字体复制到 dist，并在 `package-manifest.json` 中记录字体 hash。

如果字体文件缺失或运行时创建失败，插件会保留原字体行为并记录警告；这不会阻塞游戏启动。
