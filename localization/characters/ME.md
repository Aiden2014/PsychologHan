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

- Target register and rhythm: 第一人称内心独白，自然口语，保持克制与反思感；优先直接写当下感受，不保留英文名词化句法
- Pronouns, honorifics, and forms of address: 自称"我"; 对来访者称"你/您"视关系; 被称"医生"
- Preferred wording and allowed variants: “医生”统一；“来访者”统一；休息或空闲可说“闲下来了”“难得有空”“不太习惯”；精神状态用“睡得踏实”“精神得很”“浑身有劲”等生活化表达；温和选项应承接对方刚说出的具体心事，如“听得出来，这件事让你很不好受”；意外发现自己有某种感受时可用“还真”“倒”自然落句；梦境中的恐惧要写成即时反应，梦境意象直接落成看见或感到的东西，不先说“想想看”；失落可用“心里不是滋味”等克制表达
- Forbidden wording: “有个下午可以休息”“有一个……可以……”等英文句法；避免“休息得很充分”“充满力量”“整个世界等着我探索”等抽象或宣传式措辞；不把 `To think...` 固定译成“想想看”，不保留“名为……的……”这类英语命名句架；不把共情性的 `I'm sorry that...` 直译为“很抱歉你……”；不把 `feel bad about` 一律写成“感觉不好”“难受”；不把 `actually` 一律译成“说实话”；不使用“汇报作业情况”一类行政口吻写私人独白；不把 `bully someone else` 生硬写成“去欺负别人”；不把场景落点 `So here I am` 固定译成“所以，我就这样”；不把表示敷衍让步的 `Whatever you say` 直译成“随你说”；不要过度书面化或过度煽情
- Traits that must remain visible: 自我怀疑、职业克制、责任感
- Features that may be naturalized: 英式口语可略去；英语习语和比喻应按当下心理作用重组为自然中文
- Line-length and layout constraints: 单句独白保持短句

## Few-shot examples

Use only human-reviewed translations.

