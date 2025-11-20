from __future__ import annotations

if __package__ is None or __package__ == "":
    import sys
    from pathlib import Path

    package_root = next(
        parent for parent in Path(__file__).resolve().parents if parent.name == "hotel"
    )
    project_root = package_root.parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    __package__ = "hotel"

from . import create_app  # type: ignore[attr-defined]

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

