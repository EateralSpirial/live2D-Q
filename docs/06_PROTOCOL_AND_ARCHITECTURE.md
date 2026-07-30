# 06｜系统架构、模块边界与本地协议

本文是前端、渲染端和语音服务之间的接口契约。实现阶段可补充字段，但不得绕过版本化和适配器边界。

## 1. 进程与职责

## 1.1 `apps/control-web`

职责：

- 麦克风权限与设备选择；
- AudioContext/AudioWorklet；
- wLipSync；
- 快速音量、音高、onset 特征；
- WebUI；
- 配置编辑；
- 将 16 kHz mono PCM 发送给 speech-service；
- 将高频视素和手动控制发送到参数总线；
- 读取 ASR、情绪、服务和 overlay 状态。

禁止：

- 直接操作 Anime2.5DRig 内部全局变量；
- 把模型权重加载进普通 UI 主线程；
- 默认保存原始音频。

## 1.2 `apps/avatar-runtime`

职责：

- 加载角色资产；
- 自动绑定/读取绑定配置；
- 接收参数 frame；
- 平滑、插值、物理和渲染；
- 透明 RGBA 输出；
- 上报 FPS、draw calls、WebGL context 状态。

禁止：

- 请求麦克风或摄像头；
- 运行 ASR/情绪模型；
- 显示控制 UI；
- 持久保存秘密。

## 1.3 `services/speech-service`

职责：

- 本地 HTTP/WebSocket 服务；
- PCM ring buffer；
- VAD；
- SenseVoice ASR、情绪与事件；
- 情绪状态机；
- 参数广播和连接管理；
- 健康检查、指标和日志。

禁止：

- 参与 WebGL 渲染；
- 阻塞 WebSocket 事件循环执行模型推理；
- 未经显式设置保存录音；
- 把模型异常传播为整个应用崩溃。

## 1.4 `packages/protocol`

职责：

- 消息类型；
- JSON schema/TypeScript schema；
- Python Pydantic 对应类型；
- golden fixtures；
- 版本迁移；
- 参数 ID 和范围。

## 1.5 `packages/animation-core`

职责：

- Attack/Release、EMA、spring、clamp；
- 视素混合；
- 表情层混合；
- 情绪状态机的纯逻辑部分；
- 参数优先级；
- deterministic test vectors。

## 1.6 `packages/asset-tools`

职责：

- manifest 读取与 schema；
- PNG/PSD 验证；
- draw order 合成；
- alpha 测试；
- 兼容 PSD 打包；
- 资产报告。

---

# 2. 服务地址与端口

推荐默认：

| 服务 | 地址 | 说明 |
|---|---|---|
| HTTP/WebUI | `http://127.0.0.1:8765` | 生产/本地统一入口 |
| Vite dev | `http://127.0.0.1:5173` | 仅开发模式 |
| Health | `/api/health` | 综合健康状态 |
| Config | `/api/config` | 读取/保存配置，需本地鉴权 |
| Control WS | `/ws/control` | 控制页双向消息 |
| Overlay WS | `/ws/overlay` | overlay 订阅参数与上报诊断 |
| Audio WS | `/ws/audio` | 控制页发送 binary PCM |
| Events WS | `/ws/events` | 可合并到 control/overlay，保留为调试用途 |

所有端口可配置。默认只监听 `127.0.0.1`。局域网模式必须显式打开并使用 token。

# 3. 消息公共信封

所有 JSON 消息必须包含：

```json
{
  "schemaVersion": "1.0",
  "type": "lipsync.frame",
  "source": "control-web",
  "sessionId": "uuid",
  "seq": 12345,
  "timestampMs": 90123.456,
  "payload": {}
}
```

字段定义：

| 字段 | 类型 | 说明 |
|---|---|---|
| `schemaVersion` | string | `major.minor`；破坏性变更提升 major |
| `type` | string | 稳定消息类型 |
| `source` | string | `control-web`、`speech-service`、`overlay`、`test` |
| `sessionId` | UUID/string | 当前控制会话 |
| `seq` | uint64 | 每 source 单调递增 |
| `timestampMs` | number | source 的单调时钟毫秒，不使用墙上时间做动画同步 |
| `payload` | object | 消息体 |

可选字段：

- `correlationId`：请求/响应；
- `expiresAtMs`：过期消息；
- `priority`：`realtime`、`normal`、`background`；
- `traceId`：开发诊断。

## 3.1 兼容规则

