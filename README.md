# live2D-Q

基于**单张 Q 版角色参考图**构建的本地离线音频驱动 2D 虚拟形象项目。

本项目不以摄像头或人脸捕捉为核心。角色主要根据以下信号实时运动：

- 麦克风音频中的音素/视素（A、I、U、E、O、闭唇等），驱动口型；
- 音量、音高、语速、停顿等韵律特征，驱动头部、身体、头发与披风的轻微动作；
- 本地语音识别与语音情绪识别，驱动字幕、表情和动作状态；
- WebUI 中的手动控制、热键与预设；
- OBS Browser Source 读取透明背景的实时渲染页面。

> 当前仓库首先提供**完整的实现规格、资产清单、架构约束和验收标准**。运行时代码由本地 Codex 按阶段实现。不要把当前文档版仓库误认为已经可直接直播的成品。

![角色主参考图](assets/reference/character_reference.png)

## 已选定的主路线

```text
主参考图
  └─ See-through / ComfyUI-See-through 做初始拆层
       └─ Codex + 图像生成/修复流程补齐并输出统一画布透明 PNG
            └─ 资产校验器 + PSD/manifest 打包
                 └─ Anime2.5DRig fork 负责自动绑定与 WebGL 渲染

麦克风
  ├─ wLipSync（浏览器内、低延迟）→ A/I/U/E/O/MBP/FV 视素权重
  ├─ 音量/音高/VAD → 呼吸、点头、身体弹性、头发物理
  └─ SenseVoiceSmall（本地服务）→ ASR、情绪、事件标签

WebUI 控制器
  └─ localhost WebSocket 参数总线
       ├─ 控制页面 /control
       └─ 透明渲染页面 /overlay → OBS Browser Source
```

### 为什么这样组合

- **See-through**解决初始语义拆层和遮挡区域补全，但不负责正式绑定；
- **Anime2.5DRig**能够直接承接分层 PSD，并提供 WebGL、眨眼、头发物理、简单口型和控制 UI；
- **wLipSync**在浏览器 AudioWorklet/WASM 中直接输出音素权重，适合低延迟口型；
- **SenseVoiceSmall**负责中文友好的 ASR 与语音情绪识别，但不阻塞高频口型线程；
- **OBS Browser Source**直接加载透明网页，不需要把程序伪装成虚拟摄像头。

## 目标平台

- Windows 11
- NVIDIA RTX 4090 24 GB
- OBS Studio
- Chromium/Edge（控制页面）
- OBS Browser Source（透明输出）
- 本地 Python 与 Node.js 环境

## MVP 成功标准

- 角色在 OBS 中以透明背景显示；
- 透明边缘在黑色与白色背景上均无明显黑边/白边；
- 渲染目标 60 FPS，持续运行 30 分钟无明显内存增长；
- 快速口型主链路主观延迟不明显，工程目标为 p95 不高于约 120 ms；
- 情绪状态采用滑动窗口、阈值、滞回和最短保持时间，不频繁闪烁；
- 无摄像头也能完成眨眼、视线游移、呼吸、说话动作、头发与披风物理；
- 断开或切换麦克风后能够恢复；
- 模型下载完成后，核心直播流程可以离线运行；
- 控制页与 OBS 渲染页分离，OBS 不直接申请麦克风权限。

## 文档索引

