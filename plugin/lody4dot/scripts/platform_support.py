"""Small platform boundary for the currently supported Linux runtime tools."""

import sys


class UnsupportedPlatform(Exception):
    """A fixed, non-sensitive explanation for unsupported runtime platforms."""

    def __init__(self):
        super().__init__("Lody4dot runtime tools currently support Linux only.")


def require_supported_platform():
    """Check the OS boundary; this does not establish native-module readiness."""
    if sys.platform != "linux":
        raise UnsupportedPlatform()


def acquire_install_lock(stream):
    """Acquire the existing non-blocking POSIX lock only on a supported OS."""
    require_supported_platform()
    import fcntl

    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
