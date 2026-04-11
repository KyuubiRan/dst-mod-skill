# DST Mod Development Skill

[English](./README.md)

[![QQ Group](https://img.shields.io/badge/QQ-%E7%82%B9%E5%87%BB%E5%8A%A0%E7%BE%A4-12B7F5?style=for-the-badge&logo=tencentqq&logoColor=white&labelColor=111111)](https://qm.qq.com/cgi-bin/qm/qr?k=5hu7noeDQkIOMUGOXOCXa7Ot6DSAU2U0&jump_from=webapi&authKey=2L/jTywWWu78ZMpASDZC0YCfJXnwLHKiIvCBIobvVQmcBEqUSUfVbwG2/r+sSt4g)

这个仓库是一套面向《饥荒联机版》Mod 开发的本地 Skill。
它的目标不是替你“猜” DST 的实现，而是让 Codex 先查官方源码，再用更稳、更窄的方式完成 Mod 开发与排错。

## 这个 Skill 能做什么

- 阅读 `modinfo.lua`、`modmain.lua` 和相关入口文件
- 判断一个 Mod 是 `all-clients`、`client-only` 还是 `server-only`
- 把需求路由到 prefab、component、brain、stategraph、widget、screen、RPC、replica、persistence、shard 等正确层级
- 根据需求推断常见组件组合和 prefab tag
- 排查主机和远端客户端不一致、存档读档异常、Master 与 Caves 分片问题
- 快速检索官方 `scripts.zip` 与 `images.zip`

## 仓库里包含什么

- `SKILL.md`
  - Skill 的核心说明、工作原则和路由规则
- `references/`
  - 顶层索引文档加分层子目录，例如 `patterns/`、`signatures/`、`pitfalls/`、`templates/` 和 `components/`
- `scripts/check_skill.py`
  - 轻量自检脚本
- `scripts/dst_zip_tool.py`
  - 用于检索、阅读、提取官方 DST `scripts.zip`
- `scripts/init_dst_mod.py`
  - 用于生成基础 DST Mod 骨架
- `scripts/bundle_release.py`
  - 用于按排除规则和增量同步生成发布目录
- `scripts/tex_atlas_tool.py`
  - 用于解包官方或本地 atlas TEX/XML，或把多张 PNG 打成一个 atlas
- `scripts/resize_png.py`
  - 用于调整单张或整批 PNG 的尺寸，方便贴图工作流

## 设计原则

这套 Skill 主要遵循三条规则：

- 优先以本地官方 DST 文件为准
- 能用更窄的 Hook，就不整段复制官方实现
- 写代码前先分清 server、client、local UI、persistence 和 shard 边界

实际使用时通常会优先查看：

- `data/databundles/scripts.zip`
- `data/databundles/images.zip`

## 适合处理的任务

- “先看一下这个 Mod 到底是什么类型。”
- “帮我做一个武器 / 容器 / 生物 / 建筑 prefab。”
- “给现有 UI 或 HUD 打一个小补丁，不要整段重写。”
- “为什么主机上能用，远端客户端不生效？”
- “这个数据到底应该放在 `OnSave`、`OnLoadPostPass` 还是 `LongUpdate`？”
- “官方分片迁移是怎么处理这个问题的？”
- “帮我解包官方物品图集看看贴图内容。”

## 环境要求

- 本地安装《饥荒联机版》
- Python 3
- `tex_atlas_tool.py` 和 `resize_png.py` 需要 `Pillow`

常见游戏路径：

- Windows：
  - `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Linux：
  - `~/.local/share/Steam/steamapps/common/Don't Starve Together`
- macOS：
  - `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`

常见脚本包路径：

- `data/databundles/scripts.zip`

常见贴图包路径：

- `data/databundles/images.zip`

如果你的游戏安装在非默认目录，使用时最好明确告诉它路径。

执行脚本或 shell 命令时，要注意给路径里的特殊字符做正确引用或转义。
像 `Don't Starve Together` 这种带单引号的目录名，如果不处理好，第一次执行时就可能直接报错，白跑一轮。

## 常用命令

检索官方源码：

```bash
python scripts/dst_zip_tool.py grep AddPrefabPostInit --path-glob "scripts/*.lua"
```

查看一段官方源码：

```bash
python scripts/dst_zip_tool.py show scripts/entityscript.lua --start 600 --end 700
```

生成新 Mod：

```bash
python scripts/init_dst_mod.py .\MyNewMod --display-name "My New Mod" --description "Short summary" --mod-type all-clients
```

生成发布目录：

```bash
python scripts/bundle_release.py . --output ..\MyMod_release
```

解包官方图集：

```bash
python scripts/tex_atlas_tool.py unpack inventoryimages1
```

调整贴图尺寸：

```bash
python scripts/resize_png.py path/to/icon.png 64x64
```

运行仓库自检：

```bash
python scripts/check_skill.py
```

## 建议先看哪些文档

如果你第一次接触这个仓库，优先看这些入口：

- `SKILL.md`
- `references/task-playbook.md`
- `references/official-examples.md`
- `references/patterns.md`
- `references/patterns/modinfo-patterns.md`
- `references/patterns/modmain-patterns.md`
- `references/component-patterns.md`
- `references/feature-recipes.md`
- `references/patterns/networking-patterns.md`
- `references/patterns/persistence-patterns.md`
- `references/patterns/shard-patterns.md`
- `references/patterns/ui-patterns.md`
- `references/patterns/effects-patterns.md`

## 推荐使用方式

1. 如果 DST 不在默认目录，先告诉它本地游戏路径。
2. 先让它读目标 Mod 的 `modinfo.lua`。
3. 先判断 Mod 类型，再进入运行时实现。
4. 让它先查最接近需求的官方源码文件。
5. 再根据官方实现选择最窄的 Hook 或补丁位置。
6. 最后再做验证，不要只凭第一次 patch 成功就结束。
