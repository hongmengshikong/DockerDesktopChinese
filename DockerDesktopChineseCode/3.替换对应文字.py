import re
import pandas as pd


def replace_strings_in_file(source_filename, excel_filename, output_filename):
    # 读取Excel文件
    df = pd.read_excel(excel_filename)

    # 打开并读取源文件内容
    with open(source_filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # 替换内容
    for _, row in df.iterrows():
        original_string = row['Original String']
        # 如果没有 'Translated String' 列或者 'Translated String' 为空，则跳过该行
        if 'Translated String' not in row or pd.isna(row['Translated String']):
            continue
        new_string = row['Translated String']
        type_string = row['Type']

        # 根据类型构建正则表达式进行替换
        if type_string == 'children':
            content = re.sub(r'children:"' + re.escape(original_string) + r'"', 'children:"' + new_string + r'"',
                             content)
        elif type_string == 'label':
            content = re.sub(r'label:"' + re.escape(original_string) + r'"', 'label:"' + new_string + r'"', content)

    # 将替换后的内容保存到新的文件中
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(content)


# 调用函数进行替换
replace_strings_in_file('F:/信息安全/逆向学习/docker/build/desktop-ui-build/5983.bundle.js', 'extracted_strings.xlsx',
                        'modified_5983.bundle.js')
