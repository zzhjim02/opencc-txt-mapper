import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import opencc
import threading
import os
import chardet
from pathlib import Path


class TraditionalSimplifiedConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("TXT文件繁简转换器")
        self.root.geometry("800x600")
        
        # 文件列表
        self.file_list = []
        self.conversion_direction = "t2s"  # 默认繁体转简体
        
        # 创建UI
        self.create_ui()
    
    def create_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        # 文件选择按钮
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="选择TXT文件", command=self.select_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空列表", command=self.clear_files).pack(side=tk.LEFT, padx=(0, 5))
        
        # 文件数量显示
        self.file_count_label = ttk.Label(button_frame, text="已选择 0 个文件")
        self.file_count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 文件列表显示
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 文件列表框和滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.file_listbox.yview)
        
        # 转换设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="转换设置", padding="10")
        settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 转换方向选择
        direction_frame = ttk.Frame(settings_frame)
        direction_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(direction_frame, text="转换方向:").pack(side=tk.LEFT)
        
        self.direction_var = tk.StringVar(value="t2s")
        ttk.Radiobutton(direction_frame, text="繁体转简体", variable=self.direction_var, 
                       value="t2s").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(direction_frame, text="简体转繁体", variable=self.direction_var, 
                       value="s2t").pack(side=tk.LEFT, padx=(0, 5))
        
        # 输出目录选择
        output_frame = ttk.Frame(settings_frame)
        output_frame.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT)
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        self.output_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(output_frame, text="浏览", command=self.select_output_dir).pack(side=tk.LEFT)
        
        # 文件命名方式
        name_frame = ttk.Frame(settings_frame)
        name_frame.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(name_frame, text="文件命名:").pack(side=tk.LEFT)
        self.naming_var = tk.StringVar(value="suffix")
        ttk.Radiobutton(name_frame, text="添加后缀", variable=self.naming_var, 
                       value="suffix").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(name_frame, text="覆盖原文件", variable=self.naming_var, 
                       value="overwrite").pack(side=tk.LEFT, padx=(0, 5))
        
        # 后缀设置
        self.suffix_var = tk.StringVar(value="_converted")
        self.suffix_entry = ttk.Entry(name_frame, textvariable=self.suffix_var, width=15)
        self.suffix_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # 进度显示
        progress_frame = ttk.LabelFrame(main_frame, text="转换进度", padding="10")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # 转换按钮
        button_frame2 = ttk.Frame(main_frame)
        button_frame2.grid(row=4, column=0, pady=(0, 10))
        
        self.convert_button = ttk.Button(button_frame2, text="开始转换", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame2, text="退出", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置日志文本样式
        self.log_text.tag_config('info', foreground='black')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='orange')
    
    def select_files(self):
        """选择要转换的TXT文件"""
        files = filedialog.askopenfilenames(
            title="选择TXT文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if files:
            for file in files:
                if file not in self.file_list:
                    self.file_list.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))
            
            self.file_count_label.config(text=f"已选择 {len(self.file_list)} 个文件")
            self.log_message(f"添加了 {len(files)} 个文件到列表", 'info')
    
    def clear_files(self):
        """清空文件列表"""
        self.file_list.clear()
        self.file_listbox.delete(0, tk.END)
        self.file_count_label.config(text="已选择 0 个文件")
        self.log_message("已清空文件列表", 'info')
    
    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_path_var.set(directory)
            self.log_message(f"输出目录设置为: {directory}", 'info')
    
    def log_message(self, message, level='info'):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + '\n', level)
        self.log_text.see(tk.END)
        self.root.update()
    
    def detect_encoding(self, file_path):
        """自动检测文件编码"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result['encoding'], result['confidence']
        except Exception as e:
            return None, 0
    
    def read_file_with_encoding(self, file_path):
        """尝试用不同编码读取文件"""
        # 常见的中文编码列表
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'utf-16', 'utf-16-le', 'utf-16-be', 'ascii']
        
        # 首先尝试自动检测
        detected_encoding, confidence = self.detect_encoding(file_path)
        if detected_encoding and confidence > 0.7:
            try:
                with open(file_path, 'r', encoding=detected_encoding) as file:
                    return file.read(), detected_encoding, confidence
            except:
                pass
        
        # 如果自动检测失败，尝试常见编码
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                    # 检查是否有乱码（简单检查）
                    if '\ufffd' not in content:  # 没有替换字符
                        return content, encoding, 1.0
            except:
                continue
        
        # 如果所有编码都失败，使用utf-8并忽略错误
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read(), 'utf-8 (with errors)', 0.5
        except:
            return None, None, 0
    
    def convert_file(self, input_path, output_path):
        """转换单个文件，返回统计信息"""
        try:
            # 自动检测编码并读取文件
            text, detected_encoding, confidence = self.read_file_with_encoding(input_path)
            
            if text is None:
                return False, "无法读取文件或识别编码", None
            
            # 转换文本
            direction = self.direction_var.get()
            cc = opencc.OpenCC(direction)
            converted_text = cc.convert(text)
            
            # 统计转换信息
            stats = self.analyze_conversion(text, converted_text)
            
            # 添加编码信息到统计
            stats['original_encoding'] = detected_encoding
            stats['encoding_confidence'] = confidence
            
            # 统一写入UTF-8编码
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(converted_text)
            
            return True, None, stats
        except Exception as e:
            return False, str(e), None
    
    def analyze_conversion(self, original_text, converted_text):
        """分析转换结果，统计一对多和多对一转换"""
        stats = {
            'total_chars': len(original_text),
            'changed_chars': 0,
            'one_to_many': 0,
            'many_to_one': 0,
            'examples': []
        }
        
        # 找出所有发生变化的字符
        changed_pairs = []
        for i, (orig_char, conv_char) in enumerate(zip(original_text, converted_text)):
            if orig_char != conv_char:
                changed_pairs.append((orig_char, conv_char))
                stats['changed_chars'] += 1
        
        # 分析一对多和多对一转换
        one_to_many = {}  # 繁体 -> 多个简体
        many_to_one = {}  # 多个简体 -> 一个繁体
        
        # 构建映射关系
        for orig, conv in changed_pairs:
            if orig not in one_to_many:
                one_to_many[orig] = set()
            one_to_many[orig].add(conv)
            
            if conv not in many_to_one:
                many_to_one[conv] = set()
            many_to_one[conv].add(orig)
        
        # 统计一对多转换（一个繁体对应多个简体）
        for trad, simp_set in one_to_many.items():
            if len(simp_set) > 1:
                stats['one_to_many'] += len(simp_set) - 1
                stats['examples'].append(f"一对多: {trad} -> {', '.join(simp_set)}")
        
        # 统计多对一转换（多个简体对应一个繁体）
        for simp, trad_set in many_to_one.items():
            if len(trad_set) > 1:
                stats['many_to_one'] += len(trad_set) - 1
                stats['examples'].append(f"多对一: {', '.join(trad_set)} -> {simp}")
        
        # 只保留前5个示例
        stats['examples'] = stats['examples'][:5]
        
        return stats
    
    def start_conversion(self):
        """开始转换过程"""
        if not self.file_list:
            messagebox.showwarning("警告", "请先选择要转换的文件")
            return
        
        # 检查输出目录
        output_dir = self.output_path_var.get()
        if not output_dir:
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.log_message(f"创建输出目录: {output_dir}", 'info')
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录: {str(e)}")
                return
        
        # 禁用转换按钮
        self.convert_button.config(state='disabled')
        
        # 在新线程中执行转换
        thread = threading.Thread(target=self.process_conversion)
        thread.start()
    
    def process_conversion(self):
        """处理转换过程"""
        total_files = len(self.file_list)
        success_count = 0
        error_count = 0
        total_stats = {
            'total_chars': 0,
            'changed_chars': 0,
            'one_to_many': 0,
            'many_to_one': 0,
            'all_examples': []
        }
        
        self.log_message(f"开始转换 {total_files} 个文件...", 'info')
        
        for i, input_path in enumerate(self.file_list):
            # 更新状态
            self.status_label.config(text=f"正在转换: {i + 1}/{total_files}")
            self.log_message(f"处理文件 {i + 1}/{total_files}: {os.path.basename(input_path)}", 'info')
            
            # 生成输出路径
            input_filename = os.path.basename(input_path)
            input_name, input_ext = os.path.splitext(input_filename)
            
            naming = self.naming_var.get()
            if naming == "suffix":
                suffix = self.suffix_var.get()
                output_filename = f"{input_name}{suffix}{input_ext}"
            else:  # overwrite
                output_filename = input_filename
            
            output_path = os.path.join(self.output_path_var.get(), output_filename)
            
            # 转换文件
            success, error, stats = self.convert_file(input_path, output_path)
            
            if success:
                success_count += 1
                self.log_message(f"✓ 成功: {output_filename}", 'success')
                
                # 显示统计信息
                if stats:
                    # 显示编码信息
                    original_encoding = stats.get('original_encoding', 'unknown')
                    confidence = stats.get('encoding_confidence', 0)
                    self.log_message(f"  原始编码: {original_encoding} (置信度: {confidence:.2%})", 'info')
                    self.log_message(f"  输出编码: UTF-8", 'info')
                    
                    self.log_message(f"  总字符: {stats['total_chars']}, 变化字符: {stats['changed_chars']}", 'info')
                    if stats['one_to_many'] > 0:
                        self.log_message(f"  一对多转换: {stats['one_to_many']}个", 'warning')
                    if stats['many_to_one'] > 0:
                        self.log_message(f"  多对一转换: {stats['many_to_one']}个", 'warning')
                    
                    # 显示示例
                    for example in stats['examples']:
                        self.log_message(f"  {example}", 'warning')
                    
                    # 累计统计
                    total_stats['total_chars'] += stats['total_chars']
                    total_stats['changed_chars'] += stats['changed_chars']
                    total_stats['one_to_many'] += stats['one_to_many']
                    total_stats['many_to_one'] += stats['many_to_one']
                    total_stats['all_examples'].extend(stats['examples'])
            else:
                error_count += 1
                self.log_message(f"✗ 失败: {input_filename} - {error}", 'error')
            
            # 更新进度条
            progress = ((i + 1) / total_files) * 100
            self.progress['value'] = progress
        
        # 转换完成，显示总体统计
        self.log_message("=" * 50, 'info')
        self.log_message("转换完成统计:", 'info')
        self.log_message(f"文件: 成功 {success_count}, 失败 {error_count}", 'info')
        self.log_message(f"总字符数: {total_stats['total_chars']}", 'info')
        self.log_message(f"变化字符数: {total_stats['changed_chars']}", 'info')
        self.log_message(f"一对多转换: {total_stats['one_to_many']}个", 'warning')
        self.log_message(f"多对一转换: {total_stats['many_to_one']}个", 'warning')
        
        # 显示独特的转换示例
        unique_examples = list(set(total_stats['all_examples']))
        if unique_examples:
            self.log_message("转换示例:", 'info')
            for example in unique_examples[:10]:
                self.log_message(f"  {example}", 'warning')
        
        self.status_label.config(text=f"转换完成! 成功: {success_count}, 失败: {error_count}")
        
        # 重新启用转换按钮
        self.convert_button.config(state='normal')


def main():
    root = tk.Tk()
    app = TraditionalSimplifiedConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
