# 运行时场景扫描

插件提供一个只读诊断键：默认按 `F8` 扫描当前 active scene 中的所有 `TMP_Text` 组件，并写入 BepInEx 日志。

配置文件中的键名是：

```ini
[Audit]
ScanCurrentSceneHotkey = F8
```

日志包含：

- 当前场景名和句柄；
- TMP 层级路径；
- `activeSelf`、`activeInHierarchy`、`enabled`；
- 当前 TMP 字体资产名；
- 当前文本内容（换行会转义，超长文本会截断）。

该扫描不会翻译、改写或销毁任何对象，也不会扫描 `Resources` 中的字体/预制体资产。按键后查看 `BepInEx/LogOutput.log`，搜索 `[PsychologHan][SceneScan]`。
