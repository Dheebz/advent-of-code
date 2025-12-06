"""Reusable Intcode computer for Advent of Code 2019 puzzles."""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Iterable, List, Optional


class Intcode:
    """Simple Intcode interpreter supporting pausing for input or output."""

    def __init__(self, program: Iterable[int]) -> None:
        """Initialize interpreter state.

        Args:
            program (Iterable[int]): Program values to load into memory.
        """
        self.memory: Dict[int, int] = {idx: value for idx, value in enumerate(program)}
        self.ip = 0
        self.relative_base = 0
        self.halted = False
        self.waiting_for_input = False
        self._inputs: Deque[int] = deque()

    def clone(self) -> "Intcode":
        """Return a deep copy of the machine state."""
        clone = Intcode([])
        clone.memory = dict(self.memory)
        clone.ip = self.ip
        clone.relative_base = self.relative_base
        clone.halted = self.halted
        clone.waiting_for_input = self.waiting_for_input
        clone._inputs = deque(self._inputs)
        return clone

    def add_input(self, value: int) -> None:
        """Queue an input value."""
        self._inputs.append(value)
        self.waiting_for_input = False

    def _get(self, address: int) -> int:
        return self.memory.get(address, 0)

    def _set(self, address: int, value: int) -> None:
        self.memory[address] = value

    def _read_param(self, offset: int, mode: int) -> int:
        if mode == 0:
            return self._get(self._get(self.ip + offset))
        if mode == 1:
            return self._get(self.ip + offset)
        if mode == 2:
            return self._get(self.relative_base + self._get(self.ip + offset))
        raise ValueError(f"unknown mode {mode}")

    def _write_param(self, offset: int, mode: int, value: int) -> None:
        if mode == 0:
            address = self._get(self.ip + offset)
        elif mode == 2:
            address = self.relative_base + self._get(self.ip + offset)
        else:
            raise ValueError(f"invalid write mode {mode}")
        self._set(address, value)

    def run(
        self,
        inputs: Optional[Iterable[int]] = None,
        *,
        until_output: bool = False,
        default_input: int | None = None,
    ) -> List[int]:
        """Execute until halted or input starvation.

        When an input instruction is reached with no queued values, uses
        default_input when provided; otherwise sets waiting_for_input and stops.
        If until_output is True, returns after producing a single output.
        """
        if inputs is not None:
            for value in inputs:
                self.add_input(value)

        outputs: List[int] = []

        while not self.halted:
            instruction = self._get(self.ip)
            opcode = instruction % 100
            modes = [
                (instruction // 100) % 10,
                (instruction // 1000) % 10,
                (instruction // 10000) % 10,
            ]

            if opcode == 99:
                self.halted = True
                break

            if opcode in (1, 2, 7, 8):
                param1 = self._read_param(1, modes[0])
                param2 = self._read_param(2, modes[1])
                if opcode == 1:
                    result = param1 + param2
                elif opcode == 2:
                    result = param1 * param2
                elif opcode == 7:
                    result = int(param1 < param2)
                else:
                    result = int(param1 == param2)
                self._write_param(3, modes[2], result)
                self.ip += 4
                continue

            if opcode == 3:
                if self._inputs:
                    value = self._inputs.popleft()
                elif default_input is not None:
                    value = default_input
                else:
                    self.waiting_for_input = True
                    break
                self._write_param(1, modes[0], value)
                self.ip += 2
                continue

            if opcode == 4:
                outputs.append(self._read_param(1, modes[0]))
                self.ip += 2
                if until_output:
                    break
                continue

            if opcode in (5, 6):
                param1 = self._read_param(1, modes[0])
                param2 = self._read_param(2, modes[1])
                jump = (opcode == 5 and param1 != 0) or (opcode == 6 and param1 == 0)
                if jump:
                    self.ip = param2
                else:
                    self.ip += 3
                continue

            if opcode == 9:
                self.relative_base += self._read_param(1, modes[0])
                self.ip += 2
                continue

            raise ValueError(f"unknown opcode {opcode} at position {self.ip}")

        return outputs
