# 活动管理

**活动（Campaign）** 用于分组测试，验证特定功能/流程。

## 创建活动

1.  Dashboard 中点击 **Add Campaign**。
2.  填写：
    *   **Name**：唯一名称。
    *   **Description**：可选说明。
3.  保存后跳转到详情页。

![“Add Campaign” 表单](../../assets/campaign_add.png)
> “Add Campaign” 表单。

## 活动详情

控制中心。

![活动详情](../../assets/campaign_detail.png)
> 信息、文件、测试分区。

### 1. 信息
显示元数据，可编辑/删除。

### 2. 文件管理
管理活动关联文件。
*   **上传**：放入活动 workdir。
*   **重命名/删除**：管理文件。
*   **下载**：获取文件。

测试中可通过 `{{test.files_dir}}` 访问。

### 3. 测试列表
列出所有测试。
*   **排序**：上下箭头调整执行顺序。
*   **Add Test**：创建新测试。
*   **Execute**：单独运行测试。

## 执行活动

1.  点击 **Execute Campaign**。
2.  配置：
    *   **Name**：自动生成（如 “March 2023”），可修改。
    *   **Environment**：选择环境（变量）。
    *   **Stop on Failure**：首个失败即停止。
3.  启动，后台运行。

![执行弹窗](../../assets/campaign_rapport.png)
> 执行弹窗，含环境选择。

### 实时监控
显示进度与状态。
*   **蓝色** 运行中
*   **绿色** 成功
*   **红色** 失败

点击报告查看详细日志。
