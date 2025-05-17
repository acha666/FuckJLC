import os
import re
import shutil
import argparse
import sys
from typing import Dict, Any, List

try:
    import yaml  # 需要安装 PyYAML
except ImportError:
    print("未找到 PyYAML，请先执行：pip install pyyaml")
    sys.exit(1)

# ─────────────────────────── ANSI 颜色工具 ─────────────────────────── #
_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"


def _color(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}"


def info(msg: str):
    print(_color(msg, _CYAN))


def success(msg: str):
    print(_color(msg, _GREEN))


def warning(msg: str):
    print(_color(msg, _YELLOW))


def error(msg: str):
    print(_color(msg, _RED))


# ─────────────────────────── CLI 解析 ─────────────────────────── #


def parse_cli():
    """返回 (args, parser) 方便后续在错误时打印帮助。"""
    usage_example = (
        "示例:\n"
        "  python pcb_processor.py -i gerbers/ -o out/ -r rules.yml\n"
        "  python pcb_processor.py --dry-run --force\n"
    )
    parser = argparse.ArgumentParser(
        description="根据规则批量处理 PCB Gerber / Drill 文件，支持添加头部、复制和排除等操作。",
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input-dir", help="输入文件目录，优先于配置文件中的 input_dir"
    )
    parser.add_argument(
        "-o", "--output-dir", help="输出文件目录，优先于配置文件中的 output_dir"
    )
    parser.add_argument(
        "-c",
        "--config-file",
        default="config.yml",
        help="配置文件路径 (默认: config.yml)",
    )
    parser.add_argument(
        "-r", "--rule-file", help="YAML 规则文件路径，优先于配置文件中的 rule_file"
    )
    parser.add_argument(
        "-d",
        "--defaults-file",
        help="filetype 默认值文件路径，优先于配置文件中的 defaults_file",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="干运行，仅输出计划，不写入文件"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="强制覆盖已存在的目标文件"
    )
    return parser.parse_args(), parser


# ─────────────────────────── YAML 加载 ─────────────────────────── #


