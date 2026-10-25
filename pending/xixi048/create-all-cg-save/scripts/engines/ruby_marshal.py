#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ruby_marshal.py —— 零依赖 Ruby Marshal (MRI Marshal 4.8) 解析器与查询工具。

用途
----
解析 RPG Maker XP / VX / VX Ace 的 .rxdata / .rvdata / .rvdata2 存档，
以及其他把游戏状态 Marshal.dump 到本地的单机游戏存档。

设计要点
--------
1. 每个节点记录其在文件中的字节偏移 pos 与长度 raw_len。这是后续"精确定位
   CG 解锁位、做最小字节级改写"的基础 —— 不需要重排整个 Marshal 流。
2. 忠实还原 Marshal 树结构，包含 ivar / symlink / link / userdef / usrmarshal
   等复合语义，避免为了"好看"而丢失信息。
3. 纯标准库实现，不需要 pip 安装任何第三方包，便于随 Skill 分发。

重要结论（写 NTRPG2 全 CG 补丁时会用到）
--------------------------------------
Ruby Marshal 是一个**纯顺序、自描述**的格式：没有全局偏移表，没有 CRC/校验和，
外部也没有包裹一层长度。因此在 peers 不变的前提下，插入或删除若干字节（例如把
布尔值 False 翻成 True，或把一个整数改成宽度不同的整数）不会破坏结构 ——
唯一的例外是被 'u' (TYPE_USRDEF) 包裹的数据，它带显式长度前缀，改长度时必须同步
修正该前缀。

CLI
---
    python ruby_marshal.py <save.rvdata2>                     # 打印结构摘要
    python ruby_marshal.py <save.rvdata2> --max-depth 4
    python ruby_marshal.py <save.rvdata2> --search swit       # 按路径/类名搜索
    python ruby_marshal.py <save.rvdata2> --json tree.json    # 导出完整 JSON

作为库使用
---------
    from ruby_marshal import loads, walk
    root = loads(open('Save01.rvdata2','rb').read())
    for node, path in walk(root):
        ...
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Iterator, List, Optional, Tuple

# Marshal 版本号 / 类型字节
MARSHAL_MAJOR = 4
MARSHAL_MINOR = 8

TYPE_NIL = 0x30          # '0'
TYPE_TRUE = 0x54         # 'T'
TYPE_FALSE = 0x46        # 'F'
TYPE_FIXNUM = 0x69       # 'i'
TYPE_EXTENDED = 0x65     # 'e'
TYPE_UCLASS = 0x43       # 'C'
TYPE_OBJECT = 0x6F       # 'o'
TYPE_DATA = 0x64         # 'd'
TYPE_USRDEF = 0x75       # 'u'
TYPE_USRMARSHAL = 0x55   # 'U'
TYPE_FLOAT = 0x66        # 'f'
TYPE_BIGNUM = 0x6C       # 'l'
TYPE_STRING = 0x22       # '"'
TYPE_REGEXP = 0x2F       # '/'
TYPE_ARRAY = 0x5B        # '['
TYPE_HASH = 0x7B         # '{'
TYPE_HASH_DEF = 0x7D     # '}'
TYPE_STRUCT = 0x53       # 'S'
TYPE_MODULE_OLD = 0x4D   # 'M'
TYPE_CLASS = 0x63        # 'c'
TYPE_MODULE = 0x6D       # 'm'
TYPE_SYMBOL = 0x3A       # ':'
TYPE_SYMLINK = 0x3B      # ';'
TYPE_IVAR = 0x49         # 'I'
TYPE_LINK = 0x40         # '@'

# 会被写入 link 表（'@' 可引用）的类型。Fixnum / nil / true / false / Symbol
# 属于 Ruby 的立即值，不占 link 槽位 —— 这里必须严格对齐，否则 link 索引错位。
LINKABLE_KINDS = frozenset({
    "bignum", "float", "string", "regexp", "array", "hash",
    "object", "class", "module", "userclass", "userdef", "usrmarshal",
})


class RbSymbol(str):
    """Ruby Symbol。继承 str 便于比较与作为 dict key，同时保留原始字节。"""

    __slots__ = ("raw",)

    def __new__(cls, text: str, raw: bytes = b""):
        obj = super().__new__(cls, text)
        obj.raw = raw
        return obj

    def __repr__(self) -> str:
        return f":{str.__str__(self)}"


class MarshalError(Exception):
    """解析失败。通常意味着输入不是 Marshal 流，或格式已损坏。"""


