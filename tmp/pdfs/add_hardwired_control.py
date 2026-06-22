from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "计算机组成原理考前速背.md"

text = TARGET.read_text(encoding="utf-8")

replacements = [
    (
        "5. 第 5 章：CPU 基本功能、组成、指令周期；微程序控制器思想；微命令、微操作、微指令、微程序；流水 CPU 时空图和流水线主要问题。",
        "5. 第 5 章：CPU 基本功能、组成、指令周期；微程序控制器思想；硬布线/硬连线控制器思想；微命令、微操作、微指令、微程序；流水 CPU 时空图和流水线主要问题。",
    ),
    (
        "- 微命令、微操作、微指令、微程序的概念。\n- 水平型/垂直型微指令、字段译码法。",
        "- 微命令、微操作、微指令、微程序的概念。\n- 微程序控制器与硬布线/硬连线控制器的区别。\n- 水平型/垂直型微指令、字段译码法。",
    ),
    (
        "- CPU 数据通路、指令周期流程图、微操作控制信号。\n- 相斥/相容微操作判断，微指令控制字段编码。",
        "- CPU 数据通路、指令周期流程图、微操作控制信号。\n- 硬布线控制信号生成逻辑与微程序控制流程对比。\n- 相斥/相容微操作判断，微指令控制字段编码。",
    ),
    (
        "8. 微程序：用微指令序列解释执行机器指令。",
        "8. 微程序：用微指令序列解释执行机器指令。\n9. 硬布线控制：由组合逻辑电路直接产生控制信号，速度快但修改困难。",
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"target block not found: {old[:80]}")
    text = text.replace(old, new, 1)

section = """

### 2.5 硬布线/硬连线控制器

硬布线控制器也叫硬连线控制器，核心思想是：用组合逻辑电路根据指令操作码、节拍信号、状态条件和标志位，直接产生各个控制信号。

必背对比：

- 硬布线控制器：控制信号由逻辑门电路直接生成，速度快；结构固定，设计和修改困难，适合 RISC 或指令系统较简单的机器。
- 微程序控制器：控制信号由控制存储器中的微指令产生，设计规整，修改和扩展方便；需要读取微指令，速度相对慢，适合 CISC 或指令系统复杂的机器。

硬布线控制信号来源：

```text
控制信号 = f(指令操作码, 时序节拍, 状态条件, 标志位)
```

简答模板：

硬布线控制器不把控制过程写成微程序，而是把每条机器指令在各节拍应发出的微命令固化为逻辑电路。CPU 取出并译码指令后，控制器根据操作码、节拍脉冲和状态标志，经组合逻辑产生控制信号，控制数据通路完成指令执行。

选择题易混：

- 速度：硬布线通常快于微程序。
- 灵活性：微程序强于硬布线。
- 修改指令系统：微程序可改控存内容，硬布线通常要改电路。
- 复杂指令系统：更适合微程序控制。
"""

anchor = "### 3. 流水线\n"
if "### 2.5 硬布线/硬连线控制器" not in text:
    if anchor not in text:
        raise SystemExit("流水线 anchor not found")
    text = text.replace(anchor, section + "\n" + anchor, 1)

appendix_anchor = "### 7. CISC 与 RISC\n"
appendix_insert = """
### 6.5 硬布线控制器补充

- 硬布线控制器靠组合逻辑直接产生微命令，不需要控制存储器。
- 输入通常包括：指令译码结果、节拍/时序信号、条件码或状态标志、中断/异常等条件。
- 优点：速度快，控制信号产生直接。
- 缺点：电路复杂，设计调试困难，指令系统改变时不易修改。
- 和微程序控制器比较时，按“速度 vs 灵活性”答：硬布线速度快，微程序灵活、易扩展。

"""

if "### 6.5 硬布线控制器补充" not in text:
    if appendix_anchor not in text:
        raise SystemExit("appendix anchor not found")
    text = text.replace(appendix_anchor, appendix_insert + appendix_anchor, 1)

TARGET.write_text(text, encoding="utf-8")
print("hardwired control added")
