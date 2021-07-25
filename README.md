# FEALPy: Finite Element Analysis Library in Python

[![Join the chat at https://gitter.im/weihuayi/fealpy](https://badges.gitter.im/weihuayi/fealpy.svg)](https://gitter.im/weihuayi/fealpy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
![Python package](https://github.com/weihuayi/fealpy/workflows/Python%20package/badge.svg)
![Upload Python Package](https://github.com/weihuayi/fealpy/workflows/Upload%20Python%20Package/badge.svg)

We want to develop an efficient and easy to use finite element software
package to support our teach and research work. 

We still have lot work to do. 

关于 FEALPy 的中文帮助与安装信息请查看：
[FEALPy 帮助与安装](https://www.weihuayi.cn/fly/fealpy.html)

# Installation

## Common

To install the latest release from PyPi, use
```bash
pip install -U fealpy
``` 

If you have no `root` access on Linux/MacOS, please try 
```bash
python -m pip install -U fealpy
```

Users in China can install FEALPy from mirrors such as:
- [Aliyun](https://developer.aliyun.com/mirror/pypi)
- [Tsinghua](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)
- [USTC](https://lug.ustc.edu.cn/wiki/mirrors/help/pypi)

## From Source

```bash
git clone https://github.com/weihuayi/fealpy.git
cd fealpy
pip install .
```

For developers, please use `pip install -e .` to install it in develop mode.

On Linux system such as Ubuntu or Fedora, or MacOS, maybe you should use `pip3 install -e .` to install it in
develop mode.

## Uninstallation

```bash
pip uninstall fealpy
```

## Docker

To be added.

## Reference and Acknowledgement

We thank Dr. Long Chen for the guidance and compiling a systematic documentation for programming finite element methods.
* http://www.math.uci.edu/~chenlong/programming.html
* https://github.com/lyc102/ifem


## Citation

Please cite `fealpy` if you use it in your paper

H. Wei and Y. Huang, FEALPy: Finite Element Analysis Library in Python, https://github.com/weihuayi/fealpy, *Xiangtan University*, 2017-2021.

```bibtex
@misc{fealpy,
	title = {FEALPy: Finite Element Analysis Library in Python. https://github.com/weihuayi/
        fealpy},
	url = {https://github.com/weihuayi/fealpy},
	author = {Wei, Huayi and Huang, Yunqing},
    institution = {Xiangtan University},
	year = {Xiangtan University, 2017-2021},
}
```
