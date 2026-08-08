# Character Profile: ME (主角/心理治疗师)

Build this profile from the complete available source corpus for this character. Keep facts, inferences, and unknowns separate.

## Identity and role

- Canonical ID: `ME`
- Display name and aliases: "Doc" / 医生; 来访者叫他 "Doc"; 未给出本名
- Narrative role: 玩家扮演的心理治疗师, 第一人称叙事者。同时 `ME` 说话者也承载部分来访者场景的玩家视角(见 Evidence coverage)。
- Routes, chapters, and story stages: 办公室日常→五名来访者会谈→来访者接连遇袭→警方调查→雷蒙德对峙

## Evidence coverage

- Source files/modules: dialogue.csv (ME 说话者 784 行), choice.csv, client_info.csv (治疗师周记), ending.csv
- Analyzed lines: 784 行 ME 对话 + 相关 choice
- Covered routes/stages: 全部主线; 薇拉公寓会谈、阿什莉卡彭特路、乔的暴露练习、杰登屋顶练习、黛博拉商场
- Known gaps: 主角的具体背景(为何选择当心理治疗师)仅在 ME 内心独白中有零星线索

## Relationships and forms of address

| Other character | Relationship | Address used by this character | Address used toward this character | Story stage | Source key |
|---|---|---|---|---|---|
| 薇拉 Vera | 来访者/躯体变形障碍 | 薇拉 | Doc/医生 | 全程 | 10990 6528 |
| 阿什莉 Ashley | 来访者/疑似精神分裂 | 阿什莉 | Doc/医生 | 全程 | 18400 2442 |
| 杰登 Jaden | 来访者/恐高 | 杰登 | Doc/医生 | 全程 | 15400 5162 |
| 乔 Joe | 来访者/恐车 | 乔 | Doc/医生 | 全程 | 2000 5451 |
| 黛博拉 Deborah | 来访者/恐人群 | 黛博拉 | Doc/医生 | 全程 | 88110 2566 |
| 雷蒙德 Raymond | 前同学/反派 | 雷蒙德 | Doc/医生(讽刺) | 结尾 | 23134 10475 |
| 乔什 Josh | 同事/老同学 | 乔什 | — | 日常 | 11010 6572 |
| 香农 Shannon | 同事 | 香农 | — | 日常 | 11040 6577 |
| 老板 Boss | 上司 | 老板 | — | 日常 | 11050 6579 |
| 杰克逊 Det. Jackson | 办案警探 | 侦探 | Doc/医生 | 调查 | 15650 5243 |
| 田中警官 Sgt. Tanaka | 办案警佐 | 田中警官 | — | 调查 | 15652 5244 |

## Overall character assessment

### Observed

Record only facts, actions, and experiences directly supported by source text.

| Statement | Source key | Route/stage |
|---|---|---|
| 主角是执业心理治疗师, 在一家小公司工作, 办公室里有会谈室 | 11070 6583, 11040 6577 | 日常 |
| 同时负责五名来访者: 薇拉、阿什莉、杰登、乔、黛博拉 | 14511 8004, 501 6487 | 全程 |
| 会自我怀疑: "我分不清她是不是疯了" | 77779 2432 | 阿什莉线 |
| 会谈后常感到疲惫: "我累坏了" | 602 6702, 12602 7007 | 日常 |
| 在压力下会在内心胡思乱想 | 21157 2669 | 阿什莉线 |
| 对来访者尽力而为, 明知风险仍推进暴露治疗 | 18216 5689, 18217 5690 | 乔线 |
| 因阿什莉事件被警方传唤 | 33060 2735, 33062 2738 | 调查 |
| 最终被雷蒙德胁迫目睹其自杀 | 26642 10691 | 结尾 |

### Inferred

Cover personality, values, coping patterns, and decision tendencies. Do not infer a stable trait from one isolated line.

| Inference | Confidence | Evidence and source key | Alternative interpretation |
|---|---|---|---|
| 谨慎、共情、偏内向的执业者 | high | 多次"需要格外小心""我要格外小心她"(18401 2451); 会谈后疲惫(602 6702) | 也可能是被剧情压力逼成谨慎 |
| 自我怀疑倾向, 职业焦虑 | high | "我分不清""我不能排除"(77779 2432, 18402 2452) | 符合心理治疗师职业状态 |
| 对职业有理想与挫败并存 | medium | "我的工作很有意义, 但不太像我想象"(2301 7294, 2302 7295) | — |
| 有童年记忆(祖母家阁楼的画), 暗示内省人格 | low | 13583 7792, 13586 7798 | 可能只是场景设计 |

### Unknown/Conflicting

