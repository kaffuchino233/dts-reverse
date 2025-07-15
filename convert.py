import re
import sys
import os

def convert_hex_to_dec_in_dts(input_file_path, output_file_path):
    """
    读取DTS文件，将其中以0x开头的十六进制数值转换为十进制。
    尝试避免转换字符串和注释中的十六进制数。
    """
    
    # 正则表达式用于匹配以 0x 开头的十六进制数字
    # \b 确保是单词边界，避免匹配到变量名的一部分
    # [0-9a-fA-F]+ 匹配一个或多个十六进制字符
    hex_pattern = re.compile(r'\b0x[0-9a-fA-F]+\b')

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_file_path}' 未找到。")
        return
    except Exception as e:
        print(f"读取输入文件时发生错误：{e}")
        return

    converted_lines = []
    in_block_comment = False # 标记是否在 /* ... */ 块注释中

    for line_num, line in enumerate(lines, 1):
        original_line = line
        modified_line = line

        # 1. 处理块注释 /* ... */
        # 简单的块注释处理，不处理嵌套
        if '/*' in line:
            in_block_comment = True
        if '*/' in line:
            in_block_comment = False
            # 如果 /* 和 */ 在同一行，则只处理注释之外的部分
            if '/*' in line and '*/' in line:
                comment_start_idx = line.find('/*')
                comment_end_idx = line.find('*/') + 2
                # 尝试只在注释之外的部分进行转换
                part_before_comment = line[:comment_start_idx]
                part_after_comment = line[comment_end_idx:]
                
                # 转换注释之外的部分
                part_before_comment = hex_pattern.sub(lambda m: str(int(m.group(0), 16)), part_before_comment)
                part_after_comment = hex_pattern.sub(lambda m: str(int(m.group(0), 16)), part_after_comment)
                
                modified_line = part_before_comment + line[comment_start_idx:comment_end_idx] + part_after_comment
                converted_lines.append(modified_line)
                continue # 跳过当前行的后续处理

        if in_block_comment:
            converted_lines.append(original_line)
            continue # 在块注释中，不进行转换

        # 2. 处理行内注释 //
        # 找到 // 的位置
        single_line_comment_idx = line.find('//')
        if single_line_comment_idx != -1:
            # 分割行：注释前和注释后
            code_part = line[:single_line_comment_idx]
            comment_part = line[single_line_comment_idx:]
            
            # 只在代码部分进行十六进制转换
            code_part = hex_pattern.sub(lambda m: str(int(m.group(0), 16)), code_part)
            modified_line = code_part + comment_part
        else:
            # 如果没有行内注释，则对整行进行转换
            modified_line = hex_pattern.sub(lambda m: str(int(m.group(0), 16)), modified_line)

        # 3. 避免转换字符串中的十六进制数
        # 这是一个更复杂的场景，简单的正则表达式替换可能无法完美处理。
        # 我们可以尝试一个更复杂的替换函数，它在替换前检查是否在字符串内部。
        # 但对于DTS文件，数值通常不在字符串中，所以上述简单的处理可能已经足够。
        # 如果需要更严格的字符串排除，需要更复杂的解析逻辑，例如：
        # 遍历行中的所有匹配，然后检查每个匹配是否被双引号包围。
        
        # 重新检查，确保不在字符串中
        # 这是一个简化的检查，可能不完全准确，但对于大多数情况有效
        # 查找当前匹配之前最近的双引号
        
        # 重新实现替换逻辑，以避免字符串中的转换
        temp_line = []
        last_idx = 0
        in_string = False
        
        # 遍历行中的字符，识别字符串和非字符串区域
        for i, char in enumerate(original_line):
            if char == '"':
                in_string = not in_string
            
            if not in_string:
                # 如果不在字符串中，则处理从 last_idx 到当前位置的文本
                segment = original_line[last_idx:i]
                segment = hex_pattern.sub(lambda m: str(int(m.group(0), 16)), segment)
                temp_line.append(segment)
                last_idx = i
            
            # 将当前字符添加到结果中
            temp_line.append(char)
            last_idx = i + 1
            
        # 处理行尾剩余部分
        segment = original_line[last_idx:]
        segment = hex_pattern.sub(lambda m: str(int(m.group(0), 16)), segment)
        temp_line.append(segment)
        
        modified_line = "".join(temp_line)

        converted_lines.append(modified_line)

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            f_out.writelines(converted_lines)
        print(f"成功将 '{input_file_path}' 中的十六进制转换为十进制，并保存到 '{output_file_path}'。")
    except Exception as e:
        print(f"写入输出文件时发生错误：{e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python hex_to_dec_dts_converter.py <input_dts_file> [output_dts_file]")
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

    convert_hex_to_dec_in_dts(input_dts_file, output_dts_file)