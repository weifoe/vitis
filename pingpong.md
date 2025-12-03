# 🏓 乒乓球遊戲 AI：專家規則與自動化資料收集

# breakdown 

<img width="1342" height="889" alt="image" src="https://github.com/user-attachments/assets/9ef43166-ca0e-4c95-a030-863176610c34" />


# 訓練環境

<img width="1930" height="796" alt="image" src="https://github.com/user-attachments/assets/a1cbfb66-9055-470d-a72b-b9f47dc35f3f" />

# 得分設定

<img width="1782" height="743" alt="image" src="https://github.com/user-attachments/assets/a2d0b18e-4b86-403d-931c-aa112b228740" />

- ### 說明:其中一方十分會結束遊戲

# 訓練資料量

<img width="1559" height="921" alt="image" src="https://github.com/user-attachments/assets/927e0bb9-94a0-48a0-a71b-30e020806a94" />

- ### 現遊玩4次的資料(第一筆沒截圖到)

# 訓練結果

<img width="1744" height="1029" alt="image" src="https://github.com/user-attachments/assets/6c693629-c55f-4f53-aa4c-9f65f0cbff7d" />

<img width="1067" height="612" alt="image" src="https://github.com/user-attachments/assets/91976fdb-fac2-41cf-a9cf-8a085911f8f2" />


## A. 不動（NONE）

**意義：**  
當板子的中心點已經位於目標落點 `± 2 像素` 的「滿意範圍」之內時，專家會判定板子已到位，因此輸出 **NONE** 指令。

- 判斷條件：  
  `abs(paddle_x - target_x) <= 2`

**與訓練的關係：**  
教導 AI **「何時應該停止」**，避免不必要的晃動。

---

## B. 右移動（RIGHT）

**意義：**  
當板子的中心位於目標點左側，且差距超過 `2 像素` 時，專家會下指令 **MOVE_RIGHT** 讓板子往右移動。

- 判斷條件：  
  `paddle_x < target_x - 2`

**與訓練的關係：**  
教導 AI **「何時應該向右追趕」**，避免落點偏右時接不到球。

---

## C. 左移動（LEFT）

**意義：**  
當板子的中心位於目標點右側，且差距超過 `2 像素` 時，專家會下指令 **MOVE_LEFT** 讓板子往左移動。

- 判斷條件：  
  `paddle_x > target_x + 2`

**與訓練的關係：**  
教導 AI **「何時應該向左追趕」**，讓板子能準確回到落點位置。

---

## 🧠 核心策略：專家系統 (Rule-Based Expert)

此 AI 不依賴神經網絡進行推理，而是利用簡單的物理公式計算球的落點。策略邏輯主要分為三個步驟：

### 1. 判斷擊球時機 (Incoming Check)
為了避免無效移動，AI 首先判斷球是否「朝向自己」飛來：
- **Player 1 (下方):** 當球的垂直速度 $V_y > 0$ (向下) 時，才開始計算。
- **Player 2 (上方):** 當球的垂直速度 $V_y < 0$ (向上) 時，才開始計算。
- **待機模式:** 若球是遠離自己的，AI 會自動移動到場地中央 ($x = 100$) 守株待兔。

### 2. 落點預測 (Trajectory Prediction)
當球朝向自己飛來時，利用物理公式計算球到達板子高度時的 X 座標。

1. **計算剩餘步數 (Steps):**

$$
\text{steps} = \frac{\text{板子高度} - \text{球當前 Y}}{V_y}
$$

2. 計算無牆壁時的落點 (Predicted X):

$$
\text{PredX} = \text{球當前 X} + V_x \times \text{steps}
$$

3. 牆壁反彈處理 (Rebound Calculation)  
由於場地寬度有限 ($W = 200$)，球會碰到牆壁反彈。程式碼利用商數 (Cycle) 與餘數 (Remainder) 來計算最終落點：

$$
\text{cycle} = \text{int}(\text{PredX} / W)
$$

$$
\text{remain} = \text{PredX} \bmod W
$$

邏輯判斷：
- 若 `cycle` 為 **偶數** (0, 2, 4...)：球從左側向右移動，最終位置為 $\text{remain}$。
- 若 `cycle` 為 **奇數** (1, 3, 5...)：球碰到右牆反彈回左，最終位置為 $W - \text{remain}$。

---

## 💾 資料收集機制 (Data Collection)

此腳本會在遊戲過程中自動收集特徵資料，並在遊戲結束 (Reset) 時儲存為 `game_data.pickle`。

### 特徵定義 (State)
為了讓機器學習模型更容易收斂，所有特徵皆經過 **正規化 (Normalization)** 處理：

| 特徵索引 | 物理意義 | 正規化方式 | 範圍 |
| :--- | :--- | :--- | :--- |
| `0` | 球的 X 座標 | `Ball\_X / 200` | 0 ~ 1 |
| `1` | 球的 Y 座標 | `Ball\_Y / 500` | 0 ~ 1 |
| `2` | 球的水平速度 | $V_x / 50$ | -1 ~ 1 |
| `3` | 球的垂直速度 | $V_y / 50$ | -1 ~ 1 |
| `4` | 板子 X 座標 | `Plat\_X / 200` | 0 ~ 1 |

### 標籤定義 (Label)
記錄專家系統當下做出的決策：
- `0`: 不移動 (NONE)
- `1`: 向左移動 (MOVE\_LEFT)
- `2`: 向右移動 (MOVE\_RIGHT)

---

## 🚀 使用說明

### 1. 檔案位置
請確保此腳本 (`ml\_play.py`) 位於您的遊戲 `ml` 資料夾中。

### 2. 資料儲存
- 遊戲結束後，程式會自動將資料寫入同目錄下的 `game_data.pickle`。
- **自動累加:** 若檔案已存在，程式會讀取舊資料並合併新資料，適合連續收集多局遊戲。
- **記憶體保護:** 每累積 1000 筆資料才會寫入一次硬碟。

### 3. 如何開始訓練？
收集足夠資料 (建議 > 10,000 筆 frame) 後，您可以使用另外的訓練腳本讀取 `game_data.pickle` 來訓練 KNN、Random Forest 或 MLP 模型。

```python
# 讀取資料範例
import pickle
with open("game_data.pickle", "rb") as f:
    data = pickle.load(f)

print(f"總共收集了 {len(data)} 筆資料")

```
---

