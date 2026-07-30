# 01｜实现路线与分阶段计划

本文面向仓库所有者与本地 Codex。目标是把当前参考图和规格文档逐步变成一个可在 Windows 11 上运行、由语音驱动、可透明输入 OBS 的 Q 版 2D 虚拟形象系统。

## 1. 最终系统边界

### 1.1 输入

- 一台本地麦克风；
- 角色透明 PNG/PSD 资产；
- 用户在 WebUI 中的预设、热键与手动参数；
- 可选的 OBS WebSocket 状态；
- 不要求摄像头。

### 1.2 输出

- `http://127.0.0.1:<port>/overlay`：透明背景实时角色；
- `http://127.0.0.1:<port>/control`：控制与诊断 UI；
- 可选本地字幕/ASR 文本；
- 可选 OBS WebSocket 场景控制；
- 可导出的角色、音频、口型、情绪和渲染配置。

### 1.3 进程拓扑

```text
┌────────────────────────────────────────────────────────────┐
│ 普通浏览器：/control                                       │
│  麦克风 → AudioWorklet → wLipSync → 视素/音量/音高         │
│  UI → 手动表情、动作、物理、OBS、配置                      │
└───────────────┬────────────────────────────────────────────┘
                │ WebSocket JSON + binary PCM
                ▼
┌────────────────────────────────────────────────────────────┐
│ speech-service（Python）                                   │
│  FastAPI / WebSocket / ring buffer / VAD                   │
│  SenseVoiceSmall → ASR / emotion / event                   │
│  状态机 → 稳定的情绪和动作事件                             │
│  参数总线 → 广播给 controller 与 overlay                   │
└───────────────┬────────────────────────────────────────────┘
                │ WebSocket 参数流
                ▼
┌────────────────────────────────────────────────────────────┐
│ OBS CEF：/overlay                                          │
│  Anime2.5DRig fork / WebGL                                 │
│  角色网格、视素、眨眼、头发/披风物理、表情、特效           │
│  RGBA 透明画布                                             │
└────────────────────────────────────────────────────────────┘
```

## 2. 分阶段实施原则

- 每个 Phase 都要形成一个可启动、可观察、可回退的小闭环；
- 先实现最小通路，再加复杂模型和 UI；
- 快速口型与慢速 ASR/情绪始终分离；
- 资产质量优先于堆叠动作数量；
- 所有阶段都必须有测试、验收和文档更新；
- 不在一个阶段同时更换渲染器、协议、音频栈和模型。

---

# Phase 0｜仓库与开发环境骨架

## 目标

建立可重复的 Windows 11 开发骨架，让后续子项目能够独立安装、启动和测试。

## Codex 任务

1. 创建预期目录：
   - `apps/control-web/`
   - `apps/avatar-runtime/`
   - `services/speech-service/`
   - `packages/protocol/`
   - `packages/animation-core/`
   - `packages/asset-tools/`
   - `scripts/`
   - `tests/`
   - `third_party/`
2. 建立 Node workspace；
3. 建立 Python speech-service 独立虚拟环境说明；
4. 建立 See-through 独立 Conda 环境说明；
5. 创建统一的 `scripts/doctor.ps1`、`scripts/start-dev.ps1`、`scripts/stop-dev.ps1` 骨架；
6. 加入基础 lint/test/format；
7. 提供最小 `/health` 服务与空白 `/control`、透明 `/overlay` 页面；
8. 记录端口、路径和版本锁定策略。

## 输出

- `pnpm install` 或等价安装可以完成；
- `pytest`、前端单元测试可以运行；
- `start-dev.ps1` 能同时启动静态前端和后端健康检查；
- `/overlay` 背景 RGBA 为透明；
- `doctor.ps1` 能检测 Git、Node、Python、NVIDIA 驱动、OBS 和 Git LFS。

## 验收

- 干净 Windows 用户目录下可以按文档重复安装；
- 缺少依赖时给出具体安装建议，不出现难以理解的栈追踪；
- 端口冲突时可以修改配置；
- 所有测试通过。

---

# Phase 1｜角色资产生成与清单落地

## 目标

以 `assets/reference/local/character_reference_source.png` 为唯一主视觉参考，生成一组同画布、同坐标、透明背景、可重建的分层 PNG。

## 主流程

```text
参考图
  → 去背景并建立 2048×2048 对齐母版
  → See-through/ComfyUI-See-through 初始拆层
  → Codex 调度图像生成/修复代理补画遮挡区和差分
  → 导出 assets/generated/character_v1/*.png
  → 资产验证器
  → 合成预览、边缘检查、draw-order 检查
  → manifest 与兼容 PSD
```