| Question or conflict | Conflicting evidence and source keys | Required follow-up |
|---|---|---|
| 主角是否为"真正的Doc(博士)" | Jackson 质疑其学历(15674 5256); 主角未明确回答 | 需运行时确认 |
| 主角与来访者的关系是否在职业边界内 | 乔什的越界是反面例子(11382 6633) | — |

## Motivations, fears, values, and contradictions

| Dimension | Assessment | Evidence status | Confidence | Source key |
|---|---|---|---|---|
| 动机 | 帮助来访者克服恐惧 | observed | high | 545 6524, 2301 7294 |
| 恐惧 | 无法判断来访者是否真疯; 对自身职业能力的怀疑 | inferred | high | 77779 2432, 13526 7757 |
| 价值观 | 职业道德、坦诚、对来访者负责 | observed | high | 35093 2949, 35332 3018 |
| 矛盾 | 想帮人却因阿什莉事件被警方追责 | observed | high | 33062 2738 |

## Character arc and route-stage changes

| Route/stage | Behavioral change | Speech change | Evidence status | Source key |
|---|---|---|---|---|
| 早期 | 平静、例行公事 | 简短、叙述性 | observed | 14100 2190 |
| 来访者接连遇害 | 焦虑加剧、开始调查 | 更急促、更多自问 | observed | 20603 9382, 24043 10351 |
| 结尾对峙 | 被胁迫、试图阻止雷蒙德 | 短促、恳求 | observed | 26665 10706, 26700 10743 |

## Language fingerprint

- Typical sentence length and complexity: 简短内心独白为主, 常一两句; 复杂时也多在反思
- Pauses, hesitation, repetition, correction, and emphasis: 常以 "……" 表达犹豫("我分不清……""除非她也……")
- Formality, politeness, slang, profanity, and euphemism: 作为治疗师用语正式; 内心会用口语("该死" 4010 3035)
- Recurring speech acts: 自问、评估、决定、安抚
- Changes by emotion, relationship, route, or story stage: 面对来访者克制专业, 独白时流露真实情绪

### Frequent words and recurring phrases

| Word or phrase | Count | Context/function | Source keys |
|---|---|---|---|
| "我该/我需要" | 高频 | 决定与行动计划 | 众多 |
| "……" | 高频 | 犹豫、思考 | 众多 |

## Chinese translation contract

- Target register and rhythm: 第一人称内心独白, 自然口语, 保持克制与反思感
- Pronouns, honorifics, and forms of address: 自称"我"; 对来访者称"你/您"视关系; 被称"医生"
- Preferred wording and allowed variants: "医生"统一; "来访者"统一
- Forbidden wording: 不要过度书面化或过度煽情
- Traits that must remain visible: 自我怀疑、职业克制、责任感
- Features that may be naturalized: 英式口语略去
- Line-length and layout constraints: 单句独白保持短句

## Few-shot examples

Use only human-reviewed translations.

| Source key | Route/stage | Original | Approved translation | Character feature demonstrated |
|---|---|---|---|---|
| 77779 2432 | 阿什莉线 | Phew. To be honest, I really can't tell if she IS going mad. | 呼。说实话, 我真的分不清她是不是疯了。 | 自我怀疑 |
| 602 6702 | 日常 | The clients I had today... Vera and Jaden. They are quite demanding. Actually, I'm exhausted. | 我今天接待的来访者……薇拉和杰登。他们都相当难应付。说实话, 我累坏了。 | 疲惫与克制 |

## Counterexamples

| Source key | Route/stage | Original | Rejected translation | Corrected translation | Why it is out of character |
|---|---|---|---|---|---|
| 600 6677 | 日常 | Strange how this train is always empty. But hey, more space for me.| 真奇怪，这趟火车总是空的。不过这样一来，我的空间更大。 | 奇怪，这趟地铁总是没人。不过我可以独享这片空间了。 | 是地铁不是火车，要结合上下文；“我的空间更大”太过于直白翻译了，应该是想表达独享空间的意思。 |
| 624 6723 | 日常 | Hey, wait... where am I? | 嘿，等等……我在哪儿？ | 哎，等等……我这是在哪？ | 这里语气词用“哎”好一些。 |
| 625 6724 | 日常 | Oh no. I'm high above ground level. I'm not holding on to anything. | 糟糕。我在远离地面的高处。我什么都没抓住。 | 完了。我怎么在高空？什么也抓不住。 | 这里原来的翻译太过于机翻了。 |
| 4088 3078 | 黛博拉线 | This is my chance to get out of here! | 这是我离开这里的机会！ | 我能离开这个鬼地方了！ | 口语化一些。 |

## Human review

- Reviewer:
- Review date:
- Unresolved decisions:
