from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
WEBAPP_DIR = ROOT / "webapp"
REQUIREMENTS_FILE = WEBAPP_DIR / "requirements.txt"
PACKAGE_LOCK_FILE = FRONTEND_DIR / "package-lock.json"
REQUIRED_PYTHON_MODULES = ("flask", "openpyxl", "ortools")
CONFIG_PATHS = (ROOT / "config" / "backend.json", ROOT / "config" / "frontend.json")
LEGACY_CONFIG_PATH = WEBAPP_DIR / "config.json"


def remove_legacy_config(path: Path | None = None) -> None:
    legacy_path = LEGACY_CONFIG_PATH if path is None else path
    try:
        legacy_path.unlink(missing_ok=True)
    except OSError as exc:
        raise RuntimeError(f"Không thể xóa file cấu hình cũ tại {legacy_path}: {exc}") from exc


def ensure_config_files(paths: tuple[Path, ...] | None = None) -> None:
    created = []
    for path in CONFIG_PATHS if paths is None else paths:
        if path.exists():
            continue
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8"):
                pass
        except FileExistsError:
            continue
        except OSError as exc:
            raise RuntimeError(f"Không thể tạo file cấu hình tại {path}: {exc}") from exc
        created.append(path)
    if created:
        raise RuntimeError(
            "Đã tạo file cấu hình trống tại:\n" + "\n".join(map(str, created))
            + "\nHãy bổ sung nội dung JSON hợp lệ vào các file này trước khi chạy lại."
        )


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def interrupt_handler(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


def run(command: list[str], cwd: Path) -> None:
    print(f"\n> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def executable(name: str) -> str:
    candidates = (f"{name}.cmd", name) if os.name == "nt" else (name,)
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    raise RuntimeError(f"Không tìm thấy '{name}'. Hãy cài đặt công cụ này rồi chạy lại.")


def node_major_version(node: str) -> int:
    output = subprocess.check_output([node, "--version"], text=True).strip()
    try:
        return int(output.removeprefix("v").split(".", 1)[0])
    except ValueError as exc:
        raise RuntimeError(f"Không xác định được phiên bản Node.js: {output}") from exc


def install_missing_dependencies() -> str:
    if sys.version_info < (3, 10):
        raise RuntimeError("Dự án yêu cầu Python 3.10 trở lên.")

    node = executable("node")
    npm = executable("npm")
    if node_major_version(node) < 18:
        raise RuntimeError("Dự án yêu cầu Node.js 18 trở lên.")

    missing_modules = [
        module for module in REQUIRED_PYTHON_MODULES if importlib.util.find_spec(module) is None
    ]
    if missing_modules:
        print(f"Thiếu thư viện Python: {', '.join(missing_modules)}")
        run([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], ROOT)
    else:
        print("Thư viện Python đã đầy đủ.")

    if not (FRONTEND_DIR / "node_modules").is_dir():
        print("Chưa có thư viện frontend, bắt đầu cài đặt...")
        npm_command = "ci" if PACKAGE_LOCK_FILE.is_file() else "install"
        run([npm, npm_command], FRONTEND_DIR)
    else:
        print("Thư viện frontend đã được cài đặt.")

    return npm


def process_options() -> dict[str, object]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)


def start_services(npm: str) -> int:
    options = process_options()
    environment = os.environ.copy()
    environment["PYTHONUNBUFFERED"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"

    print("\nĐang khởi chạy backend và frontend...")
    print("Backend: http://127.0.0.1:5055")
    print("Frontend: xem địa chỉ Vite hiển thị bên dưới (thường là http://localhost:5173)")
    print("Nhấn Ctrl+C để dừng cả hai.\n")

    processes: list[subprocess.Popen[bytes]] = []
    try:
        processes.append(
            subprocess.Popen(
                [sys.executable, "app.py"], cwd=WEBAPP_DIR, env=environment, **options
            )
        )
        processes.append(subprocess.Popen([npm, "run", "dev"], cwd=FRONTEND_DIR, **options))
        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
        return next(
            (process.returncode for process in processes if process.returncode is not None), 0
        )
    except KeyboardInterrupt:
        print("\nĐang dừng ứng dụng...")
        return 0
    finally:
        for process in processes:
            stop_process(process)


def main() -> int:
    configure_console()
    if os.name == "nt":
        signal.signal(signal.SIGBREAK, interrupt_handler)
    try:
        remove_legacy_config()
        ensure_config_files()
        npm = install_missing_dependencies()
        return start_services(npm)
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"\nLỗi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
