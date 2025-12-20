
```mermaid

sequenceDiagram
    autonumber
    participant User as 使用者 (手機/車主)
    participant FE as 前端介面 (React)
    participant BE as 後端伺服器 (Django/Raspberry Pi)
    participant DB as 資料庫 (SQLite)
    participant AI as AI 辨識主機 (Local PC/VLM)
    participant HW as 硬體設備 (感測器/蜂鳴器/LED)

    Note over User, FE: 進場與車位選擇階段
    User->>FE: 掃描 QRCode (Ngrok URL) 
    FE->>BE: 請求停車場現況 API [cite: 88]
    BE->>DB: 查詢車位狀態 (空缺/占用/異常) 
    DB-->>BE: 回傳資料
    BE-->>FE: 回傳 JSON 資料
    FE-->>User: 顯示停車場平面圖與顏色標示 [cite: 78, 79]
    User->>FE: 點選空車位 [cite: 17, 80]
    FE-->>User: 顯示路線引導 (文字+路徑圖) [cite: 13, 83]

    Note over User, HW: 停車與硬體感測階段
    User->>HW: 車輛駛入車位
    HW->>BE: 超音波感測器偵測距離/角度 (GPIO) [cite: 22, 41, 58]
    
    rect rgb(255, 240, 240)
    Note right of BE: 異常判斷邏輯
    alt 車身過度歪斜/位置不正確 [cite: 23]
        BE->>HW: 觸發蜂鳴器警示、LED亮紅燈 [cite: 25, 29, 30]
        BE->>FE: 推送網頁警示 (紅框/圖示) [cite: 85]
        BE->>DB: 寫入異常紀錄 
    else 車身正常
        BE->>HW: LED亮黃燈 (或正常指示) [cite: 31]
    end
    end

    Note over FE, AI: 車牌辨識階段 (VLM)
    HW->>FE: 觸發攝影機拍攝 (透過介面或自動) [cite: 12]
    FE->>FE: 將圖片轉為 BASE64 編碼 
    FE->>AI: 發送 POST 請求 (傳送圖片) 
    Note right of AI: 執行 Ovis2-4B VLM 模型 [cite: 108]
    AI-->>FE: 回傳辨識結果 (車牌號碼)
    FE->>BE: 傳送車牌號碼與確認資訊
    BE->>DB: 更新車輛表 (車牌、時間、車位) 
    BE->>DB: 更新車位表狀態為「占用」 
    FE-->>User: 顯示停車完成/確認畫面 [cite: 19] 這個要怎麼執行？

```
---
```mermaid
graph TD
    %% 定義樣式
    classDef layer fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef component fill:#e1f5fe,stroke:#0277bd,stroke-width:1px;
    classDef external fill:#fff3e0,stroke:#ef6c00,stroke-width:1px;

    subgraph User_Layer ["第 1 層：使用者使用介面 )"]
        direction TB
        U((使用者)) -->|手機掃描| QR["QR Code (Ngrok)"]
    end

    subgraph Presentation_Layer ["第 2 層：UI部分 (Presentation Layer - React UI)"]
        direction TB
        Page_Map["停車場平面圖 (顯示車位狀態)"]
        Page_Guide["路線導引介面 (顯示路徑)"]
        Alert_UI["異常警示彈窗 (紅框/圖示)"]
    end

    subgraph Logic_Layer ["第 3 層： 影像辨識(Business Logic Layer)"]
        direction TB
        State_Mgr["狀態管理 (React State)"]
        Img_Process["影像處理 (Base64 轉碼)"]
        Cam_Ctrl["攝影機控制邏輯"]
    end

    subgraph Service_Layer ["第 4 層：通訊層 (Service Communication Layer)"]
        direction TB
        API_Client["API 請求模組 (Axios/Fetch)"]
    end

    subgraph External_Systems ["外部系統 (External Systems)"]
        Backend_API["後端 Django API"]
        AI_Server["本地 AI 辨識主機 (VLM)"]
    end

    %% 層級關聯
    QR --> Page_Map
    Page_Map --> Page_Guide
    Page_Map --> Alert_UI

    Page_Map --> State_Mgr
    Page_Guide --> State_Mgr
    Alert_UI --> State_Mgr
    
    State_Mgr --> Cam_Ctrl
    Cam_Ctrl --> Img_Process
    
    State_Mgr --> API_Client
    Img_Process --> API_Client

    API_Client -->|"請求車位資料"| Backend_API
    API_Client -->|"POST 圖片"| AI_Server

    %% 套用樣式
    class User_Layer,Presentation_Layer,Logic_Layer,Service_Layer layer;
    class Page_Map,Page_Guide,Alert_UI,State_Mgr,Img_Process,Cam_Ctrl,API_Client component;
    class Backend_API,AI_Server external;
```
```mermaid
stateDiagram-v2
    direction LR

    %% 定義狀態
    state "Idle (空車位)" as Idle
    state "Reserved (預約/導引中)" as Reserved
    state "Parking_Attempt (停車偵測中)" as Parking
    state "Identifying (AI 車牌辨識)" as AI_Check
    state "Alignment_Check (車態檢查)" as Align
    state "Parked (已停妥/占用)" as Occupied
    
    %% 異常狀態
    state "Error_Skewed (異常：歪斜)" as Err_Skew
    state "Error_Mismatch (異常：車牌不符)" as Err_Plate

    %% 初始狀態
    [*] --> Idle

    %% 狀態流轉
    Idle --> Reserved : 使用者掃碼並選位
    
    Reserved --> Parking : 超音波感測器觸發 (GPIO)
    Idle --> Parking : 未預約直接駛入
    
    Parking --> AI_Check : 車輛靜止/觸發拍照
    
    AI_Check --> Align : 辨識成功 & 車牌吻合
    AI_Check --> Err_Plate : 車牌不吻合
    
    Align --> Err_Skew : 偵測過度歪斜
    Align --> Occupied : 位置正常

    %% 錯誤處理與恢復
    Err_Skew --> Align : 車主調整車輛
    Err_Skew --> Idle : 車主離開
    Err_Plate --> Idle : 車主離開

    %% 離場
    Occupied --> Idle : 車輛駛離 (感測器數值歸零)

    %% 狀態行為註解 (Actions)
    note right of Idle
        LED: 關閉/綠燈
        Web: 顯示空缺
    end note

    note right of Reserved
        Web: 顯示路線圖
    end note

    note right of Err_Skew
        HW: 蜂鳴器響 + 紅燈
        Web: 紅框警示
    end note

    note right of Occupied
        HW: 黃燈
        DB: 更新狀態為占用
    end note
```
```mermaid
graph LR
    %% 定義節點樣式 (圓形代表頂點 Vertex)
    classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px,rx:50,ry:50;
    classDef startend fill:#fff3e0,stroke:#e65100,stroke-width:2px,rx:50,ry:50;
    classDef decision fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,rx:50,ry:50;

    %% 定義頂點 (Vertices) - 代表活動
    V0((V0<br>使用者掃描 QR Code))
    V1((V1<br>前端請求 API<br>載入車位狀態))
    V2((V2<br>使用者選位<br>顯示路線導引))
    V3((V3<br>硬體感測器<br>偵測車輛駛入))
    V4((V4<br>系統判斷<br>車身姿態))
    
    %% 分支活動
    V5((V5<br>觸發異常警示<br>蜂鳴器/紅燈))
    V6((V6<br>啟動攝影機<br>影像轉 Base64))
    V7((V7<br>執行 AI 辨識<br>VLM 模型))
    V8((V8<br>更新資料庫<br>寫入車牌/占用))
    V9((V9<br>完成指示<br>亮黃燈))

    %% 定義邊 (Edges) - 代表先後依賴關係
    V0 --> V1
    V1 --> V2
    V2 --> V3
    V3 --> V4
    
    %% 異常依賴鏈
    V4 -->|"若歪斜/異常"| V5
    
    %% 正常依賴鏈
    V4 -->|"若正常"| V6
    V6 --> V7
    V7 --> V8
    V8 --> V9

    %% 樣式套用
    class V0,V9 startend;
    class V1,V2,V3,V5,V6,V7,V8 process;
    class V4 decision;
```
```mermaid

graph TD
    %% 定義節點樣式
    classDef process fill:#fff2cc,stroke:#d6b656,stroke-width:2px;
    classDef decision fill:#fff2cc,stroke:#6c8ebf,stroke-width:2px,shape:rhombus;
    classDef terminal fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px,rx:10,ry:10;
    classDef alert fill:#ffe6cc,stroke:#d79b00,stroke-width:2px;

    %% 節點定義 (完全依照圖片文字)
    Start("Start"):::terminal
    Step1["手機掃描QRcode"]:::process
    Step2["連結至網站介面"]:::process
    Step3["選擇空車位"]:::process
    Step4["顯示所選車位的路線圖"]:::process
    Step5["攝影機辨識車牌"]:::process
    
    Check1{"車主確認<br>是否正確"}:::decision
    
    Step6["感測器偵測有車"]:::process
    
    Check2{"車牌號碼<br>是否吻合"}:::decision
    
    Check3{"車態是否<br>無過度歪斜"}:::decision
    
    Alert["蜂鳴器 警示"]:::alert
    End("End"):::terminal

    %% 連線定義 (依照箭頭流向)
    Start --> Step1
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
    Step5 --> Check1
    
    %% 判斷 1: 車主確認
    Check1 -- "否" --> Step5
    Check1 -- "是" --> Step6
    
    %% 流程接續
    Step6 --> Check2
    
    %% 判斷 2: 車牌吻合
    Check2 -- "否" --> Alert
    Check2 -- "是" --> Check3
    
    %% 判斷 3: 車態歪斜
    Check3 -- "否" --> Alert
    Check3 -- "是" --> End
    
    %% 修正蜂鳴器後的流向 (圖中蜂鳴器下方有箭頭，通常指向結束或迴圈，此處依圖示結構暫指結束方向)
    Alert -.-> End
```

