# 使用说明：
#
# 确保已安装必要的库：
#
# bash
# pip install selenium
#
#
# 需下载对应浏览器的驱动（如 ChromeDriver）并配置到环境变量中
# 脚本注意事项：
# 替换driver.get("house.html")中的 URL 为实际页面地址
# 分页按钮选择器（.el-pagination__next）可能需要根据实际页面结构调整
# 若分页是通过页码点击而非 "下一页" 按钮，需修改分页逻辑
# 可根据需要调整等待时间和页面加载延迟
# 脚本工作流程：
# 切换到 iframe 中获取内容
# 提取表头并写入 CSV
# 循环提取每一页表格数据
# 自动检测并点击下一页，直到最后一页
# 所有数据保存到 CSV 文件

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# 初始化浏览器
driver = webdriver.Chrome()
driver.maximize_window()

# 打开页面
driver.get("house.html")  # 替换为实际页面URL或本地文件路径

# 切换到iframe
try:
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe)
except Exception as e:
    print("切换iframe失败:", e)
    driver.quit()
    exit()

# 准备CSV文件
csv_file = open("二手房源数据.csv", "w", newline="", encoding="utf-8-sig")
writer = csv.writer(csv_file)

# 提取表头
try:
    header_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".el-table__header th .cell"))
    )
    headers = [header.text.strip() for header in header_elements]
    writer.writerow(headers)
    print("表头提取成功:", headers)
except Exception as e:
    print("提取表头失败:", e)
    driver.quit()
    csv_file.close()
    exit()

# 提取数据并处理分页
page = 1
while True:
    print(f"正在提取第{page}页数据...")
    try:
        # 等待表格数据加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".el-table__body tr"))
        )
        # 获取当前页所有行
        rows = driver.find_elements(By.CSS_SELECTOR, ".el-table__body tr")

        for row in rows:
            # 获取行内所有单元格数据
            cells = row.find_elements(By.CSS_SELECTOR, "td .cell")
            row_data = [cell.text.strip() for cell in cells]
            if row_data:  # 跳过空行
                writer.writerow(row_data)

        # 检查是否有下一页
        next_page_btn = driver.find_elements(By.CSS_SELECTOR, ".el-pagination__next")  # 根据实际分页按钮选择器调整
        if next_page_btn and "disabled" not in next_page_btn[0].get_attribute("class"):
            next_page_btn[0].click()
            page += 1
            time.sleep(2)  # 等待页面加载
        else:
            print("已到达最后一页")
            break

    except Exception as e:
        print(f"提取第{page}页数据失败:", e)
        break

# 清理资源
csv_file.close()
driver.quit()
print("数据提取完成，已保存至二手房源数据.csv")