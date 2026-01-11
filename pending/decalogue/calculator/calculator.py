"""
Calculator 实现脚本
可以在 Agent 的 Python 环境中执行
"""
import re


def safe_calculate(expression: str) -> float:
    """
    安全地计算数学表达式
    
    Args:
        expression: 数学表达式字符串
    
    Returns:
        计算结果
    """
    # 移除空格
    expression = expression.replace(" ", "")
    
    # 将 ^ 替换为 **
    expression = expression.replace("^", "**")
    
    # 验证表达式只包含数字、运算符和括号
    if not re.match(r'^[0-9+\-*/().\s**]+$', expression):
        raise ValueError("表达式包含不允许的字符")
    
    # 执行计算
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except ZeroDivisionError:
        raise ValueError("除以零")
    except Exception as e:
        raise ValueError(f"计算错误: {str(e)}")


if __name__ == "__main__":
    # 测试
    test_cases = [
        "2 + 3",
        "10 * 5",
        "100 / 4",
        "2 ** 8",
        "(5 + 3) * 2"
    ]
    
    for expr in test_cases:
        try:
            result = safe_calculate(expr)
            print(f"{expr} = {result}")
        except Exception as e:
            print(f"{expr} -> 错误: {e}")
