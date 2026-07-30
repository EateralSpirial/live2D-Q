# Third-party components and license notes

本文件记录计划使用的第三方项目。实现阶段必须锁定具体提交 SHA，并在 `third_party/lock.json` 或等价文件中记录。

> 本仓库自身的最终许可证尚未由仓库所有者明确指定。不要在未经确认时擅自添加项目级许可证。

| 组件 | 官方来源 | 计划用途 | 代码许可证/注意事项 |
|---|---|---|---|
| See-through | https://github.com/shitagaki-lab/see-through | 单图动漫角色语义拆层、遮挡补全、PSD 输出 | Apache-2.0；研究项目，不等同完整 Live2D 自动绑定 |
| ComfyUI-See-through | https://github.com/jtydhr88/ComfyUI-See-through | 可选的资产拆层 UI 与 PSD 导出 | MIT；第三方封装，不替代官方项目条款 |
| Anime2.5DRig | https://github.com/852wa/Anime2.5DRig | PSD 自动绑定、WebGL 渲染、头发物理和基础 UI | MIT；保留原许可证和修改记录 |
| wLipSync | https://github.com/mrxz/wLipSync | 浏览器 MFCC/WASM 低延迟口型 | MIT；需要校准 profile；AudioWorklet 要求 localhost 或 HTTPS |
| uLipSync | https://github.com/hecomi/uLipSync | wLipSync 的校准参考和算法来源 | 使用前核对仓库当前许可证；不得只复制代码而漏掉声明 |
| SenseVoice | https://github.com/QwenAudio/SenseVoice | ASR、语言识别、语音情绪与事件标签 | 仓库源码 MIT；官方权重使用独立的 FunASR Model Open Source License，下载时单独确认与记录 |
| FunASR | https://github.com/modelscope/FunASR | SenseVoice 加载、VAD、时间戳等 | 使用前锁定版本和许可证；避免无界升级 |
| OBS Studio Browser Source | https://obsproject.com/kb/browser-source | 透明网页输入 OBS | OBS 为开源软件；本项目只提供兼容页面，不捆绑 OBS 二进制 |
| OBS Spout2 plugin（可选） | https://github.com/Off-World-Live/obs-spout2-plugin | 未来原生纹理/Alpha 输出适配 | GPL-2.0；作为独立插件安装，不应把其代码混入不兼容模块 |
| ag-psd | https://github.com/Agamnentzar/ag-psd | 浏览器 PSD 解析/导出，Anime2.5DRig 已使用 | MIT；保留许可证 |
| MediaPipe（可选） | https://github.com/google-ai-edge/mediapipe | 仅保留为可选鼠标/摄像头实验，不属于主路线 | Apache-2.0；主项目不要求摄像头 |

## 模型和二进制管理规则

1. 模型权重不提交到 GitHub；使用下载脚本和校验和。
2. 下载前展示来源、目标目录、大小、许可证链接和是否允许商业使用。
3. 下载后写入本地 `models.lock.local.json`，记录文件哈希和模型卡版本；该文件默认不提交。
4. 第三方转换权重（ONNX、GGUF、量化版）必须单独核对模型卡，不能假定继承官方说明。
5. 不分发第三方示例角色、PSD、音频样例或可能含有未授权素材的测试数据。
6. 对 fork 的第三方源码保留上游 URL、提交 SHA、许可证和本项目修改清单。