class Node:
    """Marshal 树中的一个节点。

    kind 取值：
        nil / true / false / int / float / bignum / string / symbol /
        regexp / array / hash / object / userclass / userdef / usrmarshal /
        class / module / link
    """

    __slots__ = ("kind", "value", "pos", "raw_len", "extra")

    def __init__(self, kind: str, value: Any, pos: int, raw_len: int = 0,
                 extra: Optional[dict] = None):
        self.kind = kind
        self.value = value
        self.pos = pos
        self.raw_len = raw_len
        self.extra = extra or {}

    @property
    def end(self) -> int:
        return self.pos + self.raw_len

    @property
    def ruby_class(self) -> Optional[str]:
        return self.extra.get("class")

    def __repr__(self) -> str:
        return f"<Node {self.kind} @{self.pos:#x} len={self.raw_len}>"


class Reader:
    """Marshal 4.8 流式解析器。"""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.symbols: List[RbSymbol] = []
        self.objects: List[Any] = []      # '@' link 表

    # ---------- 底层读操作 ----------

    def _need(self, n: int) -> None:
        if self.pos + n > len(self.data):
            raise MarshalError(
                f"offset {self.pos:#x}: 需要 {n} 字节但已到文件末尾 "
                f"(共 {len(self.data)} 字节)")

    def _byte(self) -> int:
        self._need(1)
        b = self.data[self.pos]
        self.pos += 1
        return b

    def _raw(self, n: int) -> bytes:
        if n < 0:
            raise MarshalError(f"offset {self.pos:#x}: 非法长度 {n}")
        self._need(n)
        chunk = self.data[self.pos:self.pos + n]
        self.pos += n
        return chunk

    def read_int(self) -> int:
        """读取 Marshal 变长整数编码（含 -5 偏移技巧）。"""
        c = self._byte()
        if c > 127:
            c -= 256
        if c == 0:
            return 0
        if c > 0:
            if 4 < c < 128:          # 1..122 落在单字节里
                return c - 5
            x = 0
            for i in range(c):
                x |= self._byte() << (8 * i)
            return x
        if -129 < c < -4:            # -122..-1
            return c + 5
        n = -c
        x = -1
        for i in range(n):
            b = self._byte()
            x = (x & ~(0xFF << (8 * i))) | (b << (8 * i))
        return x

    # ---------- 链接表管理 ----------

    def _reserve(self, owner: Any) -> int:
        """为复合类型预留一个 link 槽位，允许自引用结构（如自引用的 Array）。"""
        idx = len(self.objects)
        self.objects.append(owner)
        return idx

    @staticmethod
    def _mark(node: Node, idx: int) -> None:
        node.extra["link_index"] = idx

    # ---------- 顶层入口 ----------

    def read(self) -> Node:
        start = self.pos
        t = self._byte()
        node = self._dispatch(t, start)
        node.raw_len = self.pos - start
        # link 表只登记"非立即值"：nil/true/false/Fixnum/Symbol 不占槽位，
        # 而 String/Float/Class/Module/Regexp/复合对象都要占 —— 这一点决定了
        # 后续 '@' 链接索引能否正确还原。
        if node.kind in LINKABLE_KINDS and "link_index" not in node.extra:
            node.extra["link_index"] = len(self.objects)
            self.objects.append(node)
        return node

    def _dispatch(self, t: int, start: int) -> Node:
        if t == TYPE_NIL:
            return Node("nil", None, start)
        if t == TYPE_TRUE:
            return Node("true", True, start)
        if t == TYPE_FALSE:
            return Node("false", False, start)
        if t == TYPE_FIXNUM:
            return Node("int", self.read_int(), start)
        if t == TYPE_BIGNUM:
            return self._read_bignum(start)
        if t == TYPE_FLOAT:
            return self._read_float(start)
        if t == TYPE_STRING:
            n = self.read_int()
            return Node("string", self._raw(n), start)
        if t == TYPE_SYMBOL:
            return self._read_symbol(start)
        if t == TYPE_SYMLINK:
            idx = self.read_int()
            if idx >= len(self.symbols):
                raise MarshalError(f"offset {start:#x}: 非法 symlink 索引 {idx}")
            return Node("symbol", self.symbols[idx], start)
        if t == TYPE_LINK:
            idx = self.read_int()
            if idx >= len(self.objects):
                raise MarshalError(f"offset {start:#x}: 非法 link 索引 {idx}")
            return Node("link", self.objects[idx], start)
        if t == TYPE_ARRAY:
            return self._read_array(start)
        if t in (TYPE_HASH, TYPE_HASH_DEF):
            return self._read_hash(start, has_default=(t == TYPE_HASH_DEF))
        if t == TYPE_OBJECT:
            return self._read_object(start)
        if t == TYPE_IVAR:
            return self._read_ivar(start)
        if t == TYPE_EXTENDED:
            return self._read_extended(start)
        if t == TYPE_UCLASS:
            cls = self.read()      # 类名是带 ':' 类型字节的 Symbol，不能按裸长度读
            inner = self.read()
            return Node("userclass", inner, start,
                        extra={"class": str(cls.value)})
        if t == TYPE_USRDEF:
            cls = self.read()      # 同上
            n = self.read_int()
            data_pos = self.pos
            payload = self._raw(n)
            return Node("userdef", payload, start,
                        extra={"class": str(cls.value),
                               "data_pos": data_pos, "data_len": n})
        if t == TYPE_USRMARSHAL:
            cls = self.read()      # 同上
            node = Node("usrmarshal", None, start,
                        extra={"class": str(cls.value)})
            idx = self._reserve(node)
            self._mark(node, idx)
            payload = self.read()
            node.value = payload
            self.objects[idx] = node
            return node
        if t in (TYPE_CLASS, TYPE_MODULE):
            n = self.read_int()
            return Node("class" if t == TYPE_CLASS else "module",
                        self._raw(n), start)
        if t == TYPE_REGEXP:
            pattern = self._raw(self.read_int())
            flags = self._byte()
            return Node("regexp", pattern, start, extra={"flags": flags})
        if t == TYPE_DATA:
            raise MarshalError(
                f"offset {start:#x}: 遇到受保护的 TYPE_DATA，无法解析")
        raise MarshalError(
            f"offset {start:#x}: 未知 Marshal 类型字节 "
            f"{t:#02x} ({chr(t)!r})；输入很可能不是 Ruby Marshal 流")

    # ---------- 各类型实现 ----------

    def _read_bignum(self, start: int) -> Node:
        sign = self._byte()
        n = self.read_int()
        value = 0
        for i in range(n):
            lo = self._byte()
            hi = self._byte()
            value |= (lo | (hi << 8)) << (16 * i)
        if sign == 0x2D:      # '-'
            value = -value
        return Node("bignum", value, start)

    def _read_float(self, start: int) -> Node:
        n = self.read_int()
        text = self._raw(n).decode("ascii", "replace")
        try:
            value = float(text)
        except ValueError:
            value = float("nan")
        return Node("float", value, start)

    def _read_symbol(self, start: int) -> Node:
        n = self.read_int()
        raw = self._raw(n)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1", "replace")
        sym = RbSymbol(text, raw)
        self.symbols.append(sym)
        return Node("symbol", sym, start)

    def _read_array(self, start: int) -> Node:
        count = self.read_int()
        items: List[Node] = []
        node = Node("array", items, start)
        self._mark(node, self._reserve(node))
        for _ in range(count):
            items.append(self.read())
        return node

    def _read_hash(self, start: int, has_default: bool) -> Node:
        count = self.read_int()
        pairs: List[Tuple[Node, Node]] = []
        node = Node("hash", pairs, start, extra={"default": None})
        self._mark(node, self._reserve(node))
        for _ in range(count):
            k = self.read()
            v = self.read()
            pairs.append((k, v))
        if has_default:
            node.extra["default"] = self.read()
        return node

    def _read_object(self, start: int) -> Node:
        class_sym = self.read()
        if class_sym.kind != "symbol":
            raise MarshalError(f"offset {start:#x}: object 缺少类名符号")
        attrs: Dict[str, Node] = {}
        node = Node("object", attrs, start,
                    extra={"class": str(class_sym.value)})
        idx = self._reserve(node)
        self._mark(node, idx)
        count = self.read_int()
        for _ in range(count):
            key_node = self.read()
            name = key_node.value if key_node.kind == "symbol" else None
            if name is None:
                raise MarshalError(f"offset {key_node.pos:#x}: ivar 名不是符号")
            attrs[str(name)] = self.read()
        return node

    def _read_ivar(self, start: int) -> Node:
        inner = self.read()
        count = self.read_int()
        attrs: Dict[str, Node] = {}
        for _ in range(count):
            key_node = self.read()
            name = key_node.value if key_node.kind == "symbol" else None
            if name is None:
                raise MarshalError(f"offset {key_node.pos:#x}: ivar 名不是符号")
            attrs[str(name)] = self.read()
        inner.extra.setdefault("ivars", {}).update(attrs)
        inner.raw_len = self.pos - start
        return inner

    def _read_extended(self, start: int) -> Node:
        mod = self.read()
        inner = self.read()
        mods = inner.extra.get("modules", [])
        mods.append(str(mod.value))
        inner.extra["modules"] = mods
        inner.raw_len = self.pos - start
        return inner

    def _read_userdef(self, start: int) -> Node:
        class_sym = self.read()
        n = self.read_int()
        data_pos = self.pos
        payload = self._raw(n)
        return Node("userdef", payload, start,
                    extra={"class": str(class_sym.value),
                           "data_pos": data_pos, "data_len": n})