def load_yaml(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        error(f"未找到 YAML 文件: {file_path}")
        raise
    except Exception as exc:
        error(f"读取 YAML 文件失败: {file_path} — {exc}")
        raise


# ─────────────────────────── 工具函数 ─────────────────────────── #


def _file_content_matches(
    file_path: str, regex_obj: re.Pattern, lines_to_read: int
) -> bool:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            head = "".join([next(f) for _ in range(lines_to_read)])
    except StopIteration:
        pass
    except Exception:
        return False
    else:
        return bool(regex_obj.search(head))
    return False


# ─────────────────────────── 主逻辑 ─────────────────────────── #


def main():
    args, parser = parse_cli()

    # 1. 加载全局配置
    config_ok = True
    try:
        config = load_yaml(args.config_file)
    except FileNotFoundError:
        config_ok = False
        config = {}

    # 若无参数且配置文件读取失败 → 输出帮助并退出
    if len(sys.argv) == 1 and not config_ok:
        parser.print_help(sys.stderr)
        sys.exit(1)

    rule_file = args.rule_file or config.get("rule_file")
    input_dir = args.input_dir or config.get("input_dir")
    output_base_dir = args.output_dir or config.get("output_dir")

    # 检查必须字段
    missing_fields = []
    if not rule_file:
        missing_fields.append("rule_file")
    if not input_dir:
        missing_fields.append("input_dir")
    if not output_base_dir:
        missing_fields.append("output_dir")

    if len(sys.argv) == 1 and missing_fields:
        warning(f"配置文件缺少必需参数: {', '.join(missing_fields)}\n")
        parser.print_help(sys.stderr)
        sys.exit(1)

    if missing_fields:
        error(f"缺少必需参数: {', '.join(missing_fields)}")
        sys.exit(1)

    # 校验文件路径
    if not os.path.exists(rule_file):
        error(f"规则文件不存在: {rule_file}")
        sys.exit(1)

    defaults_file = (
        args.defaults_file or config.get("defaults_file") or "filetype_defaults.yml"
    )
    if args.defaults_file and not os.path.exists(defaults_file):
        warning(f"未找到 defaults 文件: {defaults_file}，将跳过 filetype 默认覆盖。")

    # 统一绝对路径
    input_dir = os.path.abspath(input_dir)
    output_base_dir = os.path.abspath(output_base_dir)

    project = config.get("project", "")
    header_text = config.get("header", "")
    read_lines = config.get("read_lines", 40)
    text_file_name = config.get("TextFileName")
    text_file_content = config.get("TextFileContent")

    if header_text and project:
        try:
            header_text = header_text.format(project=project)
        except Exception:
            pass

    dry_run = args.dry_run
    force = args.force

    # 2. 读取 filetype
    filetypes: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(defaults_file):
        try:
            filetypes = load_yaml(defaults_file)
        except Exception:
            pass

    # 3. 解析规则
    try:
        rules_data = load_yaml(rule_file)
    except Exception:
        sys.exit(1)

    if not isinstance(rules_data, list):
        error("规则文件格式应为列表 (list)。")
        sys.exit(1)

    rules: List[Dict[str, Any]] = []
    for entry in rules_data:
        if not isinstance(entry, dict):
            continue
        pattern = entry.get("filename_pattern")
        ft_field = entry.get("filetype")
        if not pattern or not ft_field:
            warning("跳过缺少 filename_pattern 或 filetype 的规则。")
            continue

        try:
            filename_regex = re.compile(pattern, flags=re.IGNORECASE)
        except re.error as exc:
            warning(f"无效的 filename_pattern: {pattern} — {exc}，已跳过。")
            continue

        content_regex = None
        if entry.get("content_pattern"):
            try:
                content_regex = re.compile(entry["content_pattern"])
            except re.error as exc:
                warning(f"无效 content_pattern: {exc}，已忽略。")

        # 处理 filetype
        # 3-A 字符串 → 引用
        if isinstance(ft_field, str):
            ft_name = ft_field
            if ft_name not in filetypes:
                error(f"规则引用了未定义的 filetype: {ft_name}")
                sys.exit(1)

        # 3-B 对象 → 新增/覆盖
        elif isinstance(ft_field, dict):
            ft_name = ft_field.get("name")
            if not ft_name:
                error("自定义 filetype 缺少 name 字段。")
                sys.exit(1)
            base = filetypes.get(ft_name, {})
            filetypes[ft_name] = {
                **base,
                **{k: v for k, v in ft_field.items() if k != "name"},
            }

        else:
            error("filetype 字段类型非法，应为字符串或对象。")
            sys.exit(1)

        rules.append(
            {
                "filetype": ft_name,
                "filename_regex": filename_regex,
                "content_regex": content_regex,
            }
        )

    if not rules:
        error("未找到任何有效规则，终止运行。")
        sys.exit(1)

    # 4. 遍历输入目录文件
    processed_types = set()
    try:
        all_files = [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
    except FileNotFoundError:
        error(f"输入目录不存在: {input_dir}")
        sys.exit(1)

    info(f"共发现 {len(all_files)} 个文件。")

    for src_path in all_files:
        matches = [
            r for r in rules if r["filename_regex"].search(os.path.basename(src_path))
        ]
        if len(matches) > 1:
            matches = [
                r
                for r in matches
                if r["content_regex"] is None
                or _file_content_matches(src_path, r["content_regex"], read_lines)
            ]
        if len(matches) != 1:
            if len(matches) > 1:
                warning(f"文件 '{src_path}' 同时匹配多条规则，已跳过。")
            continue

        rule = matches[0]
        ft_field = rule["filetype"]
        props = filetypes.get(ft_field, {})

        if rule["content_regex"] and not _file_content_matches(
            src_path, rule["content_regex"], read_lines
        ):
            continue

        # filetype 属性
        action = props.get("action", "include")
        ext_cfg = props.get("ext")
        layer_name = props.get("layer_name", ft_field)
        default_tpl = "{project}_{layer_name}.{ext}"
        output_tpl = props.get("output", default_tpl)

        # ext
        ext_final = (ext_cfg or os.path.splitext(src_path)[1].lstrip(".") or "").lstrip(
            "."
        )

        rel_out = output_tpl.format(
            project=project, layer_name=layer_name, ext=ext_final
        )

        dest_path = os.path.join(output_base_dir, rel_out)
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.isdir(dest_dir):
            if dry_run:
                info(f"[DRY-RUN] 将创建目录: {dest_dir}")
            else:
                os.makedirs(dest_dir, exist_ok=True)

        if action == "exclude":
            info(f"排除文件: {src_path} (类型 {ft_field})")
            processed_types.add(ft_field)
            continue

        if os.path.exists(dest_path) and not force:
            warning(f"目标已存在，使用 --force 覆盖: {dest_path}")
            continue

        if dry_run:
            info(
                f"[DRY-RUN] {src_path} -> {dest_path} (类型 {ft_field}, action {action})"
            )
            processed_types.add(ft_field)
        else:
            try:
                if action == "add_header":
                    with open(
                        src_path, "r", encoding="utf-8", errors="ignore"
                    ) as src, open(
                        dest_path, "w", encoding="utf-8", errors="ignore"
                    ) as dst:
                        if header_text:
                            dst.write(header_text + "\n")
                        shutil.copyfileobj(src, dst)
                else:
                    shutil.copyfile(src_path, dest_path)
                success(
                    f"已处理 '{src_path}' -> '{dest_path}' (类型 {ft_field}, action: {action})"
                )
                processed_types.add(ft_field)
            except Exception as e:
                error(f"处理文件 '{src_path}' 时出错: {e}")

    # 5. 检查必需文件类型缺失
    for ft_field, props in filetypes.items():
        if props.get("missing_warning") and ft_field not in processed_types:
            warning(f"未处理文件类型 '{ft_field}'。")

    # 6. 可选文档文件
    if text_file_name and text_file_content is not None:
        content = str(text_file_content)
        if project:
            try:
                content = content.format(project=project)
            except Exception:
                pass
        doc_path = os.path.join(output_base_dir, text_file_name)
        if os.path.exists(doc_path) and not force:
            warning(f"文档文件 '{doc_path}' 已存在，使用 --force 可覆盖。")
        else:
            if dry_run:
                info(f"[DRY-RUN] 将写入文档文件 '{doc_path}'")
            else:
                try:
                    with open(doc_path, "w", encoding="utf-8") as docf:
                        docf.write(content)
                    success(f"已生成文档文件: '{doc_path}'")
                except Exception as e:
                    error(f"无法写入文档文件 '{doc_path}': {e}")


if __name__ == "__main__":
    main()
