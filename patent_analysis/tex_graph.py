import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['text.usetex'] = True

# 如果需要显示中文，请确保你的系统安装了 LaTeX 中文字体
# 并且你的 LaTeX 编译器支持（如 XeLaTeX）
# 这行代码告诉 Matplotlib 使用 ctex 宏包来处理中文
mpl.rcParams['text.latex.preamble'] = r'\usepackage{ctex}'
# 创建一个图
# fig = plt.figure()
fig, ax = plt.subplots()


# 在图中添加文本，并使用 LaTeX 格式
# 注意：需要用r'...'来创建一个原始字符串，这样Python就不会对\进行转义
# 使用$$...$$可以显示数学模式
formula = r"""

\documentclass[UTF8]{ctexart}
\begin{document}
\begin{table}
\caption{}
\label{}
\begin{center}
\begin{tabular}{lllllllll}
\hline
               & (1)      & (2)      & (3)     & (4)     & (5)     & (6)     & (7)     & (8)      \\
\hline
GVC            & -0.258   & -0.242   & -0.232  & -0.224  & -0.224  & -0.168  & -0.162  & -0.104   \\
               & (1.186)  & (1.183)  & (1.191) & (1.194) & (1.193) & (1.190) & (1.183) & (1.181)  \\
RO             & -0.201   & -0.180   & -0.183  & -0.173  & -0.173  & -0.181  & -0.182  &          \\
               & (0.301)  & (0.300)  & (0.300) & (0.300) & (0.300) & (0.299) & (0.297) &          \\
IFA            & 1.194    & 0.364    & 0.463   & 0.632   & 0.540   & 0.241   &         &          \\
               & (5.910)  & (5.899)  & (5.928) & (5.926) & (5.877) & (5.790) &         &          \\
DI             & -0.568   & -0.487   & -0.403  & -0.417  & -0.412  &         &         &          \\
               & (0.616)  & (0.616)  & (0.605) & (0.608) & (0.604) &         &         &          \\
UL             & 0.115    & 0.083    & 0.096   & 0.095   &         &         &         &          \\
               & (0.393)  & (0.392)  & (0.391) & (0.390) &         &         &         &          \\
FIL            & 3.305    & 2.956    & 2.553   &         &         &         &         &          \\
               & (5.849)  & (5.840)  & (5.868) &         &         &         &         &          \\
FDL            & 19.848   & 19.012   &         &         &         &         &         &          \\
               & (12.221) & (12.185) &         &         &         &         &         &          \\
RL             & -3.557   &          &         &         &         &         &         &          \\
               & (2.976)  &          &         &         &         &         &         &          \\
R-squared      & 0.017    & 0.012    & 0.004   & 0.003   & 0.003   & 0.001   & 0.001   & 0.000    \\
R-squared Adj. & nan      & nan      & nan     & nan     & nan     & nan     & nan     & nan      \\
N              & 330      & 330      & 330     & 330     & 330     & 330     & 330     & 330      \\
R-sq           & 0.0170   & 0.0122   & 0.0037  & 0.0031  & 0.0029  & 0.0013  & 0.0013  & 0.0000   \\
\hline
\end{tabular}
\end{center}
\end{table}
\bigskip
Standard errors in parentheses. \newline 
* p<.1, ** p<.05, ***p<.01
\end{document}"""

ax.text(0.5, 0.5, formula, fontsize=20)

# 隐藏坐标轴
ax.axis('off')

# 显示图
plt.show()