```mermaid

graph LR
    %% 樣式設定
    classDef std fill:#fff2cc,stroke:#d6b656,stroke-width:2px,color:black;
    classDef terminal fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px,color:black;
    classDef warn fill:#f8cecc,stroke:#b85450,stroke-width:2px,color:black;

    %% 節點定義 (使用圓角括號)
    S1(Idle<br>初始/掃碼):::terminal
    S2(Selecting<br>選位中):::std
    S3(Guiding<br>路線導引):::std
    S4(Identifying<br>辨識車牌):::std
    S5(Confirming<br>等待確認):::std
    S6(Sensing<br>超音波偵測):::std
    S7(Validating<br>偵測車態):::std
    S8(Alerting<br>異常警示):::warn
    S9(Parked<br>完成):::terminal

    %% 連線與標籤
    S1 -->|連結網站| S2
    S2 -->|選擇車位| S3
    S3 -->|啟動相機| S4
    S4 -->|辨識完成| S5
    
    S5 -->|否:重試| S4
    S5 -->|是:正確| S6
    
    S6 -->|偵測有車| S7
    
    S7 -->|否:異常| S8
    S7 -->|是:正常| S9

    %% 結束點
    S8 --> End1((End)):::terminal
    S9 --> End2((End)):::terminal
```