- minor 新字段：旧消费者忽略；
- 未知 `type`：记录一次并忽略；
- major 不兼容：拒绝连接并给出升级提示；
- 参数超范围：clamp + 警告，不允许 NaN 进入渲染器；
- 过期 realtime frame：丢弃，不补播。

# 4. 握手、心跳与重连

## 4.1 客户端握手

```json
{
  "schemaVersion": "1.0",
  "type": "client.hello",
  "source": "overlay",
  "sessionId": "uuid",
  "seq": 1,
  "timestampMs": 10.2,
  "payload": {
    "clientId": "obs-overlay-1",
    "clientVersion": "0.1.0",
    "capabilities": ["render.webgl1", "viseme.v1", "physics.v1"],
    "profile": "default",
    "readOnly": true
  }
}
```

服务端返回：

- 协议版本；
- 服务版本；
- session；
- 当前配置摘要；
- server monotonic timestamp；
- 心跳间隔；
- 最大消息大小；
- 当前角色和参数快照。

## 4.2 心跳

- 默认 2 秒；
- 3 次未响应视为断线；
- RTT 记录 p50/p95；
- overlay 断线时在 250–500 ms 内开始平滑回 idle；
- 控制页使用指数退避重连，上限 3 秒；
- 重连后先请求全量 snapshot，再消费增量 frame。

# 5. 高频口型消息

## 5.1 `lipsync.frame`

建议 30–60 Hz 发送，而不是每个 AudioWorklet quantum 都通过 WebSocket。

```json
{
  "schemaVersion": "1.0",
  "type": "lipsync.frame",
  "source": "control-web",
  "sessionId": "uuid",
  "seq": 1200,
  "timestampMs": 20001.4,
  "expiresAtMs": 20101.4,
  "priority": "realtime",
  "payload": {
    "engine": "wlipsync",
    "volume": 0.42,
    "mouthOpen": 0.57,
    "confidence": 0.81,
    "visemes": {
      "REST": 0.01,
      "A": 0.62,
      "I": 0.13,
      "U": 0.02,
      "E": 0.18,
      "O": 0.03,
      "MBP": 0.01,
      "FV": 0.0
    },
    "dominant": "A",
    "audioTimestampMs": 19962.0
  }
}
```

规则：

- 权重范围 `[0,1]`；
- 总和允许小于/大于 1，消费者统一归一化；
- `mouthOpen` 与视素形态分开；
- `audioTimestampMs` 用于估计端到端延迟；
- overlay 只使用最新未过期 frame；
- 后端不需要保存每帧历史。

## 5.2 `prosody.frame`

频率 20–50 Hz：

```json
{
  "type": "prosody.frame",
  "payload": {
    "rms": 0.18,
    "peak": 0.42,
    "noiseFloor": 0.015,
    "vadFast": true,
    "pitchHz": 178.2,
    "pitchConfidence": 0.72,
    "speechRate": 0.55,
    "onset": 0.31
  }
}
```

用途：身体脉冲、头部轻动、物理倍率。所有字段可为 `null`，不能用 0 代表“未知”。

# 6. Binary PCM 音频协议

## 6.1 格式

- 16 kHz；
- mono；
- signed 16-bit little-endian PCM；
- 推荐每帧 20 ms，即 320 samples/640 bytes；
- 不压缩，localhost 上减少编码开销；
- WebSocket binary frame 前置固定 header。

建议 header：

| 偏移 | 类型 | 内容 |
|---:|---|---|
| 0 | uint8 | protocol version = 1 |
| 1 | uint8 | flags（speech/continuation/end 等） |
| 2 | uint16 | header bytes |
| 4 | uint32 | sequence |
| 8 | float64 | capture timestamp ms |
| 16 | uint32 | sample rate |
| 20 | uint16 | channels |
| 22 | uint16 | samples per channel |
| 24 | bytes | PCM payload |

## 6.2 背压

- 浏览器发送队列超过 200 ms 时丢弃最旧 PCM，并上报；
- 不允许无限缓存追赶；
- ASR 服务忙时可降低 partial 频率，但不能让音频延迟累积数秒；
- VAD 静音期间可只发送低频 keepalive 或暂停 PCM；
- 断线重连后不补发旧音频。

# 7. ASR 消息

## 7.1 `asr.partial`