# ============================ 对外 API ============================

def _check_version(data: bytes) -> None:
    if len(data) < 2:
        raise MarshalError("输入过短，不是有效的 Marshal 流")
    if data[0] != MARSHAL_MAJOR or data[1] != MARSHAL_MINOR:
        raise MarshalError(
            f"Marshal 版本不匹配：期望 04 08，实际 {data[0]:#04x} {data[1]:#04x}")


def read_streams(data: bytes) -> List[Node]:
    """按先后顺序解析文件中首尾相接的多个 Marshal 流。

    部分引擎会把若干次 Marshal.dump 直接拼接进同一个文件（例如 NTRPG2 的
    Save0X.rvdata2：第 1 段是存档 UI 用的摘要信息，第 2 段才是真正的游戏内容），
    此时必须分段解析 —— 否则 link 表与偏移量都会错位。
    """
    _check_version(data)
    out: List[Node] = []
    pos = 0
    while pos < len(data):
        _check_version(data[pos:pos + 2])
        reader = Reader(data)
        reader.pos = pos + 2
        node = reader.read()
        node.raw_len = reader.pos - pos
        node.pos = pos          # 定位到含版本字节的流起点
        node.extra["stream_start"] = pos
        out.append(node)
        pos = reader.pos
    return out


def loads(data: bytes) -> Node:
    """把一段 Ruby Marshal 字节流解析成 Node 树（单流）。

    若文件里含有多于一个流，抛出明确提示 —— 请改用 read_streams()。
    """
    _check_version(data)
    reader = Reader(data)
    reader.pos = 2          # 跳过 major/minor 版本字节
    root = reader.read()
    if reader.pos != len(data):
        remaining = data[reader.pos:reader.pos + 16].hex(" ")
        raise MarshalError(
            f"解析未耗尽输入：已读 {reader.pos} 字节，文件共 {len(data)} 字节。"
            f"该文件很可能是多个 Marshal 流拼接而成（下一段头部：{remaining}），"
            f"请改用 read_streams() 或 CLI 的 --streams 查看。")
    return root


