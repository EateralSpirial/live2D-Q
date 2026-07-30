# 02｜功能与阶段的技术路线

本文给本地 Codex提供明确的主路线、备选路线和不采用项。主路线不是不可变，但任何替换都必须先证明接口兼容、许可证可接受、延迟和维护成本更优。

## 1. 总体决策表

| 能力 | 主路线 | 备选/降级 | 暂不采用 | 核心理由 |
|---|---|---|---|---|
| 单图拆层 | See-through V3 CLI | ComfyUI-See-through UI | 纯手工逐层重画 | 自动语义拆层、遮挡补全、PSD 输出；4090 显存足够 |
| 资产修复 | Codex 调度图像编辑/生成 + 校验器 | Krita/Photoshop 人工修复 | 每层独立从零文生图 | 从零生成容易角色漂移和坐标不一致 |
| 自动绑定 | Anime2.5DRig fork | 自建 WebGL rig | 立即迁移 Inochi2D | 现成 PSD 解析、自动锚点、网格、物理和 UI，开发闭环最快 |
| 运行时渲染 | Anime2.5DRig WebGL1 封装 | 后续 WebGL2/PixiJS | 逐帧生成视频 | 可控、稳定、低延迟、可透明输出 |
| 快速口型 | wLipSync | 音量开合回退 | ASR-only 口型 | 浏览器内 MFCC/WASM，避免等待整句识别 |
| 高精度口型增强 | wLipSync + ASR/CTC 时间戳校正 | 仅 wLipSync | 强制大模型逐帧音素 | 可在延迟与准确度之间切换 |
| ASR/情绪 | SenseVoiceSmall + FunASR | ONNX/GGUF/CPU 路线 | 云端 ASR 作为默认 | 中文支持、可本地运行、同一模型输出 ASR/情绪/事件 |
| VAD | 浏览器快速能量门 + 后端 FSMN-VAD | WebRTC VAD/Silero VAD | 仅固定音量阈值 | 快速门控与语义分段职责分离 |
| 控制面板 | React + TypeScript + Vite | 原 Anime2.5DRig UI 单独使用 | 把 UI 画进 overlay | 复杂状态和诊断需要结构化前端；控制与输出必须隔离 |
| 后端 | FastAPI + Uvicorn + WebSocket | aiohttp | Electron 内嵌 Python | Python 模型生态成熟，WebSocket 与本地服务简单 |
| 参数总线 | localhost WebSocket | 同页直连/BroadcastChannel 仅作优化 | WebRTC | 控制浏览器与 OBS CEF 不应依赖共享上下文 |
| OBS 输出 | Browser Source | Spout2 适配器 | 虚拟摄像头 | Browser Source 原生支持透明网页；实现成本最低 |
| Windows 包装 | PowerShell 启动器 | 后续 Tauri | 首版 Electron 全家桶 | 先稳定系统，再决定桌面壳 |

## 2. 资产拆层与生成

### 2.1 主路线：See-through V3

用途：把主图拆为语义层，并补全被遮挡部分，输出 PSD 和中间深度/分割结果。

实施方式：

- 在独立 Conda 环境运行；
- 使用官方 `inference_psd.py` 作为可复现 CLI；
- 4090 24 GB 首先使用 bf16 1280 或 2048 试验；
- 不把其输出直接视为最终资产；
- 后处理必须按照本项目清单重新拆分头发、眼睛、口型和手部；
- 保存原始输出、修复版本和最终版本的 lineage。

### 2.2 可选 UI：ComfyUI-See-through

适合用户在资产阶段手动调整 seed、分辨率、深度和左右拆分，并在浏览器下载 PSD。

用途限制：

- 它是第三方封装；
- 资产流水线仍需记录参数；
- UI 输出仍要通过本项目验证器；
- 正式自动化应保留 CLI 路线。

### 2.3 为什么不让 Codex 对每层单独“从零生成”

这种做法通常会造成：

- 发型和五官比例漂移；
- 金色线条和星云纹理不连续；
- 每层光照不一致；
- 同一部件在不同画布位置；
- 叠加后出现重复边缘；
- 动画时暴露缺失区域。

正确做法是以主图为编辑条件，在固定画布上进行遮罩提取、补画和差分生成。

## 3. 自动绑定与渲染

### 3.1 主路线：Anime2.5DRig fork

保留能力：

- 分层 PSD 拖入；
- 眼、眉、虹彩左右自动分离；
- 自动锚点；
- 前后发房检测；
- 头发双弹簧物理；
- 伪 3D 头部移动；
- 眨眼、呼吸、身体倾斜；
- 背景透明；
- 原有 UI 作为高级绑定工具。

本项目要增加：

- manifest + PNG 原生资产加载；
- 多视素嘴型，而非只有开/闭；
- 左右独立眼部差分；
- 统一参数接口；
- WebSocket 输入；
- `/control` 与 `/overlay` 分离；
- 物理组配置；
- 表情预设与状态混合；
- 诊断和自动测试。

### 3.2 适配器设计

