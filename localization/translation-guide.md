# Translation Guide

Psycholog is a Chinese localization project built from managed code evidence and exported Unity assets.

## Source boundary

- Keep copied game corpus, extracted CSVs, and generated exports under ignored `resources/` paths.
- Keep only reviewable coordination files in `localization/`.
- Use `resources/Assembly-CSharp-decompiled` and the exported resource type directories as the evidence base.

## Approved translation categories

- `dialogue`
- `choice`
- `item`
- `character_name`
- `client_info`
- `ending`
- `ui`
- `image`

## CSV contract

- UTF-8 encoding.
- Three columns only: `key`, `original`, `translation`.
- Preserve the original text whenever a lookup fails.
- Do not invent a second master copy beside `resources/work/entries.jsonl`.

## Style rules

- Keep speaker identity stable across dialogue, choices, and UI labels.
- Prefer natural Chinese, but do not smooth away tense, uncertainty, or character voice.
- Preserve punctuation and line breaks when they carry meaning.
- Treat proper names as fixed glossary entries unless the story context clearly changes them.

## Dialogue naturalization rules (2026-08-10)

- Translate the line's conversational function, not its English word order. `Ah`, `Oh`, `Well`, `Yes`, and `I see` may become a context-specific response such as “想起来了”“原来如此”“这样啊”“嗯”，or disappear entirely.
- Reorder, split, or merge clauses whenever spoken Chinese requires it. Avoid calques such as “作为……我……”“如果……的话，我……”“有个……可以……”“我明白你的意思” unless that wording is genuinely natural in the scene.
- Render gratitude according to the relationship and action: “谢了，听我吐槽这么半天”“多谢关心”“辛苦了”“谢谢你愿意跟我说实话”. Do not default every `Thanks for...` to “谢谢你……”.
- Distinguish apology from empathy. In warm responses, `I'm sorry that...` often means “听得出来，这件事让你很不好受” rather than “很抱歉你……”. Resolve `feel bad about` from what follows: it may mean guilt or embarrassment (“过意不去”), not generic discomfort (“感觉不好”“难受”).
- Write the protagonist's inner monologue as an immediate thought, not translated narration: “下午突然闲下来了，还真有点不习惯”, not “有个下午可以休息，感觉真奇怪”.
- Read a run of inner-monologue lines as one emotional beat. Naturalize bodily state and self-encouragement as things a person would actually think—“睡得踏实”“精神得很”“浑身有劲”—instead of abstract calques such as “休息得很充分”“充满力量”; remove repeated subjects when Chinese can carry the thought without them.
- Determine what discourse markers do before translating them. In particular, `actually` often marks an unexpected feeling or contrast and should become “还真”“倒”“其实” or be omitted; use “说实话” only when the speaker is genuinely framing the statement as a confession or candid admission.
- Treat `you know`, `believe it or not`, and `you might say` as interactional cues, not fixed phrases. Omit them when they merely keep the listener engaged, or render their local function as “没想到吧”“说来也巧”“说起来”“算是……吧”; do not default to “你懂吗”“信不信由你”.
- Resolve `Whatever you say` from the speaker's stance. Cooperative acceptance can be “都听你的”, while dismissive capitulation can be “随便你”; never mechanically render it as “随你说”.
- Translate interjections from the emotion and relationship in the scene. `Oh hell` may become “天哪”“唉” or disappear; “见鬼” is reserved for a character and moment where that Chinese exclamation genuinely sounds natural.
- Preserve what a metaphor does in the scene, not necessarily its English wording. Rebuild idioms and figurative judgments in familiar Chinese imagery and syntax; for example, a volatile client can be “像颗不知道什么时候会爆的雷”, without importing the fixed label “不定时炸弹”.
- Localize puns as complete exchanges. Keep plot-bearing phrases stable, then rebuild the joke and every callback around a Chinese sound association; never translate only the punchline and leave the replies referring to an obsolete English pun.
- Resolve auxiliary echo questions and short replies from their exact predecessor and branch. `You do?`, `She did?`, `I have.`, and `Of course I did.` do not carry a complete meaning on their own; restore the omitted action in Chinese instead of defaulting to “是吗”“我有过” or guessing a new object.
- Resolve banter, commands, and mock celebration as speech acts rather than propositions. A flat `Hurray.` can be dry sarcasm, `I WAS going to...` can be a teasing escalation, and `Stop your ranting` should sound like an actual interruption (“别嚷嚷了”), not a report about ranting.
- Translate repeated lines against their branch outcome. The same `As always` can be trusting praise after a harder assignment (“你一向看得准”) or bitter compliance after being held back (“反正你总是对的”); inspect the next response, trust mutation, and preceding choice before reusing wording.
- Name locations by story function, not by the source token alone. In the office hub, `myRoom`, `joshRoom`, `shannonsRoom`, and `bossRoom` are offices; translate them as “办公室”. Keep “房间” for actual motel rooms, bedrooms, and homes.
- Decide whether sentence-initial `So` expresses cause, conclusion, resignation, or merely resumes the scene. Use “所以” only for a real causal link; alternatives include “最后”“到头来”“那么”“这么说”, or no connector at all.
- Treat `To think...`, `Think of it`, and `Just think about it` as emphasis frames, not mandatory invitations to “想想看”. In inner monologue, state the disturbing image directly; in explanation, replace the frame with the actual logic (“道理很简单”) or omit it. Likewise, do not preserve `on the one hand / on the other hand` when ordinary Chinese contrast already makes the relation clear.
- Reconstruct physical events across adjacent evidence. For accidents, distinguish “撞到”“压到/碾到”“撞死” and figurative impacts from the preceding motion, survival branch, injury description, and later summary; do not flatten every `hit` into “被撞到”.
- Keep role-specific rhythm: Ashley seeks reassurance in short, urgent bursts; Vera hesitates and circles around her anxiety; Jaden talks through panic and jokes defensively; Deborah is dry and sarcastic; Joe is warm and self-mocking; Shannon is direct and familiar; Josh is glib and self-important; Raymond is controlled and manipulative; Jackson is needling; Tanaka is concise and factual.
- Use Chinese double quotation marks `“……”` for ordinary quotations. Use single quotation marks only for a quote nested inside another quote. Translate a standalone `...` as `……`.
- Preserve placeholders and meaningful source line breaks exactly. Naturalization never authorizes changing a stable key, placeholder, or branch layout.
- Resolve ambiguous or internally inconsistent wording against the executable story flow: inspect the preceding node, destination node, state mutation, time slot, and later reaction. A dictionary meaning must not override what the scene demonstrably does.

