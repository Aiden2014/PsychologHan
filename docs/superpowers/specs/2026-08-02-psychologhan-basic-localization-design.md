# PsychologHan 基础汉化设计

## 范围

本阶段以现有 `resources/extracted/*.csv` 为输入，完成可运行的基础汉化：界面常用文本、角色名、选项、物品提示、客户信息和结局文本。对白 CSV 保留英文原文，未提供可靠译文的条目由运行时回退英文；不重新提取、不覆盖 `scripts/extract_game_text.py`，也不修改 Steam 游戏目录。

## 数据边界

`localization/project-profile.json` 是项目决策唯一主文件；`localization/translation-guide.md`、`localization/glossary.csv`、`localization/characters/` 和 `localization/story/` 只保存可审阅的规则与故事元数据。原始导出、翻译工作集、来源清单和批准译文继续放在被忽略的 `resources/work/` 下。

新增工作集工具读取三列 CSV（key/original/translation），生成 `resources/work/entries.jsonl` 与按类别的审阅 CSV，记录原文哈希、占位符和来源文件。译文只按稳定 key 关联，不按原文反查；导入校验会拒绝未知 key、重复 key、原文变化、列数错误、空译文和占位符/换行被破坏的条目。

## 运行时接入

使用 BepInEx 5 Mono x64 与 Harmony。补丁只钩住已从 `GameManager.cs` 验证的 `addMe(int,string,int,Action)`、`addSpeaker(int,string,string,int,Action,string)`、`addOpt(int,long,string,int)`，在数据进入 `sitItems`/`optionItems` 前按 `category|||node|||speaker/option` 稳定 key 翻译。UI 采用受控的已知原文集合，在场景加载和 `updateSituationView` 后扫描可见 TMP 文本；未命中不改动原文。插件不替换所有 `Text.text`/`TMP_Text.text` 赋值，不安装字体或替换图片。

## 验证

自动验证包括项目布局/忽略策略、翻译工作集导入导出、占位符/换行保护、Python 提取器现有测试、C# Release 构建和包内容检查。运行时仍需在用户的游戏副本中先独立验证 BepInEx bootstrap，再验证插件加载、菜单/选项/结局与缺失译文回退；本阶段不宣称已完成手工路线验收。
