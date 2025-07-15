import re
import sys
import os

def convert_hex_to_dec_in_dts_v2(input_file_path, output_file_path):
    """
    读取DTS文件，将其中以0x开头的十六进制数值转换为十进制。
    此版本尝试更鲁棒地处理字符串和注释，避免误转换。
    """
    
    # 匹配所有以 0x 开头，后面跟着一个或多个十六进制字符的序列
    # 这里的 \b 确保是单词边界，避免匹配到变量名的一部分
    hex_pattern = re.compile(r'\b0x[0-9a-fA-F]+\b')

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            content = f_in.read()
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_file_path}' 未找到。")
        return
    except Exception as e:
        print(f"读取输入文件时发生错误：{e}")
        return

    # 用于存储最终转换后的内容
    converted_content_parts = []
    last_idx = 0

    # 遍历所有匹配到的十六进制数
    for match in hex_pattern.finditer(content):
        hex_str = match.group(0)
        start, end = match.span()

        # 将当前匹配之前的文本添加到结果中
        converted_content_parts.append(content[last_idx:start])

        # 检查当前匹配是否在字符串或注释中
        # 1. 检查是否在字符串中 (双引号内部)
        # 查找当前匹配之前和之后最近的双引号数量
        preceding_quotes = content.count('"', 0, start)
        following_quotes = content.count('"', end)
        
        # 如果前面有奇数个双引号，并且后面有奇数个双引号，则认为在字符串内部
        # 这是一个简化的判断，可能不完美，但对于大多数情况有效
        is_in_string = (preceding_quotes % 2 == 1) and (following_quotes % 2 == 1)

        # 2. 检查是否在 // 注释中
        # 找到当前行
        line_start = content.rfind('\n', 0, start) + 1
        line_end = content.find('\n', end)
        if line_end == -1: # 如果是最后一行
            line_end = len(content)
        current_line = content[line_start:line_end]
        
        single_line_comment_idx = current_line.find('//')
        is_in_single_line_comment = False
        if single_line_comment_idx != -1:
            # 如果 // 在十六进制数之前，则认为在注释中
            if (line_start + single_line_comment_idx) < start:
                is_in_single_line_comment = True

        # 3. 检查是否在 /* */ 块注释中
        # 这是一个更复杂的判断，需要跟踪块注释的状态
        # 我们可以通过查找最近的 /* 和 */ 来判断
        block_comment_start_idx = content.rfind('/*', 0, start)
        block_comment_end_idx = content.rfind('*/', 0, start)
        
        is_in_block_comment = False
        if block_comment_start_idx != -1 and \
           (block_comment_end_idx == -1 or block_comment_start_idx > block_comment_end_idx):
            # 找到了一个未闭合的 /* 在当前匹配之前
            # 还需要检查当前匹配之后是否有 */ 来闭合它
            next_block_comment_end_idx = content.find('*/', end)
            if next_block_comment_end_idx != -1:
                is_in_block_comment = True

        # 如果不在字符串、单行注释或块注释中，则进行转换
        if not is_in_string and not is_in_single_line_comment and not is_in_block_comment:
            try:
                dec_val = int(hex_str, 16)
                converted_content_parts.append(str(dec_val))
            except ValueError:
                # 转换失败，保留原始十六进制字符串
                converted_content_parts.append(hex_str)
        else:
            # 在字符串或注释中，保留原始十六进制字符串
            converted_content_parts.append(hex_str)
        
        last_idx = end

    # 添加文件中剩余的部分
    converted_content_parts.append(content[last_idx:])

    final_converted_content = "".join(converted_content_parts)

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            f_out.write(final_converted_content)
        print(f"成功将 '{input_file_path}' 中的十六进制转换为十进制，并保存到 '{output_file_path}'。")
    except Exception as e:
        print(f"写入输出文件时发生错误：{e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python dts_hex_to_dec_v2.py <input_dts_file> [output_dts_file]")
        print("  <input_dts_file>：要转换的DTS文件路径。")
        print("  [output_dts_file]：可选，转换后DTS文件的保存路径。")
        print("                     如果未指定，则默认为 'input_dts_file_dec.dts'。")
        sys.exit(1)

    input_dts_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_dts_file = sys.argv[2]
    else:
        # 自动生成输出文件名
        base_name = os.path.splitext(input_dts_file)[0]
        output_dts_file = f"{base_name}_dec.dts"

    convert_hex_to_dec_in_dts_v2(input_dts_file, output_dts_file)