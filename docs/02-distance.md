# 第二课：从经纬度计算米制距离

第一课按类别筛选；本课增加“距离”的概念，为后面的附近地点查询做准备。
本课只实现一个函数 `distance_m(lon1, lat1, lon2, lat2)`。按半径筛选、排序和参数校验将在后续课程完成。

## 1. 获取本课的新增材料

从聊天中下载 `gis-agent-lesson-02.zip`，拖入 Codespaces 左侧文件资源管理器的项目根目录。
在项目根目录的终端执行：

```bash
pwd
python3 -m zipfile -e gis-agent-lesson-02.zip .
```

这个压缩包只有以下 5 个新文件，不包含第一课文件：

```text
requirements-lesson-02.txt
docs/02-distance.md
examples/measure_distances.py
exercises/lesson_02.py
checks/lesson_02.py
```

确认 `ls examples` 能看到 `measure_distances.py`，再继续。
如果这些第二课文件已经存在且你已修改过，请继续使用自己的文件，避免再次解压覆盖同名文件。

## 2. 在自己的虚拟环境安装 pyproj

```bash
source .venv/bin/activate
python -m pip install -r requirements-lesson-02.txt
```

`pyproj` 是地理计算库，本课使用已经验证的 `3.7.2` 版本。
`python -m pip` 使用当前 Python 对应的包安装工具；`install` 表示安装；`-r` 表示从指定文件读取依赖清单。
安装发生在你的 Codespaces 环境中。导师环境中安装过，并不意味着你的环境里也已安装。

验证安装：

```bash
python -c "import pyproj; print(pyproj.__version__)"
```

预期输出 `3.7.2`。`import` 加载库，`__version__` 是库提供的版本信息。

## 3. 经纬度的单位是度

课程数据的坐标 `[121.4737, 31.2304]` 表示经度 121.4737 度、纬度 31.2304 度。
经度在前、纬度在后，这个顺序必须与计算函数要求对应。

| 概念 | 本课中的含义 |
| --- | --- |
| 经度 longitude，简称 lon | 东西方向的角度位置 |
| 纬度 latitude，简称 lat | 南北方向的角度位置 |
| CRS，坐标参考系统 | 规定坐标数字如何对应地球上的位置 |
| WGS 84 | 本课数据使用的地理参考系统，其椭球模型可用于计算距离 |
| 米 meter | 本课函数返回的距离单位 |

两个经度相减，得到的仍是角度差。纬度不同，同样 1 度经度对应的地面距离也不同。
因此不能直接把坐标差当成米，也不能对所有地方套用同一个“每度多少米”的常数。

本课保留经纬度坐标，使用 WGS 84 椭球上的测地线算法计算两点间的距离。
可以先把测地线理解为沿地球参考椭球表面的最短路径；这个数值不包含道路绕行或地形高差。

## 4. 先运行一个完整示例

```bash
python examples/measure_distances.py
```

默认教学数据的输出应为：

```text
数据来源：教学合成数据，不代表真实地点
查询中心：经度=121.47，纬度=31.23
距离类型：WGS 84 椭球面测地线距离；单位：米
- 教学医院甲 | hospital | 距离=355.3 米
- 教学公园 | park | 距离=888.6 米
- 教学医院乙 | hospital | 距离=2204.5 米
```

打开 `examples/measure_distances.py`，重点阅读三个部分。

第一部分，导入计算工具：

```python
from pyproj import Geod
```

`Geod` 是库提供的测地线计算类。可以先将类理解为创建计算工具的模板。

第二部分，创建一个按 WGS 84 椭球计算的工具对象：

```python
geod = Geod(ellps="WGS84")
```

`ellps` 指定椭球模型，`"WGS84"` 是这个模型的名字。
`geod` 保存创建出的对象，后面可以通过它调用距离计算方法。

第三部分，调用方法并接收三个返回值：

```python
forward_azimuth, back_azimuth, meters = geod.inv(
    center_lon, center_lat, longitude, latitude
)
```

参数依次是起点经度、起点纬度、终点经度、终点纬度。
`inv` 根据两点求方向和距离，返回值依次是：正向方位角、反向方位角、以米为单位的距离。本课使用第三个值。
参见 [pyproj 的 Geod.inv 官方文档](https://pyproj4.github.io/pyproj/stable/api/geod.html#pyproj.Geod.inv)。

这种写法叫解包：把多个返回值分别放进对应的变量。例如：

```python
first, second, third = (10, 20, 30)
print(third)  # 输出 30
```

示例里的 `meters:.1f` 表示显示时保留一位小数。计算过程中仍保留完整精度，筛选边界时也应使用完整精度。

## 5. 亲手封装函数

打开 `exercises/lesson_02.py`，只修改 `distance_m` 的函数体，替换占位的 `raise NotImplementedError(...)`。

函数输入为 4 个合法的经纬度数值：

```python
distance_m(lon1, lat1, lon2, lat2)
```

要求：

1. 使用 WGS 84 椭球。
2. 按正确的经纬度顺序计算距离。
3. 返回第三个计算结果，单位为米。
4. 在函数中保留完整精度，返回数值而不是带有“米”的字符串。
5. 相同点的距离应为 0，调换起终点后距离应相同。

提示：函数体的工作顺序是“创建计算对象 → 调用 inv → 返回距离”。
本课不要求手写测地线数学算法；你需要理解并正确封装现成库的输入输出。

完成后运行：

```bash
python exercises/lesson_02.py
python -m checks.lesson_02
```

练习输出应包含：

```text
查询中心到教学医院甲：355.3 米
教学医院甲位于中心的 1000 米范围内
```

检查会验证相同点、赤道参考距离、距离对称性、不同纬度、教学地点以及跨越 ±180 度经线这 6 类行为。
通过时末尾显示 `Ran 6 tests` 和 `OK`；尚未实现时提示“第二课练习尚未实现”。

## 6. 保存自己的成果

先阅读修改；如果出现分页查看界面，按 `q` 退出：

```bash
git diff
git add requirements-lesson-02.txt docs/02-distance.md examples/measure_distances.py exercises/lesson_02.py checks/lesson_02.py
git diff --cached --stat
git commit -m "feat: complete geodesic distance lesson"
git push
```

这份明确的文件清单只提交本课源码与文档，不包含上传的 ZIP。
第一课如果还有尚未提交的答案，可以单独提交保存，避免只在 Codespaces 中留有修改。

## 本课完成标准

- 能解释为什么经纬度差不能直接当成米。
- 能说出 `Geod.inv` 四个输入和三个输出的顺序。
- 自己完成距离函数，并通过 6 项检查。
- 能根据默认数据判断：半径 1000 米时，医院甲在范围内，医院乙在范围外。

下一课会把第一课的类别筛选与本课的距离函数组合，返回指定半径内的地点，并按距离排序。
