"""Minimal macOS Accessibility bindings with explicit Core Foundation ownership.

Import is portable. Only NativeAX construction loads system libraries. A returned
AXElement owns one native reference: close it when done (idempotently); collection
also releases it. No method requests permission, retries, or launches an app.
"""

from __future__ import annotations

from contextlib import contextmanager
import ctypes as C
import errno
import os
import sys


class AXError(RuntimeError):
    """A native failure classified for the caller's observation/action policy."""

    def __init__(self, status: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.retryable = retryable


# Darwin's LP64 CFIndex/CFTypeID remain 64 bit even in portable boundary tests
# running on Windows, where ctypes.c_long is only 32 bit.
_Index = C.c_int64
_TypeID = C.c_uint64
_Ref = C.c_void_p
_Boolean = C.c_ubyte
_UTF8 = 0x08000100


class _CFRange(C.Structure):
    _fields_ = [("location", _Index), ("length", _Index)]


class _ProcBSDInfo(C.Structure):
    # Apple's xnu/bsd/sys/proc_info.h, struct proc_bsdinfo (MAXCOMLEN=16).
    # Size 136; the two uint64_t start fields begin at offsets 120 and 128.
    _fields_ = [
        ("pbi_flags", C.c_uint32), ("pbi_status", C.c_uint32),
        ("pbi_xstatus", C.c_uint32), ("pbi_pid", C.c_uint32),
        ("pbi_ppid", C.c_uint32), ("pbi_uid", C.c_uint32),
        ("pbi_gid", C.c_uint32), ("pbi_ruid", C.c_uint32),
        ("pbi_rgid", C.c_uint32), ("pbi_svuid", C.c_uint32),
        ("pbi_svgid", C.c_uint32), ("rfu_1", C.c_uint32),
        ("pbi_comm", C.c_char * 16), ("pbi_name", C.c_char * 32),
        ("pbi_nfiles", C.c_uint32), ("pbi_pgid", C.c_uint32),
        ("pbi_pjobc", C.c_uint32), ("e_tdev", C.c_uint32),
        ("e_tpgid", C.c_uint32), ("pbi_nice", C.c_int32),
        ("pbi_start_tvsec", C.c_uint64), ("pbi_start_tvusec", C.c_uint64),
    ]


class _Bindings:
    """Private FFI setup boundary; libraries own their function pointers."""

    def __init__(self, cf, ax, proc):
        self.cf, self.ax, self.proc = cf, ax, proc
        signatures = [
            (cf, "CFRetain", _Ref, [_Ref]),
            (cf, "CFRelease", None, [_Ref]),
            (cf, "CFGetTypeID", _TypeID, [_Ref]),
            (cf, "CFStringGetTypeID", _TypeID, []),
            (cf, "CFBooleanGetTypeID", _TypeID, []),
            (cf, "CFArrayGetTypeID", _TypeID, []),
            (cf, "CFStringCreateWithBytes", _Ref, [_Ref, _Ref, _Index, C.c_uint32, _Boolean]),
            (cf, "CFStringGetLength", _Index, [_Ref]),
            (cf, "CFStringGetMaximumSizeForEncoding", _Index, [_Index, C.c_uint32]),
            (cf, "CFStringGetBytes", _Index,
             [_Ref, _CFRange, C.c_uint32, C.c_ubyte, _Boolean, _Ref, _Index, C.POINTER(_Index)]),
            (cf, "CFBooleanGetValue", _Boolean, [_Ref]),
            (cf, "CFArrayGetCount", _Index, [_Ref]),
            (cf, "CFArrayGetValueAtIndex", _Ref, [_Ref, _Index]),
            (ax, "AXUIElementGetTypeID", _TypeID, []),
            (ax, "AXIsProcessTrusted", _Boolean, []),
            (ax, "AXUIElementCreateApplication", _Ref, [C.c_int32]),
            (ax, "AXUIElementCopyAttributeValue", C.c_int32, [_Ref, _Ref, C.POINTER(_Ref)]),
            (ax, "AXUIElementCopyActionNames", C.c_int32, [_Ref, C.POINTER(_Ref)]),
            (ax, "AXUIElementIsAttributeSettable", C.c_int32,
             [_Ref, _Ref, C.POINTER(_Boolean)]),
            (ax, "AXUIElementSetAttributeValue", C.c_int32, [_Ref, _Ref, _Ref]),
            (ax, "AXUIElementPerformAction", C.c_int32, [_Ref, _Ref]),
            (ax, "AXUIElementGetPid", C.c_int32, [_Ref, C.POINTER(C.c_int32)]),
            (proc, "proc_pidinfo", C.c_int32,
             [C.c_int32, C.c_int32, C.c_uint64, _Ref, C.c_int32]),
            (proc, "proc_pidpath", C.c_int32, [C.c_int32, _Ref, C.c_uint32]),
        ]
        for library, name, result, arguments in signatures:
            function = getattr(library, name)
            function.restype = result
            function.argtypes = arguments


def _load_native() -> _Bindings:
    if sys.platform != "darwin" or C.sizeof(_Ref) != 8:
        raise AXError("native_unavailable", "Accessibility requires a 64-bit macOS Python runtime")
    try:
        return _Bindings(
            C.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation", use_errno=True),
            C.CDLL("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices", use_errno=True),
            C.CDLL("/usr/lib/libproc.dylib", use_errno=True),
        )
    except (OSError, AttributeError) as error:
        raise AXError("native_unavailable", "Required macOS system APIs are unavailable") from error


def _check(code: int, operation: str) -> None:
    if code == 0:
        return
    status, retryable = {
        -25201: ("invalid_data", False),       # kAXErrorIllegalArgument
        -25202: ("stale_element", True),       # kAXErrorInvalidUIElement
        -25204: ("provider_unavailable", True),  # kAXErrorCannotComplete
        -25205: ("unsupported", False),        # kAXErrorAttributeUnsupported
        -25206: ("unsupported", False),        # kAXErrorActionUnsupported
        -25208: ("unsupported", False),        # kAXErrorNotImplemented
        -25211: ("permission_denied", False),  # kAXErrorAPIDisabled
        -25212: ("unsupported", False),        # kAXErrorNoValue
        -25213: ("unsupported", False),        # kAXErrorParameterizedAttributeUnsupported
        -25214: ("invalid_data", False),       # kAXErrorNotEnoughPrecision
    }.get(code, ("native_error", False))
    raise AXError(status, f"{operation} failed (AXError {code})", retryable=retryable)


def _pid(pid: int) -> int:
    if type(pid) is not int or not 0 < pid <= 0x7FFFFFFF:
        raise AXError("invalid_data", "PID must be a positive signed 32-bit integer")
    return pid


class AXElement:
    """One owned AXUIElementRef, independent of any array that contained it."""

    def __init__(self, bindings: _Bindings, reference: int):
        self._bindings = bindings
        self._reference = reference

    def close(self) -> None:
        reference = self._reference
        self._reference = None
        if reference:
            self._bindings.cf.CFRelease(reference)

    def __del__(self):
        if getattr(self, "_reference", None):
            self.close()


def _close_elements(value) -> None:
    if isinstance(value, AXElement):
        value.close()
    elif isinstance(value, list):
        for item in value:
            _close_elements(item)


class NativeAX:
    """System-only adapter. The worker owns permission policy and all retries."""

    def __init__(self):
        self._native = _load_native()

    def _element(self, element: AXElement) -> int:
        if not isinstance(element, AXElement) or element._bindings is not self._native:
            raise AXError("invalid_data", "Element belongs to a different native adapter")
        if not element._reference:
            raise AXError("stale_element", "Element has been released", retryable=True)
        return element._reference

    @contextmanager
    def _string(self, value: str):
        if not isinstance(value, str):
            raise AXError("invalid_data", "Accessibility text must be a string")
        try:
            data = value.encode("utf-8")
        except UnicodeError as error:
            raise AXError("invalid_data", "Accessibility text is not valid UTF-8") from error
        buffer = C.create_string_buffer(data)
        reference = self._native.cf.CFStringCreateWithBytes(None, buffer, len(data), _UTF8, False)
        if not reference:
            raise AXError("native_error", "CFString creation failed")
        try:
            yield reference
        finally:
            self._native.cf.CFRelease(reference)

    def _convert(self, reference: int, *, allow_element: bool = False):
        if not reference:
            raise AXError("invalid_data", "Native API returned a null value on success")
        cf = self._native.cf
        type_id = cf.CFGetTypeID(reference)
        if type_id == cf.CFStringGetTypeID():
            length = cf.CFStringGetLength(reference)
            capacity = cf.CFStringGetMaximumSizeForEncoding(length, _UTF8)
            if length < 0 or capacity < 0:
                raise AXError("invalid_data", "Invalid CFString length")
            buffer = C.create_string_buffer(capacity + 1)
            used = _Index()
            converted = cf.CFStringGetBytes(reference, _CFRange(0, length), _UTF8,
                                          0, False, buffer, capacity, C.byref(used))
            if converted != length or not 0 <= used.value <= capacity:
                raise AXError("invalid_data", "Incomplete CFString UTF-8 conversion")
            try:
                return buffer.raw[:used.value].decode("utf-8")
            except UnicodeError as error:
                raise AXError("invalid_data", "Native text is not valid UTF-8") from error
        if type_id == cf.CFBooleanGetTypeID():
            return bool(cf.CFBooleanGetValue(reference))
        if type_id == cf.CFArrayGetTypeID():
            count = cf.CFArrayGetCount(reference)
            if count < 0:
                raise AXError("invalid_data", "Invalid CFArray length")
            values = []
            try:
                for index in range(count):
                    child = cf.CFArrayGetValueAtIndex(reference, index)
                    values.append(self._convert(child, allow_element=True))
                return values
            except BaseException:
                _close_elements(values)
                raise
        if allow_element and type_id == self._native.ax.AXUIElementGetTypeID():
            retained = cf.CFRetain(reference)
            if not retained:
                raise AXError("native_error", "CF retain failed")
            return AXElement(self._native, retained)
        raise AXError("invalid_data", "Unsupported Core Foundation value type")

    def trusted(self) -> bool:
        return bool(self._native.ax.AXIsProcessTrusted())

    def application(self, pid: int) -> AXElement:
        reference = self._native.ax.AXUIElementCreateApplication(_pid(pid))
        if not reference:
            raise AXError("native_error", "Application element creation failed")
        return AXElement(self._native, reference)

    def attribute(self, element: AXElement, name: str) -> str | bool | list | None:
        reference = self._element(element)
        output = _Ref()
        with self._string(name) as key:
            try:
                code = self._native.ax.AXUIElementCopyAttributeValue(reference, key, C.byref(output))
                if code in (-25205, -25212):
                    return None
                _check(code, "Read attribute")
                value = self._convert(output.value)
                if name == "AXValue" and not isinstance(value, (str, bool)):
                    _close_elements(value)
                    raise AXError("invalid_data", "AXValue must be text or boolean")
                return value
            finally:
                if output.value:
                    self._native.cf.CFRelease(output.value)

    def actions(self, element: AXElement) -> list[str]:
        reference = self._element(element)
        output = _Ref()
        try:
            code = self._native.ax.AXUIElementCopyActionNames(reference, C.byref(output))
            if code == -25206:
                return []
            _check(code, "Read actions")
            value = self._convert(output.value)
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                _close_elements(value)
                raise AXError("invalid_data", "Action names must be an array of strings")
            return value
        finally:
            if output.value:
                self._native.cf.CFRelease(output.value)

    def is_settable(self, element: AXElement, name: str) -> bool:
        reference = self._element(element)
        output = _Boolean()
        with self._string(name) as key:
            code = self._native.ax.AXUIElementIsAttributeSettable(reference, key, C.byref(output))
            if code == -25205:
                return False
            _check(code, "Check settable attribute")
            return bool(output.value)

    def set_attribute(self, element: AXElement, name: str, value: str) -> None:
        reference = self._element(element)
        with self._string(name) as key, self._string(value) as text:
            _check(self._native.ax.AXUIElementSetAttributeValue(reference, key, text), "Set attribute")

    def perform_action(self, element: AXElement, name: str) -> None:
        reference = self._element(element)
        with self._string(name) as action:
            _check(self._native.ax.AXUIElementPerformAction(reference, action), "Perform action")

    def element_pid(self, element: AXElement) -> int:
        output = C.c_int32()
        _check(self._native.ax.AXUIElementGetPid(self._element(element), C.byref(output)), "Read element PID")
        return _pid(output.value)

    @staticmethod
    def _process_error(operation: str):
        code = C.get_errno()
        status = "permission_denied" if code in (errno.EPERM, errno.EACCES) else "process_unavailable"
        return AXError(status, f"{operation} failed (errno {code})")

    def _start_time(self, pid: int) -> list[int]:
        info = _ProcBSDInfo()
        C.set_errno(0)
        count = self._native.proc.proc_pidinfo(pid, 3, 0, C.byref(info), C.sizeof(info))
        if count != C.sizeof(info):
            raise self._process_error("Read process identity")
        if info.pbi_pid != pid:
            raise AXError("process_unavailable", "Process identity changed during lookup")
        if not info.pbi_start_tvsec or info.pbi_start_tvusec >= 1000000:
            raise AXError("invalid_data", "Invalid process start timestamp")
        return [info.pbi_start_tvsec, info.pbi_start_tvusec]

    def identity(self, pid: int) -> dict:
        pid = _pid(pid)
        before = self._start_time(pid)
        buffer = C.create_string_buffer(4096)  # PROC_PIDPATHINFO_MAXSIZE
        C.set_errno(0)
        size = self._native.proc.proc_pidpath(pid, buffer, len(buffer))
        if size <= 0:
            raise self._process_error("Read process executable")
        if size >= len(buffer) or not buffer.value or not os.path.isabs(os.fsdecode(buffer.value)):
            raise AXError("invalid_data", "Invalid process executable path")
        executable = os.path.realpath(os.fsdecode(buffer.value))
        if before != self._start_time(pid):
            raise AXError("process_unavailable", "Process identity changed during lookup")
        return {"pid": pid, "executable": executable, "start_time": before}