```mermaid
gantt
    title Cordic Pipeline Timing (Critical Path = 13 CLK)
    dateFormat  HH:mm
    axisFormat  %-M
    
    %% 設定 1 CLK = 1 分鐘
    
    section Main Cordic
    Range (Input)       :done,    m_range, 00:00, 1m
    iter 1              :active,  m_it1, after m_range, 2m
    s1 (Red)            :crit,    m_s1, after m_it1, 1m
    iter 2              :active,  m_it2, after m_s1, 2m
    s2 (Red)            :crit,    m_s2, after m_it2, 1m
    iter 3              :active,  m_it3, after m_s2, 2m
    s3 (Red)            :crit,    m_s3, after m_it3, 1m
    iter 4 (Branch Pt)  :active,  m_it4, after m_s3, 2m

    

    section Path Mid (S_exp)
    S_exp (Red)         :crit,    mid_se, after m_it4, 1m
    buffer...     :done,    mid_wait, after mid_se, 4m

    section Path Top (SQ1)
    SQ1_exp (Red)       :crit,    t_sq1e, after m_it4, 1m
    square1 (Blue)      :active,  t_sq1, after t_sq1e, 1m
    buffer...     :done,    t_wait, after t_sq1, 3m

    section Path Bot (SQ2)
    S_q1 (Red)          :crit,    b_sq1, after m_it4, 1m
    square1 (Blue)      :active,  b_sq1b, after b_sq1, 1m
    S_q2 (Red)          :crit,    b_sq2, after b_sq1b, 1m
    square2 (Blue)      :active,  b_sq2b, after b_sq2, 1m
    SQ2_exp (Red)       :crit,    b_exp, after b_sq2b, 1m

    section Result
    Buffer Latch        :done,    buf, after b_exp, 1m



```

<img width="1982" height="854" alt="image" src="https://github.com/user-attachments/assets/5fb9655b-bd7e-46b1-a03d-33544365572e" />


```mermaid

gantt
    title Cordic Pipeline Timing (單變數單行顯示)
    dateFormat  HH:mm
    axisFormat  %-M
    
    %% 設定 barHeight 讓圖表不要太過擁擠，保持整潔
    %%{init: { 'gantt': {'barHeight': 25, 'sectionFontSize': 14} } }%%

    %% =======================
    %% Main Cordic Chain
    %% =======================
    section Range (Input)
    Data        :done,   m_range, 00:00, 1m
    
    section iter 1
    Calc        :active, m_it1, after m_range, 2m
    
    section s1 (Red)
    Reg         :crit,   m_s1, after m_it1, 1m
    
    section iter 2
    Calc        :active, m_it2, after m_s1, 2m
    
    section s2 (Red)
    Reg         :crit,   m_s2, after m_it2, 1m
    
    section iter 3
    Calc        :active, m_it3, after m_s2, 2m
    
    section s3 (Red)
    Reg         :crit,   m_s3, after m_it3, 1m
    
    section iter 4
    Branch Pt   :active, m_it4, after m_s3, 2m

    %% =======================
    %% Path Mid (S_exp)
    %% =======================
    section S_exp (Mid)
    Reg         :crit,   mid_se, after m_it4, 1m
    
    section Buffer (Mid)
    Wait        :done,   mid_wait, after mid_se, 4m

    %% =======================
    %% Path Top (SQ1)
    %% =======================
    section SQ1_exp (Top)
    Reg         :crit,   t_sq1e, after m_it4, 1m
    
    section square1 (Top)
    Calc        :active, t_sq1, after t_sq1e, 1m
    
    section Buffer (Top)
    Wait        :done,   t_wait, after t_sq1, 3m

    %% =======================
    %% Path Bot (SQ2)
    %% =======================
    section S_q1 (Bot)
    Reg         :crit,   b_sq1, after m_it4, 1m
    
    section square1 (Bot)
    Calc        :active, b_sq1b, after b_sq1, 1m
    
    section S_q2 (Bot)
    Reg         :crit,   b_sq2, after b_sq1b, 1m
    
    section square2 (Bot)
    Calc        :active, b_sq2b, after b_sq2, 1m
    
    section SQ2_exp (Bot)
    Reg         :crit,   b_exp, after b_sq2b, 1m

    %% =======================
    %% Final Result
    %% =======================
    section Buffer Latch
    Output      :done,   buf, after b_exp, 1m



```


