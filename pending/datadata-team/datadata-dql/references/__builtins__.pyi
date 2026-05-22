from typing import final, overload, Any, List, Dict, Tuple, Optional, Union, Literal, Callable, TypedDict, TypeVar, Generic


T = TypeVar('T')

Number = int | float
"""
数字类型，int ho float
"""

DType = Literal["object", "int", "bool", "float", "string", "date", "time", "timetz", "timestamp", "timestamptz"]
"""
数据集数据类型
"""


@final
class json:
    @staticmethod
    def dumps(obj: Any, *, indent: None | int | str = None) -> str:
        """
        Serialize obj to a JSON formatted str

        Args:
          indent: 缩进
        """
        ...

    @staticmethod
    def loads(s: str) -> Any:
        """
        Deserialize s to an object
        """
        ...



@final
class math:
    @staticmethod
    def ceil(x: float) -> int:
        """
        Returns the ceiling of x, the smallest integer greater than or equal to x.
        """
        ...

    @staticmethod
    def copysign(x: float, y: float) -> float:
        """
        Returns a value with the magnitude of x and the sign of y.
        """
        ...

    @staticmethod
    def fabs(x: float) -> float:
        """
        Returns the absolute value of x as float.
        """
        ...

    @staticmethod
    def floor(x: float) -> int:
        """
        Returns the floor of x, the largest integer less than or equal to x.
        """
        ...

    @staticmethod
    def mod(x: float, y: float) -> float:
        """
        Returns the floating-point remainder of x/y. The magnitude of the result is less than y and its sign agrees with that of x.
        """
        ...

    @staticmethod
    def pow(x: float, y: float) -> float:
        """
        Returns x**y, the base-x exponential of y.
        """
        ...

    # remainder(x, y) - Returns the IEEE 754 floating-point remainder of x/y.
    @staticmethod
    def remainder(x: float, y: float) -> float:
        """
        Returns the IEEE 754 floating-point remainder of x/y.
        """
        ...

    # round(x) - Returns the nearest integer, rounding half away from zero.
    @staticmethod
    def round(x: float) -> int:
        """
        Returns the nearest integer, rounding half away from zero.
        """
        ...

    # exp(x) - Returns e raised to the power x, where e = 2.718281… is the base of natural logarithms.
    @staticmethod
    def exp(x: float) -> float:
        """
        Returns e raised to the power x, where e = 2.718281… is the base of natural logarithms.
        """
        ...

    # sqrt(x) - Returns the square root of x.
    @staticmethod
    def sqrt(x: float) -> float:
        """
        Returns the square root of x.
        """
        ...

    # acos(x) - Returns the arc cosine of x, in radians.
    @staticmethod
    def acos(x: float) -> float:
        """
        Returns the arc cosine of x, in radians.
        """
        ...

    # asin(x) - Returns the arc sine of x, in radians.
    @staticmethod
    def asin(x: float) -> float:
        """
        Returns the arc sine of x, in radians.
        """
        ...

    # atan(x) - Returns the arc tangent of x, in radians.
    @staticmethod
    def atan(x: float) -> float:
        """
        Returns the arc tangent of x, in radians.
        """
        ...

    # atan2(y, x) - Returns atan(y / x), in radians.
    @staticmethod
    def atan2(y: float, x: float) -> float:
        """
        Returns atan(y / x), in radians.

        The result is between -pi and pi.
        The vector in the plane from the origin to point (x, y) makes this angle with the positive X axis.
        The point of atan2() is that the signs of both inputs are known to it, so it can compute the correct
        quadrant for the angle.
        For example, atan(1) and atan2(1, 1) are both pi/4, but atan2(-1, -1) is -3*pi/4.
        """
        ...

    # cos(x) - Returns the cosine of x, in radians.
    @staticmethod
    def cos(x: float) -> float:
        """
        Returns the cosine of x, in radians.
        """
        ...

    # hypot(x, y) - Returns the Euclidean norm, sqrt(x*x + y*y). This is the length of the vector from the origin to point (x, y).
    @staticmethod
    def hypot(x: float, y: float) -> float:
        """
        Returns the Euclidean norm, sqrt(x*x + y*y). This is the length of the vector from the origin to point (x, y).
        """
        ...

    # sin(x) - Returns the sine of x, in radians.
    @staticmethod
    def sin(x: float) -> float:
        """
        Returns the sine of x, in radians.
        """
        ...

    # tan(x) - Returns the tangent of x, in radians.
    @staticmethod
    def tan(x: float) -> float:
        """
        Returns the tangent of x, in radians.
        """
        ...

    # degrees(x) - Converts angle x from radians to degrees.
    @staticmethod
    def degrees(x: float) -> float:
        """
        Converts angle x from radians to degrees.
        """
        ...

    # radians(x) - Converts angle x from degrees to radians.
    @staticmethod
    def radians(x: float) -> float:
        """
        Converts angle x from degrees to radians.
        """
        ...


    # acosh(x) - Returns the inverse hyperbolic cosine of x.
    @staticmethod
    def acosh(x: float) -> float:
        """
        Returns the inverse hyperbolic cosine of x.
        """
        ...


    # asinh(x) - Returns the inverse hyperbolic sine of x.
    @staticmethod
    def asinh(x: float) -> float:
        """
        Returns the inverse hyperbolic sine of x.
        """
        ...


    # atanh(x) - Returns the inverse hyperbolic tangent of x.
    @staticmethod
    def atanh(x: float) -> float:
        """
        Returns the inverse hyperbolic tangent of x.
        """
        ...


    # cosh(x) - Returns the hyperbolic cosine of x.
    @staticmethod
    def cosh(x: float) -> float:
        """
        Returns the hyperbolic cosine of x.
        """
        ...


    # sinh(x) - Returns the hyperbolic sine of x.
    @staticmethod
    def sinh(x: float) -> float:
        """
        Returns the hyperbolic sine of x.
        """
        ...


    # tanh(x) - Returns the hyperbolic tangent of x.
    @staticmethod
    def tanh(x: float) -> float:
        """
        Returns the hyperbolic tangent of x.
        """
        ...


    # log(x, base) - Returns the logarithm of x in the given base, or natural logarithm by default.
    @staticmethod
    def log(x: float, base: float) -> float:
        """
        Returns the logarithm of x in the given base, or natural logarithm by default.
        """
        ...


    # gamma(x) - Returns the Gamma function of x.
    @staticmethod
    def gamma(x: float) -> float:
        """
        Returns the Gamma function of x.
        """
        ...