```json
{
  "type": "asr.partial",
  "source": "speech-service",
  "payload": {
    "utteranceId": "uuid",
    "text": "我现在准备",
    "language": "zh",
    "confidence": 0.73,
    "audioStartMs": 32000.0,
    "audioEndMs": 32900.0,
    "revision": 4
  }
}
```

partial 可以被同一 `utteranceId` 的后续 revision 替换。

## 7.2 `asr.final`

```json
{
  "type": "asr.final",
  "source": "speech-service",
  "payload": {
    "utteranceId": "uuid",
    "text": "我现在准备开始实现。",
    "language": "zh",
    "confidence": 0.88,
    "audioStartMs": 32000.0,
    "audioEndMs": 34320.0,
    "tokens": [
      {"text": "我", "startMs": 32010.0, "endMs": 32200.0, "confidence": 0.91}
    ]
  }
}
```

`tokens` 可缺省。ASR 辅助口型只在时间戳存在且足够新时使用。

# 8. 情绪与事件消息

## 8.1 `emotion.raw`

```json
{
  "type": "emotion.raw",
  "source": "speech-service",
  "payload": {
    "windowStartMs": 41000.0,
    "windowEndMs": 42300.0,
    "scores": {
      "neutral": 0.44,
      "happy": 0.29,
      "angry": 0.06,
      "sad": 0.04,
      "surprised": 0.17
    },
    "modelLabel": "happy",
    "modelVersion": "sensevoice-small"
  }
}
```

## 8.2 `emotion.state`

只由状态机输出：

```json
{
  "type": "emotion.state",
  "source": "speech-service",
  "payload": {
    "state": "happy",
    "intensity": 0.58,
    "confidence": 0.71,
    "enteredAtMs": 42050.0,
    "minHoldUntilMs": 43050.0,
    "automatic": true,
    "reason": "rolling-vote"
  }
}
```

## 8.3 `audio.event`

```json
{
  "type": "audio.event",
  "payload": {
    "event": "laughter",
    "confidence": 0.84,
    "startMs": 51000.0,
    "endMs": 51800.0
  }
}
```

# 9. 参数消息与优先级

## 9.1 参数来源优先级

从高到低：

1. `emergency`：闭嘴、reset、暂停；
2. `manual-lock`：用户锁定表情/姿势；
3. `macro`：热键或外部命令；
4. `emotion-event`：惊讶、笑声等短事件；
5. `emotion-state`：稳定情绪；
6. `lipsync/prosody`：实时音频；
7. `idle`：自动眨眼、呼吸、随机视线；
8. `default`。

同一参数采用权重混合或覆盖策略，必须在参数注册表中声明。

## 9.2 `parameter.frame`

高频聚合消息：

```json
{
  "type": "parameter.frame",
  "payload": {
    "values": {
      "mouth.open": 0.61,
      "viseme.A": 0.72,
      "viseme.I": 0.18,
      "eye.open.left": 0.94,
      "eye.open.right": 0.95,
      "head.y": 0.04,
      "body.bounce": 0.09,
      "physics.hair.multiplier": 1.08
    }
  }
}
```

## 9.3 `parameter.set`

用于手动单项设置：

```json
{
  "type": "parameter.set",
  "payload": {
    "id": "expression.thoughtful",
    "value": 1.0,
    "sourceMode": "manual-lock",
    "transitionMs": 250,
    "ttlMs": null
  }
}
```

## 9.4 `expression.set` 与 `pose.set`

- 预设名称必须来自配置；
- 不存在时返回错误，不静默创建；
- 支持 `transitionMs`、`holdMs`、`priority`、`interruptible`；
- 互斥姿势由状态机保证。

# 10. 参数注册表

至少定义以下标准 ID：

## 10.1 嘴

- `mouth.open`
- `mouth.jawY`
- `viseme.REST/A/I/U/E/O/MBP/FV`
- `mouth.smile`
- `mouth.tense`
- `mouth.sad`

## 10.2 眼

- `eye.open.left/right`
- `eye.gazeX.left/right`
- `eye.gazeY.left/right`
- `eye.pupilScale.left/right`
- `eye.highlight.left/right`
- `eye.smile.left/right`
- `eye.surprised.left/right`

## 10.3 眉

- `brow.height.left/right`
- `brow.angle.left/right`
- `brow.inner.left/right`

## 10.4 头与身体

- `head.x/y/z`
- `body.leanX/leanY`
- `body.breath`
- `body.bounce`
- `body.speechPulse`

## 10.5 物理