```mermaid

gantt
    title Pipeline Timing (刻度 = 分鐘數, 10ns = 1CLK)
    
    %% 1. 設定時間格式為「小時:分鐘」
    dateFormat  HH:mm
    
    %% 2. 設定軸線只顯示「分鐘數 (不補0)」
    %% 如果你的編輯器不支援 %-M，請改回 %M (會顯示 00, 01, 02...)
    axisFormat  %-M
    
    %% 3. 強制 X 軸從 00:00 開始
    %% 所有的長度單位都改用 "m" (分鐘)
    
    section rap_Data 1
    Input (1CLK)      :done,    d1_in, 00:00, 1m
    ite1 (2CLK)         :active,  d1_s1, after d1_in, 2m
    ite2 (2CLK)         :active,  d1_s2, after d1_s1, 2m
    ite3 (1CLK)         :         d1_s3, after d1_s2, 1m
    ite4 (2CLK)         :crit,    d1_s4, after d1_s3, 2m
    ite5 (2CLK)         :crit,    d1_s5, after d1_s4, 2m
    Buffer (1CLK)     :done,    d1_buf, after d1_s5, 1m

    section rap_Data 2
    %% II=2，所以從 00:02 開始
    Input (1CLK)      :done,    d2_in, 00:01, 1m
    ite1 (2CLK)         :active,  d2_s1, after d2_in, 2m
    ite2 (2CLK)         :active,  d2_s2, after d2_s1, 2m
    ite3 (1CLK)         :         d2_s3, after d2_s2, 1m
    ite4 (2CLK)         :crit,    d2_s4, after d2_s3, 2m
    ite5 (2CLK)         :crit,    d2_s5, after d2_s4, 2m
    Buffer (1CLK)     :done,    d2_buf, after d2_s5, 1m

    section rap_Data 3
    %% II=2，所以從 00:04 開始
    Input (1CLK)      :done,    d3_in, 00:02, 1m
    ite1 (2CLK)         :active,  d3_s1, after d3_in, 2m
    ite2 (2CLK)         :active,  d3_s2, after d3_s1, 2m
    ite3 (1CLK)         :         d3_s3, after d3_s2, 1m
    ite4 (2CLK)         :crit,    d3_s4, after d3_s3, 2m
    ite5 (2CLK)         :crit,    d3_s5, after d3_s4, 2m
    Buffer (1CLK)     :done,    d3_buf, after d3_s5, 1m

```
```mermaid
%%{init: { 'gantt': {'tickInterval': '1s', 'axisFormat': '%S'} } }%%
gantt
    title Exp-Adder-Div Pipeline (單位: 秒, 請嘗試拉寬視窗)
    
    %% 改用秒數格式，試圖強制顯示更細的刻度
    dateFormat  s
    axisFormat  %S
    
    %% 設定 1 CLK = 1 秒 (s)
    
    %% --- 情境 A: 運算時間 8 CLK (最快) ---
    section Path Fast (8 CLK)
    Data In             :done,    p8_in, 0, 1s
    Exp (Fast)          :active,  p8_exp, after p8_in, 8s
    Buffer              :done,    p8_buf, after p8_exp, 1s
    Adder (2CLK)        :active,  p8_add, after p8_buf, 2s
    Rap (10CLK)         :crit,    p8_rap, after p8_add, 10s
    Mul (1CLK)          :done,    p8_mul, after p8_rap, 1s

    %% --- 情境 B: 運算時間 9 CLK (中等) ---
    section Path Med (9 CLK)
    Data In             :done,    p9_in, 0, 1s
    Exp (Med)           :active,  p9_exp, after p9_in, 9s
    Buffer              :done,    p9_buf, after p9_exp, 1s
    Adder (2CLK)        :active,  p9_add, after p9_buf, 2s
    Rap (10CLK)         :crit,    p9_rap, after p9_add, 10s
    Mul (1CLK)          :done,    p9_mul, after p9_rap, 1s

    %% --- 情境 C: 運算時間 10 CLK (最慢) ---
    section Path Slow (10 CLK)
    Data In             :done,    p10_in, 0, 1s
    Exp (Slow)          :active,  p10_exp, after p10_in, 10s
    Buffer              :done,    p10_buf, after p10_exp, 1s
    Adder (2CLK)        :active,  p10_add, after p10_buf, 2s
    Rap (10CLK)         :crit,    p10_rap, after p10_add, 10s
    Mul (1CLK)          :done,    p10_mul, after p10_rap, 1s

```

