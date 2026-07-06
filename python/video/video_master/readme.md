### test
```shell
#使用方法
#基本扫描（默认会展示重复视频列表及可节省的空间大小）：
python3 main.py -d /path/to/your/videos
#交互式清理（对每组重复视频逐个确认要保留的文件）：
python3 main.py -d /path/to/your/videos --delete-interactive
#自动清理（每组只保留第一个文件，自动删除多余副本）：
python3 main.py -d /path/to/your/videos --delete-keep-first
#保存报告（将查重结果输出为 JSON 文件）：
python3 main.py -d /path/to/your/videos --json report.json
#快速查重模式（高速度，适合TB级或超大视频文件扫描） 添加 --fast 参数。程序会跳过第二步的全文件完整读取与验证，仅比对文件大小和头尾 64KB 哈希，速度将提升成百上千倍：
python3 main.py -d /path/to/your/videos --fast
##test
python3 main.py -d   /Volumes/mm
```