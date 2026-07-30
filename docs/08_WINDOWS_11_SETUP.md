# 08｜Windows 11 本地环境与启动规划

本文面向 RTX 4090 24 GB 的 Windows 11 主机。当前为实施规格；Codex 建立实际脚本后，应把示例命令替换为经过验证的一键流程。

## 1. 为什么使用原生 Windows

直播主流程需要同时访问：

- 麦克风；
- OBS Studio；
- OBS Browser Source/CEF；
- NVIDIA GPU；
- 浏览器权限；
- 可选 Spout2 和全局热键。

因此主应用建议原生 Windows 运行。WSL 可用于一般开发，但不作为麦克风和 OBS 运行时的默认环境。

## 2. 预备软件

建议安装：

- Git for Windows；
- Git LFS；
- PowerShell 7（Windows PowerShell 也可作为兼容目标）；
- Node.js 当前 LTS；
- pnpm 或仓库最终锁定的包管理器；
- Python 3.11，用于 speech-service；
- Miniforge/Miniconda，用于 See-through Python 3.12 环境；
- OBS Studio；
- 最新稳定 NVIDIA 驱动；
- Edge 或 Chrome；
- 可选 Krita/Photoshop，用于人工检查资产；
- 可选 ComfyUI，用于 See-through UI 路线。

Codex 应提供 `scripts/doctor.ps1` 检测具体版本，不应只在文档中让用户猜。

## 3. NVIDIA 与 CUDA

先运行：

```powershell
nvidia-smi
```

确认：

- 能识别 RTX 4090；
- 驱动没有报错；
- 直播时没有其他程序长期占满显存。

优先使用项目锁定的 PyTorch CUDA wheel。除非某个依赖明确需要编译 CUDA 扩展，否则不要把系统级 CUDA Toolkit 设为首要前置条件。

## 4. 克隆仓库

```powershell
git clone https://github.com/EateralSpirial/live2D-Q.git
cd live2D-Q
git lfs install
```

仓库中的 PNG 可以普通 Git 管理；未来 PSD/Krita 大文件按 `.gitattributes` 使用 Git LFS。

## 5. 目录建议

项目代码：

```text
D:\Projects\live2D-Q\
```

本地模型和缓存建议放在独立数据根目录，例如：

```text
D:\AIModels\live2D-Q\
├─ sensevoice\
├─ funasr\
├─ see-through\
└─ cache\
```

用户配置建议：

```text
%LOCALAPPDATA%\live2D-Q\
├─ config\
├─ profiles\
├─ logs\
└─ diagnostics\
```

不要把模型、缓存、录音和秘密放进 Git 工作树。

## 6. Python 环境隔离

## 6.1 speech-service

使用 Python 3.11 的独立 `.venv`：

```powershell
py -3.11 -m venv services\speech-service\.venv
services\speech-service\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
# 后续由锁定 requirements/uv.lock 安装
```

该环境只放：

- FastAPI/Uvicorn；
- SenseVoice/FunASR；
- 音频处理；
- Pydantic；
- 测试和诊断。

## 6.2 See-through

按上游要求使用独立 Python 3.12 Conda 环境。不要把其 diffusers、PyTorch、分割依赖装进 speech-service 环境。

概念命令：

```powershell
conda create -n live2dq-seethrough python=3.12 -y
conda activate live2dq-seethrough
# 按锁定上游提交和 requirements 安装
```

资产生成是离线阶段。直播时不启动 See-through。

## 7. Node/WebUI 环境

项目最终应固定 Node 与包管理器版本，例如通过：

- `packageManager` 字段；
- `.node-version` 或 `.tool-versions`；
- lockfile；
- `corepack`。

概念流程：

```powershell
corepack enable
pnpm install --frozen-lockfile
pnpm test
```

不要在文档和 CI 中混用 npm、yarn、pnpm。

## 8. PowerShell 执行策略

若本地不允许脚本，可在理解风险后仅对当前用户设置：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

安装脚本不得要求关闭系统安全功能，也不得要求全局 `Unrestricted`。

## 9. 预期脚本

Codex 应实现：

