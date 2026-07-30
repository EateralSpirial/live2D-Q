# 04｜图片资产清单与生成规格

本文定义交给本地 Codex及图像生成子代理的完整资产任务。机器可读版本位于 [`config/character-assets.yaml`](../config/character-assets.yaml)。

## 1. 唯一主参考

- 本地正式源文件：`assets/reference/local/character_reference_source.png`；
- GitHub 缩略预览：[`assets/reference/character_reference_preview.webp`](../assets/reference/character_reference_preview.webp)；
- 开始 Phase 1 前必须执行 `python scripts/check_reference.py`；
- 原图：1254×1254，粉色背景已与人物合并；
- 目标运行时画布：**2048×2048 RGBA**；
- 目标角色位置、比例和姿势：严格参考主图；
- 运行时背景：完全透明；
- 主图中的装饰星星：拆为独立 FX；
- 主图只做参考，不直接作为运行时图层。

## 2. 通用输出规则

所有资产均必须：

1. 2048×2048；
2. RGBA、sRGB、straight alpha；
3. 透明背景；
4. 与其他层完全同坐标，不裁切、不重新居中；
5. 不含不属于本层的相邻部件；
6. 在被遮挡方向补画足够区域；
7. 透明边缘无粉色背景残留；
8. 文件名使用 ASCII 小写、下划线；
9. 生成记录包含来源、工具、提示词/遮罩、尺寸和校验结果；
10. 默认合成时视觉上恢复主图中的角色。

建议目录：

```text
assets/generated/character_v1/
├─ hair/
├─ face/
├─ eyes/
├─ mouth/
├─ body/
├─ headwear/
├─ fx/
├─ poses/
├─ previews/
└─ generation-records/
```

## 3. 优先级

- **P0**：MVP 必须；缺少则不允许进入绑定阶段；
- **P1**：正式直播建议；允许在 MVP 后补齐；
- **P2**：可选增强，不得拖延主链路。

## 4. 遮挡补全规则

- 脸部必须在刘海下完整补画到头部轮廓；
- 后发必须在脸、前发和身体后方连续；
- 刘海根部需延伸到头顶发帽下方；
- 眼白、虹膜和睫毛需在眼睑下方保留合理余量；
- 颈部/衣领需在头部和饰品下方补全；
- 袖子和披风需要在手、腰带和身体下方补全；
- 金色边线在分层接缝处至少有 8–24 px 重叠；
- 大幅补画区域要在 `generation-records` 中标记，方便人工检查。

## 5. 绘制顺序概览

```text
后方装饰星
→ 最远后发
→ 后发分束
→ 下半身/鞋
→ 后侧披袖
→ 躯干/袖/手
→ 腰带与胸饰
→ 脸/耳
→ 眼白/虹膜/睫毛/眉/嘴
→ 前发发帽与刘海分束
→ 额饰
→ 前景光效与情绪 FX
```

精确顺序以 YAML 的 `draw_order` 为准。

---

# 6. 资产清单

## A. 后发：重点物理组

| ID | 优先级 | 文件 | 内容与生成要求 | 绑定/物理 |
|---|---:|---|---|---|
| `hair.back.far` | P0 | `hair/hair_back_far.png` | 头部后方最远的粉色发量底层，覆盖完整后脑和肩后区域；被身体遮挡处补全；不含前发和脸 | 慢速、大阻尼、最小幅度 |
| `hair.back.left_outer` | P0 | `hair/hair_back_left_outer.png` | 画面左侧最外层后发，包含外翻发梢；根部延伸到头顶内部 | 独立双弹簧，外梢较软 |
| `hair.back.left_inner` | P0 | `hair/hair_back_left_inner.png` | 画面左侧内层后发，位于外层和脸之间 | 中等幅度 |
| `hair.back.center` | P0 | `hair/hair_back_center.png` | 后脑中央和颈后发束，补全至肩后 | 稳定、低幅度 |
| `hair.back.right_inner` | P0 | `hair/hair_back_right_inner.png` | 画面右侧内层后发 | 中等幅度 |
| `hair.back.right_outer` | P0 | `hair/hair_back_right_outer.png` | 画面右侧最外层后发和外翻发梢 | 独立双弹簧，外梢较软 |
| `hair.side.left_back` | P0 | `hair/hair_side_left_back.png` | 贴近脸侧、但位于前刘海之后的左侧发束 | 轻微跟头 + 独立摆动 |
| `hair.side.right_back` | P0 | `hair/hair_side_right_back.png` | 贴近脸侧、但位于前刘海之后的右侧发束 | 轻微跟头 + 独立摆动 |

