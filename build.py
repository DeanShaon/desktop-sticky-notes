import subprocess
import sys

print("开始打包...")
print("=" * 50)

# 使用 --onefile 选项打包为单个 exe
args = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "桌面便签",
    "--clean",
    "main.py"
]

print("执行命令:", " ".join(args[2:]))
print("=" * 50)

result = subprocess.run(args)
sys.exit(result.returncode)