### Human-reviewed naturalization anchors

| Source key | Literal or rejected direction | Approved translation | Decision |
|---|---|---|---|
| `5010|||5011|||4914` | “我就在你身边” | 我看得出你现在很慌，杰登。\n别怕，我陪着你。 | Translate reassurance as an action in the relationship. |
| `5010|||5014|||4917` | “如果需要，就闭上眼睛” | 杰登，先别说话，缓一缓。\n要是实在难受，就先闭上眼睛。 | State the condition that makes the advice useful. |
| `13175|||BOSS|||7462` | “我的朋友，我把你叫来……” | 今天叫你过来，就是想问问，你在这儿工作还顺不顺心。 | Omit phatic `my friend`; keep the boss's performative concern. |
| `13178|||BOSS|||7465` | Managerial English syntax | 所以我这个当老板的，就得听听你们各自的想法。人不一样，带法自然也不能一样。 | Rebuild the sentence around natural Chinese management talk. |
| `13321|||SHANNON|||7586` | “你去……的话，我跟你一起” | 也该吃午饭了。你要去本尼餐馆吗？一起去吧。 | Turn the conditional into a familiar invitation. |
| `13388|||SHANNON|||7671` | “谢谢你听我说” | 谢了，听我吐槽这么半天。明天见。 | Name what Shannon was actually doing: venting. |
| `13390|||ME|||7673` | “有个下午可以休息” | 下午突然闲下来了，还真有点不习惯。 | Write the felt experience directly. |
| `13583|||ME|||7792` | “啊，对了” | 想起来了。这幅画以前挂在我祖父母家，就在二楼阁楼门边。 | Translate recognition, not the interjection. |
| `1601|||VERA|||11337` | Clause-by-clause architectural description | 就拿地下室的窗户来说吧，有些居然直接被封死了……你敢信吗？他们大概是这么想的：“反正这个洞也用不上了，遮起来不就得了！” | Preserve Vera's anxious rambling in idiomatic Chinese. |
| `1602|||1603|||11339` | “是的，我明白你的意思” | 嗯，我懂你的意思了。 | Use a natural acknowledgement. |
| `14082|||SHANNON|||7096` | Treating `scram` as hostile “滚” | 给，钥匙拿好。赶紧去吧！ | The line returns to the office hub after Shannon hands over the key; this is a brisk send-off, unlike the hostile `Scram.` at `19242`. |
| `14256|||SHANNON|||7136` | “我把午饭睡过去了” | 糟了，我把下午的会谈睡过去了。得赶紧回办公室。先走了…… | The code places this after lunch and after Shannon ate from her lunch box; translate the story event, not the inconsistent surface noun. |
| `14514|||ME|||8009` | “杰登像一颗不定时炸弹” | 杰登就难说了。他像颗随时会爆的雷，治疗最后是好是坏，我心里也没底。 | Turn the English label into a natural, immediate judgment in ME's inner voice. |
| `14515|||ME|||8010` | “他会汇报课后练习的情况。说实话，我还挺期待” | 明天他会告诉我作业做得怎么样。我还真有点期待。 | `Actually` marks ME's mildly surprising anticipation, not a confession; avoid administrative wording for a private thought. |
| `14517|||ME|||8013` | “她们心里的问题都很深，而且不止一个” | 她们俩的情况都很复杂，困扰她们的也远不止一件事。 | Express the assessment as idiomatic Chinese instead of mapping `deeply troubled` and `in more ways than one` clause by clause. |
| `2200|||JOE|||5583` | A sentence-by-sentence rendering of the accident memory | 我小时候见过一场……车祸。那时我还小，真的就只是个孩子。我想，我应该没看到被撞的那个人。可那场景还是一直留在我脑子里。那天热得要命，警察在现场走来走去，却一个个都很平静。 | Rebuild the passage as a hesitant remembered account while preserving Joe's repetition and unreliable recall; “走来走去” is the spoken way to say `walked about`, not “来来回回”. |
| `2205|||JOE|||5587` | “见鬼……你懂吗？” | 天哪……我记得现场还站着另一个孩子，正舔着冰淇淋。可整个现场平静得根本不像出了车祸。没人慌，也没人哭，好像什么都没发生。 | Translate distress and the uncanny calm directly; the listener cue does not need a literal question. |
| `15355|||JOSH|||8175` | “信不信由你，我们俩在同一家事务所上班” | 挺好的！说来也巧，我们俩现在还在同一家公司上班。 | Here `believe it or not` marks coincidence, not a challenge to Raymond's credibility. |
| `15360|||RAYMOND|||8181` | “算是吧。我在另一个行业找到了自己的路” | 我嘛，后来发现自己更适合干别的。 | The line answers “你呢”; `Well` opens Raymond's answer and does not agree with a proposition. |
| `15814|||15816|||5362` and callbacks | “面部毛发？” followed by literal hair wording | “植点胡须”？ / 他说的肯定不是“植点胡须”。 | Keep “直面恐惧” as the plot clue, rebuild `face that fear / facial hair` as the Chinese near-sound joke `直面恐惧 / 植点胡须`, and update the whole callback chain. |
| `16533|||ME|||8468` | “去欺负别人吧……” | 别再来找我麻烦了…… | In the subway nightmare, ME sees the boss behind the peephole and wants him to stop targeting ME; translate the frightened plea, not the literal object. |
| `18356|||18357|||6023` | “你也注意到了？” | 你们在躲着对方？ | `You do?` echoes Shannon's immediately preceding “我和乔什在躲着对方”; it is surprise at their behavior, not a claim that Shannon noticed something. |
| `18380|||18380|||6047` | “我有过。” | 嗯，我也看出来了。 | `I have.` answers whether ME has seen signs of Josh's behavior; restore the omitted predicate from the question. |
| `18388|||SHANNON|||6063` | “你办公室里那个人” | 听你也这么觉得，我……就放心些了。我是说，之前偷偷进过你办公室的那个男人，我和乔什之间的事，还有……老板。 | Source node `14079` establishes that Shannon saw a strange man leave ME's locked office; make the callback identifiable in Chinese. |
| `20340|||ME|||9203` | “所以，我就这样一个人吃午饭。感觉糟透了” | 最后还是一个人来吃午饭了。心里真不是滋味。 | Both colleagues have declined lunch; `So here I am` lands on ME's resigned outcome rather than expressing a formal cause. |
| `30283|||DET. JACKSON|||9967` | “他的腿还是被撞到了” | 我说“差一点”，是因为很遗憾，他的双腿还是被车压到了，造成了几处骨折。 | Joe nearly jumped clear of the attacking car; the adjacent report and survival branch establish that the vehicle still caught/ran over his legs. |
| `26660|||26661|||10704` | “随你说，雷蒙德” | 随便你。 | Raymond is coercing ME into repeating his instructions; the choice is curt, dismissive capitulation, and the vocative is unnecessary in Chinese. |
| `1000-1020|||ME|||11038-11048` | “卧室看着真舒服 / 感觉休息得很充分，也充满力量 / 看看我 / 整个世界等着我探索” | 阳光照进卧室，感觉真不错。 / 都多少年没睡得这么踏实了。现在精神得很，浑身都有劲。 / 瞧瞧，我连上班的衣服都穿好了。 / 乍一看，还真像个正常人。 / 该出门了。外面还有那么多地方等着我去看看。 | These lines form the falsely upbeat opening of Vera's narrated dream. Translate them as a continuous run of natural morning self-talk while preserving the ironic “正常人” turn and the later collapse into mirror anxiety. |
| `1250|||1251-1252|||11298-11299` | “很抱歉你感觉不好 / 具体来说，是什么让你难受？” | 听得出来，这件事让你很不好受。 / 具体是哪件事，让你觉得过意不去？ | Vera has just admitted that something makes her feel guilty about treatment. The warm option acknowledges the burden; the analytical option asks what she feels guilty about. Neither branch uses generic “感觉不好”. |
| `5200|||JADEN|||4978` | “好啊，医生。我们到楼顶了。万岁” | 好了，医生。总算到楼顶了。可真棒。 | Jaden has just endured an elevator panic and immediately exaggerates the building's height; the clipped `Hurray.` is exhausted, defensive sarcasm rather than a literal cheer. |
| `5252|||5254-5255|||4997-4998` | “我本来正想让你跳上去 / 先别嚷了，听我告诉你该怎么做” | 我本来还想让你直接跳到栏杆上呢。 / 别嚷嚷了，接下来照我说的做。 | The first option deliberately scares Jaden as a joke; the second cuts off his panicked protest with a stern spoken command. |
| `5362|||JADEN|||5057` | “我还活着。去他的恐惧” | 我还活着。恐高算个屁。 | After completing the exposure step, Jaden turns his usual profanity into a burst of triumph; use his own colloquial register and name the fear at issue. |
| `5486/5491|||JADEN|||5114/5121` | Both rendered as “又说对了，一如既往” | 哇……也是。你一向看得准。 / 嗯……大概还是你说得对。反正你总是对的。 | The seventh-floor branch restores confidence; the third-floor branch makes him feel graded as a failure. Identical English wording carries opposite attitudes across the two outcomes. |
| `621-623|||ME|||6720-6721` | Repeating “想想看” and preserving `called HOME/WORK` noun structure | 人们居然住在这种庞然大物里，还把它们叫作“楼房”。 / 每天早上，我从“家”这座钢铁笼子里出来，转头又钻进“单位”那座笼子。 | This is a falling dream that turns the city into hostile architecture. State the images directly and preserve the parallel cages without narrating the English emphasis frame. |
| `628|||ME|||6733` | “一定是杰登的恐高症终于影响到我了” | 怪了。大概是杰登的恐高也传染给我了。 | On waking, ME half-jokingly attributes the dream to emotional carryover from Jaden; colloquial metaphor is more natural than an abstract causal diagnosis. |
| `2135-2137|||JOE|||5516-5517` | “想想看 / 另一方面 / 我勉强还能过” | 其实住在城里，我碰上车流的机会反而比城外少。道理很简单：住在郊区或乡下，没车根本哪儿也去不了。 / 可在城里，我需要的东西走一两条街基本都能找到。只要避开车流最密集的那几个时段，日子倒也过得下去。 | Joe is explaining a practical paradox in everyday terms. Rebuild the whole argument as spoken Chinese rather than translating its English discourse scaffolding. |
| `2071|||JOE|||5522` | “能让我在这车来车往的地方过得下去” | 另外，我还有几个小窍门，不然在这车来车往的地方，我可撑不住。 | Render `make my life bearable` as a colloquial conditional (“不然……我可撑不住”), and do not reuse the already-used “过得下去” in the same scene. |
| `2145|||JOE|||5551` | “我的日子一年比一年窄” | 因为这破事，我的生活圈子一年比一年小。 | `life has grown smaller` describes a contracted world; “生活圈子一年比一年小” is the natural spoken equivalent, “窄” is a calque. |
| `2150|||JOE|||5552` | “最糟的是” | 最让我难受的是，我儿子现在也有自己的家了，可我一次都没去看过他，因为……因为…… | Open an emotional disclosure with a natural spoken phrase; “最糟的是” is not how Chinese speakers lead this sentence. |
| `2185|||JOE|||5571` | “我现在还真庆幸自己来了” | 哈哈哈！没想到吧，我现在还真觉得来对了。那接下来怎么办？ | “庆幸” is a written register; spoken Chinese says “来对了”. |
| `2175|||2177|||5568` | “那当然，老爷子” | 那当然，包在我身上！ | The playful `grandpa` vocative has no natural Chinese equivalent for a therapist addressing a client; keep the jaunty promise and drop the imported address. |
| `12331|||ME|||6859` | “不过有人陪着，吃起来还是更香” | 不过一个人吃总觉得差点意思。下次叫上香农一起。 | Write the lone-lunch thought from ME's own side (“差点意思”), not a generic taste comparison. |
| `4100|||DEBORAH|||3093` | “好了，医生。……——可是你让我说的” | 喏，医生，这就是我最怕的情形——是你让我说的。 | `So there you have it ... As you asked` is a self-justifying presentation (“喏……是你让我说的”), not a contrast introduced by “可是”. |
| `4160|||4161|||3118` | “不过，你之所以来这儿，就是为了解决这个” | 不完全是。但你是来解决问题的。 | Keep the joking reply short; the “之所以……就是为了” frame is stilted in spoken give-and-take. |
| `4263|||DEBORAH|||3163` | “二十号在卡彭特路做第一次练习” | 你真觉得二十号去卡彭特路做第一次练习合适吗？ | Order the question by Chinese speech rhythm (time + place + action) instead of stacking modifiers around the verb. |
| `45414|||DEBORAH|||10954` | “悠着点，老爷子” | 悠着点，大叔。你跟我们可不是一代人。 | `gramps` as playful teasing lands as “大叔”; “老爷子” as a direct address carries a dialectal register Chinese speakers avoid here. |
| `12602|||ME|||7007` | “累得像被公交车碾过一样” | 可我还是累得快散架了。 | Exhaustion hyperbole must use an idiomatic Chinese metaphor (“散架”), not a calqued bus metaphor. |
| `12603|||ME|||7008` | “像是完全不费劲” | 有时真羡慕乔什，他面对来访者总能那么放松，好像毫不费力。 | “毫不费力” is the idiomatic phrasing; “像是完全不费劲” is a stiff clause-by-clause calque. |
| `12620-12622|||ME|||7018-7024` | “把自己交托给他人的善意 / 愿我永远别失去这份孩子般的信任” | 我穿行于车流之间。 / 仰赖着他人的善意。 / 愿我永不失去这份孩童般的信任。 | These three lines form a dreamlike prose-poem over the traffic march; keep a literary register (“于”“仰赖”“孩童般”“永不”) instead of everyday speech. |
| `13098|||ME|||7371` | “偏偏这么巧？” | 你说巧不巧？今天好不容易一整天都没约来访者，老板却还是非要我来办公室。 | `Isn't it typical?` is ironic complaint; the idiomatic spoken opener is “你说巧不巧”, not the stiff “偏偏这么巧”. |
| `13099|||ME|||7379` | “他明明随便换个时间和我谈都行” | 他明明可以改天再谈的。 | Keep the grumble short and spoken (“明明可以……的”); the stacked “随便换个时间……都行” reads like translated syntax. |
| `13166|||13167|||7457` | “她当时有点不对劲” | 她当时看起来有点不对劲。 | `seemed` is an observational impression; keep “看起来” instead of stating the judgment flatly. |
| `13185|||BOSS|||7479` | “听你这么说，……大家合得来很重要。” | 有你这句话，我对咱们今后共事就有信心了。公司人不多，大家合得来比什么都重要。 | Naturalize `Hearing that makes me...` and `it's important that...` into idiomatic management speech (“有你这句话”“比什么都重要”). |
| `13184|||BOSS|||7475` | “团队里的人相处融洽也很重要。” | 是吗？当然，客户始终是第一位的。不过团队里大家也得处得来。 | Same `get along` sentence pattern as 13185; use “处得来” instead of the flat “相处融洽也很重要”. |
| `13199|||13042|||7521` | “我觉得他们差不多。” | 我觉得他们业务能力不相上下。 | The boss asked about professional performance; restore the compared subject (“业务能力”“不相上下”) instead of a vague “差不多”. |
| `13386|||SHANNON|||7669` | “活像个糖被抢走的小孩。” | 活像个被抢了糖的小孩。 | Put the modifier before the noun in natural attributive order; the preceding “闹别扭” line makes the simile instantly clear. |
| `13500|||ME|||7716` | “最近怎么再没见过乔什和香农待在一起。” | 不知道怎么回事，最近都没见乔什和香农在一块儿了。 | Open the wondering with the spoken “不知道怎么回事” and use “在一块儿” for `together`. |
| `13502|||ME|||7723` | “不管怎样，享受一点安静吧。” | 算了，正好享受一下清静。车厢里就我一个人。 | `Anyway` closing a rumination lands as “算了”; “享受清静” is the idiomatic collocation, and “车厢里就我一个人” reads as speech. |
| `26030|||ME|||6104` | “不管怎样，我很快就有一场会谈。” | 行了，我待会儿还有会谈，该回办公室了。 | Same `Anyway` filler; “行了” closes the thought and returns to the schedule naturally. |
| `13527|||ME|||7758` | “不管怎样，我会尽力。” | 总之，我会尽力。 | Here `Anyway` means “in any case” (despite doubt); keep the connector as “总之”, matching 2143's established usage. |
| `14603|||ME|||8087` | “下次开会得提一提。” | 我们该装一套更好的安保系统了。下次开会得要提一嘴。 | “提一嘴” is the spoken form of raising a point; “该……了” fits the inner-monologue decision. |
| `14464|||14466|||2380` | “因为他让你想到一种确实存在的可能：你也许会出现精神病性症状。” | 他代表着一个非常现实的威胁：你也有可能会精神失常。 | The analytical option must state the threat directly so Ashley's reply “那才是我最大的恐惧” connects; avoid the stiff “确实存在的可能/出现……症状” frame. |
| `2250|||JOE|||5604` | “总之，我受够害怕了。……也想去哪儿都能自己走。” | 总之，我怕够了。我想去看看儿子和他的家人，想自己去哪儿就能去哪儿。 | Resolution lines: “怕够了” and “想去哪儿就能去哪儿” are spoken Chinese; “受够害怕”“自己走” are calques. |
| `15386|||8209` | “但你和我是在帮助别人。这让一切有了意义。” | 可咱们是在帮人啊，这才叫有意义。 | Banter between old colleagues: “咱们”“帮人啊”“这才叫有意义” sound like speech; “你和我是在帮助别人” is a word-by-word carry-over. |
| `15458|||BOSS|||5193` | “很遗憾要告诉你，……对吗？” | 我得告诉你个不好的消息。你的来访者……是杰登·汤普森吧？ | Breaking bad news: the boss hedges with a spoken opener and the “是……吧” confirmation, not the written “很遗憾要告诉你……对吗”. |
| `15465|||BOSS|||5198` | “出了这种事，我真的很遗憾。……再来找我一趟” | 这件事，我真的很遗憾。等你从医院回来，到我办公室来一趟，好吗？ | Anchor the apology to the specific news (“这件事”) and name the place (“到我办公室来一趟”). |
| `18240|||JOE|||5704` / `18245|||JOE|||5731` | “好，我们到了。” / “我们到了。我的老天。” | 好，到地方了。 / 到地方了。我的天啊。 | Arrival at the exposure site is “到地方了”; “我的天啊” beats “我的老天” as the natural exclamation. |
| `88185|||88185|||2611` | “你那么小就听这些故事，一定吓坏了。” | 小小年纪就听这些，肯定吓坏了吧？ | Empathetic exclamation uses the idiom “小小年纪” and the softener “肯定……吧”. |
| `88185|||88187|||2613` | “两名出现精神病性症状的人产生完全相同的妄想……” | 两个精神失常的人出现完全相同的妄想，这种情况非常罕见。 | Split the long clinical clause into a main sentence plus “这种情况非常罕见”; keep the spoken register that Ashley's “真的很少见吗？” replies to. |
| `88401|||ASHLEY|||2627` | “你能来看我，真好。” | 谢谢你来看我。 | Plain direct thanks matches Ashley's earnest, unvarnished voice; “你能来看我，真好” carries a translated nuance. |
| `88402|||ASHLEY|||2628` | “我想这样我就能回公寓了。” | 再陪我聊一会儿，好吗？聊完我应该就能回公寓了。反正我爸也快回来了。 | Write the request as chat (“聊完……”“反正……”); drop the stiff “我想这样我就能……” frame. |
| `18650-18655|||ME|||7222-7230` | “身边发生着这么多事……”“原始的……邪恶”“身披绿服” | 你身边发生着多少事，又潜伏着多少危险。 / 还没等你回过神……就会有什么东西撞上你。 / 也许是一辆车，也许是一个看似无害的路人。 / 甚至可能是某种来自太古的……邪恶。 / “凶恶之物，身披绿衣。”这句诗是谁写的来着？ / 威胁也可能来自你的内心——有什么东西，正把你往悬崖边缘拽。 | The `greenDream` march is the same prose-poem register as 12620-12622: use “多少……多少”“回过神”“看似无害”“来自太古”“绿衣”“悬崖边缘” and keep the quoted poem intact. |
| `19295|||JOSH|||8593` | “我从没想过自己会坐在警察面前……” | 我做梦也没想到，自己会坐在警察对面，被盘问同事的事……还有我自己的事。 | “做梦也没想到” is the spoken idiom for `I never thought`; “坐在警察对面” reads as speech. |
| `19296-19297|||JOSH|||8602-8603` | “咱俩都得打起精神……靠一个汉堡。” | 我看咱俩都该好好补补…… ……用一个汉堡。走吧。 | The ellipsis sets up the burger punchline: “补补……用一个汉堡” lands the joke in Chinese; “走吧” closes naturally. |
| `19359|||JOSH|||8668` / `19366|||JOSH|||8678` | “就已经死了两个” / “现在五个里已经没了两个” | 就已经有两个出事了。 / 现在五个里已经有两个出事了。 | In the two-saved branch, `lost` means the clients were harmed and are out of treatment, not dead; “出事了” keeps it unambiguous. |
| `19340 item 8643/8647/8651` | “不过，这不是很奇怪吗？短短几天里……” | 不过，你就没觉得不对劲？你两个来访者，前后没几天就都死了。 / ……一死一伤。 / ……都遭到了袭击。 | Dynamic Josh variants must match the dialogue base line 8639 (“你就没觉得不对劲？……前后没几天……”) instead of the stiff “这不是很奇怪吗”. |
| `1532 item 11507/11512` | “现在，请享用你的咖啡吧。” | 行了，喝你的咖啡吧。 | Raymond's sarcastic dismissal is “喝你的咖啡吧” (get back to your coffee), not a waiter's “请享用”. |
| `15700 item 5290` | Template sentence with floor expression | 昨晚九点左右，汤普森先生站在大学大楼 B2 区`{floor}`层的一扇开着的窗边，推测是在做某种“认知行为疗法”的练习。 | Keep the dynamic floor placeholder exactly; smooth the surrounding statement (“九点左右”“站在……窗边”“推测是在做……的练习”). |
| `1800|||VERA|||11519` | “一想到这事我就很不舒服” | 医生，我想了想……我觉得自己还没准备好。一想到那件事，我就浑身不自在。我还没准备好。 | Keep Vera's circling repetition (“还没准备好”), but write the discomfort as “浑身不自在”; “我刚才在想” is not how she opens. |
| `19613|||ME|||8806` | “他根本不是他装出来的那个好好先生” | 香农已经跟我说了，他平时那副好好先生的样子，全是装出来的。 | Break the relative clause with “那副……的样子，全是装出来的” to avoid the double-他 calque. |
| `19624|||ME|||8821` | “整件事乱成一团。” | 这整件事都乱套了。 | “乱套了” is the spoken way to say the situation is a mess. |
| `20220-20222|||BOSS|||8951-8953` | “公司声誉也不能不考虑 / 提这个很小气 / 从来没当成小事” | 公司的声誉，咱们也不能不管。 / 这种时候我还提什么声誉，显得挺小家子气的——可这关系到咱们所有人的饭碗。 / 员工过得好不好，对我来说可不是小事。 | The boss's meeting speech should read as spoken management talk: “不能不管”“提什么声誉”“对我来说可不是小事”“饭碗”. |
| `2732|||DEBORAH|||3378` / `2734|||DEBORAH|||3380` | “好。我去了。祝我好运。” / “没多久我就做到了！” | 行，我去了。祝我好运吧！ / 没花多长时间，我就做到了！ | Deborah's dry register: “行”“祝我好运吧”“没花多长时间” are spoken; “没多久我就做到了” is flat. |
| `20571-20572|||VERA|||9352-9353` | “别说了。我从一开始就知道。 / 你不是个好人，知道吗？” | 别解释了。我从一开始就知道。 / 你根本不是什么好人，你自己心里清楚吧？ | Dream accusation: “别解释了” blocks excuses; “根本不是什么好人”“心里清楚吧” carry the anger. |
| `20574|||ME|||9355` | “天啊……真是场怪梦。” | 天啊……这做的什么梦啊。 | Waking exclamation uses “这做的什么梦啊”. |
| `20575|||ME|||9359` | “在地铁上睡着……可不能这样。我得振作起来。” | 居然在地铁上睡着了……这可不行。我得打起精神来。 | “居然”“这可不行”“打起精神” are the natural inner-monologue forms. |
| `20601|||ME|||9377` | “今天我只好一个人吃午饭。” | 今天午饭又是我一个人吃的。乔什和香农现在都躲着我。 | “又是我一个人” carries the accumulating isolation better than “只好”. |
| `20602|||ME|||9381` | “他们怎么会怀疑我做过伤害来访者的事？” | 他们怎么会怀疑我伤害过来访者？ | Simplify to “伤害过” instead of the “做过……的事” frame. |
| `35005-35012` choices | “这周发生过什么……特别的事吗？” / “你现在来了。这才是重要的。” | 这周有没有发生什么……特别的事？ / 你现在来了，这才是最重要的。 | Session choices must read as the therapist speaking: natural word order (“有没有发生什么”), warm register (“守时很重要”), and complete rhythm. |
| `21418-21426|||ME|||9625-9633` | “跟了多久了？感觉都过去几小时了。/ 说真的，我几乎不知道它的存在。/ 像城市肌理上一道裂开的伤口。” | 跟了多久了？仿佛已经过去了好几个小时。 / 这片城区，我以前很少踏足。 / 其实，我几乎不知道世间还有这么个地方。 / 像是片工业区，又脏，又冷清。 / 像城市身上一道豁开的伤口。 | The tailing walk through the industrial district is the same prose-poem register as 12620-12622 and 18650-18655: “仿佛”“踏足”“世间还有这么个地方”“豁开的伤口”. |
| `21550|||ME|||9761` | “明早第一件事就是回藏身处” | 明早第一件事就是去那个藏身处 | The hideout belongs to the suspect, not ME: use “去”, never “回”. |
| `23211|||23211|||10526` | “当地游泳队在展示肌肉。” | 海边站着一长排人。 | The inkblot shows a long row of people at the seashore; describe the picture, don't invent a team. |
| `23240|||23240|||10557` | “随心所欲地排列物品。” | 像是被人随心所欲摆放的物品。 | Inkblot descriptions are stative scenes (“摆放的物品”), not active verbs (“排列”). |
| `23270|||23271|||10582` | “宣告所有人都将下地狱的死亡天使。” | 几个死亡天使在楼宇间穿行，宣告所有人都要下地狱。 | The picture shows angels flying between buildings; the description must match the visible scene. |
| `23280|||23282|||10591` / `23290|||23290|||10597` | “他们彼此都恨着对方。” / “在街上庆祝的骗子和叛徒。” | 他们互相憎恨。 / 骗子和叛徒在街上庆祝。 | Drop the redundant “彼此……对方”; write inkblot captions as sentences, not noun phrases. |
| `26500|||ME|||10602` | “没能操纵人格测试的结果” | 我费尽心思，还是没能蒙混过关。 | `game the tests` means fooling/getting past them: “蒙混过关”, not “操纵结果”. |
| `26632-26633|||RAYMOND|||10683-10684` | “除掉你，医生，没什么意思。/ 死掉也不是毫无意义。” | 我想过了，医生，除掉你没什么意思。 / 可除掉我自己，倒还有点意思。 | Keep the parallel “除掉你 / 除掉我自己……有点意思” that the original builds on. |
| `22464|||DEBORAH|||3505` | “你疯了。我不干了。” | 你疯了。我不治了。 | `I'm out` here means Deborah quits treatment: “我不治了”, not a job-quitting “我不干了”. |
| `22430|||DEBORAH|||3483` | “哎哟，你可真惨！” | 哎哟，可真够可怜的！ | Said after ME was held up by police, it is mocking sympathy, not genuine pity. |
| `45520|||MIKE|||11005` | “老规矩。大家听好。” | 照例还是有的。大家听好。 | `As always` answers “Any words of wisdom?” — “照例还是有的”, not a rule announcement. |
| `45464|||VERA|||10978` | “不……大概只是看起来像吧。” | 不……大概只是看着像在牵手吧。 | Restore the omitted object from Joe's “他们牵手了？”: “看着像在牵手”. |