| Source key | Route/stage | Original | Approved translation | Character feature demonstrated |
|---|---|---|---|---|
| 77779 2432 | 阿什莉线 | Phew. To be honest, I really can't tell if she IS going mad. | 呼……说真的，我也拿不准她是不是真要疯了。 | 自我怀疑；`to be honest` 在这里确实是坦白判断 |
| 602 6702 | 日常 | The clients I had today... Vera and Jaden. They are quite demanding. Actually, I'm exhausted. | 今天见的薇拉和杰登，都挺让人费心的。我已经累坏了。 | 直接承认疲惫，不给 `actually` 硬配“说实话” |
| 13390 7673 | 日常 | Feels strange to have an afternoon off. | 下午突然闲下来了，还真有点不习惯。 | 直接表达当下感受的自然独白 |
| 13583 7792 | 地铁回忆 | Ah, yes. It used to hang in my grandparents' house, just by the attic door, up on the second floor. | 想起来了。这幅画以前挂在我祖父母家，就在二楼阁楼门边。 | 用“想起来了”表达记忆被唤醒，不照搬语气词 |
| 14514 8009 | 来访者回顾 | Jaden, on the other hand, is somewhat of a loose cannon. I feel it may go either way with him. | 杰登就难说了。他像颗随时会爆的雷，治疗最后是好是坏，我心里也没底。 | 保留风险感，但写成克制、自然的即时判断 |
| 14515 8010 | 来访者回顾 | Tomorrow, he will report on his homework assignment. I'm actually looking forward to it. | 明天他会告诉我作业做得怎么样。我还真有点期待。 | `actually` 表示出乎自己意料的期待，不是“说实话” |
| 14517 8013 | 来访者回顾 | They are deeply troubled individuals, in more ways than one. | 她们俩的情况都很复杂，困扰她们的也远不止一件事。 | 用自然的整体判断承接薇拉和阿什莉，不逐词拆译习语 |
| 16533 8468 | 地铁噩梦 | Go and bully someone else... | 别再来找我麻烦了…… | 隔着猫眼看见老板后的恐惧与抗拒；直接写 ME 想摆脱针对的念头 |
| 16535-16537 8470-8474 | 梦醒 | Just a dream. [...] Need to stay professional. | 原来是场梦。这星期听了太多来访者的烦心事，连我都快被压垮了。得调整好状态，保持专业。 | 梦醒后迅速自我解释并收束情绪，符合职业克制 |
| 20340 9203 | 独自午餐 | So here I am. Lunching by myself. Feeling miserable. | 最后还是一个人来吃午饭了。心里真不是滋味。 | 乔什和香农都拒绝同行后的失落落点，简短而不煽情 |
| 20341 9212 | 独自午餐 | I'd do anything for some company right now. | 现在只要有人肯陪我吃顿饭就好。 | 把英语夸张收束成当下真实愿望 |
| 26660/26661 10704 | 雷蒙德地下室胁迫 | Whatever you say, Raymond. | 随便你。 | 被胁迫时不再争辩的冷淡让步，短促而克制 |
| 1000-1020 11038-11048 | 薇拉讲述的梦境开场 | I haven't slept this well in years. [...] Almost as if I'm NORMAL. | 都多少年没睡得这么踏实了。现在精神得很，浑身都有劲。 / 乍一看，还真像个正常人。 | 晨间自我鼓劲要像即时念头，同时保留“正常人”一词突然泄露出的自我否定 |
| 1250/1251 11298 | 薇拉第一次会谈 | I'm sorry that you feel bad. | 听得出来，这件事让你很不好受。 | 温和回应承接她的内疚，不虚构医生在为某件事道歉 |
| 621-623 6720-6721 | 地铁坠落梦境 | To think that people actually live [...] / To think that every morning [...] | 人们居然住在这种庞然大物里，还把它们叫作“楼房”。 / 每天早上，我从“家”这座钢铁笼子里出来，转头又钻进“单位”那座笼子。 | 直接铺出城市异化的意象，连续推进到坠落，不重复“想想看”打断梦境 |
| 628 6733 | 梦醒 | Must be Jaden's fear of heights that's finally getting to me. | 怪了。大概是杰登的恐高也传染给我了。 | 用半开玩笑的自我解释表现来访者情绪已经渗进 ME 的梦里 |
| 2138 2140 5520 | 乔初次会谈(选择) | This is why I love my job! Learning new things every day. | 所以我才爱干这行嘛！每天都能学到新东西。 | 玩笑式选择用“所以……嘛”“爱干这行”承接乔的出人意料，不用“这工作我就喜欢这一点”的直译 |
| 2175 2177 5568 | 乔初次会谈(选择) | You bet I will, grandpa. | 那当然，包在我身上！ | 把对62岁来访者的玩笑式称呼“grandpa”本土化为干脆的承诺，不硬译成“老爷子” |
| 12331 6859 | 本尼餐馆 | It tastes better with company, though. Next time I'll ask Shannon to join me. | 不过一个人吃总觉得差点意思。下次叫上香农一起。 | 独自吃饭的独白用“差点意思”写当下感受，不用“吃起来还是更香” |
| 12602 7007 | 地铁回家 | Still, I feel like I've been run over by a bus or something. I'm exhausted. | 可我还是累得快散架了。 | 疲惫夸张用中文惯用比喻“散架”，不照搬“被公交车碾过” |
| 12603 7008 | 地铁回家 | Sometimes I wish that I could be as relaxed as Josh seems to be with his clients. It seems so effortless to him. | 有时真羡慕乔什，他面对来访者总能那么放松，好像毫不费力。 | “毫不费力”是中文惯用说法，比“像是完全不费劲”自然 |
| 12620-12622 7018-7024 | 穿行车流的梦游式独白 | I move through the traffic. / Counting on the goodwill of others. / May I never lose that childish sense of trust. | 我穿行于车流之间。 / 仰赖着他人的善意。 / 愿我永不失去这份孩童般的信任。 | 三句连读是散文诗式独白：保持文言化的“于”“仰赖”“孩童般”“永不”，不写成日常口语 |
| 13098 7371 | 难得空闲却被叫去办公室 | Isn't it typical? Today, FOR ONCE, I have a whole day without clients booked. But my boss sees to it that I have to turn up at the office anyway. | 你说巧不巧？今天好不容易一整天都没约来访者，老板却还是非要我来办公室。 | 反讽的“Isn't it typical”用口语“你说巧不巧”承接，不用生硬的“偏偏这么巧” |
| 13099 7379 | 难得空闲却被叫去办公室 | He could easily have scheduled out meeting any other time. | 他明明可以改天再谈的。 | 简短口语的抱怨，“明明可以……的”比“明明随便换个时间……都行”自然 |
| 13166 13167 7457 | 老板问起香农(选择) | She seemed off-balance, somehow. | 她当时看起来有点不对劲。 | “seemed”是观察到的印象，中文保留“看起来”，比直接下判断自然 |
| 13199 13042 7521 | 老板比较乔什与香农(选择) | I'd say they rank about equal. | 我觉得他们业务能力不相上下。 | 老板问的是专业表现/谁更有能力，“不相上下”点明比较对象，不说空泛的“差不多” |
| 13500 7716 | 地铁回家 | I wonder why I never see Josh and Shannon together any more. | 不知道怎么回事，最近都没见乔什和香农在一块儿了。 | 疑惑用“不知道怎么回事”自然开头，“在一块儿”是口语说法 |
| 13502 7723 | 地铁回家 | Anyway, let's enjoy some peace and quiet. All alone in the subway cart. | 算了，正好享受一下清静。车厢里就我一个人。 | `Anyway` 收束思绪用“算了”，不固定译成“不管怎样”；“享受清静”比“享受一点安静”自然 |
| 26030 6104 | 办公室走廊 | Anyway, I have a session soon. I should go back to the office. | 行了，我待会儿还有会谈，该回办公室了。 | 同上：`Anyway` 是收尾填充词，用“行了”落地 |
| 13527 7758 | 地铁回家 | Anyway, I'll do my best. | 总之，我会尽力。 | 此处 `Anyway` 表“无论如何”（对上文不确定的收束），按 2143 惯例用“总之” |
| 14603 8087 | 地铁回家 | We should install a better security system. Someone should bring that up on the next meeting. | 我们该装一套更好的安保系统了。下次开会得要提一嘴。 | “提一嘴”是口语说法，比“提一提”自然 |
| 14466 2380 | 阿什莉会谈(选择) | He represents the very real threat of you turning psychotic. | 他代表着一个非常现实的威胁：你也有可能会精神失常。 | 分析型选项直接点明威胁（下文阿什莉“那才是我最大的恐惧”接得上），不用拗口的“你也许会出现精神病性症状” |
| 15386 8209 | 本尼餐馆与乔什(选择) | But you and me are HELPING people. That gives meaning. | 可咱们是在帮人啊，这才叫有意义。 | 熟人聊天里反驳“理想幻灭”用“帮人啊”“这才叫有意义”，不写“你和我是在帮助别人” |
| 88185 2611 | 阿什莉卡彭特路(选择) | Hearing such stories as a small child must have been terrifying! | 小小年纪就听这些，肯定吓坏了吧？ | 共情惊叹用“小小年纪”“肯定……吧”的口语收尾 |
| 88187 2613 | 阿什莉卡彭特路(选择) | It's very rare for two psychotic individuals to share the exact same delusions. | 两个精神失常的人出现完全相同的妄想，这种情况非常罕见。 | 分析型判断把长定语拆成“主句+这种情况非常罕见”，避免书面长句（阿什莉的“真的很少见吗？”接得上） |
| 18650-18655 7222-7230 | 绿衣人之梦游行 | So much happening all around you. So many dangers. / Before you know it... something hits you. / [...] / "Something mean. Clad in green." / The threat might come from INSIDE yourself, too. | 你身边发生着多少事，又潜伏着多少危险。 / 还没等你回过神……就会有什么东西撞上你。 / 也许是一辆车，也许是一个看似无害的路人。 / 甚至可能是某种来自太古的……邪恶。 / “凶恶之物，身披绿衣。”这句诗是谁写的来着？ / 威胁也可能来自你的内心——有什么东西，正把你往悬崖边缘拽。 | 梦游式散文诗：与 12620-12622 同一文体，用“多少……多少”“回过神”“看似无害”“来自太古”“悬崖边缘”保持念白节奏 |
| 19613 8806 | 地铁(怀疑老板) | I already know from Shannon that in reality, he isn't this Mr. Nice Guy that he pretends to be. | 香农已经跟我说了，他平时那副好好先生的样子，全是装出来的。 | 用“那副……的样子，全是装出来的”拆开关系从句，避免“他根本不是他……”的双“他” |
| 19624 8821 | 地铁(怀疑所有人) | This whole situation is a mess. | 这整件事都乱套了。 | “乱套了”比“乱成一团”更口语 |
| 20574 9355 | 噩梦惊醒 | Oh man... what a dream. | 天啊……这做的什么梦啊。 | 梦醒惊叹用“这做的什么梦啊” |
| 20575 9359 | 噩梦惊醒 | Falling asleep on the subway... That just won't do. I need to get a grip on myself. | 居然在地铁上睡着了……这可不行。我得打起精神来。 | “居然”“这可不行”“打起精神”是自然独白 |
| 20601 9377 | 地铁(被孤立) | I had to lunch by myself today. Josh and Shannon avoid me now. | 今天午饭又是我一个人吃的。乔什和香农现在都躲着我。 | “又是我一个人”带出连日孤立的落寞，比“只好”自然 |
| 20602 9381 | 地铁(被怀疑) | How can they suspect that I did bad things to my clients? | 他们怎么会怀疑我伤害过来访者？ | 简化为“伤害过”，去掉“做过……的事”的翻译腔 |