def load(path: str) -> Node:
    with open(path, "rb") as f:
        return loads(f.read())


# ---------- 遍历 / 路径 ----------

def children(node: Node) -> List[Tuple[str, Node]]:
    """返回 [(子路径片段, 子节点)]。"""
    out: List[Tuple[str, Node]] = []
    if node.kind == "array" and isinstance(node.value, list):
        for i, item in enumerate(node.value):
            out.append((f"[{i}]", item))
    elif node.kind == "hash" and isinstance(node.value, list):
        for k, v in node.value:
            key = _scalar_repr(k)
            out.append((f"->{key}", v))
        if node.extra.get("default") is not None:
            out.append(("<default>", node.extra["default"]))
    elif node.kind == "object" and isinstance(node.value, dict):
        for name, v in node.value.items():
            out.append((f".{'@' + name if not name.startswith('@') else name}", v))
        for name, v in node.extra.get("ivars", {}).items():
            out.append((f".@iv_{name}", v))
    elif node.kind in ("userclass", "usrmarshal") and isinstance(node.value, Node):
        out.append((".<inner>", node.value))
    elif node.kind == "userdef":
        pass
    return out


def walk(node: Node, prefix: str = "", _depth: int = 0,
         max_depth: int = 64) -> Iterator[Tuple[Node, str]]:
    """深度优先遍历整棵树，产出 (node, path)。"""
    yield node, prefix or "<root>"
    if _depth >= max_depth:
        return
    for frag, child in children(node):
        if isinstance(child, Node):
            yield from walk(child, prefix + frag, _depth + 1, max_depth)