## Naming and consistency decisions (2026-08-04)

Human-reviewed decisions that apply to all approved CSV files:

- The protagonist is always addressed as 医生 ("Doc"). 治疗师 is reserved for the profession (心理治疗师); as an address it is replaced by 医生.
- Police ranks: Detective Jackson is 杰克逊侦探; Sergeant Tanaka is 田中警官. Avoid 警佐/警长/警探/探长.
- Names are unified to the glossary: 杰登 (not 杰顿), 埃杰顿 (not 埃哲顿), 艾米莉 (not 艾米丽), 雷蒙德 (not 雷蒙), 乔 (not 约瑟夫), 香农, 乔什, 薇拉·米尔斯, 阿什莉·泰勒, 黛博拉·史密斯, 杰登·汤普森, 乔·埃杰顿.
- Proper nouns are fully localized: streets (华盛顿街, 门罗街, 卡彭特路, 枫树路, 长角街, 雪松大道), neighborhoods (河畔郊区, 雪松高地), the hospital (圣乔治医院), and JW大楼. CBT is translated 认知行为疗法; DSM is translated 精神障碍诊断与统计手册 (DSM-5 kept as DSM-5).
- Steam and the game title PSYCHOLOG remain as-is.
- Level-1 scene development labels (e.g. "Vera death message at office", "Deborah: mall/session") are internal scene titles and are intentionally left in English.
- Character profiles under localization/characters/ are the authoritative per-character voice contract; review them before polishing dialogue.

## Runtime and image policy

- Use BepInEx 5 stable Mono x64.
- Patch a verified localization or data seam first.
- Fall back to the original text or asset on every failure.
- Build TMP fonts with the bundle-first strategy.
- Replace images only after human-confirmed correlation.

## QA gate

Do not treat automated checks as enough on their own.

- Confirm menus and settings.
- Confirm save and load.
- Confirm the critical story and choice branches.
- Confirm failure routes and endings.
- Confirm original behavior with the plugin disabled.
- Ship only when P0 and P1 findings are both zero and a human signs off.