```mermaid

%%{init: { 'gantt': {'tickInterval': '2s', 'axisFormat': '%S'} } }%%
gantt
    title 完整順序: Exp(8->9->10) -> Buffer -> Adder -> Rap -> Mul
    dateFormat  s
    axisFormat  %S
    
    %% 設定 1 CLK = 1 秒
    
    %% ==========================================
    %% 階段 1: Exp 運算 (依序執行)
    %% ==========================================
    section Exp Calculation
    %% 1. 先算 8 CLK 的 4 筆資料
    Batch 1 (Exp 8clk)    :done,    b1, 0, 8s
    
    %% 2. 接著算 9 CLK 的 4 筆資料 (從 8s 開始)
    Batch 2 (Exp 9clk)    :active,  b2, after b1, 9s
    
    %% 3. 接著算 10 CLK 的 4 筆資料 (從 17s 開始)
    Batch 3 (Exp 10clk)   :crit,    b3, after b2, 10s

    %%此時時間來到 T=27 (8+9+10)

    %% ==========================================
    %% 階段 2: 統一存入 Buffer
    %% ==========================================
    section Data Latch
    %% "以上時序完成後" -> 接著存入 Buffer
    %% 所有資料在這裡被鎖存，準備給 Adder 用
    Buffer Latch (All)    :done,    buf, after b3, 1s

    %% ==========================================
    %% 階段 3: 後續處理 (Adder -> Rap -> Mul)
    %% ==========================================
    section Processing
    %% Buffer 之後接著 Adder
    Adder (Sum All)       :active,  add, after buf, 2s
    
    %% Adder 之後接著 Rap
    Rap (Div 10CLK)       :crit,    rap, after add, 10s
    
    %% Rap 之後接著 Mul
    Mul (1CLK)            :done,    mul, after rap, 1s

```

```mermaid

%%{init: { 'gantt': {'tickInterval': '2s', 'axisFormat': '%S'} } }%%
gantt
    title Exp(4平行通道 x 3批次) -> Buffer -> Adder -> Rap -> Mul
    dateFormat  s
    axisFormat  %S
    
    %% 設定 1 CLK = 1 秒
    
    %% ==========================================
    %% 批次 1：8 CLK (4筆平行)
    %% ==========================================
    section Batch 1 (8clk)
    Exp Ch1 (Data 1)      :active, b1_1, 0, 8s
    Exp Ch2 (Data 2)      :active, b1_2, 0, 8s
    Exp Ch3 (Data 3)      :active, b1_3, 0, 8s
    Exp Ch4 (Data 4)      :active, b1_4, 0, 8s

    %% ==========================================
    %% 批次 2：9 CLK (4筆平行)
    %% 接著 Batch 1 之後開始
    %% ==========================================
    section Batch 2 (9clk)
    Exp Ch1 (Data 5)      :active, b2_1, after b1_1, 9s
    Exp Ch2 (Data 6)      :active, b2_2, after b1_2, 9s
    Exp Ch3 (Data 7)      :active, b2_3, after b1_3, 9s
    Exp Ch4 (Data 8)      :active, b2_4, after b1_4, 9s

    %% ==========================================
    %% 批次 3：10 CLK (4筆平行)
    %% 接著 Batch 2 之後開始
    %% ==========================================
    section Batch 3 (10clk)
    Exp Ch1 (Data 9)      :crit,   b3_1, after b2_1, 10s
    Exp Ch2 (Data 10)     :crit,   b3_2, after b2_2, 10s
    Exp Ch3 (Data 11)     :crit,   b3_3, after b2_3, 10s
    Exp Ch4 (Data 12)     :crit,   b3_4, after b2_4, 10s

    %% ==========================================
    %% 後續處理 (不變)
    %% 等 Batch 3 全部結束後才開始
    %% ==========================================
    section Post Process
    Buffer Latch          :done,   buf, after b3_1, 1s
    Adder (Sum All)       :active, add, after buf, 2s
    Rap (10clk)           :crit,   rap, after add, 10s
    Mul (1clk)            :done,   mul, after rap, 1s

```

```mermaid

%%{init: { 'gantt': {'barHeight': 25, 'sectionFontSize': 14} } }%%
gantt
    title Cordic Pipeline (長條圖名稱已更新)
    dateFormat  HH:mm
    axisFormat  %-M
    
    %% =======================
    %% Main Cordic Chain
    %% =======================
    section Range (Input)
    Range       :done,   m_range, 00:00, 1m
    
    section iter 1
    iter 1      :active, m_it1, after m_range, 2m
    
    section iter 2
    iter 2      :active, m_it2, after m_it1, 2m
    
    section iter 3
    iter 3      :active, m_it3, after m_it2, 2m
    
    section iter 4
    iter 4      :active, m_it4, after m_it3, 1m

    %% =======================
    %% Path Mid
    %% =======================
    section Buffer (Mid)
    Buffer      :done,   mid_wait, after m_it4, 2m

    %% =======================
    %% Path Top
    %% =======================
    section square1 (Top)
    square1     :active, t_sq1, after m_it4, 1m
    
    section Buffer (Top)
    Buffer      :done,   t_wait, after t_sq1, 1m

    %% =======================
    %% Path Bot
    %% =======================
    section square1 (Bot)
    square1     :active, b_sq1b, after m_it4, 1m
    
    section square2 (Bot)
    square2     :active, b_sq2b, after b_sq1b, 1m

    %% =======================
    %% Final Result
    %% =======================
    section Buffer Latch
    Buffer Latch :done,   buf, after b_sq2b, 1m

```



