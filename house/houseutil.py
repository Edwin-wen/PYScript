from matplotlib.pyplot import MultipleLocator
import numpy as np
import matplotlib.pyplot as plt

TOTAL = 2000000  # 房款总额
Tc = 0.15 * TOTAL  # 首付款
Td = TOTAL - Tc  # 总贷款
Tdg = 1540000  # 公积金贷款
Tds = Td - Tdg  # 商业贷款
Rg = 2.6 / 100 / 12  # 公积金月利率
Rs = 3.05 / 100 / 12  # 商贷月利率
Rc = 1.75 / 100 / 12  # 三年期存款利率
N = 360  # 贷款月份


def sumC(x):
    # 每月存款利息
    Cm = TOTAL * Rc
    result = []
    for i in x:
        result.append(Cm * i)
    return result


def sumD(x, T, R):
    total = 0
    result = []
    for i in x:
        # 每月贷款利息
        month = (T - (T / N) * i) * R
        total += month
        result.append(total)
    return result


def sumDAll(x, Dg, Ds):
    result = []
    for i in x:
        result.append(Dg[i] + Ds[i])
    return result


def cost(x, Sc, Sd):
    result = []
    for i in x:
        result.append(Sc[i] - Sd[i])
    return result


def draw():
    x = np.arange(0, N, 1)

    # 每月存款利息
    Cm = TOTAL * Rc

    # 每月贷款利息
    Dmg = (Tdg - (Tdg / N) * x) * Rg  # 每月公积金贷款利息
    Dms = (Tds - (Tds / N) * x) * Rs  # 每月商业贷款利息
    Dm = Dms + Dmg  # 每月总利息

    Sc = sumC(x)  # 总存款利息

    Sdg = sumD(x, Tdg, Rg)  # 总公积金利息
    Sds = sumD(x, Tds, Rs)  # 总商业贷利息
    Sd = sumDAll(x, Sdg, Sds)  # 总房贷利息

    Cost = cost(x, Sc, Sd)  # 总收益/支出

    monthRent = TOTAL * 0.01 / 12 # 配售放每年贬值1%，等同租金

    write2File(x, Dm, Sc, Sd, Cost, monthRent)

    plt.rcParams['font.family'] = 'DeJavu Serif'
    plt.rcParams['font.serif'] = ['Times New Roman']

    # 把x轴的刻度间隔设置为1，并存在变量里
    x_major_locator = MultipleLocator(12)
    # 把y轴的刻度间隔设置为10000，并存在变量里
    y_major_locator = MultipleLocator(20000)
    # ax为两条坐标轴的实例
    ax = plt.gca()
    # 把x轴的主刻度设置为1的倍数
    ax.xaxis.set_major_locator(x_major_locator)
    # 把y轴的主刻度设置为10的倍数
    ax.yaxis.set_major_locator(y_major_locator)
    # 把x轴的刻度范围设置为-0.5到11，因为0.5不满一个刻度间隔，所以数字不会显示出来，但是能看到一点空白
    plt.xlim(0, 200)
    # 把y轴的刻度范围设置为-5到110，同理，-5不会标出来，但是能看到一点空白
    plt.ylim(-1000, 500000)

    plt.plot(x, Cost, label=u"Total", linestyle="-")
    plt.plot(x, Sc, label=u"in", linestyle="--")
    plt.plot(x, Sd, label=u"out", linestyle="--")
    plt.xlabel("month")
    plt.ylabel("money")
    plt.title('House')
    plt.legend()  # 打上标签
    plt.show()


outFile = "人才房或配售房收益表.csv"


def formatPercent(value):
    return '{:.2%}'.format(value)


def write2File(x, dm, sc, sd, total, monthRent):
    Cm = TOTAL * Rc
    with open(outFile, "a") as file:
        file.seek(0)
        file.truncate()  # 清空文件
        info = "房款总额：" + str(TOTAL) + " 首付款:" + str(Tc) + " 总贷款:" + str(Td) + " 公积金贷款:" + str(Tdg) + " 商业贷款:" + str(
            Tds) + "\n"
        info2 = "贷款月份:" + str(N) + " 公积金年利率：" + str(formatPercent(Rg * 12)) + " 商贷年利率：" + str(formatPercent(Rs * 12))\
                + " 三年期存款年利率:" + str(formatPercent(Rc * 12)) + "\n"
        title = "第N个月,月供,月存款利息,月贷款利息,截止当月存款利息和, 截止当月贷款利息和,总收益/亏损,配售房等同租金" + "\n"
        file.write(info + info2 + title)
        for i in x:
            pay = (Td / N) + dm[i]
            wStr = str(i) + "," + str(pay) + "," + str(Cm) + "," + str(dm[i]) + "," + str(sc[i]) + "," + str(sd[i]) + "," + str(
                total[i]) + "," + str(monthRent) + "\n"
            file.write(wStr)
    file.close()


if __name__ == '__main__':
    draw()
