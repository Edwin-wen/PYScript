(async function () {
    // 配置常量 - 可根据需要调整
    const ELEMENT_TIMEOUT = 15000; // 元素加载超时时间(毫秒)
    const PAGE_SWITCH_DELAY = 2000; // 页面切换等待时间(毫秒)
    const FILTER_APPLY_DELAY = 5000; // 筛选条件应用后等待时间(毫秒)
    const UNIQUE_DELIMITER = '|'; // 用于生成唯一标识的分隔符（避免与数据中的符号冲突）

    // 直接操作当前文档
    const doc = document;

    // 等待元素加载的工具函数
    function waitForElement(selector, timeout = ELEMENT_TIMEOUT) {
        return new Promise((resolve, reject) => {
            // 先检查元素是否已存在
            const existing = doc.querySelector(selector);
            if (existing) {
                resolve(existing);
                return;
            }

            // 不存在则监听DOM变化
            const timer = setTimeout(() => reject(new Error('元素加载超时: ' + selector)), timeout);
            const observer = new MutationObserver((mutations, obs) => {
                const el = doc.querySelector(selector);
                if (el) {
                    clearTimeout(timer);
                    obs.disconnect();
                    resolve(el);
                }
            });
            observer.observe(doc.body, {childList: true, subtree: true});
        });
    }

    // 生成记录的唯一标识（用于去重）
    function getRecordUniqueKey(record) {
        // 将记录的所有字段拼接成一个字符串作为唯一标识
        return record.join(UNIQUE_DELIMITER);
    }

    // 提取单个筛选条件下的所有数据
    async function extractDataForFilter() {
        // 等待表格和分页控件加载
        await waitForElement('.el-table__header');
        await waitForElement('.el-pagination, .pagination-container');

        // 提取表头（只在首次提取时返回表头）
        const headerCells = doc.querySelectorAll('.el-table__header th');
        const headers = Array.from(headerCells).map(th => {
            const cell = th.querySelector('.cell');
            return (cell ? cell.textContent : th.textContent).trim();
        }).filter(text => text);

        if (headers.length === 0) {
            alert('未找到表头数据，请检查选择器是否正确');
            return null;
        }

        // 存储当前筛选条件下的所有数据
        const allData = [];
        let currentPage = 1;
        let hasNextPage = true;

        console.log(`开始提取当前筛选条件下的数据`);

        // 循环提取所有分页
        while (hasNextPage) {
            console.log(`正在提取第${currentPage}页数据...`);

            // 等待当前页数据加载完成
            await waitForElement('.el-table__body tr');

            // 提取当前页数据行
            const rows = doc.querySelectorAll('.el-table__body tr:not(.el-table__empty-block)');
            const pageData = Array.from(rows).map(row => {
                const tds = Array.from(row.querySelectorAll('td')).slice(0, headers.length);
                return tds.map(td => {
                    const cell = td.querySelector('.cell');
                    return (cell ? cell.textContent : td.textContent).trim();
                });
            }).filter(row => row.length === headers.length && row.some(cell => cell));

            if (pageData.length === 0) {
                console.log(`第${currentPage}页无数据，停止提取`);
                break;
            }

            allData.push(...pageData);
            console.log(`第${currentPage}页提取完成，共${pageData.length}条数据`);

            // 检查下一页按钮
            const nextBtnSelectors = [
                '.btn-next',
                '.btn-next .el-icon-arrow-right',
                'button.btn-next',
                'button:has(.el-icon-arrow-right)'
            ];

            let nextBtn = null;
            for (const selector of nextBtnSelectors) {
                nextBtn = doc.querySelector(selector);
                if (nextBtn) break;
            }

            // 检查下一页按钮状态
            if (!nextBtn) {
                hasNextPage = false;
                console.log('未找到下一页按钮，已到达最后一页');
            } else if (nextBtn.disabled ||
                nextBtn.classList.contains('disabled') ||
                nextBtn.classList.contains('is-disabled') ||
                nextBtn.style.display === 'none') {
                hasNextPage = false;
                console.log('已到达最后一页');
            } else {
                // 点击下一页
                nextBtn.click();
                currentPage++;
                await new Promise(resolve => setTimeout(resolve, PAGE_SWITCH_DELAY));
            }
        }

        console.log(`当前筛选条件下数据提取完成，共${allData.length}条记录`);
        return {headers, data: allData};
    }

    try {
        // 等待筛选控件加载
        console.log('正在查找筛选条件...');
        await waitForElement('.el-radio-group');

        // 获取所有筛选选项
        const radioLabels = doc.querySelectorAll('.el-radio-group .el-radio');
        const filterOptions = Array.from(radioLabels).map((label, index) => {
            const labelText = label.querySelector('.el-radio__label').textContent.trim();
            const input = label.querySelector('.el-radio__original');
            const value = input ? input.value : labelText;
            return {index, label: labelText, element: label, value};
        });

        if (filterOptions.length === 0) {
            alert('未找到筛选选项，请检查页面');
            return;
        }

        // 显示筛选选项供用户选择
        console.log('找到以下筛选选项：');
        filterOptions.forEach(option => {
            console.log(`${option.index + 1}. ${option.label}`);
        });

        // 让用户选择需要提取的选项（通过弹窗输入）
        const houseCounts = prompt(
            `请输入需要提取的户型选项序号（多个序号用逗号分隔，例如：2,3）\n` +
            filterOptions.map(option => `${option.index + 1}. ${option.label}`).join('\n')
        );

        const selectedIndices = prompt(
            `请输入需要提取的选项序号（多个序号用逗号分隔，例如：10,11）\n` +
            filterOptions.map(option => `${option.index + 1}. ${option.label}`).join('\n')
        );

        if (!selectedIndices || !houseCounts) {
            alert('未选择任何选项，脚本终止');
            return;
        }

        // 解析用户选择
        const selectedIndexes = selectedIndices.split(',')
            .map(idx => parseInt(idx.trim()) - 1) // 转换为0基索引
            .filter(idx => !isNaN(idx) && idx >= 0 && idx < filterOptions.length);

        const houseCountIndexs = houseCounts.split(',')
            .map(idx => parseInt(idx.trim()) - 1) // 转换为0基索引
            .filter(idx => !isNaN(idx) && idx >= 0 && idx < filterOptions.length);

        if (selectedIndexes.length === 0 || houseCountIndexs.length === 0) {
            alert('未选择有效的选项，脚本终止');
            return;
        }

        console.log(`用户选择了以下户型选项：${houseCountIndexs.map(idx => filterOptions[idx].label).join(', ')}`);
        console.log(`用户选择了以下额外选项：${selectedIndexes.map(idx => filterOptions[idx].label).join(', ')}`);

        // 存储所有筛选条件下的合并数据
        let combinedData = null;
        let totalRecords = 0;
        let duplicateCount = 0;
        // 使用Set存储已存在的记录标识，实现O(1)时间复杂度的去重判断
        const existingRecords = new Set();

        // 依次处理每个选中的筛选条件
        for (const houseIndex of houseCountIndexs) {

            const filter = filterOptions[houseIndex];
            console.log(`开始处理户型筛选条件：${filter.label}`);

            // 点击选择当前筛选条件
            filter.element.click();
            console.log(`已选择：${filter.label}`);

            // 等待筛选条件应用并加载数据
            await new Promise(resolve => setTimeout(resolve, FILTER_APPLY_DELAY));

            for (const index of selectedIndexes) {
                const filter = filterOptions[index];
                console.log(`开始处理筛选条件：${filter.label}`);

                // 点击选择当前筛选条件
                filter.element.click();
                console.log(`已选择：${filter.label}`);

                // 等待筛选条件应用并加载数据
                await new Promise(resolve => setTimeout(resolve, FILTER_APPLY_DELAY));

                // 提取当前筛选条件下的数据
                const result = await extractDataForFilter();
                if (!result) {
                    console.warn(`无法提取${filter.label}的数据，跳过该选项`);
                    continue;
                }

                // 初始化合并数据（添加表头）
                if (!combinedData) {
                    combinedData = [result.headers];
                }

                // 处理当前筛选条件下的数据，进行去重
                result.data.forEach(record => {
                    const uniqueKey = getRecordUniqueKey(record);
                    if (!existingRecords.has(uniqueKey)) {
                        // 记录不存在，添加到合并数据
                        combinedData.push(record);
                        existingRecords.add(uniqueKey);
                        totalRecords++;
                    } else {
                        // 记录已存在，计数加1
                        duplicateCount++;
                    }
                });

                console.log(`${filter.label}数据处理完成，新增${result.data.length - (result.data.length - (totalRecords - (combinedData.length - 1 - result.data.length)))}条新记录，重复${result.data.length - (totalRecords - (combinedData.length - 1 - result.data.length))}条`);
            }

        }

        if (!combinedData || combinedData.length <= 1) {
            alert('未提取到有效数据');
            return;
        }

        // 生成CSV内容
        const csvContent = combinedData.map(row =>
            row.map(cell => {
                if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
                    return `"${cell.replace(/"/g, '""')}"`;
                }
                return cell;
            }).join(',')
        ).join('\n');

        // 创建下载链接
        const blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
        const url = URL.createObjectURL(blob);
        const link = doc.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `筛选表格数据_去重后_${new Date().toLocaleDateString()}.csv`);
        link.style.display = 'none';
        doc.body.appendChild(link);
        link.click();
        doc.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log(`所有筛选条件数据处理完成，原始总记录${totalRecords + duplicateCount}条，去重后${totalRecords}条，去除重复${duplicateCount}条`);
        alert(`提取成功！共获取${totalRecords + duplicateCount}条原始数据，去重后保留${totalRecords}条，已合并为一个CSV文件下载`);
    } catch (error) {
        console.error('提取过程出错：', error);
        alert(`提取失败：${error.message}\n请查看控制台了解详细信息`);
    }
})();