> 每个后发层都应保留足够发量。不能把一侧所有发丝塞进一张薄片，否则物理时会像纸片摆动。

## B. 身体与服装：少量动作即可

| ID | 优先级 | 文件 | 内容与生成要求 | 绑定/用途 |
|---|---:|---|---|---|
| `body.lower` | P0 | `body/body_lower.png` | 白色下摆、短腿与袜装基础，不含鞋、腰带和披袖 | 与躯干轻微呼吸 |
| `foot.left` | P0 | `body/foot_left.png` | 画面左脚深蓝短靴，含金色星装饰 | 轻微跟随身体 |
| `foot.right` | P0 | `body/foot_right.png` | 画面右脚深蓝短靴，含金色星装饰 | 轻微跟随身体 |
| `cape.left_back` | P0 | `body/cape_left_back.png` | 画面左侧青绿蓝紫星云宽袖/披风，含金色边线；不含手 | 中等物理，音量/语速联动 |
| `cape.right_back` | P0 | `body/cape_right_back.png` | 画面右侧星云宽袖/披风，含金色边线；不含手 | 中等物理，音量/语速联动 |
| `body.core` | P0 | `body/body_core.png` | 躯干、脖子、白色内衬和深蓝领口的连续基础；不含手臂、披袖、腰带、胸饰 | 呼吸和身体倾斜；建议脖子与躯干合并避免接缝 |
| `sleeve.left` | P0 | `body/sleeve_left.png` | 画面左侧白色内袖/肩部结构，位于星云披袖前或内侧 | 跟随左臂和躯干 |
| `sleeve.right` | P0 | `body/sleeve_right.png` | 画面右侧白色内袖/肩部结构 | 跟随右臂和躯干 |
| `hand.left.present` | P0 | `body/hand_left_present.png` | 主图画面左侧抬起、掌心向上的完整手；补全与袖口重叠部分 | 默认展示姿势 |
| `hand.right.idle` | P0 | `body/hand_right_idle.png` | 主图画面右侧自然放下的手 | 默认姿势 |
| `belt.base` | P0 | `body/belt_base.png` | 深蓝腰带和金色结构，不含中心星盘 | 跟随躯干 |
| `belt.medallion` | P0 | `body/belt_medallion.png` | 金色圆环星盘与粉紫星心 | 可轻微旋转/发光 |
| `collar` | P0 | `body/collar.png` | 深蓝高领/颈部装饰的前层 | 跟随头/躯干中间值 |
| `chest.pendant` | P0 | `body/chest_pendant.png` | 领口下方蓝色小吊坠与金线 | 独立轻摆 |
| `hand.left.idle` | P1 | `poses/hand_left_idle.png` | 左手放下的替代姿势，袖口衔接保持一致 | 手势切换 |
| `hand.right.wave` | P1 | `poses/hand_right_wave.png` | 右手抬起挥手的替代姿势 | 手势切换/热键 |
| `hand.right.point` | P2 | `poses/hand_right_point.png` | 右手轻指向侧面的姿势，保持克制 | 演示/讲解动作 |

## C. 脸部基础

| ID | 优先级 | 文件 | 内容与生成要求 | 绑定/用途 |
|---|---:|---|---|---|
| `face.base` | P0 | `face/face_base.png` | 完整脸部肤色底图，不含眼、眉、鼻、嘴、刘海；刘海下和脸侧需补全 | 头部基准和锚点 |
| `ear.left` | P0 | `face/ear_left.png` | 画面左耳，保持主图简化风格；被头发遮挡处补全 | 跟随头部 |
| `ear.right` | P0 | `face/ear_right.png` | 画面右耳 | 跟随头部 |
| `nose` | P0 | `face/nose.png` | 主图极简小鼻线/阴影，不增加写实结构 | 跟随脸 |
| `face.blush` | P1 | `face/face_blush.png` | 默认非常淡的双颊粉色，可调透明度 | happy/embarrassed |
| `face.shadow_serious` | P1 | `face/face_shadow_serious.png` | 额头/眼上极淡的认真阴影，不改变肤色整体 | serious/angry 低强度 |
| `face.shadow_tired` | P1 | `face/face_shadow_tired.png` | 眼下轻微困倦阴影 | tired |
| `face.blush_strong` | P2 | `fx/face_blush_strong.png` | 比默认腮红更明显但仍克制 | embarrassed/笑场 |