@final
class Time():
    @property
    def tm_year(self) -> int:
        ...

    @property
    def tm_mon(self) -> int:
        ...

    @property
    def tm_mday(self) -> int:
        ...

    @property
    def tm_hour(self) -> int:
        ...

    @property
    def tm_min(self) -> int:
        ...

    @property
    def tm_sec(self) -> int:
        ...

    @property
    def tm_wday(self) -> int:
        ...

    @property
    def tm_yday(self) -> int:
        ...

    @property
    def tm_isdst(self) -> int:
        ...

@final
class time():
    altzone: int
    """
    返回格林威治西部的夏令时地区的偏移秒数。如果该地区在格林威治东部会返回负值（如西欧，包括英国）。对夏令时启用地区才能使用。
    """

    timezone: int
    """
    属性 time.timezone 是当地时区（未启动夏令时）距离格林威治的偏移秒数（>0，美洲<=0大部分欧洲，亚洲，非洲）。
    """

    tzname: tuple[str, str]
    """
    属性time.tzname包含一对根据情况的不同而不同的字符串，分别是带夏令时的本地时区名称，和不带的。
    """

    @staticmethod
    def asctime(t: Time = ..., /) -> str:
        """
        接受时间对象并返回一个可读的形式为"Tue Dec 11 18:07:14 2008"（2008年12月11日 周二18时07分14秒）的24个字符的字符串。
        """
        ...

    @staticmethod
    def ctime(seconds: float | None = None, /) -> str:
        """
        作用相当于asctime(localtime(secs))，未给参数相当于asctime()
        """
        ...

    @staticmethod
    def gmtime(seconds: float | None = None, /) -> Time:
        """
        接收时间戳（1970纪元后经过的浮点秒数）并返回格林威治天文时间下的时间t。
        """
        ...

    @staticmethod
    def localtime(seconds: float | None = None, /) -> Time:
        """
        接收时间戳（1970纪元后经过的浮点秒数）并返回当地时间下的时间t。
        """
        ...

    @staticmethod
    def mktime(t: Time, /) -> float:
        """
        接受时间元组并返回时间戳（1970纪元后经过的浮点秒数）。
        """
        ...

    @staticmethod
    def strftime(format: str, t: Time = ..., /) -> str:
        """
        接收以时间元组，并返回以可读字符串表示的当地时间，格式由fmt决定。
        """
        ...

    @staticmethod
    def strptime(data_string: str, format: str = "%a %b %d %H:%M:%S %Y", /) -> Time:
        """
        根据fmt的格式把一个时间字符串解析为时间对象。
        """
        ...

    @staticmethod
    def time() -> float:
        """
        返回当前时间的时间戳（1970纪元后经过的浮点秒数）。
        """
        ...


