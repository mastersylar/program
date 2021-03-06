#epsabs=1.49e-06, epsrel=1.49e-06#精度
import numpy
import scipy.integrate
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D
import csv
#initial_value：冠幅，间距，冠高，面积，宽，长，分段个数，R, B, H, square_dm, s_length, step_point, accept_p
def m_s(initial_value):
    accept_p = numpy.zeros(2)
    #基本参数设置
    R, B, H, S, length, step_point, accept_p[0], accept_p[1] = initial_value
    width = length
    V_s = S * H#穿透雨的立方形体积
    R2 = pow(R, 2)
    step_range = range(0, step_point, 1)#生成分割序列
    mode_limit = R + B / 2
    d_limit = mode_limit / (step_point - 1)#分割段长度
    #四个树冠的圆心
    def canopy_center():#四个树冠的圆心
        canopy_center_point = numpy.zeros((4, 2))
        canopy_center_point[0][0] = 0
        canopy_center_point[0][1] = 0
        canopy_center_point[1][0] = 2 * R + B
        canopy_center_point[1][1] = 0
        canopy_center_point[2][0] = 2 * R + B
        canopy_center_point[2][1] = 2 * R + B
        canopy_center_point[3][0] = 0
        canopy_center_point[3][1] = 2 * R + B
        return canopy_center_point
    canopy_dot = canopy_center()#四个树冠的圆心
    #第i个树冠体积函数
    def f_canopy(i):#i=tree_num
        return lambda x, y: H - numpy.sqrt((x - canopy_dot[i][0]) ** 2 + (y - canopy_dot[i][1]) ** 2) * H / R
    #第i个树冠的上半圆函数
    def f_up_canopy(i):#i=tree_num
        return lambda x: canopy_dot[i][1] + numpy.sqrt(R2 - (x - canopy_dot[i][0]) ** 2)#上半圆函数
    #第i个树冠的下半圆函数
    def f_down_canopy(i):#i=tree_num
        return lambda x: canopy_dot[i][1] - numpy.sqrt(R2 - (x - canopy_dot[i][0]) ** 2)#下半圆函数
    #生成水槽中心点数组，第一维：某点的穿透雨量、X轴坐标、Y轴坐标，第二维X轴定值的Y轴点集合，第三维X轴的集合
    ucs = numpy.zeros((step_point, step_point, 3))#中心点数组：截留量、X、Y坐标
    #对水槽中心点数组赋值X、Y坐标
    for i in step_range:#对水槽中心点数组赋值X、Y坐标
        for j in step_range:
            ucs[i][j][1] = d_limit * i
            ucs[i][j][2] = d_limit * j
    #赋值：xa,xb,2个ab交点，2个cd焦点和圆左右边界 的X轴坐标集合，8个数，分段积分：7段
    def intersection_point_sequence(tree, rec_arr):
        r_i_s_get = numpy.zeros(8)
        r_i_s_get[0] = rec_arr[0][0]#长方形xa
        r_i_s_get[1] = rec_arr[1][0]#长方形xb
        r_i_s_get[2] = rec_arr[0][0]  # 长方形ab的第一个交点
        r_i_s_get[3] = rec_arr[0][0]  # 长方形ab的第二个交点
        r_i_s_get[4] = rec_arr[0][0]  # 长方形cd的第一个交点
        r_i_s_get[5] = rec_arr[0][0]  # 长方形cd的第二个交点
        r_i_s_get[6] = canopy_dot[tree][0] - R#树冠左边界
        r_i_s_get[7] = canopy_dot[tree][0] + R#树冠右边界
        #ab与树冠圆心距离的绝对值
        y_ab = abs(canopy_dot[tree][1] - rec_arr[0][1])
        #cd与树冠圆心距离的绝对值
        y_cd = abs(canopy_dot[tree][1] - rec_arr[3][1])
        if y_ab < R:
            # 长方形ab的第一个交点
            r_i_s_get[2] = canopy_dot[tree][0] - numpy.sqrt(R2 - y_ab ** 2)
            # 长方形ab的第二个交点
            r_i_s_get[3] = canopy_dot[tree][0] + numpy.sqrt(R2 - y_ab ** 2)
        if y_cd < R:
            # 长方形cd的第一个交点
            r_i_s_get[4] = canopy_dot[tree][0] - numpy.sqrt(R2 - y_cd ** 2)
            # 长方形cd的第二个交点
            r_i_s_get[5] = canopy_dot[tree][0] + numpy.sqrt(R2 - y_cd ** 2)
        return sorted(r_i_s_get)#排升序
    #对各长方形4个点赋值，并求与4个树冠相交部分的截留量
    for one_dimensional in ucs:#第一维
        for two_dimensional in one_dimensional:#第二维
            suqare = numpy.zeros((4, 2))  # 生成长方形4个点的数组
            canopy_interception = numpy.zeros(4)  # 4个树冠的截留量
            half_width = width / 2
            half_length = length / 2
            suqare[0][0] = two_dimensional[1] - half_width#xa
            suqare[0][1] = two_dimensional[2] - half_length#ya
            suqare[1][0] = two_dimensional[1] + half_width#xb
            suqare[1][1] = two_dimensional[2] - half_length#yb
            suqare[2][0] = two_dimensional[1] + half_width#xc
            suqare[2][1] = two_dimensional[2] + half_length#yc
            suqare[3][0] = two_dimensional[1] - half_width#xd
            suqare[3][1] = two_dimensional[2] + half_length#yd
            #xa,xb,2个ab交点，2个cd焦点，R的集合，分段积分-6段
            for tree in range(0, 4, 1):
                #第i个树冠的分段截留量
                rain_i = numpy.zeros(7)
                #交点赋值
                s_i_s = intersection_point_sequence(tree, suqare)
                left_limit = max(suqare[0][0], canopy_dot[tree][0] - R)
                right_limit = min(suqare[1][0], canopy_dot[tree][0] + R)
                for i in range(0, 7, 1):
                    if left_limit <= s_i_s[i] < s_i_s[i+1] <= right_limit:
                        a = s_i_s[i]
                        b = s_i_s[i + 1]
                        midpoint_x = (a + b) / 2
                        canopy_mid_down_y = f_down_canopy(tree)(midpoint_x)
                        canopy_mid_up_y = f_up_canopy(tree)(midpoint_x)
                        if canopy_mid_down_y >= suqare[3][1] or canopy_mid_up_y <= suqare[0][1]:
                            continue
                        if canopy_mid_down_y > suqare[0][1]:
                            func_g = f_down_canopy(tree)
                        else:
                            func_g = suqare[0][1]
                        if canopy_mid_up_y < suqare[3][1]:
                            func_h = f_up_canopy(tree)
                        else:
                            func_h = suqare[3][1]
                        rain_i[i] = scipy.integrate.dblquad(f_canopy(tree), a, b, func_g, func_h,
                                                            epsabs=1.49e-06, epsrel=1.49e-06)[0]
                canopy_interception[tree] = numpy.sum(numpy.abs(rain_i))
            two_dimensional[0] = (V_s - numpy.sum(canopy_interception)) / S
    square_p_num = 0
    for i in step_range:  # 第一维
        for j in step_range:  # 第二维
            # ucs_rain[j][i] = ucs[i][j][0]
            # ucs_rain_T[i][j] = ucs[i][j][0]
            if accept_p[0] < ucs[i][j][0] < accept_p[1]:
                square_p_num = square_p_num + 1
    return square_p_num
    #生成X,Y的集合
    # ucs_x = numpy.linspace(0, mode_limit, step_point)
    # ucs_y = numpy.linspace(0, mode_limit, step_point)
    # UX, UY = numpy.meshgrid(ucs_x, ucs_y)#meshgrid函数用两个坐标轴上的点在平面上画格
    #生成穿透雨量的二维矩阵，并赋值
    #ucs_rain = numpy.zeros((step_point, step_point))
    #ucs_rain_T = numpy.zeros(step_point, step_point)

# initial_value = [30, 10 ,50, 10, 10, 1, 36, [18.450429643955072, 27.67564446593261]]
# print (m_r(initial_value))