def _scalar_repr(node: Node, limit: int = 48) -> str:
    if node is None:
        return "nil"
    if node.kind == "nil":
        return "nil"
    if node.kind == "symbol":
        return str(node.value)
    if node.kind == "string":
        raw = node.value
        sample = raw[:limit]
        try:
            text = sample.decode("utf-8")
            shown = repr(text)
        except UnicodeDecodeError:
            shown = sample.hex(" ")
        return f"str({len(raw)}){shown}"
    if node.kind == "class":
        return f"<Class:{node.value}>"
    if node.kind == "module":
        return f"<Module:{node.value}>"
    if node.kind == "link":
        return "<link>"
    return repr(node.value)


def describe(node: Node) -> str:
    kind = node.kind
    if kind == "array":
        return f"Array({len(node.value)})"
    if kind == "hash":
        return f"Hash({len(node.value)})"
    if kind == "object":
        return f"<{node.ruby_class}> ivars={len(node.value)}"
    if kind == "userclass":
        return f"<UserClass:{node.ruby_class}>"
    if kind == "usrmarshal":
        return f"<UserMarshal:{node.ruby_class}>"
    if kind == "userdef":
        return f"<UserDef:{node.ruby_class}> bytes={node.extra.get('data_len')}"
    if kind == "string":
        return f'String({len(node.value)}) {_scalar_repr(node)}'
    return _scalar_repr(node)


# ---------- 编码器（写回存档时需要） ----------

