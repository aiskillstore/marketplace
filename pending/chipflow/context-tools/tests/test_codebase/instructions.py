"""Test file with enum-like classes for testing symbol search."""

from enum import Enum
from typing import Union


class InstructionData(Enum):
    """Represents different types of instructions in the IR."""

    # Basic instructions
    Nop = 0
    Return = 1
    Branch = 2

    # PHI-related instructions
    Phi = 3
    PhiNode = 4  # The actual variant we're looking for

    # Arithmetic instructions
    Add = 10
    Sub = 11
    Mul = 12
    Div = 13

    # Comparison instructions
    Eq = 20
    Ne = 21
    Lt = 22
    Le = 23
    Gt = 24
    Ge = 25


class ControlFlow:
    """Control flow instruction definitions."""

    def __init__(self, block_id: int):
        self.block_id = block_id

    def is_phi(self) -> bool:
        """Check if this is a PHI instruction."""
        return isinstance(self, PhiInstruction)


class PhiInstruction(ControlFlow):
    """PHI node instruction for SSA form."""

    def __init__(self, block_id: int, inputs: list):
        super().__init__(block_id)
        self.inputs = inputs

    def merge_values(self):
        """Merge values from different control flow paths."""
        pass
