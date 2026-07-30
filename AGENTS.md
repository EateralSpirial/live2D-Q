# AGENTS.md

本文件是本仓库中 Codex、子代理和自动化开发流程的最高优先级项目说明。除非用户明确修改目标，否则所有实现都必须遵守。

## 1. 项目目标

构建一个运行在 Windows 11 本地的 Q 版 2D 虚拟形象系统：

- 不依赖摄像头或人脸捕捉；
- 根据麦克风的音素/视素低延迟驱动口型；
- 根据音量、音高、语速、停顿驱动轻微身体和物理动作；
- 使用本地 ASR 与语音情绪识别驱动字幕、表情与动作状态；
- 通过透明网页作为 OBS Browser Source；
- 提供独立的总 WebUI 控制面板；
- 主要依赖开源项目，第三方代码和模型许可证可追踪。

## 2. 文档权威顺序

发生冲突时按以下顺序处理：

1. 用户在当前任务中的明确要求；
2. 本文件；
3. `docs/01_IMPLEMENTATION_ROADMAP.md`；
4. `docs/06_PROTOCOL_AND_ARCHITECTURE.md`；
5. `docs/07_TEST_AND_ACCEPTANCE.md`；
6. 其他文档与示例配置。

发现文档冲突时，不要静默选择。记录冲突、采用影响最小的临时方案，并在同一变更中修正文档。

## 3. 核心架构约束

### 3.1 高频口型与低频语义必须解耦

- `wLipSync` 或等价快速引擎负责 10–20 ms 音频帧的口型权重；
- ASR、情绪识别只能作为慢速增强，不得阻塞口型或渲染循环；
- ASR 不可成为张嘴/闭嘴的唯一依据；
- 后端超时或崩溃时，口型必须退化到本地快速模式。

### 3.2 控制页与 OBS 渲染页必须分离

- `/control` 获取麦克风并展示 UI；
- `/overlay` 只接收参数并渲染透明角色；
- `/overlay` 默认只读，不申请麦克风、摄像头或文件系统权限；
- 参数通过 localhost WebSocket 广播；不要假定 OBS CEF 与普通浏览器共享内存或 BroadcastChannel。

### 3.3 第三方引擎必须通过适配器隔离

至少建立以下接口：

- `RigAdapter`：Anime2.5DRig 与未来替代引擎；
- `LipSyncEngine`：wLipSync、音量回退、测试信号；
- `SpeechEngine`：SenseVoice/FunASR、ONNX/CPU 回退；
- `OutputAdapter`：Browser Source，未来可增加 Spout2；
- `AssetLoader`：PSD 兼容层与 manifest/PNG 原生层。

业务代码不得直接散落调用第三方实现细节。

### 3.4 参数与协议必须版本化

- 所有跨进程消息必须有 `schemaVersion`、`type`、`source`、`seq`、`timestampMs`；
- TypeScript 使用运行时 schema 校验；Python 使用 Pydantic；
- 未知字段可忽略，未知消息类型必须记录但不得导致崩溃；
- 破坏性协议变更必须提升主版本并提供迁移说明。

### 3.5 资产必须可重建和可验证

- 所有运行时 PNG 均为同一画布、同一坐标、透明背景；
- 不允许单独裁切后依靠人工摆放；
- 资产生成记录需包含参考图、模型/工具、提示词或操作说明、尺寸和校验结果；
- 提供一键重建合成预览和 alpha 边缘检查；
- 不提交用户原始录音、模型缓存或临时中间文件。

## 4. 首选技术栈

- 前端控制面板：TypeScript + React + Vite；
- 渲染端：Anime2.5DRig fork 的 WebGL 运行时，逐步模块化；
- 浏览器音频：WebAudio + AudioWorklet + wLipSync；
- 本地后端：Python + FastAPI/Uvicorn + WebSocket；
- ASR/情绪：SenseVoiceSmall/FunASR；
- 测试：Vitest、Playwright、pytest；
- 配置：YAML/JSON + schema；
- 输出：OBS Browser Source，Spout2 仅作为后续可选适配器。

更换主技术栈前，先在 `docs/02_TECHNICAL_ROUTES.md` 增加 ADR 风格的取舍记录。

## 5. 实现顺序

严格按以下顺序建立可运行闭环：

1. 工程骨架、健康检查、测试框架；
2. 资产清单、验证器、合成预览；
3. Anime2.5DRig 基线导入和透明渲染；
4. 参数总线与控制/overlay 分离；
5. wLipSync 低延迟口型与校准；
6. SenseVoice 服务、VAD、ASR；
7. 情绪状态机与动作映射；
8. 总 WebUI；
9. OBS 引导与可选 OBS WebSocket；
10. Windows 一键安装/启动、稳定性和性能优化。

不要在前一阶段没有验收时并行堆叠后续功能。

## 6. 子代理建议

允许使用子代理，但必须划定文件所有权和接口：

- `asset-agent`：仅处理 `assets/`、资产脚本与资产文档；
- `renderer-agent`：仅处理 `apps/avatar-runtime/`；
- `audio-agent`：仅处理浏览器音频和 wLipSync；
- `speech-agent`：仅处理 `services/speech-service/`；
- `ui-agent`：仅处理 `apps/control-web/`；
- `qa-agent`：仅处理测试、基准和验收报告。

多个代理不得同时修改共享协议。共享协议先由主代理定稿，再由各代理消费。

## 7. 代码质量要求

- TypeScript 开启严格模式，不使用无理由的 `any`；
- Python 对公共函数添加类型标注；
- 对音频、WebSocket、模型加载和文件读取提供明确错误信息；
- 所有长时间任务必须支持取消；
- 所有设备、端口和路径必须可配置；
- 所有默认值必须在 UI 有可见说明；
- 禁止隐藏遥测；默认不进行外网请求；
- 日志不得记录原始音频或完整隐私文本，除非用户显式打开调试录制；
- UI 至少提供简体中文；内部标识符和代码使用英文。

## 8. 第三方与许可证

- 引入源码前记录仓库 URL、提交 SHA、许可证和修改说明；
- 许可证文件及 NOTICE 不得删除；
- SenseVoice 代码许可证与模型权重许可证不是同一件事，下载脚本必须展示并记录模型条款；
- 不把大型模型权重提交到 Git；
- 不把第三方示例角色或无权分发的 PSD 提交到本仓库；
- 角色主参考图为本项目资产，仅用于本项目资产生成和测试。

## 9. 完成定义

每个阶段完成时必须同时满足：

- 功能可在 Windows 11 本地重复启动；
- 新增自动测试已运行并通过；
- 有明确的手工验收步骤；
- 错误和降级路径可测试；
- 相关配置、README 和进度文档已更新；
- 没有把模型、缓存、录音、日志或秘密提交到仓库；
- `git status` 清洁；
- 输出一份简短的阶段报告，包含性能数据、已知限制和下一步。

## 10. 禁止事项

- 不要把生成式逐帧视频模型放入实时主循环；
- 不要让情绪分类结果每个推理周期直接切换表情；
- 不要在 OBS overlay 内启动模型服务或申请麦克风；
- 不要依赖固定盘符或用户目录；
- 不要把所有组件塞进单一 Python 环境；
- 不要跳过资产对齐和透明边缘校验；
- 不要在未测量前声称“零延迟”；
- 不要在没有用户同意时改变角色设计、性别气质、颜色体系或饰品结构。
