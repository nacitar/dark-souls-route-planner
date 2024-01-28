import subprocess
from pathlib import Path


def main() -> int:
    script_dir = Path(__file__).parent
    css_dir = script_dir / "route_planner" / "styles"
    css_files = [
        str(path.relative_to(script_dir))
        for path in css_dir.iterdir()
        if path.suffix.lower() == ".css"
    ]

    try:
        commands = [
            ["black", "."],
            ["isort", "."],
            ["mypy", "."],
            ["flake8", "."],
        ]
        if css_files:
            commands.append(["css-beautify", "-nr"] + css_files)
        commands.append(["pytest", "."])

        for command in commands:
            print(f"Running {command[0]}...")
            subprocess.run(command, check=True, cwd=script_dir)
            print()
    except subprocess.CalledProcessError as e:
        return e.returncode
    print("All checks completed successfully!")
    return 0