```ts
interface RigAdapter {
  loadCharacter(source: CharacterSource): Promise<void>;
  setParameter(id: string, value: number): void;
  setExpression(id: string, weight: number): void;
  setPose(id: string): void;
  update(deltaMs: number): void;
  render(): void;
  getDiagnostics(): RigDiagnostics;
  dispose(): void;
}
```

不要让控制面板直接操作 Anime2.5DRig 内部变量。这样未来可替换为 WebGL2、PixiJS 或 Inochi2D。

### 3.3 WebGL1 与 WebGL2

首版保留 WebGL1，减少 fork 风险。只有出现以下事实时再升级：

- 纹理尺寸或 draw call 明显限制性能；
- 需要更复杂的 blend/后处理；
- OBS CEF 对当前 WebGL1 存在稳定性问题；
- 自动化测试证明升级不会破坏现有资产。

## 4. 实时口型路线

### 4.1 快速模式（默认）

```text
Microphone → AudioWorklet → wLipSync → viseme weights → smoothing → RigAdapter
```

特点：

- 不等待文字识别；
- 适合 10–20 ms 音频帧；
- 需要个人 profile；
- 直接输出权重和音量；
- 后端不可用时仍能工作。

推荐视素集合：

- `REST`
- `A`
- `I`
- `U`
- `E`
- `O`
- `MBP`
- `FV`

渲染端不要简单硬切 PNG。应采用：

1. 音量门控计算 `mouthOpen`；
2. 视素权重归一化；
3. 选取前 1–2 个主导视素；
4. 进行短时交叉淡化；
5. MBP 在爆破音附近强制闭唇；
6. 静音时回到 REST；
7. Smile/Tense 作为独立形态偏置，不替代音素。

### 4.2 音量回退模式

当 profile 无效、WASM 加载失败或用户未校准时：

- 音量低 → REST；
- 音量中 → 小开口；
- 音量高 → A/O 混合大开口；
- 使用 Attack/Release 平滑；
- UI 必须提示“当前为简化口型”。

### 4.3 ASR 辅助模式（P1）

SenseVoice partial/final 文本加 CTC 时间戳，经过普通话拼音/音素映射，生成候选视素时间线。它只用于：

- 修正 wLipSync 对相似元音的歧义；
- 改善 MBP/FV 等辅音闭唇；
- 录制模式或允许 150–300 ms 额外延迟的高质量模式。

不得用 ASR 辅助覆盖用户实时发音的全部权重。若时间戳过旧、置信度低或网络队列堆积，立即回到快速模式。

### 4.4 普通话视素映射建议

| 拼音/发音类别 | 目标视素 |
|---|---|
| a、ia、ua | A |
| i、yi、部分 j/q/x 后韵母 | I |
| u、wu | U |
| e、ê、ei | E |
| o、uo、ou | O |
| ü、yu | U 与 I 的前圆唇混合 |
| b、p、m | MBP |
| f | FV |
| 静音、停顿 | REST |

映射表必须配置化，并通过用户校准数据调整。

## 5. 音频特征与身体动作

不需要额外生成式模型。首版使用可解释规则：

| 音频信号 | 动作参数 |
|---|---|
| RMS/音量包络 | 张嘴、身体上下脉冲、披风幅度 |
| 音节起始 | 短促点头或身体弹性 |
| 基频 F0 | 眉眼轻微抬落、头部 Y |
| 语速 | 头发/披风物理强度、随机动作密度 |
| 长停顿 | 回到 neutral、视线游移、眨眼 |
| laughter 事件 | 笑眼、肩部轻动、星光增强 |
| 突然高能量 | 短促强调，不直接判定 angry |

规则输出必须有限幅、低通和冷却，避免音量噪声导致角色抽动。

## 6. ASR、情绪与 VAD

### 6.1 主路线：SenseVoiceSmall + FunASR

职责：

- ASR；
- 语言识别；
- 语音情绪标签；
- laughter/cough 等事件；
- 可选时间戳。

部署原则：

- 独立 Python 进程；
- 启动时预热；
- 只接收 16 kHz mono PCM；
- 推理结果通过 WebSocket 广播；
- 原始音频默认不落盘；
- 模型崩溃不影响口型和渲染。

### 6.2 VAD 双层设计

1. **浏览器快速门**：RMS/noise floor，决定是否发送音频和是否闭嘴；
2. **后端语音段 VAD**：FSMN-VAD 或等价，决定 ASR 片段、final 边界和情绪窗口。

### 6.3 情绪不是单帧标签

模型输出先进入状态机：

```text
raw scores
  → label normalization
  → confidence threshold
  → neutral bias
  → rolling vote / EMA
  → hysteresis
  → minimum hold
  → cooldown
  → expression transition
```

建议初始值：

- 置信度进入阈值：0.65；
- 退出阈值：0.45；
- 至少连续 2–3 次支持；
- 最短保持 0.8–1.2 s；
- 进入渐变 0.2–0.4 s；
- 退出渐变 0.4–0.8 s；
- 所有值必须可在 UI 调整。

### 6.4 CPU/轻量回退

可选路径：