```mermaid

gantt
    title Pipeline Timing (刻度 = 分鐘數, 10ns = 1CLK)
    
    %% 1. 設定時間格式為「小時:分鐘」
    dateFormat  HH:mm
    
    %% 2. 設定軸線只顯示「分鐘數 (不補0)」
    %% 如果你的編輯器不支援 %-M，請改回 %M (會顯示 00, 01, 02...)
    axisFormat  %-M
    
    %% 3. 強制 X 軸從 00:00 開始
    %% 所有的長度單位都改用 "m" (分鐘)
    
    section rap_Data 1
    Input (1CLK)      :done,    d1_in, 00:00, 1m
    ite1 (2CLK)         :active,  d1_s1, after d1_in, 2m
    ite2 (2CLK)         :active,  d1_s2, after d1_s1, 2m
    ite3 (1CLK)         :         d1_s3, after d1_s2, 1m
    ite4 (2CLK)         :crit,    d1_s4, after d1_s3, 2m
    ite5 (2CLK)         :crit,    d1_s5, after d1_s4, 2m
    Buffer (1CLK)     :done,    d1_buf, after d1_s5, 1m

    section rap_Data 2
    %% II=2，所以從 00:02 開始
    Input (1CLK)      :done,    d2_in, 00:01, 1m
    ite1 (2CLK)         :active,  d2_s1, after d2_in, 2m
    ite2 (2CLK)         :active,  d2_s2, after d2_s1, 2m
    ite3 (1CLK)         :         d2_s3, after d2_s2, 1m
    ite4 (2CLK)         :crit,    d2_s4, after d2_s3, 2m
    ite5 (2CLK)         :crit,    d2_s5, after d2_s4, 2m
    Buffer (1CLK)     :done,    d2_buf, after d2_s5, 1m

    section rap_Data 3
    %% II=2，所以從 00:04 開始
    Input (1CLK)      :done,    d3_in, 00:02, 1m
    ite1 (2CLK)         :active,  d3_s1, after d3_in, 2m
    ite2 (2CLK)         :active,  d3_s2, after d3_s1, 2m
    ite3 (1CLK)         :         d3_s3, after d3_s2, 1m
    ite4 (2CLK)         :crit,    d3_s4, after d3_s3, 2m
    ite5 (2CLK)         :crit,    d3_s5, after d3_s4, 2m
    Buffer (1CLK)     :done,    d3_buf, after d3_s5, 1m

```

```mermaid

%%{init: { 'gantt': {'barHeight': 25, 'sectionFontSize': 14} } }%%
gantt
    title Flowchart to Tspec (Pipeline Timing)
    dateFormat  HH:mm
    axisFormat  %-M
    
    %% =======================
    %% Input
    %% =======================
    section Data (Input)
    data        :done,   d_in, 00:00, 1m

    %% =======================
    %% Stage 1 [First Iteration Block]
    %% =======================
    section It1 (iteration)
    iteration 1 :active, it1, after d_in, 1m

    section S1 (Red)
    s1          :crit,   s1, after it1, 1m

    section It2 (iteration)
    iteration 2 :active, it2, after s1, 1m

    section S2 (Red)
    s2          :crit,   s2, after it2, 1m

    section It3 (iteration)
    iteration 3 :active, it3, after s2, 1m

    %% =======================
    %% Middle Connection
    %% =======================
    section S3 (Red)
    s3          :crit,   s3, after it3, 1m

    %% =======================
    %% Stage 2 [Second Iteration Block]
    %% =======================
    section It4 (iteration)
    iteration 4 :active, it4, after s3, 1m

    section S4 (Red)
    s4          :crit,   s4, after it4, 1m

    section It5 (iteration)
    iteration 5 :active, it5, after s4, 1m

    section S5 (Red)
    s5          :crit,   s5, after it5, 1m

    section It6 (iteration)
    iteration 6 :active, it6, after s5, 1m

    %% =======================
    %% Output
    %% =======================
    section Buffer (Output)
    Buffer      :done,   buf, after it6, 1m

```

```mermaid

%%{init: { 'gantt': {'barHeight': 25, 'sectionFontSize': 14} } }%%
gantt
    title Pipeline Tspec: Normalize (Pre-S3) vs Iteration (Post-S3)
    dateFormat  HH:mm
    axisFormat  %-M
    
    %% 設定 1 CLK = 1 分鐘 (m)

    %% =======================
    %% Input
    %% =======================
    section Input Data
    Data_In         :done,   d_in, 00:00, 1m

    %% =======================
    %% Phase 1: Normalize (S3 之前)
    %% =======================
    
    %% It1 -->|1CLK+1CLK| S1 (Merge -> 2m)
    section Normalize 1 (It1)
    norm_val_1      :active, n1, after d_in, 2m

    %% It2 -->|1CLK+1CLK| S2 (Merge -> 2m)
    section Normalize 2 (It2)
    norm_val_2      :active, n2, after n1, 2m

    %% It3 -->|1CLK| S3 (Merge -> 1m)
    section Normalize 3 (It3)
    norm_val_3      :active, n3, after n2, 1m

    %% =======================
    %% Phase 2: Iteration (S3 之後)
    %% =======================

    %% It4 -->|1CLK+1CLK| S4 (Merge -> 2m)
    section Iteration 1 (It4)
    iter_val_1      :crit,   i1, after n3, 2m

    %% It5 -->|1CLK+1CLK| S5 (Merge -> 2m)
    section Iteration 2 (It5)
    iter_val_2      :crit,   i2, after i1, 2m

    %% It6 -->|1CLK| Buffer (Merge -> 1m)
    section Iteration 3 (It6)
    iter_val_3      :crit,   i3, after i2, 1m

    %% =======================
    %% Output
    %% =======================
    section Buffer Output
    Buf_Out         :done,   buf, after i3, 1m


```