| 文档 | 面向对象 | 内容 |
|---|---|---|
| [AGENTS.md](AGENTS.md) | Codex/开发者 | 项目级执行规则、模块边界与完成定义 |
| [00_PROJECT_STATUS.md](docs/00_PROJECT_STATUS.md) | 用户 + Codex | 当前阶段、阻塞项与每阶段验收记录 |
| [01_IMPLEMENTATION_ROADMAP.md](docs/01_IMPLEMENTATION_ROADMAP.md) | 用户 + Codex | 从零到可直播版本的分阶段实现计划 |
| [02_TECHNICAL_ROUTES.md](docs/02_TECHNICAL_ROUTES.md) | Codex/开发者 | 每项功能的主路线、备选路线与取舍 |
| [03_USER_GUIDE.md](docs/03_USER_GUIDE.md) | 基础用户 | 功能说明、启动流程、OBS 使用与常见问题 |
| [04_ASSET_MANIFEST.md](docs/04_ASSET_MANIFEST.md) | 资产生成代理 + Codex | 完整图片资产清单、绘制规则与验收要求 |
| [05_WEBUI_SPEC.md](docs/05_WEBUI_SPEC.md) | 前端开发者 | 总控制面板的页面、控件、状态和优先级 |
| [06_PROTOCOL_AND_ARCHITECTURE.md](docs/06_PROTOCOL_AND_ARCHITECTURE.md) | 前后端开发者 | 进程拓扑、WebSocket 协议、参数模型与时序 |
| [07_TEST_AND_ACCEPTANCE.md](docs/07_TEST_AND_ACCEPTANCE.md) | 测试/开发者 | 自动测试、视觉测试、延迟与稳定性验收 |
| [08_WINDOWS_11_SETUP.md](docs/08_WINDOWS_11_SETUP.md) | 本地用户 | Windows 11 环境、依赖、目录与启动脚本规划 |
| [09_CHARACTER_STYLE_GUIDE.md](docs/09_CHARACTER_STYLE_GUIDE.md) | 资产生成代理 | 角色造型、颜色、风格和禁止漂移项 |
| [THIRD_PARTY.md](THIRD_PARTY.md) | 维护者 | 第三方项目、许可证和模型权重注意事项 |

机器可读配置：

- [`config/character-assets.yaml`](config/character-assets.yaml)：资产 ID、文件名、绘制顺序和绑定角色；
- [`config/animation-presets.example.yaml`](config/animation-presets.example.yaml)：表情/动作预设样例；
- [`config/runtime.example.yaml`](config/runtime.example.yaml)：运行时配置样例。

## 建议的本地 Codex 启动方式

克隆后先让 Codex只执行一个阶段，避免一次性改动过大：

```text
请先阅读 AGENTS.md、docs/01_IMPLEMENTATION_ROADMAP.md 和 docs/07_TEST_AND_ACCEPTANCE.md。
只执行 Phase 0：建立工程骨架、依赖锁定、最小健康检查和测试框架。
不要提前实现后续阶段。完成后运行测试、更新进度文档，并给出下一阶段阻塞项。
```

后续每个阶段使用同样方式推进，并要求 Codex：

1. 先读对应文档；
2. 列出将修改的文件；
3. 实现最小闭环；
4. 运行自动测试与手工验收；
5. 更新文档和变更记录；
6. 再进入下一阶段。

## 预期仓库结构

```text
live2D-Q/
├─ apps/
│  ├─ control-web/          # WebUI 控制面板
│  └─ avatar-runtime/       # Anime2.5DRig fork + 透明 overlay
├─ services/
│  └─ speech-service/       # SenseVoice、VAD、ASR、情绪服务
├─ packages/
│  ├─ protocol/             # TS/Python 共享协议定义
│  ├─ animation-core/       # 平滑、状态机、参数映射
│  └─ asset-tools/          # 资产验证、合成、PSD/manifest 工具
├─ assets/
│  ├─ reference/            # 主参考图
│  ├─ generated/            # 对齐透明 PNG 资产
│  └─ profiles/             # 口型校准与角色配置
├─ config/
├─ docs/
├─ scripts/
├─ tests/
└─ third_party/             # 按锁定提交引入的第三方源码
```

## 当前不做的事情

- 不以摄像头面捕为主要输入；
- 不使用逐帧生成式 Talking Head 作为实时主渲染器；
- 不在高频口型线程中运行大模型；
- 不把 OBS 控制 UI 一起输出到直播画面；
- 不把模型权重、缓存、日志或用户录音提交到 Git；
- 不在没有核对许可证和保留声明的情况下复制第三方代码。
