# 實驗設計

<img width="2263" height="1083" alt="1768992278316278522730991434524" src="https://github.com/user-attachments/assets/dd5eb251-9ac4-4376-8ed4-1fda5cc8b363" />


# 時程表
```mermaid
gantt
    title 嵌入式 AI 加速實作與論文撰寫計畫 (1月 - 6月)
    dateFormat  YYYY-MM-DD
    axisFormat  %m月

    section 前置與模擬 (1/21前-2/21)
    前置文獻與工具準備       :2026-01-01, 2026-01-20
    Spike QEMU 環境搭建     :2026-01-21, 12d
    QEMU 功能驗證與模擬      :crit, 2026-02-05, 2026-03-21

    section 實體板實作 (2/21-3/21)
    ResNet 50 模型移植       :2026-02-21, 10d
    軟體 Softmax 基準測試    :2026-03-05, 5d
    硬體 Softmax 加速實作    :2026-03-10, 7d
    SW HW 數據比較與採集     :crit, 2026-03-17, 2026-03-21

    section 論文數據與架構 (3/22-4/30)
    實驗數據整理與圖表繪製   :p1, 2026-03-22, 10d
    撰寫系統架構 Method      :p2, after p1, 14d
    撰寫實驗結果分析 Result  :p3, after p2, 14d

    section 論文完稿與修訂 (5月-6月)
    撰寫緒論與相關研究       :2026-05-05, 14d
    論文初稿完成             :milestone, 2026-05-23, 0d
    指導教授審閱與修改       :2026-05-24, 20d
    格式調整與最終定稿       :crit, 2026-06-17, 10d
    論文繳交與口試準備       :milestone, 2026-06-30, 0d



```

- ### 說明: 1/21 ~ 2/21(spike/qemu模擬) 2/21 ~ 3/21 (實體板子實作(softmax應用resnet50)) 3/22 ~ 4/30(論文數據與架構整理) 5/1 ~ 6/30(論文完稿和校正)
