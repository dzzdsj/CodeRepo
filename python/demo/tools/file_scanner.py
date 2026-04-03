# file_scanner.py
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

class FileScanner:
    """
    硬盘文件扫描和整理工具
    """

    def __init__(self):
        self.file_stats = defaultdict(int)
        self.size_stats = defaultdict(int)
        self.extension_stats = defaultdict(int)
        self.files_info = []

    def scan_directory(self, directory: str) -> Dict:
        """
        扫描指定目录中的所有文件

        Args:
            directory: 要扫描的目录路径

        Returns:
            包含扫描结果的字典
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"目录 {directory} 不存在")

        self.file_stats.clear()
        self.size_stats.clear()
        self.extension_stats.clear()
        self.files_info.clear()

        total_files = 0
        total_size = 0

        # 遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # 获取文件信息
                    stat = os.stat(file_path)
                    size = stat.st_size
                    ext = os.path.splitext(file)[1].lower() or '无扩展名'

                    # 记录文件信息
                    self.files_info.append({
                        'path': file_path,
                        'name': file,
                        'size': size,
                        'extension': ext,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })

                    # 更新统计信息
                    total_files += 1
                    total_size += size
                    self.extension_stats[ext] += 1

                    # 按文件大小分类
                    if size < 1024:  # < 1KB
                        self.size_stats['<1KB'] += 1
                    elif size < 1024 * 1024:  # 1KB-1MB
                        self.size_stats['1KB-1MB'] += 1
                    elif size < 1024 * 1024 * 1024:  # 1MB-1GB
                        self.size_stats['1MB-1GB'] += 1
                    else:  # >1GB
                        self.size_stats['>1GB'] += 1

                except (OSError, IOError) as e:
                    print(f"无法访问文件 {file_path}: {e}")

        return {
            'total_files': total_files,
            'total_size': total_size,
            'file_stats': dict(self.file_stats),
            'size_stats': dict(self.size_stats),
            'extension_stats': dict(self.extension_stats),
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def get_largest_files(self, count: int = 10) -> List[Dict]:
        """
        获取最大的几个文件

        Args:
            count: 返回文件数量

        Returns:
            包含最大文件信息的列表
        """
        sorted_files = sorted(self.files_info, key=lambda x: x['size'], reverse=True)
        return sorted_files[:count]

    def get_files_by_extension(self, extension: str) -> List[Dict]:
        """
        根据扩展名获取文件列表

        Args:
            extension: 文件扩展名

        Returns:
            包含指定扩展名文件的列表
        """
        return [f for f in self.files_info if f['extension'] == extension]

    def organize_files_by_extension(self, source_dir: str, target_dir: str,
                                  move: bool = False) -> Dict[str, int]:
        """
        按扩展名整理文件

        Args:
            source_dir: 源目录
            target_dir: 目标目录
            move: True表示移动文件，False表示复制文件

        Returns:
            整理结果统计
        """
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        organized_count = defaultdict(int)

        for root, dirs, files in os.walk(source_dir):
            # 跳过目标目录本身
            if os.path.abspath(root).startswith(os.path.abspath(target_dir)):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower() or 'no_extension'

                # 创建扩展名对应的目录
                ext_dir = os.path.join(target_dir, ext.lstrip('.'))
                if not os.path.exists(ext_dir):
                    os.makedirs(ext_dir)

                # 目标文件路径
                target_path = os.path.join(ext_dir, file)

                try:
                    if move:
                        shutil.move(file_path, target_path)
                    else:
                        shutil.copy2(file_path, target_path)
                    organized_count[ext] += 1
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")

        return dict(organized_count)

    def organize_files_by_size(self, source_dir: str, target_dir: str,
                             move: bool = False) -> Dict[str, int]:
        """
        按文件大小整理文件

        Args:
            source_dir: 源目录
            target_dir: 目标目录
            move: True表示移动文件，False表示复制文件

        Returns:
            整理结果统计
        """
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        organized_count = defaultdict(int)

        for root, dirs, files in os.walk(source_dir):
            # 跳过目标目录本身
            if os.path.abspath(root).startswith(os.path.abspath(target_dir)):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)

                    # 根据文件大小确定目录
                    if size < 1024 * 1024:  # < 1MB
                        size_dir = "small_files"
                    elif size < 100 * 1024 * 1024:  # 1MB-100MB
                        size_dir = "medium_files"
                    else:  # >100MB
                        size_dir = "large_files"

                    # 创建对应目录
                    target_subdir = os.path.join(target_dir, size_dir)
                    if not os.path.exists(target_subdir):
                        os.makedirs(target_subdir)

                    # 目标文件路径
                    target_path = os.path.join(target_subdir, file)

                    if move:
                        shutil.move(file_path, target_path)
                    else:
                        shutil.copy2(file_path, target_path)
                    organized_count[size_dir] += 1

                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")

        return dict(organized_count)

    def generate_report(self, output_file: str = None) -> str:
        """
        生成扫描报告

        Args:
            output_file: 输出文件路径，如果为None则返回报告字符串

        Returns:
            报告内容字符串
        """
        report = []
        report.append("=" * 50)
        report.append("文件扫描报告")
        report.append("=" * 50)
        report.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"文件总数: {len(self.files_info)}")
        report.append(f"总大小: {self._format_size(sum(f['size'] for f in self.files_info))}")
        report.append("")

        # 文件类型统计
        report.append("文件类型统计:")
        report.append("-" * 30)
        for ext, count in sorted(self.extension_stats.items(),
                                key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"{ext}: {count} 个文件")
        report.append("")

        # 文件大小分布
        report.append("文件大小分布:")
        report.append("-" * 30)
        for size_range, count in self.size_stats.items():
            report.append(f"{size_range}: {count} 个文件")
        report.append("")

        # 最大文件
        report.append("最大的10个文件:")
        report.append("-" * 30)
        for i, file_info in enumerate(self.get_largest_files(10), 1):
            report.append(f"{i}. {file_info['name']} "
                         f"({self._format_size(file_info['size'])}) "
                         f"- {file_info['path']}")

        report_content = "\n".join(report)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

        return report_content

    def _format_size(self, size: int) -> str:
        """
        格式化文件大小显示

        Args:
            size: 文件大小（字节）

        Returns:
            格式化后的大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

