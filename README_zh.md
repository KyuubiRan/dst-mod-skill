# DST Mod Development Skill

[English](./README.md)

这是一个面向《饥荒联机版》Mod 开发的本地 Skill 仓库，用于帮助 Codex 在编写、分析、调试 DST Mod 时参考官方游戏脚本。

它的核心目标很简单：

- 先查官方 `scripts.zip`
- 再确认运行上下文和主客机边界
- 最后用最窄、最稳的方式实现或修复功能

## 适用范围

这个 Skill 主要覆盖以下工作：

- 分析 `modinfo.lua` / `modmain.lua`
- 判断 Mod 类型：`all-clients` / `client-only` / `server-only`
- 查找和验证常用 Hook，如 `AddPrefabPostInit`、`AddComponentPostInit`
- 分析 prefab / component / stategraph / brain / widget / screen
- 把用户意图映射到常见组件组合与 prefab tag
- 处理 recipe、placer、asset、RPC、replica、classified、netvar
- 用共享工厂模式组织重复度高的 prefab 家族
- 做症状驱动的排查和 Lua 调试

## 设计原则

- 以本地 DST 官方安装文件为准
- 默认优先读取 `data/databundles/scripts.zip`
- 能用现成 Hook 时，不整段复制官方函数
- 先分清 server / client / local UI，再写代码
- 对已有 Mod，先读 `modinfo.lua` 判断类型，再决定实现路径

## 仓库结构

```text
.
├─ SKILL.md
├─ agents/
├─ references/
└─ scripts/
```

- `SKILL.md`
  - Skill 主说明，定义工作流、使用原则和阅读顺序
- `agents/`
  - agent 元信息
- `references/`
  - 主题化速查文档，包括 creation、UI、action、networking、brain、recipe、assets、diagnostics 等
- `scripts/`
  - 辅助脚本
  - `dst_zip_tool.py`：直接检索官方 `scripts.zip`
  - `init_dst_mod.py`：生成基础 Mod 骨架

## 依赖环境

- 本地安装《饥荒联机版》
- 常见 Windows 游戏路径：
  - `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- 常见 Windows 脚本包路径：
  - `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip`
- 常见 Linux 游戏路径：
  - `~/.local/share/Steam/steamapps/common/Don't Starve Together`
- 常见 Linux 脚本包路径：
  - `~/.local/share/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- 常见 macOS 游戏路径：
  - `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`
- 常见 macOS 脚本包路径：
  - `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- Python 3

如果你的游戏路径不同，建议在使用时明确提供路径，避免引用错误的官方文件。

## 常用命令

列出匹配文件：

```bash
python scripts/dst_zip_tool.py list modutil
```

搜索符号：

```bash
python scripts/dst_zip_tool.py grep AddPrefabPostInit --path-glob "scripts/*.lua"
```

查看源码片段：

```bash
python scripts/dst_zip_tool.py show scripts/entityscript.lua --start 600 --end 700
```

提取官方文件：

```bash
python scripts/dst_zip_tool.py extract scripts/modutil.lua --output tmp/modutil.lua
```

生成新 Mod：

```bash
python scripts/init_dst_mod.py .\MyNewMod --display-name "My New Mod" --description "Short summary" --mod-type all-clients
```

## 文档重点

`references/` 里比较常用的几类文档：

- `official-files.md`
  - 先看哪些官方文件
- `component-patterns.md`
  - 高频组件、组件组合、反向约束
- `tag-patterns.md`
  - 高频 tag、tag 来源、tag 路由含义
- `task-playbook.md`
  - 任务分流与排查顺序
- `creation-patterns.md`
  - prefab / component / replica 的创建与加载
- `animstate-patterns.md`
  - `AnimState`、动画切换、图层与通道
- `template-patterns.md`
  - 常见最小模板与变体 prefab 工厂模式
- `diagnostic-patterns.md`
  - 按症状排查问题
- `debug-techniques.md`
  - Lua `debug` 高级技巧，如 upvalue patch

## 推荐的 Agent 工作流

当这个 Skill 被用于 agent 工作流时，推荐流程是：

1. 先确认本地 DST 路径可读
2. 先读目标 Mod 的 `modinfo.lua`
3. 判断它是客户端、服务端还是全端 Mod
4. 再去查最小的官方源码入口
5. 最后才动代码