## Counterexamples

| Source key | Route/stage | Original | Rejected translation | Corrected translation | Why it is out of character |
|---|---|---|---|---|---|
| 600 6677 | 日常 | Strange how this train is always empty. But hey, more space for me.| 真奇怪，这趟火车总是空的。不过这样一来，我的空间更大。 | 奇怪，这趟地铁总是没人。不过我可以独享这片空间了。 | 是地铁不是火车，要结合上下文；“我的空间更大”太过于直白翻译了，应该是想表达独享空间的意思。 |
| 624 6723 | 日常 | Hey, wait... where am I? | 嘿，等等……我在哪儿？ | 哎，等等……我这是在哪？ | 这里语气词用“哎”好一些。 |
| 625 6724 | 日常 | Oh no. I'm high above ground level. I'm not holding on to anything. | 糟糕。我在远离地面的高处。我什么都没抓住。 | 完了。我怎么在高空？什么也抓不住。 | 这里原来的翻译太过于机翻了。 |
| 4088 3078 | 黛博拉线 | This is my chance to get out of here! | 这是我离开这里的机会！ | 我能离开这个鬼地方了！ | 口语化一些。 |
| 13390 7673 | 日常 | Feels strange to have an afternoon off. | 有个下午可以休息，感觉真奇怪。 | 下午突然闲下来了，还真有点不习惯。 | “有个下午可以休息”照搬英文结构，中文独白应直接写突然空闲后的不适应 |
| 13583 7792 | 地铁回忆 | Ah, yes. It used to hang in my grandparents' house, just by the attic door, up on the second floor. | 啊，对了。它以前挂在祖父母家二楼的阁楼门边。 | 想起来了。这幅画以前挂在我祖父母家，就在二楼阁楼门边。 | `Ah, yes` 在这里是突然认出旧物，不是汉语中的“啊，对了” |
| 14514 8009 | 来访者回顾 | Jaden, on the other hand, is somewhat of a loose cannon. I feel it may go either way with him. | 杰登则像一颗不定时炸弹。他的治疗可能成功，也可能彻底失控。 | 杰登就难说了。他像颗随时会爆的雷，治疗最后是好是坏，我心里也没底。 | “不定时炸弹”“可能成功或彻底失控”像译文标签和解释，不像 ME 当下拿不准的念头 |
| 14515 8010 | 来访者回顾 | Tomorrow, he will report on his homework assignment. I'm actually looking forward to it. | 明天他会汇报课后练习的情况。说实话，我还挺期待。 | 明天他会告诉我作业做得怎么样。我还真有点期待。 | “汇报……情况”过于行政化；`actually` 是意外强调，“说实话”反而虚构了一层坦白或辩解 |
| 14517 8013 | 来访者回顾 | They are deeply troubled individuals, in more ways than one. | 她们心里的问题都很深，而且不止一个。 | 她们俩的情况都很复杂，困扰她们的也远不止一件事。 | 逐词拼接 `deeply troubled` 与 `in more ways than one`，不符合中文心理评估式独白的表达习惯 |
| 16533 8468 | 地铁噩梦 | Go and bully someone else... | 去欺负别人吧…… | 别再来找我麻烦了…… | 旧译像在冷静指使老板另找受害者；源码画面和前两句表明 ME 是在噩梦里害怕老板又来针对自己 |
| 20340 9203 | 独自午餐 | So here I am. Lunching by myself. Feeling miserable. | 所以，我就这样一个人吃午饭。感觉糟透了。 | 最后还是一个人来吃午饭了。心里真不是滋味。 | “所以，我就这样”照搬英语落场结构；“感觉糟透了”也不像 ME 克制的即时独白 |
| 26660/26661 10704 | 雷蒙德地下室胁迫 | Whatever you say, Raymond. | 随你说，雷蒙德。 | 随便你。 | “随你说”是逐词拼接；中文在这种敷衍让步中直接说“随便你”即可，称呼也不必硬保留 |
| 1005-1020 11045-11048 | 薇拉讲述的梦境开场 | I feel so rested and strong. [...] There's a world to explore. | 感觉休息得很充分，也充满力量。 / 外面还有整个世界等着我探索。 | 现在精神得很，浑身都有劲。 / 外面还有那么多地方等着我去看看。 | 旧译用抽象状态词和宣传式句法拆译连续独白，既不像晨起自言自语，也削弱了后续照镜子前的虚假轻快感 |
| 1250/1251 11298 | 薇拉第一次会谈 | I'm sorry that you feel bad. | 很抱歉你感觉不好。 | 听得出来，这件事让你很不好受。 | 英语用 `sorry` 表达共情；中文照搬成“抱歉你……”既语序生硬，也错误暗示医生在道歉 |
| 621-623 6720-6721 | 地铁坠落梦境 | To think that [...] | 想想看，人们居然真的住在这些被称作“建筑”的怪物里。 / 想想看，每天早上，我离开名为“家”的钢铁牢笼，只为去另一个名为“工作”的钢铁牢笼。 | 人们居然住在这种庞然大物里，还把它们叫作“楼房”。 / 每天早上，我从“家”这座钢铁笼子里出来，转头又钻进“单位”那座笼子。 | 重复“想想看”和“名为……”把梦境独白写成翻译腔议论文，也让两个笼子的并行意象失去冲击力 |
| 628 6733 | 梦醒 | Must be Jaden's fear of heights that's finally getting to me. | 真有意思。一定是杰登的恐高症终于影响到我了。 | 怪了。大概是杰登的恐高也传染给我了。 | 旧译像在下诊断；这里是 ME 刚醒后带点自嘲的联想，应当轻一些、口语一些 |
| 12602 7007 | 地铁回家 | Still, I feel like I've been run over by a bus or something. I'm exhausted. | 可我还是累得像被公交车碾过一样。 | 可我还是累得快散架了。 | “像被公交车碾过”是英语比喻直译；中文疲惫夸张的惯用说法是“散架” |

## Human review

- Reviewer: 用户（针对主角休假独白、旧画回忆、杰登风险判断、来访者回顾、地铁坠落与地铁噩梦、独自午餐、雷蒙德地下室胁迫选项及薇拉梦境开场独白的直接反馈）
- Review date: 2026-08-15
- Unresolved decisions: 无；同类英语句法已纳入全局反向筛查