def encode_int(value: int) -> bytes:
    """把整数编回 Marshal 变长整数格式（与 read_int 互逆）。"""
    if value == 0:
        return b"\x00"
    if 0 < value <= 122:
        return bytes([value + 5])
    if -122 <= value < 0:
        return bytes([256 + value - 5])
    if value > 0:
        raw = value.to_bytes((value.bit_length() + 7) // 8, "little")
        if len(raw) > 4:                       # 超过 4 字节应改用 Bignum
            raise ValueError(f"{value} 过大，请改用 bignum 编码")
        return bytes([len(raw)]) + raw
    # 负数：用最小长度的两补数表示，长度前缀为负
    for n in range(1, 5):
        try:
            raw = value.to_bytes(n, "little", signed=True)
        except OverflowError:
            continue
        if int.from_bytes(raw, "little", signed=True) == value:
            return bytes([256 - n]) + raw
    raise ValueError(f"{value} 超出可编码范围")


def encode_bool(value: bool) -> bytes:
    """True -> b'T'，False -> b'F'。两者等长，是最小写入成本的标志位翻转。"""
    return b"\x54" if value else b"\x46"


def _selftest() -> bool:
    """encode_int 与 read_int 的往返一致性检查。"""
    cases = [0, 1, 2, 121, 122, 123, 124, 255, 256, 9999, 65535, 65536,
             2 ** 24 - 1, 2 ** 31 - 1, -1, -2, -121, -122, -123, -1000,
             -2 ** 24, -2 ** 31]
    for v in cases:
        data = encode_int(v)
        r = Reader(data)
        got = r.read_int()
        if got != v or r.pos != len(data):
            print(f"[FAIL] {v}: 编码 {data.hex(' ')} 解码为 {got}")
            return False
    return True


# ---------- 摘要输出 ----------

PREVIEW_LIMIT = 6        # 容器内最多预览多少个成员
BIG_LIST_LIMIT = 24      # 超过此长度的标量子数组折叠显示


def summarize(root: Node, max_depth: int = 4,
              stream=sys.stdout, collapse_scalar_arrays: bool = True) -> None:
    def rec(node: Node, prefix: str, depth: int) -> None:
        head = f"{prefix}  @{node.pos:#x}({node.pos}) [{node.raw_len}B]"
        # 纯标量数组（如 $game_variables 的 @data）折叠显示，避免刷屏
        if (collapse_scalar_arrays and node.kind == "array" and node.value
                and all(c.kind in ("int", "float", "true", "false", "nil")
                        for c in node.value)):
            vals = [("T" if c.kind == "true" else "F" if c.kind == "false"
                     else "." if c.kind == "nil" else str(c.value))
                    for c in node.value]
            shown = ",".join(vals[:BIG_LIST_LIMIT])
            tail = f"…(共{len(vals)}项)" if len(vals) > BIG_LIST_LIMIT else ""
            print(f"{head} Array({len(vals)}) [{shown}]{tail}", file=stream)
            return
        print(f"{head} {describe(node)}", file=stream)
        if depth >= max_depth:
            if children(node):
                print(f"{prefix}  …（已到最大层级 {max_depth}）", file=stream)
            return
        kids = children(node)
        for frag, child in kids[:PREVIEW_LIMIT]:
            if isinstance(child, Node):
                rec(child, prefix + frag, depth + 1)
        if len(kids) > PREVIEW_LIMIT:
            print(f"{prefix}  …另有 {len(kids) - PREVIEW_LIMIT} 个子项", file=stream)

    rec(root, "", 0)


def to_json_obj(node: Node) -> Any:
    """转成可 JSON 序列化的结构（会丢掉字节偏移，仅供肉眼查阅）。"""
    kind = node.kind
    if kind == "nil":
        return None
    if kind in ("true", "false", "int", "float"):
        return node.value
    if kind == "string":
        raw = node.value
        try:
            return {"_t": "string", "v": raw.decode("utf-8")}
        except UnicodeDecodeError:
            return {"_t": "bytes", "v": raw.hex()}
    if kind in ("symbol", "class", "module"):
        return {"_t": kind, "v": str(node.value)}
    if kind == "link":
        return {"_t": "link"}
    if kind == "array":
        return [to_json_obj(x) for x in node.value]
    if kind == "hash":
        return {"_t": "hash",
                "v": [[to_json_obj(k), to_json_obj(v)] for k, v in node.value]}
    if kind == "object":
        return {"_t": "object", "class": node.ruby_class,
                "ivars": {k: to_json_obj(v) for k, v in node.value.items()}}
    if kind == "userdef":
        return {"_t": "userdef", "class": node.ruby_class,
                 "hex": node.value.hex()}
    if kind == "usrmarshal":
        return {"_t": "usrmarshal", "class": node.ruby_class,
                "v": to_json_obj(node.value)}
    if kind == "userclass":
        return {"_t": "userclass", "class": node.ruby_class,
                "v": to_json_obj(node.value)}
    return {"_t": kind}


def search(root: Node, needle: str) -> Iterator[Tuple[Node, str]]:
    """按路径或 Ruby 类名做子串匹配。"""
    needle = needle.lower()
    for node, path in walk(root):
        if needle in path.lower():
            yield node, path
        elif node.ruby_class and needle in node.ruby_class.lower():
            yield node, path


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Ruby Marshal 存档解析器（零依赖）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    ap.add_argument("file", help="存档文件，如 Save01.rvdata2")
    ap.add_argument("--max-depth", type=int, default=4, help="摘要最大层级")
    ap.add_argument("--no-collapse", action="store_true",
                    help="不折叠标量数组，完整展开")
    ap.add_argument("--search", metavar="NEEDLE",
                    help="按路径 / Ruby 类名搜索，输出命中的路径")
    ap.add_argument("--search-limit", type=int, default=40)
    ap.add_argument("--stream", type=int, default=None, metavar="N",
                    help="多流文件：只解析第 N 段（从 1 开始）")
    ap.add_argument("--streams", action="store_true",
                    help="列出文件中所有 Marshal 流的概览")
    ap.add_argument("--json", metavar="OUT", help="导出完整树到 JSON")
    args = ap.parse_args(argv)

    data = open(args.file, "rb").read()

    if args.streams:
        try:
            streams = read_streams(data)
        except MarshalError as exc:
            print(f"[!] 解析失败：{exc}", file=sys.stderr)
            return 2
        print(f"# {args.file}  共 {len(streams)} 个 Marshal 流")
        for i, node in enumerate(streams, 1):
            print(f"  [{i:>2}] {node.pos:#x}({node.pos}) 长度 {node.raw_len} 字节  "
                  f"{describe(node)}  (结束于 {node.end:#x})")
        return 0

    try:
        root = (read_streams(data)[args.stream - 1] if args.stream
                else loads(data))
    except MarshalError as exc:
        print(f"[!] 解析失败：{exc}", file=sys.stderr)
        return 2

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(to_json_obj(root), f, ensure_ascii=False)
        print(f"[+] 已导出 {args.json}")
        return 0

    if args.search:
        hits = 0
        for node, path in search(root, args.search):
            print(f"{path}  @{node.pos:#x}  {describe(node)}")
            hits += 1
            if hits >= args.search_limit:
                print(f"…（超过 {args.search_limit} 条，已截断；"
                      f"可用 --search-limit 调大）")
                break
        if hits == 0:
            print("[!] 没有命中")
        return 0

    print(f"# {args.file}")
    summarize(root, args.max_depth, collapse_scalar_arrays=not args.no_collapse)
    return 0


if __name__ == "__main__":
    sys.exit(main())
