# 角色参考图

本目录中的 `character_reference_preview.webp` 是用于 GitHub 文档预览的缩略图，**不可作为正式分层资产生成的唯一输入**。

在 Windows 11 本地克隆仓库后，请将本项目的原始主图复制到：

```text
assets/reference/local/character_reference_source.png
```

原始文件应满足：

- 尺寸：1254×1254；
- 格式：PNG；
- 色彩：RGBA；
- 当前 alpha 全部不透明，粉色背景与角色已合并；
- SHA-256：`a8699cd228353110c0ddc16b0d46721143400d6d5008273a24f03c340eacfb4b`。

复制完成后运行：

```powershell
python scripts/check_reference.py
```

校验通过后，Phase 1 的拆层、补画和资产生成任务才可以开始。`assets/reference/local/` 默认被 Git 忽略，避免重复提交原始大图或后续私有参考素材。