## D. 眼睛、眉毛和视线：重点表情组

| ID | 优先级 | 文件 | 内容与生成要求 | 绑定/用途 |
|---|---:|---|---|---|
| `eye.white.left` | P0 | `eyes/eye_white_left.png` | 左白眼完整形状，在睫毛和眼睑下补全 | 眼睛开合遮罩 |
| `eye.white.right` | P0 | `eyes/eye_white_right.png` | 右白眼完整形状 | 同上 |
| `eye.iris.left` | P0 | `eyes/eye_iris_left.png` | 左虹膜与瞳孔主体，保留深红/紫/蓝层次，不含高光 | 视线和瞳孔缩放 |
| `eye.iris.right` | P0 | `eyes/eye_iris_right.png` | 右虹膜与瞳孔主体 | 视线和瞳孔缩放 |
| `eye.highlight.left` | P0 | `eyes/eye_highlight_left.png` | 左眼所有白色/粉蓝高光，独立于虹膜 | 闪烁、情绪亮度 |
| `eye.highlight.right` | P0 | `eyes/eye_highlight_right.png` | 右眼高光 | 同上 |
| `eye.lash.left` | P0 | `eyes/eye_lash_left.png` | 左上睫毛与眼线，不含眼白/虹膜 | 眼睑变形 |
| `eye.lash.right` | P0 | `eyes/eye_lash_right.png` | 右上睫毛与眼线 | 同上 |
| `eye.closed.left` | P0 | `eyes/eye_closed_left.png` | 左闭眼线，位置与睁眼中心一致 | 眨眼 |
| `eye.closed.right` | P0 | `eyes/eye_closed_right.png` | 右闭眼线 | 眨眼 |
| `eye.half.left` | P1 | `eyes/eye_half_left.png` | 左半睁眼，适合思考/吐槽/疲惫 | 表情差分 |
| `eye.half.right` | P1 | `eyes/eye_half_right.png` | 右半睁眼 | 表情差分 |
| `eye.smile.left` | P1 | `eyes/eye_smile_left.png` | 左笑眼弧线 | happy/laughter |
| `eye.smile.right` | P1 | `eyes/eye_smile_right.png` | 右笑眼弧线 | happy/laughter |
| `eye.surprised.left` | P1 | `eyes/eye_surprised_left.png` | 左眼略放大的睁眼差分，不改变中心 | surprised |
| `eye.surprised.right` | P1 | `eyes/eye_surprised_right.png` | 右眼略放大 | surprised |
| `brow.left` | P0 | `eyes/brow_left.png` | 左眉基础线条 | 位移、旋转、弯曲 |
| `brow.right` | P0 | `eyes/brow_right.png` | 右眉基础线条 | 位移、旋转、弯曲 |

> 左右眼必须独立导出。即使兼容 PSD 会将左右合并，原生 manifest 仍保留单独资产。

## E. 多视素嘴型：低延迟口型核心

每张嘴型都是**完整嘴部 sprite**，中心、基线、宽度和脸部坐标必须一致。不能每次重新生成整个脸。

| ID | 优先级 | 文件 | 内容与生成要求 | 绑定/用途 |
|---|---:|---|---|---|
| `mouth.rest` | P0 | `mouth/mouth_rest.png` | 默认小微笑/自然闭口 | 静音、neutral |
| `mouth.mbp` | P0 | `mouth/mouth_mbp.png` | 双唇明确闭合，适合 b/p/m；可比 rest 更紧 | MBP |
| `mouth.a` | P0 | `mouth/mouth_a.png` | 纵向较大、自然“啊”口；含简化口腔、舌/牙但不过度写实 | A |
| `mouth.i` | P0 | `mouth/mouth_i.png` | 横向较扁、嘴角略展开 | I |
| `mouth.u` | P0 | `mouth/mouth_u.png` | 小而圆、前突的“乌”口 | U/ü 混合 |
| `mouth.e` | P0 | `mouth/mouth_e.png` | 中等开口、横向略宽 | E |
| `mouth.o` | P0 | `mouth/mouth_o.png` | 比 U 更大更圆 | O |
| `mouth.fv` | P1 | `mouth/mouth_fv.png` | 下唇轻触上齿的简化形态 | FV |
| `mouth.smile` | P1 | `mouth/mouth_smile.png` | 更明显但克制的微笑，可作为情绪偏置 | happy |
| `mouth.tense` | P1 | `mouth/mouth_tense.png` | 轻微抿嘴/严肃形态 | serious/angry |
| `mouth.sad` | P1 | `mouth/mouth_sad.png` | 嘴角轻微向下，避免夸张哭脸 | sad/tired |