def main():
    """
    主函数 - 提供命令行交互界面
    """
    scanner = FileScanner()

    while True:
        print("\n" + "="*50)
        print("硬盘文件扫描和整理工具")
        print("="*50)
        print("1. 扫描目录")
        print("2. 查看扫描结果")
        print("3. 按扩展名整理文件")
        print("4. 按大小整理文件")
        print("5. 生成报告")
        print("0. 退出")

        choice = input("\n请选择操作 (0-5): ").strip()

        if choice == '1':
            directory = input("请输入要扫描的目录路径: ").strip()
            try:
                print("正在扫描目录...")
                result = scanner.scan_directory(directory)
                print(f"\n扫描完成！")
                print(f"文件总数: {result['total_files']}")
                print(f"总大小: {scanner._format_size(result['total_size'])}")
            except Exception as e:
                print(f"扫描出错: {e}")

        elif choice == '2':
            if not scanner.files_info:
                print("请先扫描目录！")
                continue

            print("\n1. 查看文件类型统计")
            print("2. 查看最大文件")
            print("3. 按扩展名查找文件")

            sub_choice = input("请选择 (1-3): ").strip()

            if sub_choice == '1':
                print("\n文件类型统计:")
                for ext, count in sorted(scanner.extension_stats.items(),
                                       key=lambda x: x[1], reverse=True):
                    print(f"  {ext}: {count} 个文件")

            elif sub_choice == '2':
                print("\n最大的10个文件:")
                for i, file_info in enumerate(scanner.get_largest_files(10), 1):
                    print(f"  {i}. {file_info['name']} "
                          f"({scanner._format_size(file_info['size'])})")

            elif sub_choice == '3':
                ext = input("请输入文件扩展名 (如 .txt): ").strip()
                files = scanner.get_files_by_extension(ext)
                if files:
                    print(f"\n扩展名为 {ext} 的文件:")
                    for file_info in files:
                        print(f"  {file_info['name']} "
                              f"({scanner._format_size(file_info['size'])}) "
                              f"- {file_info['path']}")
                else:
                    print(f"未找到扩展名为 {ext} 的文件")

        elif choice == '3':
            source = input("请输入源目录路径: ").strip()
            target = input("请输入目标目录路径: ").strip()
            action = input("移动文件还是复制文件? (move/copy): ").strip().lower()

            if not os.path.exists(source):
                print("源目录不存在！")
                continue

            try:
                print("正在整理文件...")
                result = scanner.organize_files_by_extension(
                    source, target, move=(action == 'move'))
                total = sum(result.values())
                print(f"整理完成！共处理 {total} 个文件")
                for ext, count in result.items():
                    print(f"  {ext}: {count} 个文件")
            except Exception as e:
                print(f"整理出错: {e}")

        elif choice == '4':
            source = input("请输入源目录路径: ").strip()
            target = input("请输入目标目录路径: ").strip()
            action = input("移动文件还是复制文件? (move/copy): ").strip().lower()

            if not os.path.exists(source):
                print("源目录不存在！")
                continue

            try:
                print("正在整理文件...")
                result = scanner.organize_files_by_size(
                    source, target, move=(action == 'move'))
                total = sum(result.values())
                print(f"整理完成！共处理 {total} 个文件")
                for size_range, count in result.items():
                    print(f"  {size_range}: {count} 个文件")
            except Exception as e:
                print(f"整理出错: {e}")

        elif choice == '5':
            if not scanner.files_info:
                print("请先扫描目录！")
                continue

            output_file = input("请输入报告输出文件路径 (留空则只显示): ").strip()
            if output_file:
                scanner.generate_report(output_file)
                print(f"报告已保存到 {output_file}")
            else:
                print(scanner.generate_report())

        elif choice == '0':
            print("感谢使用！")
            break

        else:
            print("无效选择，请重新输入！")

if __name__ == "__main__":
    main()