```mermaid
%%{init: { 'gantt': {'tickInterval': '1s', 'axisFormat': '%S'} } }%%
gantt
    title Softmax 3-Stage Pipeline (Exp與Adder重疊執行)
    dateFormat  s
    axisFormat  %S s

    %% ==========================================
    %% Stage 1: Exponential Calculation (Main Engine)
    %% 特點：Exp 單元一直很忙，沒有停下來等 Adder
    %% ==========================================
    section Stage 1: Exp Unit
    Batch 1 (8clk)       :active, e1, 0, 8s
    Batch 2 (9clk)       :active, e2, after e1, 9s
    Batch 3 (10clk)      :active, e3, after e2, 10s

    %% ==========================================
    %% Stage 2: Accumulation Pipeline
    %% 特點：這是流水線的關鍵。
    %% 當 Stage 1 在算 Batch 2 時，Stage 2 正在加總 Batch 1
    %% ==========================================
    section Stage 2: Adder Pipe
    Wait B1             :done,   wait1, 0, 8s
    Buf+Add (Batch 1)   :crit,   acc1, after e1, 3s
    
    %% 空閒時間 (等待 Batch 2 算完)
    Wait B2             :done,   wait2, after acc1, 6s 
    Buf+Add (Batch 2)   :crit,   acc2, after e2, 3s

    %% 等待 Batch 3 算完
    Wait B3             :done,   wait3, after acc2, 7s
    Buf+Add (Batch 3)   :crit,   acc3, after e3, 3s

    %% ==========================================
    %% Stage 3: Final Result (Rap & Mul)
    %% 必須等最後一次加總 (Total Sum) 完成
    %% ==========================================
    section Stage 3: Final Ops
    Rap (Reciprocal)    :active, rap, after acc3, 10s
    Mul (Result)        :done,   mul, after rap, 1s
```

```mermaid
%%{init: { 'gantt': {'barHeight': 20, 'sectionFontSize': 14, 'axisFormat': '%M'} } }%%
gantt
    title Pipeline: Data 1(8clk) -> Data 2(9clk) -> Data 3(10clk)
    dateFormat  HH:mm
    axisFormat  %-M m

    %% ====================================================
    %% Data 1: 標準 8 CLK (參考你的原始代碼)
    %% Main Path: 1(R) + 2(i1) + 2(i2) + 2(i3) + 1(i4) = 8
    %% ====================================================
    section Data 1 (8 CLK)
    Range             :done,    d1_r, 00:00, 1m
    iter 1            :active,  d1_i1, after d1_r, 2m
    iter 2            :active,  d1_i2, after d1_i1, 2m
    iter 3            :active,  d1_i3, after d1_i2, 2m
    iter 4            :active,  d1_i4, after d1_i3, 1m
    Sq1+Sq2 (Bot)     :         d1_bot, after d1_i4, 2m
    Buffer Latch      :         d1_out, after d1_bot, 1m

    %% ====================================================
    %% Data 2: 變為 9 CLK
    %% 流水線入口：延後 2m 進入 (00:02)
    %% 變化：Iter 3 變為 3m (紅色標示)
    %% Main Path: 1 + 2 + 2 + 3 + 1 = 9
    %% ====================================================
    section Data 2 (9 CLK)
    Range             :done,    d2_r, 00:02, 1m
    iter 1            :active,  d2_i1, after d2_r, 2m
    iter 2            :active,  d2_i2, after d2_i1, 2m
    iter 3 (Long)     :crit,    d2_i3, after d2_i2, 3m
    iter 4            :active,  d2_i4, after d2_i3, 1m
    Sq1+Sq2 (Bot)     :         d2_bot, after d2_i4, 2m
    Buffer Latch      :         d2_out, after d2_bot, 1m

    %% ====================================================
    %% Data 3: 變為 10 CLK
    %% 流水線入口：延後 4m 進入 (00:04)
    %% 變化：Iter 3 變為 3m, Iter 4 變為 2m (紅色標示)
    %% Main Path: 1 + 2 + 2 + 3 + 2 = 10
    %% ====================================================
    section Data 3 (10 CLK)
    Range             :done,    d3_r, 00:04, 1m
    iter 1            :active,  d3_i1, after d3_r, 2m
    iter 2            :active,  d3_i2, after d3_i1, 2m
    iter 3 (Long)     :crit,    d3_i3, after d3_i2, 3m
    iter 4 (Long)     :crit,    d3_i4, after d3_i3, 2m
    Sq1+Sq2 (Bot)     :         d3_bot, after d3_i4, 2m
    Buffer Latch      :         d3_out, after d3_bot, 1m

```
```mermaid

%%{init: { 'gantt': {'barHeight': 20, 'sectionFontSize': 14, 'axisFormat': '%M'} } }%%
gantt
    title Pipeline Path Selection: No SQ(8) vs SQ1(9) vs SQ1+2(10)
    dateFormat  HH:mm
    axisFormat  %-M m

    %% ====================================================
    %% Data 1: 總長 8 CLK (最短路徑)
    %% 路徑: Range(1)+i1(2)+i2(2)+i3(2)+i4(1) = 8
    %% 特點: 不經過 Square，直接 Latch
    %% ====================================================
    section Data 1 (8 CLK - No SQ)
    Range             :done,    d1_r, 00:00, 1m
    iter 1            :active,  d1_i1, after d1_r, 2m
    iter 2            :active,  d1_i2, after d1_i1, 2m
    iter 3            :active,  d1_i3, after d1_i2, 2m
    iter 4            :active,  d1_i4, after d1_i3, 1m
    Buffer Latch      :done,    d1_out, after d1_i4, 1m

    %% ====================================================
    %% Data 2: 總長 9 CLK
    %% Start: 延後 2m 進入 (00:02)
    %% 路徑: ... + i4(1) + Square1(1) = 9
    %% 特點: 經過 Square 1
    %% ====================================================
    section Data 2 (9 CLK - SQ1)
    Range             :done,    d2_r, 00:02, 1m
    iter 1            :active,  d2_i1, after d2_r, 2m
    iter 2            :active,  d2_i2, after d2_i1, 2m
    iter 3            :active,  d2_i3, after d2_i2, 2m
    iter 4            :active,  d2_i4, after d2_i3, 1m
    Square 1          :crit,    d2_sq1, after d2_i4, 1m
    Buffer Latch      :done,    d2_out, after d2_sq1, 1m

    %% ====================================================
    %% Data 3: 總長 10 CLK (最長路徑)
    %% Start: 延後 4m 進入 (00:04)
    %% 路徑: ... + i4(1) + Square1(1) + Square2(1) = 10
    %% 特點: 經過 Square 1 和 Square 2
    %% ====================================================
    section Data 3 (10 CLK - SQ1+SQ2)
    Range             :done,    d3_r, 00:04, 1m
    iter 1            :active,  d3_i1, after d3_r, 2m
    iter 2            :active,  d3_i2, after d3_i1, 2m
    iter 3            :active,  d3_i3, after d3_i2, 2m
    iter 4            :active,  d3_i4, after d3_i3, 1m
    Square 1          :crit,    d3_sq1, after d3_i4, 1m
    Square 2          :crit,    d3_sq2, after d3_sq1, 1m
    Buffer Latch      :done,    d3_out, after d3_sq2, 1m

```

