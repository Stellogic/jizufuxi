from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "计算机组成原理考前速背.md"

text = TARGET.read_text(encoding="utf-8")
marker = "### 12. 低频但可能偷袭的点"

addition = """

### 12. 低频但可能偷袭的点

- 存储器技术指标：存储容量、存取时间、存储周期、存储器带宽、位价、可靠性。存取时间是一次访问从启动到完成的时间，存储周期是两次连续访问之间的最短间隔。
- 双端口存储器：同一个存储器有两套相互独立的地址、数据和控制端口，可支持两个部件同时访问；若同时访问同一单元，需要冲突检测和仲裁。
- 堆栈寻址：操作数默认在栈顶，由栈指针 SP 指出，常用于子程序调用、中断现场保护、表达式求值。
- 程序查询方式基本过程：CPU 启动外设 -> 读状态寄存器 -> 判断 Ready 位 -> 未就绪继续查 -> 就绪后传送数据 -> 判断是否传完。
- 无条件传送/程序直接控制：默认外设总是准备好，不查询状态，硬件简单但适用范围窄。
- 中断方式涉及的问题：中断源识别、中断判优、中断屏蔽、中断嵌套、现场保护和恢复、中断向量。
- 通道类型：字节多路通道适合多台低速设备交叉传送；数组多路通道适合多台高速设备成组交叉传送；选择通道一次只为一台高速设备服务。
- 不同外设接入主机要解决的问题：速度差异、数据格式转换、命令传送、状态反馈、数据地址识别和控制。
- 性能指标易混：吞吐率是单位时间完成多少任务，响应时间是完成一个任务花多久。
"""

if marker not in text:
    text = text.rstrip() + addition + "\n"
    TARGET.write_text(text, encoding="utf-8")
    print("appended low-frequency points")
else:
    print("low-frequency points already present")