| 脚本 | 用途 |
|---|---|
| `scripts/doctor.ps1` | 检查 Git、LFS、Node、Python、Conda、GPU、OBS、端口、模型 |
| `scripts/install.ps1` | 创建环境、安装锁定依赖、下载模型、校验哈希 |
| `scripts/start-dev.ps1` | 开发模式启动后端和 Vite |
| `scripts/start.ps1` | 正式模式启动统一服务并打开控制页 |
| `scripts/stop.ps1` | 优雅停止本项目进程 |
| `scripts/update.ps1` | 更新代码和依赖，保留配置 |
| `scripts/validate-assets.ps1` | 运行资产检查和生成预览 |
| `scripts/benchmark.ps1` | 延迟/FPS/稳定性测试 |
| `scripts/export-diagnostics.ps1` | 导出已脱敏诊断包 |

所有脚本必须：

- 支持带空格路径；
- 支持重复运行；
- 失败时返回非零码；
- 不静默修改系统级设置；
- 打印下一步；
- 记录但不泄露秘密。

## 10. 模型下载

模型下载器应显示：

- 模型名称；
- 官方来源；
- 版本/commit；
- 预计大小；
- 目标目录；
- 许可证链接和确认；
- SHA256；
- 是否需要外网；
- 是否可用镜像源。

下载完成后：

- 校验哈希；
- 写入本地模型锁；
- 测试加载；
- 预热并记录耗时；
- 不提交模型到 Git。

## 11. 麦克风和 Windows 设置

建议：

- 使用有线 USB/XLR 麦克风，降低蓝牙延迟；
- Windows 声音设置确认输入设备和电平；
- 高级属性中避免不必要的独占模式；
- 控制页和 OBS 使用同一设备时测试是否冲突；
- 浏览器首次打开 `/control` 时允许麦克风；
- `/overlay` 不需要麦克风权限；
- 不要在 `file://` 直接打开需要 AudioWorklet 的页面，使用 localhost。

## 12. 防火墙与端口

默认仅监听：

```text
127.0.0.1:8765
```

通常不需要开放 Windows 防火墙入站规则。若启用局域网遥控：

- 显式切换到 LAN 模式；
- 设置 token；
- 限制来源地址；
- 显示安全警告；
- 不暴露模型下载、文件系统或任意命令 API。

## 13. OBS 设置

### 13.1 添加角色

- 来源 → `+` → 浏览器；
- URL：控制页给出的 `/overlay`；
- 宽高：按角色/节目画布；
- 自定义帧率：60；
- 背景保持透明；
- 初期不要启用“不可见时关闭”；
- 把角色源置于背景上方。

### 13.2 颜色和 alpha

Browser Source 使用透明网页。渲染器应以 `(0,0,0,0)` 清屏。对半透明光效，必须用黑/白背景对比检查边缘。

### 13.3 音频同步

- 控制页显示口型延迟估计；
- 在 OBS 麦克风高级音频属性中设置同步偏移；
- 以 60–100 ms 为初始试验范围；
- 使用固定测试向量/拍手法实测；
- 蓝牙耳机和复杂降噪链可能额外增加延迟。

## 14. 建议的 4090 资源使用

- 资产生成阶段：可让 See-through 使用大量显存；不要同时直播；
- 直播阶段：只加载 SenseVoice、角色纹理和 OBS 编码；
- 模型预热后记录稳定 VRAM；
- 若 OBS NVENC、游戏或其他模型同时使用 GPU，提供：
  - 降低情绪推理频率；
  - CPU/ONNX/GGUF 回退；
  - 30 FPS 预设；
  - 关闭高成本 FX；
- 不应因为 24 GB 显存就无限增加图层或纹理。

## 15. 首次启动向导应做什么

1. 检查版本和 GPU；
2. 选择角色包；
3. 选择麦克风；
4. 测量 noise floor；
5. 选择/创建口型 profile；
6. 测试 A/I/U/E/O；
7. 预热 SenseVoice；
8. 测试 ASR 和情绪；
9. 复制 overlay URL；
10. 展示 OBS 添加步骤；
11. 运行 alpha 测试；
12. 保存默认 profile。

## 16. 备份与迁移

备份：

- `assets/generated/`；
- 角色 manifest；
- 口型 profile；
- runtime/animation presets；
- 用户配置；
- 生成记录；
- 不需要备份可重新下载的模型缓存。

升级前：

- 自动备份配置；
- 显示 schema 迁移；
- 保留旧版可回退；
- 不覆盖用户生成的角色资产。

## 17. 卸载

卸载说明应区分：

- 项目代码；
- Python/Node 环境；
- 模型缓存；
- 用户配置；
- 角色资产；
- OBS Browser Source 配置；
- 可选 Spout2 插件。

默认卸载脚本不得删除用户资产和 profile，除非用户再次确认。
