from langchain_core.runnables import Runnable
from langchain_core.tools import tool
from pydantic import BaseModel, Field


"""
    ###标准的tool 工具应该怎么写####
    1.要有装饰器 @tool   from langchain_core.tools import tool
    2.要有工具注解 """""" 这种方式
    3.要有参数注解  可参考下面的 选择一种
    4.参数要有类型 a:float 这种
"""






class CalculateArgs(BaseModel):
    a: float = Field(description="第一个需要输入的数字。")
    b: float = Field(description="第二个需要输入的数字。")
    operation: str = Field(description="运算类型，只能是add、subtract、multiply和divide中的任意一个。")


@tool('calculate', args_schema=CalculateArgs)
def calculate2(a: float, b: float, operation: str) -> float:
    """工具函数：计算两个数字的运算结果"""
    print(f"调用 calculate 工具，第一个数字：{a}, 第二个数字：{b}, 运算类型：{operation}")

    result = 0.0
    match operation:
        case "add":
            result = a + b
        case "subtract":
            result = a - b
        case "multiply":
            result = a * b
        case "divide":
            if b != 0:
                result = a / b
            else:
                raise ValueError("除数不能为零")

    return result


@tool('calculate')
def calculate3(
        x: Annotated[float, '第一个需要输入的数字,必须要传入。'],
        y: Annotated[float, '第二个需要输入的数字,必须要传入。'],
        operation: Annotated[str, '运算类型，只能是add、subtract、multiply和divide中的任意一个,必须要传入。']) -> float:
    """工具函数：计算两个数字的运算结果"""
    print(f"调用 calculate 工具，第一个数字：{x}, 第二个数字：{y}, 运算类型：{operation}")

    result = 0.0
    match operation:
        case "add":
            result = x + y
        case "subtract":
            result = x - y
        case "multiply":
            result = x * y
        case "divide":
            if y != 0:
                result = x / y
            else:
                raise ValueError("除数不能为零")

    return result

@tool('calculate', parse_docstring=True)
def calculate4(
        a: float,
        b: float,
        operation: str) -> float:
    """工具函数：计算两个数字的运算结果

    Args:
        a: 第一个需要输入的数字。
        b: 第二个需要输入的数字。
        operation: 运算类型，只能是add、subtract、multiply和divide中的任意一个。

    Returns:
        返回两个输入数字的运算结果。

    """
    print(f"调用 calculate 工具，第一个数字：{a}, 第二个数字：{b}, 运算类型：{operation}")

    result = 0.0
    match operation:
        case "add":
            result = a + b
        case "subtract":
            result = a - b
        case "multiply":
            result = a * b
        case "divide":
            if b != 0:
                result = a / b
            else:
                raise ValueError("除数不能为零")

    return result
