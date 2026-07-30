# 项目状态与阶段记录

> 本文件是本地 Codex 每个阶段完成后必须更新的进度入口。不要只在聊天记录中报告进度。

## 当前状态

- 当前版本：规格与资产规划基线
- 当前阶段：Phase 0 尚未开始
- 可直播运行时：尚未实现
- 主参考图缩略预览：已纳入 `assets/reference/character_reference_preview.webp`
- 主参考图完整源文件：克隆后需复制到 `assets/reference/local/character_reference_source.png` 并通过校验
- 资产清单：已定义
- 运行时协议：已定义初版
- WebUI 功能范围：已定义
- Windows 11 安装与启动流程：已规划

## 阶段清单

- [ ] Phase 0：工程骨架、依赖锁定、健康检查、测试框架
- [ ] Phase 1：资产目录、manifest 校验器、合成预览、alpha QA
- [ ] Phase 2：Anime2.5DRig 基线导入、透明渲染、overlay 页面
- [ ] Phase 3：WebSocket 参数总线、control/overlay 分离
- [ ] Phase 4：wLipSync、个人声音校准、音量回退口型
- [ ] Phase 5：SenseVoice 服务、VAD、ASR、字幕
- [ ] Phase 6：情绪状态机、表情和动作映射
- [ ] Phase 7：完整 WebUI、预设、热键、诊断页
- [ ] Phase 8：OBS 引导、透明输出验收、可选 OBS WebSocket
- [ ] Phase 9：Windows 一键安装、启动、更新与故障恢复
- [ ] Phase 10：性能、稳定性、长时间运行和发布验收

## 当前已知阻塞项

1. 角色分层透明 PNG 尚未生成。
2. Anime2.5DRig 具体锁定提交 SHA 尚未确定。
3. wLipSync 的个人声音 Profile 尚未采集。
4. SenseVoice 模型权重尚未下载并接受对应许可条款。
5. OBS 场景尚未建立。

## 阶段报告模板

每次完成阶段后，将以下内容追加到“阶段历史”：

```markdown
### YYYY-MM-DD — Phase N：阶段名称

- 状态：完成 / 部分完成 / 阻塞
- 提交：<commit SHA>
- 环境：Windows 11；GPU；Node/Python/驱动版本
- 已完成：
  - ...
- 自动测试：
  - 命令：...
  - 结果：...
- 手工验收：
  - 步骤：...
  - 结果：...
- 性能数据：
  - FPS：...
  - 延迟：...
  - 显存/内存：...
- 已知限制：
  - ...
- 下一阶段阻塞：
  - ...
```

## 阶段历史

尚无运行时实施记录。