建议渲染参数：

- `mouthOpen` 控制整体开合和下颌微移；
- `viseme.*` 控制上述 sprite 权重；
- `emotionSmile` 与 `emotionTense` 作为偏置；
- 只混合前两个主导视素，避免多层半透明造成重影。

## F. 前发与刘海：重点物理组

| ID | 优先级 | 文件 | 内容与生成要求 | 绑定/物理 |
|---|---:|---|---|---|
| `hair.front.cap` | P0 | `hair/hair_front_cap.png` | 头顶前层发帽和主轮廓，不含可独立摆动的刘海尖端 | 头部刚性跟随，轻微形变 |
| `hair.bang.left_outer` | P0 | `hair/hair_bang_left_outer.png` | 最左外侧刘海束及外翻尖端 | 独立摆动 |
| `hair.bang.left_inner` | P0 | `hair/hair_bang_left_inner.png` | 左内侧刘海束 | 独立摆动 |
| `hair.bang.center_left` | P0 | `hair/hair_bang_center_left.png` | 中央偏左、靠近中央星饰的刘海束 | 小幅摆动，防额饰穿插 |
| `hair.bang.center` | P0 | `hair/hair_bang_center.png` | 中央垂落发束，位于眉间上方 | 低幅度、较高阻尼 |
| `hair.bang.center_right` | P0 | `hair/hair_bang_center_right.png` | 中央偏右刘海束 | 小幅摆动 |
| `hair.bang.right_inner` | P0 | `hair/hair_bang_right_inner.png` | 右内侧刘海束 | 独立摆动 |
| `hair.bang.right_outer` | P0 | `hair/hair_bang_right_outer.png` | 最右外侧刘海与外翻发梢 | 独立摆动 |
| `hair.side.left_front` | P0 | `hair/hair_side_left_front.png` | 脸前左侧长发束，覆盖部分脸侧 | 中等幅度，碰撞限幅 |
| `hair.side.right_front` | P0 | `hair/hair_side_right_front.png` | 脸前右侧长发束 | 中等幅度，碰撞限幅 |
| `hair.ahoge.left` | P1 | `hair/hair_ahoge_left.png` | 顶部偏左轻翘发丝 | 软、快速回弹 |
| `hair.ahoge.center` | P1 | `hair/hair_ahoge_center.png` | 顶部中央轻翘发丝 | 软、快速回弹 |

## G. 额饰/头饰

| ID | 优先级 | 文件 | 内容与生成要求 | 绑定/用途 |
|---|---:|---|---|---|
| `headwear.chain.left` | P0 | `headwear/headwear_chain_left.png` | 中央星左侧金链与蓝紫小星，补全到发丝下方 | 轻微摆动，跟头 |
| `headwear.chain.right` | P0 | `headwear/headwear_chain_right.png` | 中央星右侧金链与小星 | 轻微摆动，跟头 |
| `headwear.star.center` | P0 | `headwear/headwear_star_center.png` | 中央蓝紫晶体星与金色框架 | 轻微旋转/发光 |
| `headwear.charm.drop` | P0 | `headwear/headwear_charm_drop.png` | 中央星下方金色结构和蓝色小吊坠 | 独立摆动 |

额饰必须位于正确发层前后关系。链条不应完全浮在所有刘海之前；必要时可在打包阶段按遮挡拆成前后两段，但视觉结构不得改变。

## H. 光效与情绪 FX