```mermaid

%%{init: { 'gantt': {'barHeight': 20, 'sectionFontSize': 14, 'axisFormat': '%M'} } }%%
gantt
    title Tight Pipeline: Data 1(No SQ) / Data 2(SQ1) / Data 3(SQ1+2)
    dateFormat  HH:mm
    axisFormat  %-M m

    %% ====================================================
    %% Data 1: 總長 8 CLK (No Square)
    %% 時間: 00:00 開始
    %% 當它在 00:01 進入 iter 1 時，Data 2 剛好開始 Input
    %% ====================================================
    section Data 1 (8 CLK)
    Range (In)        :done,    d1_r, 00:00, 1m
    iter 1            :active,  d1_i1, after d1_r, 2m
    iter 2            :active,  d1_i2, after d1_i1, 2m
    iter 3            :active,  d1_i3, after d1_i2, 2m
    iter 4            :active,  d1_i4, after d1_i3, 1m
    Buffer Latch      :done,    d1_out, after d1_i4, 1m

    %% ====================================================
    %% Data 2: 總長 9 CLK (With SQ1)
    %% 時間: 00:01 開始 (緊接著 Data 1 的 Input 之後)
    %% ====================================================
    section Data 2 (9 CLK)
    Range (In)        :done,    d2_r, 00:01, 1m
    iter 1            :active,  d2_i1, after d2_r, 2m
    iter 2            :active,  d2_i2, after d2_i1, 2m
    iter 3            :active,  d2_i3, after d2_i2, 2m
    iter 4            :active,  d2_i4, after d2_i3, 1m
    Square 1          :crit,    d2_sq1, after d2_i4, 1m
    Buffer Latch      :done,    d2_out, after d2_sq1, 1m

    %% ====================================================
    %% Data 3: 總長 10 CLK (With SQ1 + SQ2)
    %% 時間: 00:02 開始 (緊接著 Data 2 的 Input 之後)
    %% ====================================================
    section Data 3 (10 CLK)
    Range (In)        :done,    d3_r, 00:02, 1m
    iter 1            :active,  d3_i1, after d3_r, 2m
    iter 2            :active,  d3_i2, after d3_i1, 2m
    iter 3            :active,  d3_i3, after d3_i2, 2m
    iter 4            :active,  d3_i4, after d3_i3, 1m
    Square 1          :crit,    d3_sq1, after d3_i4, 1m
    Square 2          :crit,    d3_sq2, after d3_sq1, 1m
    Buffer Latch      :done,    d3_out, after d3_sq2, 1m

```