## Codex 任务

1. 读取：
   - `docs/04_ASSET_MANIFEST.md`
   - `docs/09_CHARACTER_STYLE_GUIDE.md`
   - `config/character-assets.yaml`
2. 编写 `asset-tools`：
   - 尺寸/模式/alpha 检查；
   - 文件缺失检查；
   - alpha bbox 和空层检查；
   - 绘制顺序合成；
   - 黑/白/棋盘格边缘预览；
   - 生成资产报告；
3. 生成或拆分资产；
4. 输出 `assets/generated/character_v1/`；
5. 为每个资产保留生成记录；
6. 生成平面 PSD 兼容包，层名符合 Anime2.5DRig；
7. 生成默认表情合成图与参考图并排对比。

## 关键限制

- 所有 PNG 必须是 2048×2048 RGBA；
- 不允许单层裁切到局部尺寸；
- 不允许改变人物比例、发型、星形额饰、眼睛颜色和星云披袖结构；
- 遮挡补全应延伸到覆盖层下方，防止变形时露洞；
- 运行时背景完全透明；背景星星作为独立 FX；
- 直线和金色描边必须在各层接缝处连续。

## 验收

- manifest 中所有 P0 资产存在；
- 资产重建图与去背景主图视觉一致；
- 头部左右轻移、刘海摆动、手臂切换时不露背景洞；
- alpha 边缘无粉色背景残留；
- 兼容 PSD 可被 Anime2.5DRig 读取。

---

# Phase 2｜Anime2.5DRig 基线与透明渲染

## 目标

先不接入 AI。让角色能够在 WebGL 中稳定加载、自动绑定、眨眼、呼吸、头发摆动，并能作为透明 OBS Browser Source。

## Codex 任务

1. 以锁定提交引入 Anime2.5DRig；
2. 保留上游许可证和原始说明；
3. 把原单页代码封装到 `apps/avatar-runtime/`；
4. 建立 `RigAdapter`；
5. 支持两种加载方式：
   - Anime2.5DRig 平面 PSD；
   - 本项目 `character-assets.yaml + PNG`；
6. 暴露统一参数：
   - `eyeOpenLeft/Right`
   - `gazeX/Y`
   - `browLeft/Right`
   - `mouthOpen`
   - `viseme.*`
   - `headX/Y/Z`
   - `bodyLean`
   - `breath`
   - `hairPhysics.*`
   - `capePhysics.*`
   - `expression.*`
7. 建立 `/overlay` 无 UI 模式；
8. 建立帧率、渲染耗时、WebGL 错误诊断。

## 验收

- 默认角色能够加载；
- 透明画布在 OBS 中正常叠加；
- 60 FPS 目标下运行 30 分钟无明显内存增长；
- 切换背景调试色不会污染实际 alpha；
- 手动滑块可驱动全部核心参数；
- 第三方代码改动集中且可追踪。

---

# Phase 3｜参数协议与控制页/overlay 分离

## 目标

建立不依赖具体渲染器的本地参数总线，使普通浏览器控制页可以驱动 OBS 内的 overlay。

## Codex 任务

1. 实现 `packages/protocol`：
   - TypeScript schema；
   - Python Pydantic schema；
   - 协议版本与兼容测试；
2. 后端提供：
   - `/health`
   - `/config`
   - `/ws/control`
   - `/ws/audio`
   - `/ws/events`
3. 实现连接握手、心跳、seq、时间戳、重连和队列上限；
4. 控制页发送参数；
5. overlay 订阅参数；
6. 断线时 overlay 平滑回到 idle，不冻结在夸张表情；
7. 实现只读 overlay token 或仅 localhost 限制。

## 验收

- 控制页和 overlay 可在不同浏览器进程中同步；
- 后端重启后 3 秒内自动重连；
- 丢包或消息乱序不会造成参数爆跳；
- 未知消息不会导致崩溃；
- 网络队列有上限并显示丢弃计数。

---

# Phase 4｜wLipSync 低延迟口型

## 目标

让麦克风音频直接驱动 A/I/U/E/O/MBP/FV 视素与张嘴幅度，且即使后端模型未启动也能工作。

## Codex 任务

1. 控制页请求麦克风权限；
2. 使用 AudioWorklet 处理音频；
3. 接入 wLipSync；
4. 提供 profile 导入、导出和校准向导；
5. 建立视素到口型资产/网格的映射；
6. 实现：
   - 音量门限；
   - Attack/Release；
   - 视素权重归一化；
   - 主导视素选择；
   - 权重交叉淡化；
   - 静音闭口；
   - MBP 闭唇保持；
   - 过度抖动抑制；