@final
class canvas():
    @staticmethod
    def Context(width: int, height: int) -> Context:
        """
        创建一个新的 canvas.Context 对象

        Args:
            width (int): canvas 的宽度
            height (int): canvas 的高度

        Returns:
            Context: Context 对象
        """
        ...
    @staticmethod
    def radians(degrees: float) -> float:
        """
        将角度转换为弧度
        """
        ...
    @staticmethod
    def degrees(radians: float) -> float:
        """
        将弧度转换为角度
        """
        ...
class Context():
    def draw_point(self, x: float, y: float, r: float) -> None: ...
    def draw_line(self, x1: float, y1: float, x2: float, y2: float) -> None: ...
    def draw_rectangle(self, x: float, y: float, w: float, h: float) -> None: ...
    def draw_rounded_rectangle(self, x: float, y: float, w: float, h: float, r: float) -> None: ...
    def draw_circle(self, x: float, y: float, r: float) -> None: ...
    def draw_arc(self, x: float, y: float, r: float, angle1: float, angle2: float) -> None: ...
    def draw_ellipse(self, x: float, y: float, rx: float, ry: float) -> None: ...
    def draw_elliptical_arc(self, x: float, y: float, rx: float, ry: float, angle1: float, angle2: float) -> None: ...
    def draw_regular_polygon(self, n: int, x: float, y: float, r: float, rotation: float) -> None: ...
    def set_pixel(self, x: int, y: int) -> None: ...
    def move_to(self, x: float, y: float) -> None: ...
    def line_to(self, x: float, y: float) -> None: ...
    def quadratic_to(self, x1: float, y1: float, x2: float, y2: float) -> None: ...
    def cubic_to(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> None: ...
    def close_path(self) -> None: ...
    def clear_path(self) -> None: ...
    def new_sub_path(self) -> None: ...
    def clear(self) -> None: ...
    def stroke(self) -> None: ...
    def fill(self) -> None: ...
    def stroke_preserve(self) -> None: ...
    def fill_preserve(self) -> None: ...
    # Text Functions
    def draw_string(self, s: str, x: float, y: float) -> None: ...
    def draw_string_anchored(self, s: str, x: float, y: float, ax: float, ay: float) -> None: ...
    def draw_string_wrapped( self, s: str, x: float, y: float, ax: float, ay: float, width: float, lineSpacing: float, align: 0|1|2 ) -> None: ...
    def measure_string(self, s: str) -> Tuple[float, float]: ...
    def measure_multiline_string(self, s: str, lineSpacing: float) -> Tuple[float, float]: ...
    def word_wrap(self, s: str, w: float) -> List[str]: ...
    # Color Functions
    def set_rgb(self, r: float, g: float, b: float) -> None: ...
    def set_rgba(self, r: float, g: float, b: float, a: float) -> None: ...
    def set_rgb255(self, r: int, g: int, b: int) -> None: ...
    def set_rgba255(self, r: int, g: int, b: int, a: int) -> None: ...
    def set_hex_color(self, x: str) -> None: ...
    # Stroke & Fill Options
    def set_line_width(self, lineWidth: float) -> None: ...
    def set_line_cap(self, lineCap: 0|1|2) -> None: ...
    def set_line_join(self, lineJoin: 0|1) -> None: ...
    def set_dash(self, *dashes: float) -> None: ...
    def set_dash_offset(self, offset: float) -> None: ...
    def set_fill_rule(self, fillRule: 0|1) -> None: ...
    # Gradients & Patterns
    def new_linear_gradient(self, x0: float, y0: float, x1: float, y1: float) -> None: ...
    def new_radial_gradient(self, x0: float, y0: float, r0: float, x1: float, y1: float, r1: float) -> None: ...
    def new_conic_gradient(self, cx: float, cy: float, deg: float) -> None: ...
    # Transformation Functions
    def identity(self) -> None: ...
    def translate(self, x: float, y: float) -> None: ...
    def scale(self, x: float, y: float) -> None: ...
    def rotate(self, angle: float) -> None: ...
    def shear(self, x: float, y: float) -> None: ...
    def scale_about(self, sx: float, sy: float, x: float, y: float) -> None: ...
    def rotate_about(self, angle: float, x: float, y: float) -> None: ...
    def shear_about(self, sx: float, sy: float, x: float, y: float) -> None: ...
    def transform_point(self, x: float, y: float) -> Tuple[float, float]: ...
    def invert_y(self) -> None: ...
    # Stack Functions
    def push(self) -> None: ...
    def pop(self) -> None: ...
    # Clipping Functions
    def clip(self) -> None: ...
    def clip_preserve(self) -> None: ...
    def reset_clip(self) -> None: ...
    def invert_mask(self) -> None: ...
    # 其他方法
    def get_data_uri(self) -> str: ...



def query(sql: str, *args: Number | str) -> DataFrame:
    """
    执行 SQL 查询
    """
    ...


@final
class Response:
    ok: bool
    """
    Whether the request was successful. status code >= 200 and < 300
    """
    proto: str
    """
    HTTP version
    """
    proto_major: int
    """
    HTTP major version
    """
    proto_minor: int
    """
    HTTP minor version
    """
    status: int
    """
    HTTP status code
    """
    status_text: str
    """
    HTTP status text
    """
    uncompressed: bool
    """
    Whether the response was uncompressed
    """
    headers: Dict[str, str]
    """
    HTTP headers
    """
    body: Any
    """
    HTTP body, can be str or dict
    """

def fetch(url: str, method=Literal["GET", "PUT", "POST", "HEAD", "DELETE"], headers: Dict[str, str]=None, body: Any=None, timeout: int=30) -> Response:
    """
    Perform an HTTP request.

    Args:
        url (str): The URL to request.
        method (str, optional): The HTTP method to use (GET, POST, etc.). Defaults to "GET".
        headers (dict, optional): A dictionary of HTTP headers to include in the request. Defaults to None.
        body (str, optional): The body of the request for POST method. Defaults to None.
        timeout (int, optional): Timeout in seconds for the request. Defaults to 30.

    Returns:
        Response: A dictionary containing the status code, headers, and body of the response.
    """
    ...



class LocIndexer:
    """
    位置索引器
    """



class LocIndexerSeries(LocIndexer):
    @overload
    def __getitem__(self, key: Series[bool]) -> Series:
        ...



class LocIndexerDataFrame(LocIndexer):
    @overload
    def __getitem__(self, key: int) -> Dict[str, Any]:
        ...

    @overload
    def __getitem__(self, key: Tuple[int, str]) -> Any:
        ...

    @overload
    def __getitem__(self, key: List) -> DataFrame:
        ...

    @overload
    def __getitem__(self, key: Tuple[list[int], str]) -> Series[Any]:
        ...

    @overload
    def __getitem__(self, key: Series[bool]) -> DataFrame:
        ...


class DataFrame:
    """
    DataFrame 表示一个二维表格
    """

    @overload
    def __getitem__(self, key: str) -> Series:
        """
        返回 DataFrame 中的元素
        """

    @overload
    def __getitem__(self, key: int) -> Dict[str, Any]:
        """
        返回 DataFrame 的一行
        """

    def __init__(self):
        ...

    columns: any

    dtypes: any

    size: any

    shape: any

    empty: any

    has_more: any

    loc: LocIndexerDataFrame
    """
    索引器
    """

    def head(self):
        ...

    def tail(self):
        ...

    def rename(self):
        ...

    def items(self):
        ...

    def iterrows(self):
        ...

    def to_list(self):
        ...

    def append(self):
        ...

    def ffill(self):
        ...

    def bfill(self):
        ...

    def fillna(self):
        ...

    def apply(self):
        ...

    def merge(self):
        ...

    def nunique(self):
        ...

    def abs(self):
        ...

    def min(self):
        ...

    def max(self):
        ...

    def sum(self):
        ...

    def count(self):
        ...

    def std(self):
        ...

    def var(self):
        ...

    def mean(self):
        ...

    def mode(self):
        ...

    def skew(self):
        ...

    def kurt(self):
        ...

    def median(self):
        ...

    def diff(self):
        ...

    def cumprod(self):
        ...

    def pct_change(self):
        ...

    def sort_values(self):
        ...

    def pivot(self):
        ...

    def rolling(self):
        ...

    def resample(self):
        ...

    def round(self):
        ...

    def groupby(self):
        ...

    def drop_duplicates(self, subset: str|List[str] = None, keep: Literal["first", "last", False] = 'first', inplace: bool = False) -> DataFrame:
        """
        返回已删除重复值的 DataFrame
        
        Args:
            subset: subset
            inplace: 是否在原对象上进行填充
        
        
        Returns:
            已删除重复值的 DataFrame
        
        """
        ...


class DataFrameGroupBy:

    def apply(self):
        ...

    def transform(self):
        ...

    def aggregation(self):
        ...

    def min(self):
        ...

    def max(self):
        ...

    def sum(self):
        ...

    def std(self):
        ...

    def var(self):
        ...

    def mean(self):
        ...

    def skew(self):
        ...

    def kurt(self):
        ...

    def median(self):
        ...

    def diff(self):
        ...

    def cumprod(self):
        ...

    def pct_change(self):
        ...


class ExponentialMovingWindow:

    def mean(self):
        ...

    def sum(self):
        ...

    def var(self):
        ...

def concat(objs: Union[Series, DataFrame], join: Literal["inner", "outer"] = "outer") -> Union[Series, DataFrame]:
    """
    用于连接 Series 或 DataFrame 对象
    
    Args:
        objs: Series 或 DataFrame
    
    
    Returns:
        返回合并后的 Series 或 DataFrame
    
    """
    ...

def throw(err: Any):
    """
    抛出错误
    
    Args:
        err: 任意错误信息
    
    """
    ...

def Error():
    ...


class Interval:

    def __init__(self, left: Number, right: Number, closed: Literal["left", "right", "both", "neither"] = "right"):
        """
        区间对象
        
        Args:
            left: 区间左端点
            right: 区间右端点
            closed: 区间闭合类型
        
        """
        ...

    length: Number
    """
    The length of the Interval
    """


class Resampler:

    def min(self):
        ...

    def max(self):
        ...

    def sum(self):
        ...

    def std(self):
        ...

    def var(self):
        ...

    def mean(self):
        ...

    def skew(self):
        ...

    def kurt(self):
        ...

    def apply(self):
        ...


class Rolling:

    def min(self):
        ...

    def max(self):
        ...

    def sum(self):
        ...

    def std(self):
        ...

    def var(self):
        ...

    def mean(self):
        ...

    def skew(self):
        ...

    def kurt(self):
        ...

    def median(self):
        ...

    def apply(self):
        ...


class Series(Generic[T]):
    """
    Series 表示一列数据
    """

    def __eq__(self, other: Any) -> Series[bool]:
        """
        相等
        """

    def __init__(self, data, dtype: DType, name: str):
        """
        Series 表示数据表中的一行
        
        Args:
            data: 数据
            dtype: 数据类型
            name: 名称
        
        """
        ...

    name: str
    """
    列名
    """

    size: int
    """
    长度
    """

    dtype: DType
    """
    数据类型
    """

    group: any

    loc: LocIndexerSeries
    """
    索引器
    """

    def map(self, fn: Callable[[any], any], ignore_none: bool = None):
        """
        Map Series to a new Series.
        
        Args:
            fn: 映射函数
            ignore_none: 忽略 None
        
        """
        ...

    def apply(self, fn: Callable[[any], any]):
        """
        Invoke function on values of Series.
        
        Args:
            fn: 函数
        
        """
        ...

    def filter(self, fn: Callable[[any], any]):
        """
        根据给定的函数过滤 Series 中的元素。
        
        Args:
            fn: 函数
        
        """
        ...

    def reduce(self, fn: Callable[[any], any], acc: Any):
        """
        对 Series 中的元素进行累积计算
        
        Args:
            fn: 函数
            acc: 初始值
        
        """
        ...

    def append(self, value: Any):
        """
        向 Series 添加一个值。
        
        Args:
            value: 添加到 Series 的值
        
        """
        ...

    def ffill(self, inplace: bool = False):
        """
        Fill NA/NaN values by propagating the last valid observation to next valid.
        
        Args:
            inplace: 是否在原对象上进行填充
        
        """
        ...

    def bfill(self, inplace: bool = False):
        """
        Fill NA/NaN values by using the next valid observation to fill the gap.
        
        Args:
            inplace: 是否在原对象上进行填充
        
        """
        ...

    def fillna(self, value: Any, inplace: bool = False):
        """
        Fill NA/NaN values using the specified method.
        
        Args:
            value: 填充值
            inplace: 是否在原对象上进行填充
        
        """
        ...

    def unique(self) -> List[Any]:
        """
        Return unique values of Series object.
        
        Uniques are returned in order of appearance. Hash table-based unique, therefore does NOT sort.
        
        Returns:
            去重后的值
        
        """
        ...

    def nunique(self, dropna: bool):
        """
        Return number of unique elements in the object.
        
        Args:
            dropna: Don't include NaN in the count
        
        """
        ...

    def replace(self, to_replace: Any, value: Any, inplace: bool):
        """
        Replace values given in to_replace with value.
        
        Args:
            to_replace: find the values that will be replaced
            value: Value to replace any values matching to_replace with
            inplace: If True, performs operation inplace
        
        """
        ...

    def isin(self, value: List):
        """
        Whether elements in Series are contained in values.
        
        Return a boolean Series showing whether each element in the Series matches an element in the passed sequence of values exactly.
        
        Args:
            value: Value to replace any values matching to_replace with
        
        """
        ...

    def abs(self):
        """
        Return a Series/DataFrame with absolute numeric value of each element.
        
        This function only applies to elements that are all numeric.
        """
        ...

    def min(self, skipna: bool, numeric_only: bool):
        """
        Return the minimum of the values over the requested axis.
        
        Args:
            skipna: Exclude NA/null values when computing the result.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        """
        ...

    def max(self, skipna: bool, numeric_only: bool):
        """
        Return the maximum of the values over the requested axis.
        
        Args:
            skipna: Exclude NA/null values when computing the result.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        """
        ...

    def sum(self, skipna: bool, numeric_only: bool):
        """
        Return the sum of the values over the requested axis.
        
        Args:
            skipna: Exclude NA/null values when computing the result.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        """
        ...

    def std(self, skipna: bool, ddof: int, numeric_only: bool):
        """
        Return sample standard deviation over requested axis.
        
        Normalized by N-1 by default. This can be changed using the ddof argument.
        
        Args:
            skipna: Exclude NA/null values when computing the result.
            ddof: Delta Degrees of Freedom. The divisor used in calculations is N - ddof, where N represents the number of elements.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        """
        ...

    def var(self, skipna: bool, ddof: int, numeric_only: bool):
        """
        Return unbiased variance over requested axis.
        
        Normalized by N-1 by default. This can be changed using the ddof argument.
        
        Args:
            skipna: Exclude NA/null values when computing the result.
            ddof: Delta Degrees of Freedom. The divisor used in calculations is N - ddof, where N represents the number of elements.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        """
        ...

    def cov(self, other: Series, min_periods: int, ddof: int):
        """
        Compute covariance with Series, excluding missing values.
        
        The two Series objects are not required to be the same length and will be aligned internally before the covariance is calculated.
        
        Args:
            other: Series with which to compute the correlation.
            min_periods: Minimum number of observations needed to have a valid result.
            ddof: Delta Degrees of Freedom. The divisor used in calculations is N - ddof, where N represents the number of elements.
        
        """
        ...

    def corr(self, other: Series, min_periods: int, ddof: int):
        """
        Compute correlation with other Series, excluding missing values.
        
        The two Series objects are not required to be the same length and will be aligned internally before the correlation function is applied.
        
        Args:
            other: Series with which to compute the correlation.
            min_periods: Minimum number of observations needed to have a valid result.
            ddof: Delta Degrees of Freedom. The divisor used in calculations is N - ddof, where N represents the number of elements.
        
        """
        ...

    def lin_reg(self, other: Series):
        """
        线性回归
        
        Args:
            other: Series with which to compute
        
        """
        ...

    def r2(self, other: Series, alpha: float, beta: float):
        """
        线性回归模型的决定系数
        
        Args:
            other: Series with which to compute
            alpha: 系数
            beta: 常数
        
        """
        ...

    def mean(self, skipna: bool, numeric_only: bool):
        """
        Return the mean of the values over the requested axis.
        
        Args:
            skipna: Exclude NA/null values when computing the result.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        """
        ...

    def count(self) -> int:
        """
        Return number of non-NA/null observations in the Series.
        
        Returns:
            Number of non-NA/null observations
        
        """
        ...

    def round(self, decimals: int) -> Series:
        """
        Return number of non-NA/null observations in the Series.
        
        Args:
            decimals: Number of decimal places to round to. If decimals is 0, returns the integer part of the result.
        
        
        Returns:
            Rounded values of the Series.
        
        """
        ...

    def mode(self, dropna: bool) -> Series:
        """
        Return the mode(s) of the Series.
        
        The mode is the value that appears most often. There can be multiple modes.
        
        Always returns Series even if only one value is returned.
        
        Args:
            dropna: Don't consider counts of NaN/NaT.
        
        
        Returns:
            Modes of the Series in sorted order.
        
        """
        ...

    def skew(self, dropna: bool, numeric_only: bool) -> float:
        """
        Return unbiased skew over requested axis.
        
        Normalized by N-1.
        
        Args:
            dropna: Don't consider counts of NaN/NaT.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        
        Returns:
            scalar or scalar
        
        """
        ...

    def kurt(self, dropna: bool, numeric_only: bool) -> float:
        """
        Return unbiased kurtosis over requested axis.
        
        Kurtosis obtained using Fisher's definition of kurtosis (kurtosis of normal == 0.0). Normalized by N-1.
        
        Args:
            dropna: Don't consider counts of NaN/NaT.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        
        Returns:
            scalar or scalar
        
        """
        ...

    def median(self, skipna: bool, numeric_only: bool) -> float:
        """
        Return the median of the values over the requested axis.
        
        Args:
            skipna: Exclude NA/null values when computing the result.
            numeric_only: Include only float, int, boolean columns. Not implemented for Series.
        
        
        Returns:
            scalar or scalar
        
        """
        ...

    def diff(self, periods: int = 1) -> Series:
        """
        First discrete difference of element.
        
        Calculates the difference of a Series element compared with another element in the Series (default is element in previous row).
        
        Args:
            periods: Periods to shift for calculating difference, accepts negative values.
        
        
        Returns:
            First differences of the Series.
        
        """
        ...

    def cumprod(self, skipna: bool) -> Series:
        """
        Return cumulative product over a DataFrame or Series axis.
        
        Returns a DataFrame or Series of the same size containing the cumulative product.
        
        Args:
            skipna: Exclude NA/null values. If an entire row/column is NA, the result will be NA.
        
        
        Returns:
            Return cumulative product of scalar or Series.
        
        """
        ...

    def rolling(self, window: any, min_periods: int, timeline: Series) -> Rolling:
        """
        Provide rolling window calculations.
        
        Args:
            window: Size of the moving window.
            min_periods: Minimum number of observations in window required to have a value
            timeline: timeline of the window.
        
        
        Returns:
            滚动窗口对象
        
        """
        ...

    def ewm(self, com: float, span: float, alpha: float, min_periods: int, adjust: bool) -> ExponentialMovingWindow:
        """
        Provide exponentially weighted (EW) calculations.
        Exactly one of `com`, `span`, `halflife`, or `alpha` must be provided if times is not provided.
        If `times` is provided, `halflife` and one of `com`, `span` or `alpha` may be provided.
        
        Args:
            com: Specify decay in terms of center of mass. comass must satisfy: comass >= 0.
            span: Specify decay in terms of span. span must satisfy: span >= 1.
            alpha: Specify smoothing factor α directly. alpha must satisfy: 0 < alpha <= 1.
            min_periods: Minimum number of observations in window required to have a value; otherwise, result is np.nan.
            adjust: Divide by decaying adjustment factor in beginning periods to account for imbalance in relative weightings (viewing EWMA as a moving average).
        
        
        Returns:
            指数移动窗口
        
        """
        ...

    def resample(self, rule: str, timeline: Series) -> Resampler:
        """
        Resample time-series data.
        
        Args:
            rule: Resampling rule
            timeline: timeline to use.
        
        
        Returns:
            Resampler object.
        
        """
        ...

    def pct_change(self, periods: int) -> Series:
        """
        Fractional change between the current and a prior element.
        
        Args:
            periods: Periods to shift for forming percent change.
        
        
        Returns:
            The same type as the calling object.
        
        """
        ...

    def value_counts(self, normalize: bool = False, sort: bool = True, ascending: bool = False, bins: int = None, dropna: bool = True) -> Series:
        """
        Return a Series containing counts of unique values.
        
        Args:
            normalize: If True then the object returned will contain the relative frequencies of the unique values.
            sort: Sort by frequencies when True. Preserve the order of the data when False.
            ascending: Sort in ascending order.
            bins: Rather than count values, group them into half-open bins, a convenience for pd.cut, only works with numeric data.
            dropna: Don't include counts of NaN.
        
        
        Returns:
            series
        
        """
        ...

    def rename(self, name: str) -> Series:
        """
        Alter Series index labels or name.
        
        Args:
            name: new series name
        
        
        Returns:
            series
        
        """
        ...

    def items(self) -> any:
        """
        Iterate over (index, value) tuples.
        
        Returns:
            Iterable of tuples containing the (index, value) pairs from a Series.
        
        """
        ...

    def values(self) -> List:
        """
        Return Series value list
        
        Returns:
            values
        
        """
        ...

    def to_list(self) -> List:
        """
        Return a list of the values.
        
        Returns:
            values
        
        """
        ...

    def sort_values(self, ascending: bool = True, inplace: bool = False, na_position: str = 'last') -> Series:
        """
        Sort by the values.
        
        Args:
            ascending: If True, sort values in ascending order, otherwise descending.
            inplace: If True, perform operation in-place.
            na_position: Argument ‘first’ puts NaNs at the beginning, ‘last’ puts NaNs at the end.
        
        
        Returns:
            Series ordered by values
        
        """
        ...

    def nsmallest(self, n: int = 5, keep: str = 'first') -> Series:
        """
        Return the smallest n elements.
        
        Args:
            n: Return this many ascending sorted values.
            keep: When there are duplicate values that cannot all fit in a Series of n elements: first: return the first n occurrences in order of appearance. last: return the last n occurrences in reverse order of appearance. all: keep all occurrences. This can result in a Series of size larger than n.
        
        
        Returns:
            The n smallest values in the Series, sorted in increasing order.
        
        """
        ...

    def nlargest(self, n: int = 5, keep: str = 'first') -> Series:
        """
        Return the largest n elements.
        
        Args:
            n: Return this many descending sorted values.
            keep: When there are duplicate values that cannot all fit in a Series of n elements: first: return the first n occurrences in order of appearance. last: return the last n occurrences in reverse order of appearance. all: keep all occurrences. This can result in a Series of size larger than n.
        
        
        Returns:
            The n largest values in the Series, sorted in decreasing order.
        
        """
        ...

    def drop_duplicates(self, keep: Literal["first", "last", False] = 'first', inplace: bool = False) -> Series:
        """
        返回已删除重复值的Series
        
        Args:
            inplace: 是否在原对象上进行填充
        
        
        Returns:
            已删除重复值的Series
        
        """
        ...


class SeriesGroupBy:

    def min(self):
        ...

    def max(self):
        ...

    def sum(self):
        ...

    def std(self):
        ...

    def var(self):
        ...

    def mean(self):
        ...

    def skew(self):
        ...

    def kurt(self):
        ...

    def median(self):
        ...

    def apply(self):
        ...

    def transform(self):
        ...

    def diff(self):
        ...

    def cumprod(self):
        ...

    def pct_change(self):
        ...


class Timestamp:

    def __init__(self, value: Union[str, int]):
        """
        Timestamp
        
        	Timestamp("2024-05-07T15:06:24+08:00")
        
        Args:
            value: 支持常见的时间、日期格式，如果参数为 int 则代表以毫秒表示的 unix 时间戳
        
        """
        ...

    dtype: str
    """
    时间戳的类型
    """
