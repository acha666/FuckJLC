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
* `rules/*.yml` 针对不同软件 Gerber 的识别规则
* `filetype_defaults.yml` 针对不同 Gerber 层的默认处理逻辑

# 规则文件

规则文件是一个 YAML 文件，指定用于把输入文件匹配为具体 Gerber 层或文件作用的规则

示例：

```yaml
# Gerber 文件只需匹配到内置的文件类型，将套用内置的默认处理逻辑
- filename_pattern: "^.*\\.GTL$"
  filetype: TopLayer

# 钻孔文件以及钻孔映射文件可能需要自定义输出规则
- filename_pattern: "^.*\\.TXT$"
  filetype: Custom_Drill
  content_pattern: "^M48" # 仅匹配以 M48 开头的文件
  action: include # 不添加文件头
  missing_warning: true # 匹配不到时发出警告
  output: '{project}_DrillDrawing.DRL' # 自定义输出文件名
```

| 字段               | 必需  | 作用                                 |
| :----------------- | :---: | :----------------------------------- |
| `filename_pattern` |   ✅   | 文件名正则 (Python RE)               |
| `filetype`         |   ✅   | 自定义的文件类型名，与 defaults 对应 |
| `action`           |   ❌   | `include` / `add_header` / `exclude` |
| `output`           |   ❌   | 输出模板，优先于 defaults            |
| `ext`              |   ❌   | 指定扩展名，占位符 `{ext}` 时必需    |
| `content_pattern`  |   ❌   | 对文件内容再匹配 (Python RE)         |
| `missing_warning`  |   ❌   | 该类型缺失时是否报警                 |

# 提示

目前仅对有限格式的 Gerber 做适配，其他软件请发 Issue 并附带目录结构或者自力更生 PR

脚本并未严格测试，仅给各位提供一个绕过检测的思路，保险起见仍建议各位手动进行修改

作者并没有仔细研究嘉立创的判定规则，目前看来凑合能用，就这样吧

作者不为使用脚本造成的任何后果负责

欢迎一切 新功能 / bug / 建议 / 对线 / 改错字 Issue / PRs

# 工作原理

脚本将会将你的 Gerber 重命名为立创 EDA 的命名格式，并在 Gerber 文件的头部添加立创 EDA 的注释信息

除此之外，脚本不会做任何处理

**低调使用**

**嘉立创舔狗什么时候死啊**