7. 提供音量回退模式；
8. 输出实时延迟、AudioWorklet underrun 和 profile 状态。

## 校准向导

用户依次持续发音：

- `啊` → A
- `衣` → I
- `乌` → U
- `诶` → E
- `哦` → O
- `姆/吧/啪` → MBP
- `夫` → FV（可选）

每个样本提供录制进度、环境噪声检查、可重录、试听和质量评分。

## 验收

- 后端关闭时仍能口型同步；
- 静音时 150 ms 内自然闭嘴；
- 长元音能够稳定保持对应口型；
- 快速普通话不出现每帧乱跳；
- 麦克风切换后能重新初始化 AudioContext；
- p95 口型响应工程目标约不高于 120 ms。

---

# Phase 5｜SenseVoice ASR 与语音事件服务

## 目标

建立独立的本地语音服务，输出 ASR、语言、置信度、情绪和音频事件，不干扰口型主链路。

## Codex 任务

1. 建立独立 Python 环境；
2. 集成 SenseVoiceSmall/FunASR；
3. 使用浏览器下采样后的 16 kHz 单声道 PCM；
4. 实现 ring buffer 与 VAD；
5. 支持：
   - partial transcript；
   - final transcript；
   - CTC/时间戳（模型链路支持时）；
   - emotion tag 与置信度；
   - laughter/cough 等 event tag；
6. 提供模型预热；
7. 提供 GPU/CPU、精度和设备信息；
8. 模型不可用时返回明确状态，不阻塞其他功能；
9. 不默认保存原始音频。

## 建议的初始窗口

- PCM frame：20 ms；
- 快速 VAD：每帧；
- ASR partial：由 VAD 与 0.5–1.0 s 累积触发；
- emotion window：约 1.0–1.5 s；
- emotion hop：约 0.2–0.4 s；
- 参数必须可调，不写死在代码中。

## 验收

- 中文普通话能够输出可读转写；
- 无声时不持续生成文本；
- 模型预热后推理不会造成 overlay 掉帧；
- 断开控制页后 ring buffer 会清理；
- GPU 不可用时可选择 CPU 降级或关闭服务；
- 模型/权重许可证和来源被记录。

---

# Phase 6｜情绪状态机与动作映射

## 目标

把不稳定的模型标签转成适合直播的平滑表情和动作，不出现情绪闪烁。

## Codex 任务

1. 实现 `EmotionStateMachine`；
2. 输入：模型标签、置信度、音量、音高、语速、停顿、用户锁定状态；
3. 支持：
   - neutral
   - happy
   - excited
   - thoughtful
   - serious
   - angry
   - sad
   - surprised
   - tired
   - confused
4. 提供：
   - 置信度阈值；
   - neutral bias；
   - 多次一致确认；
   - 滞回阈值；
   - 最短保持时间；
   - 冷却时间；
   - 手动锁定/覆盖；
   - 渐入渐出；
5. 将状态映射到眉、眼、嘴、身体、头发物理、披风物理、星光特效；
6. 区分“情绪状态”和“瞬时事件”：
   - 惊叹/音量峰值 → 短促强调；
   - laughter → 笑眼/肩部轻动；
   - cough → 不自动触发夸张表情；
7. 提供可视化状态时间线。

## 验收

- 连续中性说话不频繁跳到 angry/sad；
- 手动表情可立即覆盖自动情绪；
- 覆盖解除后平滑回到自动状态；
- 模型置信度低时保持 neutral 或上一稳定状态；
- 所有映射都可在配置中调整。

---

# Phase 7｜统一 WebUI 控制面板

## 目标

把 Anime2.5DRig 原有控制、音频、ASR、情绪、物理、OBS 与诊断整合成一个总控制台，同时保留子项目原 UI 的高级入口。

## Codex 任务

1. 按 `docs/05_WEBUI_SPEC.md` 实现页面和优先级；
2. 提供简洁模式与高级模式；
3. 提供：
   - 首页/状态；
   - 模型与资产；
   - 音频；
   - 口型；
   - ASR/字幕；
   - 情绪；
   - 表情/动作；
   - 头发/披风物理；
   - 渲染；
   - OBS；
   - 热键；
   - 配置；
   - 诊断；
4. 保留 Anime2.5DRig 原始 UI 作为 `/legacy-rig` 或“高级绑定”标签；
5. 所有滑块显示当前值、默认值和重置按钮；
6. 高风险操作需要明确确认；
7. 提供配置导入/导出和版本迁移。

