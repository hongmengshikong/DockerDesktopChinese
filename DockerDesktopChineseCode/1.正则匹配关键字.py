import re
import pandas as pd


def extract_strings_to_table(filename):
    # 打开并读取文件内容
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # 使用正则表达式匹配children:"%s"中的内容
    children_pattern = r'children:"(.*?)"'
    children_matches = re.findall(children_pattern, content)

    # 使用正则表达式匹配label:"%s"中的内容
    label_pattern = r'label:"(.*?)"'
    label_matches = re.findall(label_pattern, content)

    # 创建DataFrame，将每条内容放在单独的一列
    df_children = pd.DataFrame({'String': children_matches})
    df_label = pd.DataFrame({'String': label_matches})

    # 合并两个DataFrame
    df = pd.concat([df_children, df_label], ignore_index=True)

    # 打印DataFrame
    print(df)

    # 将结果保存到xlsx文件
    # df.to_excel('extracted_strings.xlsx', index=False)


# 调用函数并传递文件名
extract_strings_to_table('F:/信息安全/逆向学习/docker/build/desktop-ui-build/5983.bundle.js')
