from converter import TraditionalSimplifiedConverter
import tkinter as tk
import os

def test_encoding_detection():
    """测试编码检测和转换功能"""
    print("=" * 60)
    print("测试编码检测和转换功能")
    print("=" * 60)

    # 创建临时窗口
    root = tk.Tk()
    root.withdraw()
    app = TraditionalSimplifiedConverter(root)

    # 测试文件列表
    test_files = [
        ('test_utf8.txt', 'UTF-8'),
        ('test_gbk.txt', 'GBK'),
        ('test_gb2312.txt', 'GB2312')
    ]

    print("\n1. 编码检测测试:")
    print("-" * 60)
    for filename, expected_encoding in test_files:
        if os.path.exists(filename):
            text, detected_encoding, confidence = app.read_file_with_encoding(filename)
            print(f"文件: {filename}")
            print(f"  期望编码: {expected_encoding}")
            print(f"  检测编码: {detected_encoding}")
            print(f"  置信度: {confidence:.2%}")
            print(f"  读取内容长度: {len(text)} 字符")
            print()

    print("\n2. 文件转换测试:")
    print("-" * 60)
    app.direction_var.set("t2s")  # 繁体转简体

    for filename, _ in test_files:
        if os.path.exists(filename):
            output_file = f"output_{filename}"
            success, error, stats = app.convert_file(filename, output_file)

            print(f"文件: {filename}")
            if success:
                print(f"  [OK] 转换成功")
                print(f"  原始编码: {stats.get('original_encoding', 'unknown')}")
                print(f"  编码置信度: {stats.get('encoding_confidence', 0):.2%}")
                print(f"  总字符: {stats['total_chars']}")
                print(f"  变化字符: {stats['changed_chars']}")
                print(f"  一对多转换: {stats['one_to_many']}个")
                print(f"  多对一转换: {stats['many_to_one']}个")

                # 验证输出文件编码
                with open(output_file, 'rb') as f:
                    output_encoding = chardet.detect(f.read())
                print(f"  输出编码: {output_encoding['encoding']} (置信度: {output_encoding['confidence']:.2%})")

                if stats['examples']:
                    print(f"  转换示例:")
                    for example in stats['examples'][:3]:
                        print(f"    {example}")
            else:
                print(f"  [FAIL] 转换失败: {error}")
            print()

    print("=" * 60)
    print("测试完成!")
    print("=" * 60)

    # 清理临时文件
    for filename, _ in test_files:
        output_file = f"output_{filename}"
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"已清理临时文件: {output_file}")

if __name__ == "__main__":
    import chardet
    test_encoding_detection()
