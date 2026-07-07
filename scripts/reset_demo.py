from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

project_root_text = str(
    PROJECT_ROOT
)

if (
    project_root_text
    not in sys.path
):
    sys.path.insert(
        0,
        project_root_text,
    )

from apps.api.services.demo_reset_service import (
    reset_demo_state,
)


def main() -> int:
    result = reset_demo_state()

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