| ID | 优先级 | 文件 | 内容与生成要求 | 用途 |
|---|---:|---|---|---|
| `fx.star.left_large` | P1 | `fx/fx_star_left_large.png` | 主图左侧较大粉色四角星 | 背景漂浮/呼吸闪烁 |
| `fx.star.left_small` | P1 | `fx/fx_star_left_small.png` | 主图左侧小紫星 | 背景漂浮 |
| `fx.star.right_large` | P1 | `fx/fx_star_right_large.png` | 主图右侧较大粉色星 | 背景漂浮 |
| `fx.star.right_small` | P1 | `fx/fx_star_right_small.png` | 主图右侧小紫星 | 背景漂浮 |
| `fx.chest_glow` | P1 | `fx/fx_chest_glow.png` | 腰部星盘/胸饰周围柔和蓝紫金光，不改变饰品本体 | inspiration/excited |
| `fx.eye_glow.left` | P1 | `fx/fx_eye_glow_left.png` | 左眼局部柔光，透明边缘干净 | high-light awakening |
| `fx.eye_glow.right` | P1 | `fx/fx_eye_glow_right.png` | 右眼局部柔光 | 同上 |
| `fx.sweat_drop` | P2 | `fx/fx_sweat_drop.png` | 小型蓝色汗滴，风格克制 | 无语/尴尬 |
| `fx.question_mark` | P2 | `fx/fx_question_mark.png` | 蓝紫金色抽象问号或几何符号 | confused；可关闭 |
| `fx.inspiration_halo` | P2 | `fx/fx_inspiration_halo.png` | 头后淡金蓝星轨/圆环，半透明 | 顿悟/高光觉醒 |

## 7. Anime2.5DRig 兼容 PSD 映射

Anime2.5DRig 基线要求平面层结构。资产打包器应自动生成以下兼容层：

| 兼容层名 | 来源 |
|---|---|
| `back hair_1..8` | 各后发 PNG，保持独立层 |
| `bottomwear` | `body.lower` |
| `footwear` | 左右鞋合成 |
| `topwear` | `body.core`；可包含脖子以避免接缝 |
| `handwear_1..N` | 袖、手、披袖和姿势层，按需要独立 |
| `face` | `face.base` |
| `ears` | 左右耳合成 |
| `eyewhite` | 左右眼白合成 |
| `irides` | 左右虹膜合成；高光可独立自定义层 |
| `eyelash` | 左右睫毛合成 |
| `eye_close` | 左右闭眼合成 |
| `eyebrow` | 左右眉合成 |
| `mouth_close` | `mouth.rest` |
| `mouth_open` | `mouth.a` 作为基线开口 |
| `nose` | `nose` |
| `front hair_1..N` | 发帽、刘海和前侧发独立层 |
| `headwear` | 额饰合成；原生运行时仍保留分层 |

兼容 PSD 只是启动 Anime2.5DRig 的基线。正式运行时应优先读取原生 manifest，以使用多视素、独立眼部和精细物理。

## 8. 资产生成任务模板

每个资产任务必须写清：

```yaml
id: hair.bang.center
reference: assets/reference/local/character_reference_source.png
canvas: 2048x2048
output: assets/generated/character_v1/hair/hair_bang_center.png
include:
  - 主图中央垂落刘海束
  - 被发帽遮挡的根部补全
exclude:
  - 脸、眉、额饰、其他刘海
occlusion_padding_px: 32
style_constraints:
  - 与主图同线稿、色板、光照
  - 不改变人物比例
validation:
  - alpha_nonempty
  - exact_canvas
  - no_background_halo
  - default_composite_visual_check
```

## 9. 自动验证要求

资产工具至少输出：

- `asset-report.json`；
- `asset-report.md`；
- `previews/default_composite.png`；
- `previews/alpha_on_black.png`；
- `previews/alpha_on_white.png`；
- `previews/alpha_checkerboard.png`；
- `previews/bounds_overlay.png`；
- `previews/draw_order_contact_sheet.png`；
- `previews/pose_contact_sheet.png`；
- 缺失层、空层、全不透明层、尺寸错误、边缘污染列表。

## 10. 人工验收清单

- [ ] 默认合成与主图人物一致；
- [ ] 性别气质和脸型没有漂移；
- [ ] 眼睛保留深红/深紫/深蓝层次；
- [ ] 刘海与额饰没有穿模；
- [ ] 后发摆动不露粉色背景洞；
- [ ] 眼睛开合时虹膜不越过眼白；
- [ ] 所有嘴型中心一致，切换不跳动；
- [ ] 星云披袖纹理和金边在分层接缝处连续；
- [ ] 手势切换时袖口连接自然；
- [ ] 黑白背景下无 alpha halo；
- [ ] 所有 P0 文件通过脚本检查；
- [ ] 生成记录完整。
