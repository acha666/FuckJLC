# FuckJLC

将其他 EDA 软件的 Gerber 转换为傻逼立创 EDA 格式的脚本

立创 EDA 狗都不用

# Usage

首先查看 `rules` 文件夹，选择适合你的规则或者撰写你自己的规则

然后运行脚本，在输出目录中查看处理完成的 Gerber

``` shell
# yum/apt/brew/scoop/winget install python3
pip install pyyaml

python3 modify.py \
  -i gerbers/ \
  -o outputs/ \
  -r rules/your-rule.yml
```
# CLI 选项

| 选项                  | 说明                                |
| :-------------------- | :---------------------------------- |
| `-i, --input-dir`     | 输入目录（优先级高于 `config.yml`） |
| `-o, --output-dir`    | 输出目录（优先级高于 `config.yml`） |
| `-c, --config-file`   | 全局配置文件路径，默认 `config.yml` |
| `-r, --rule-file`     | 规则文件路径                        |
| `-d, --defaults-file` | 文件类型默认值文件路径，可选        |
| `--dry-run`           | 仅输出计划，不写入文件              |
| `-f, --force`         | 覆盖已存在的目标文件                |
| `-h, --help`          | 显示帮助并退出                      |

# 文件结构

* `modify.py` 脚本主文件
* `config.yml` 通用配置信息
* `rules/*.yml` 针对不同软件 Gerber 的匹配规则
* `filetype_defaults.yml` 针对不同 Gerber 层的默认处理逻辑

# 规则文件（`rules/*.yml`）

规则文件是一个 YAML 文件，只负责把输入文件映射到某个 `filetype`，其余处理逻辑完全来自 filetype 定义。

示例：

```yaml
# 1) 直接引用已有 filetype —— 顶层铜层
- filename_pattern: '^.*-F_Cu\\.gbr$'
  filetype: TopLayer            # 脚本将在 defaults 中查找 TopLayer 的处理方式

# 2) 新增或覆盖 filetype —— 钻孔映射图
- filename_pattern: '.*-PTH-drl_map\.gbr$'
  content_pattern: 'FileFunction,Drillmap'    # 仅匹配 Gerber X2 格式的钻孔映射
  filetype: 
    name: DrillMapping_PTH                    # 新 filetype 名（或覆盖同名）
    action: include                           # 此处可写 filetype 级别的 action
    ext: "GBR"                                # 强制扩展名
    output: "{project}_DrillMapping_PTH.{ext}"
    missing_warning: false
```

| 字段               | 必需  | 说明                                             |
| ------------------ | :---: | ------------------------------------------------ |
| `filename_pattern` |   ✅   | 文件名正则（Python RE）                          |
| `content_pattern`  |   ❌   | （可选）再按文件内容匹配，常用于区分同扩展名文件 |
| `filetype`         |   ✅   | - **字符串**：引用现有 filetype                  |
|                    |       | - **对象**：见上述示例，用于新增/覆盖配置        |

# Filetype 文件（`filetype_defaults.yml`）

每个 filetype 都可被规则文件覆盖

示例：

```yaml
Outline:
  ext: GKO
  layer_name: BoardOutlineLayer  # 用于默认输出文件名
  action: add_header             # include / add_header / exclude
  missing_warning: true          # 如缺失则报警
  # 可选，自定义输出模板；未写时使用默认 {project}_{layer_name}.{ext}
  # output: "{project}_{layer_name}.{ext}"
```

# 提示

目前仅对有限格式的 Gerber 做适配，其他软件请发 Issue 并附带目录结构或者自力更生 PR

脚本并未严格测试，仅给各位提供一个绕过检测的思路，保险起见仍建议各位手动进行修改

作者并没有仔细研究嘉立创的判定规则，目前看来凑合能用，就这样吧

作者不为使用脚本造成的任何后果负责

欢迎一切 新功能 / bug / 建议 / 对线 / 改错字 Issue / PRs

# 工作原理

脚本将会将你的 Gerber 重命名为立创 EDA 的命名格式，并在 Gerber 文件的头部添加立创 EDA 的注释信息

**低调使用**

**嘉立创舔狗什么时候死啊**