- `physics.global`
- `physics.hair.multiplier`
- `physics.cape.multiplier`
- `physics.accessory.multiplier`
- 每组 `physics.<group>.stiffness/damping/gravity/maxAngle`

## 10.6 表情与 FX

- `expression.<preset>`
- `fx.star.intensity`
- `fx.eyeGlow.left/right`
- `fx.chestGlow`
- `fx.inspirationHalo`
- `face.blush`
- `face.shadow.serious/tired`

## 10.7 姿势

- `pose.hand.left.present/idle`
- `pose.hand.right.idle/wave/point`

每个参数在 schema 中包含：

- type；
- min/max/default；
- blend mode；
- smoothing；
- priority policy；
- persistence；
- UI metadata；
- renderer binding。

# 11. 全量快照与恢复

## 11.1 `state.snapshot.request`

客户端连接或发现 seq 缺口时请求。

## 11.2 `state.snapshot`

包含：

- 当前角色/profile；
- 持久配置版本；
- 手动锁定；
- 当前稳定情绪；
- 当前姿势；
- 当前参数静态值；
- 不包含过期的实时视素 frame；
- 不包含秘密或原始音频。

重连后：

1. 应用快照；
2. 清空本地物理速度或使用安全恢复；
3. 消费新的 realtime frame；
4. 300–500 ms 平滑进入当前状态。

# 12. 配置 API

推荐资源：

- `GET /api/config`
- `PUT /api/config`
- `POST /api/config/validate`
- `POST /api/config/import`
- `GET /api/config/export`
- `GET /api/profiles`
- `POST /api/profiles/:id/activate`
- `GET /api/assets/report`
- `POST /api/assets/validate`

写入要求：

- optimistic concurrency (`etag`/revision)；
- 原子写入临时文件后 replace；
- 自动备份最近版本；
- schema 校验；
- 导入前 diff；
- 秘密字段单独存储。

# 13. 日志与指标

## 13.1 日志字段

- timestamp；
- level；
- component；
- event；
- sessionId；
- correlationId；
- durationMs；
- error code；
- redacted details。

禁止默认记录：

- 原始 PCM；
- 完整 ASR 文本；
- OBS 密码/token；
- 用户路径中不必要的个人信息。

## 13.2 指标

- `lipsync_latency_ms` p50/p95；
- `asr_inference_ms`；
- `emotion_inference_ms`；
- `ws_rtt_ms`；
- `ws_dropped_frames`；
- `audio_underruns`；
- `overlay_fps`；
- `render_frame_ms`；
- `webgl_context_loss_total`；
- `model_load_seconds`；
- `process_memory_bytes`；
- `gpu_vram_bytes`（可得时）。

# 14. 故障与降级状态

| 故障 | 系统行为 |
|---|---|
| speech-service 未启动 | 控制页提示；wLipSync、idle、手动控制继续 |
| wLipSync profile 缺失 | 切换音量回退；提示校准 |
| AudioWorklet 失败 | 尝试重建；仍失败则手动/测试模式 |
| 麦克风断开 | 平滑闭嘴、回 idle、提示重新选择 |
| overlay 断线 | 控制页显示；服务端保留配置但不缓存 realtime 历史 |
| 控制页断线 | overlay 平滑回 idle；后端不保留音频 |
| WebGL context lost | overlay 尝试恢复并重新加载角色；上报错误 |
| 情绪模型超时 | 保持 neutral/上一稳定状态；不影响口型 |
| ASR 队列堆积 | 丢弃旧 partial，保留最近音频或重新分段 |
| 配置损坏 | 备份损坏文件、加载默认、显示可恢复提示 |

# 15. 安全边界

- 默认只监听 loopback；
- 控制和 overlay 使用不同 token 权限；
- overlay token 只读；
- 不接受任意文件路径，所有路径限制在项目数据根目录；
- 模型下载 URL 使用白名单/明确来源；
- 不从 ASR 文本执行命令；
- 外部热键/OSC/HTTP 命令只允许预定义 action；
- WebUI 不渲染未经转义的 ASR HTML；
- 诊断包先展示内容再导出。

# 16. 测试契约

必须维护：

- 同一消息的 TS/Python golden fixture；
- 旧 minor 版本兼容 fixture；
- seq 乱序、重复、丢失测试；
- NaN/Infinity/超范围拒绝测试；
- 断线、重连、快照恢复测试；
- PCM header round-trip；
- 背压和丢弃策略测试；
- overlay 只读权限测试；
- 日志脱敏测试。
