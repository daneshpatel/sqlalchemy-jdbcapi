"""
JVM management and initialization.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from .exceptions import JVMNotStartedError

logger = logging.getLogger(__name__)

_jvm_started = False


def get_classpath() -> list[Path]:
    """
    Get JDBC driver classpath from environment or system property.

    Returns:
        List of paths to JDBC driver JAR files.
    """
    classpath = os.environ.get("CLASSPATH", "")
    if not classpath:
        classpath = os.environ.get("JDBC_DRIVER_PATH", "")

    if not classpath:
        return []

    paths = []
    for path_str in classpath.split(os.pathsep):
        path = Path(path_str)
        if path.exists():
            paths.append(path)
        else:
            logger.warning(f"Classpath entry not found: {path}")

    return paths


def start_jvm(
    classpath: list[Path] | None = None,
    jvm_path: Path | None = None,
    jvm_args: list[str] | None = None,
) -> None:
    """
    Start the JVM with specified classpath and arguments.

    Args:
        classpath: List of paths to add to classpath. If None, uses environment.
        jvm_path: Path to JVM library. If None, JPype will auto-detect.
        jvm_args: Additional JVM arguments (e.g., ['-Xmx512m']).

    Raises:
        JVMNotStartedError: If JVM fails to start.
    """
    global _jvm_started

    if _jvm_started:
        logger.debug("JVM already started")
        return

    try:
        import jpype
    except ImportError as e:
        raise JVMNotStartedError(
            "JPype is not installed. Install with: pip install JPype1"
        ) from e

    if jpype.isJVMStarted():
        _jvm_started = True
        logger.debug("JVM already started by another process")
        return

    # Build classpath
    if classpath is None:
        classpath = get_classpath()

    classpath_str = os.pathsep.join(str(p) for p in classpath)

    # Build JVM arguments
    args = jvm_args or []
    if classpath_str:
        args.append(f"-Djava.class.path={classpath_str}")

    # Start JVM
    try:
        if jvm_path:
            jpype.startJVM(str(jvm_path), *args, convertStrings=True)
        else:
            jpype.startJVM(*args, convertStrings=True)

        _jvm_started = True
        logger.info("JVM started successfully")
        logger.debug(f"Classpath: {classpath_str}")
        logger.debug(f"JVM args: {args}")

    except Exception as e:
        raise JVMNotStartedError(f"Failed to start JVM: {e}") from e


def is_jvm_started() -> bool:
    """Check if JVM is started."""
    try:
        import jpype

        return jpype.isJVMStarted()
    except ImportError:
        return False


def shutdown_jvm() -> None:
    """Shutdown the JVM (optional, usually not needed)."""
    global _jvm_started

    try:
        import jpype

        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            _jvm_started = False
            logger.info("JVM shutdown")
    except ImportError:
        pass


def get_java_class(class_name: str) -> Any:
    """
    Get a Java class by name.

    Args:
        class_name: Fully qualified Java class name.

    Returns:
        Java class object.

    Raises:
        JVMNotStartedError: If JVM is not started.
    """
    if not is_jvm_started():
        raise JVMNotStartedError("JVM is not started. Call start_jvm() first.")

    try:
        import jpype

        return jpype.JClass(class_name)
    except Exception as e:
        raise JVMNotStartedError(f"Failed to load Java class {class_name}: {e}") from e
