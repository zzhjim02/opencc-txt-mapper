import opencc

# 测试繁体转简体
test_cases = ['乾浄', '髮型', '麵包', '後來', '併購', '裏面', '隻有', '製作', '鐘錶', '衝突']
cc = opencc.OpenCC('t2s')

print('繁体 -> 简体转换测试:')
for t in test_cases:
    s = cc.convert(t)
    print(f'{t} -> {s}')

print('\n简体 -> 繁体转换测试:')
test_cases_simp = ['干净', '发型', '面包', '后来', '并购', '里面', '只有', '制作', '钟表', '冲突']
cc_s2t = opencc.OpenCC('s2t')

for t in test_cases_simp:
    s = cc_s2t.convert(t)
    print(f'{t} -> {s}')

# 测试一对多和多对一
print('\n复杂转换测试:')
complex_text = "乾浄的髮型設計師正在製作麵包，後來決定併購。"
converted = cc.convert(complex_text)
print(f'原文: {complex_text}')
print(f'转换: {converted}')