## 验收

- 基础用户能在 10 分钟内完成麦克风选择、口型测试和 OBS 添加；
- 高级参数不阻塞基础流程；
- 控件修改立即反映到 overlay；
- 刷新控制页不会丢失已保存配置；
- 配置损坏时回退到默认并保留错误副本。

---

# Phase 8｜OBS 集成

## 目标

让用户无需绿幕，即可把角色作为透明源加入 OBS，并能诊断常见问题。

## Codex 任务

1. 输出可复制的 overlay URL；
2. 提供推荐宽高、FPS、CSS 和刷新设置；
3. 提供黑/白/棋盘格 alpha 测试页；
4. 可选接入 OBS WebSocket：
   - 连接测试；
   - 选择场景与源；
   - 显示/隐藏角色；
   - 刷新 Browser Source；
   - 读取当前 FPS/状态；
5. 提供音频同步偏移建议和测量工具；
6. 保留 Spout2 作为后续输出适配器，不作为 MVP 前置依赖。

## 验收

- Browser Source 在透明背景下显示；
- 60 FPS 配置有效；
- 切场景后 overlay 能自动恢复；
- 控制 UI 不进入直播画面；
- OBS 未运行时系统仍可正常启动和预览。

---

# Phase 9｜Windows 一键安装、启动与恢复

## 目标

把开发环境转成可维护的本地应用体验。

## Codex 任务

1. `scripts/install.ps1`：依赖检查、环境创建、模型下载、校验和；
2. `scripts/start.ps1`：启动服务、等待健康、打开控制页；
3. `scripts/stop.ps1`：优雅停止；
4. `scripts/update.ps1`：仅更新项目代码和锁定依赖；
5. `scripts/doctor.ps1`：全面诊断；
6. 明确模型缓存、配置、日志和生成资产的位置；
7. 支持非管理员用户；
8. 端口被占用时自动给出替代端口；
9. 崩溃后下次启动可以恢复配置但不恢复异常瞬时状态；
10. 可选创建桌面快捷方式。

## 验收

- 新机器按文档执行一次安装后可启动；
- 重复运行安装脚本幂等；
- 网络断开后已下载模型仍可运行；
- 日志可导出但不含原始音频；
- 卸载说明清晰，不删除用户资产和配置。

---

# Phase 10｜性能、稳定性与发布候选

## 目标

形成可长期直播的候选版本。

## Codex 任务

1. 完成 `docs/07_TEST_AND_ACCEPTANCE.md` 全部 P0 测试；
2. 进行 30/120 分钟 soak test；
3. 测量：
   - 音频到口型延迟；
   - ASR/情绪推理耗时；
   - overlay FPS；
   - WebSocket 队列；
   - CPU/GPU/VRAM；
   - 内存增长；
4. 优化图层数量、纹理尺寸和 draw calls；
5. 为 30 FPS、60 FPS、低功耗模式提供预设；
6. 输出已知限制、故障恢复和备份文档；
7. 打标签并生成 changelog。

## 发布候选验收

- 60 FPS 模式连续运行 2 小时；
- 麦克风热插拔、后端重启、OBS 场景切换均能恢复；
- 情绪不会高频抖动；
- 角色边缘无明显 alpha halo；
- 配置可导入/导出；
- 核心流程可离线；
- 所有第三方依赖与模型许可证可追踪。

---

# 3. Codex 推荐任务粒度

每次只让 Codex完成一个可验收单元，例如：

```text
阅读 AGENTS.md 和 Phase 4。
只实现麦克风设备选择、AudioWorklet 输入、音量电平和音量回退口型。
不要接入 wLipSync 或 SenseVoice。
补充单元测试、Playwright 设备模拟测试和手工验收步骤。
完成后更新 docs/PROGRESS.md。
```

下一次再实现 wLipSync。这样可以降低同时排查浏览器权限、WASM、模型和 WebGL 的复杂度。

# 4. 建议的分支与提交

- `phase/0-bootstrap`
- `phase/1-assets`
- `phase/2-renderer`
- `phase/3-protocol`
- `phase/4-lipsync`
- `phase/5-speech`
- `phase/6-emotion`
- `phase/7-webui`
- `phase/8-obs`
- `phase/9-packaging`
- `phase/10-release`

提交信息建议使用：

```text
feat(audio): add microphone device selection and level meter
fix(renderer): preserve straight-alpha edges in overlay
chore(third-party): pin Anime2.5DRig upstream commit
```
