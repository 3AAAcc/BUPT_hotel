from __future__ import annotations

if __package__ is None or __package__ == "":
    import sys
    from pathlib import Path

    # 获取当前文件所在目录
    current_file = Path(__file__).resolve()
    current_dir = current_file.parent
    
    # 如果当前目录有 __init__.py，说明当前目录就是 hotel 包
    # 需要将父目录添加到路径，这样才能导入 hotel 包
    if (current_dir / "__init__.py").exists():
        parent_dir = current_dir.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        __package__ = "hotel"
    else:
        # 否则尝试找到包含 hotel 的父目录
        try:
            package_root = next(
                parent for parent in current_file.parents if parent.name == "hotel"
            )
            project_root = package_root.parent
            root_str = str(project_root)
            if root_str not in sys.path:
                sys.path.insert(0, root_str)
            __package__ = "hotel"
        except StopIteration:
            # 如果找不到，假设当前目录就是包目录
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))
            __package__ = "hotel"

from . import create_app  # type: ignore[attr-defined]

app = create_app()


if __name__ == "__main__":
    from .config import Config
    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=True)