- SenseVoice ONNX；
- 官方或可靠第三方 GGUF/llama.cpp 路线；
- 只开 ASR、不做情绪；
- 完全关闭 speech-service，只保留 wLipSync。

第三方转换权重必须重新核对模型卡和许可证。

## 7. WebUI 与状态管理

### 7.1 主路线

- React + TypeScript + Vite；
- 运行时 schema 校验；
- 持久配置和瞬时参数分离；
- UI 状态与角色参数状态分离；
- 复杂面板按模块懒加载；
- 简洁模式隐藏开发和高级物理项。

### 7.2 页面角色

- `/control`：完整控制台、麦克风、校准；
- `/overlay`：OBS 透明输出；
- `/assets`：资产检查与预览；
- `/calibrate/lipsync`：口型 profile 向导；
- `/diagnostics`：性能与日志；
- `/legacy-rig`：保留 Anime2.5DRig 原 UI。

### 7.3 状态分层

- **Persistent profile**：模型、音频设备偏好、阈值、映射、热键；
- **Session state**：当前连接、当前情绪、实时音量、临时表情；
- **Transient frame state**：视素权重、物理速度、渲染时间；
- **Secrets**：OBS WebSocket 密码、token，仅保存在本机安全位置。

## 8. WebSocket 与数据格式

主路线使用本地 WebSocket：

- JSON：控制、状态、ASR、情绪、诊断；
- binary PCM：16-bit little-endian mono；
- 所有消息带 seq 和单调时间戳；
- overlay 只订阅，不发送原始音频；
- 服务端对每类消息设置队列上限；
- 高频参数可批量为一个 frame message。

详细协议见 `docs/06_PROTOCOL_AND_ARCHITECTURE.md`。

## 9. OBS 输出路线

### 9.1 主路线：Browser Source

优点：

- 透明背景原生可用；
- 不需要虚拟摄像头；
- WebGL 可直接运行；
- 控制页与直播画面可以完全分离；
- 集成成本低。

推荐设置：

- URL：本地 `/overlay`；
- 尺寸：与模型画布或节目画布匹配；
- 自定义 FPS：60；
- 背景 CSS：透明；
- 初期不要开启“源不可见时关闭”，避免切场景后服务重置；
- 测试稳定后再决定是否开启“场景激活时刷新”。

### 9.2 可选：Spout2

只有出现以下需求时再做：

- 自建原生渲染器；
- 浏览器源帧率或 CEF 兼容性不可接受；
- 需要 GPU 纹理直接共享；
- 需要和其他视觉软件互通。

Spout2 是后续 `OutputAdapter`，不是首版前置依赖。

## 10. Windows 部署路线

### 10.1 环境隔离

- Node workspace：前端与工具；
- Python 3.11 venv：speech-service；
- Python 3.12 Conda：See-through；
- 模型缓存：仓库外或 `.gitignore` 目录；
- 不强迫安装系统级 CUDA Toolkit，优先使用匹配的 PyTorch wheel；
- 不在 WSL 中运行直播主流程，避免麦克风、OBS 和 CEF 互通复杂度。

### 10.2 启动器

首版 PowerShell：

1. 检查依赖；
2. 启动 speech-service；
3. 等待 `/health`；
4. 启动前端服务；
5. 打开 `/control`；
6. 输出 `/overlay` URL；
7. 退出时优雅停止子进程。

Tauri/桌面壳在系统稳定后再评估。

## 11. 测试技术路线

- TypeScript：Vitest；
- UI：Playwright；
- Python：pytest；
- 协议：双语言 golden fixtures；
- 音频：固定 WAV 测试向量；
- 渲染：截图基线 + alpha 检查；
- 资产：尺寸、alpha、draw order、重建预览；
- 性能：浏览器 Performance API、后端计时、WebSocket seq；
- soak：30/120 分钟脚本化运行。

## 12. 关键风险与缓解

| 风险 | 表现 | 缓解 |
|---|---|---|
| 自动拆层不适合变形 | 转头露洞、发丝断裂 | 遮挡补画、重叠边、资产验证、减少头部幅度 |
| wLipSync profile 不匹配 | 元音判断抖动 | 校准向导、质量评分、音量回退 |
| 情绪误判 | 表情频繁跳变 | neutral bias、滞回、最短保持、手动锁定 |
| OBS CEF 与普通浏览器不同 | overlay 行为不一致 | Playwright + OBS 手测、避免非标准 API、WebSocket 通信 |
| Python 依赖冲突 | See-through 与 SenseVoice 互相破坏 | 独立环境、锁定版本、启动器检测 |
| 4090 资源被资产模型占满 | 直播时掉帧 | 资产生成与直播运行分时；运行时只加载 speech 模型 |
| 第三方项目更新破坏接口 | 突然无法启动 | 锁定 commit SHA、适配器、升级测试 |
| alpha halo | 黑边/粉边 | straight-alpha PNG、黑白背景测试、预乘设置明确 |
| 配置膨胀 | 用户难以使用 | 简洁/高级模式、默认预设、分区重置 |
