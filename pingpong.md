# 🏓 乒乓球遊戲 AI：專家規則與自動化資料收集(冠傑)
# Ping Pong AI: Rule-Based Expert & Data Collection

本專案實作了一個基於 **物理預測 (Physics-Based Prediction)** 的專家系統 AI。它不僅能自動進行遊戲（接近無敵狀態），還能同時收集遊戲過程中的「狀態 (State)」與「動作 (Action)」，用於訓練後續的機器學習模型。

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

# 🏓 乒乓球遊戲 AI：偏移策略專家系統
# Ping Pong AI: Offset-Enhanced Rule-Based Expert

本專案實作了一個基於 **物理預測與偏移策略 (Physics Prediction + Offset Strategy)** 的專家系統 AI，能自動打球並收集遊戲資料以供後續機器學習使用。

---

## 🧠 核心策略

此 AI 採用**物理預測 + 偏移策略**來決定板子移動：

1. **判斷球是否朝自己飛來 (Incoming Check)**
   - 下方板子 (Player 1)：當球垂直速度 $V_y > 0$ 時，球向下飛來。
   - 上方板子 (Player 2)：當球垂直速度 $V_y < 0$ 時，球向上飛來。
   - 若球遠離板子，AI 移動到場地中央：$x = W/2$。

### 落點預測 (Trajectory Prediction)

- 計算剩餘步數：
$$
steps = \frac{plat\_y - ball\_y}{V_y}
$$

- 無牆壁落點：
$$
pred\_x = ball\_x + V_x \times steps
$$

### 牆壁反彈計算 (Rebound Calculation)

由於場地寬度有限 ($W = 200$)，球會碰到牆壁反彈。

- 計算落點：
$$
cycle = \lfloor pred\_x / W \rfloor
$$
$$
remain = pred\_x \bmod W
$$
$$
target\_x = 
\begin{cases} 
remain & \text{if cycle is even} \\ 
W - remain & \text{if cycle is odd} 
\end{cases}
$$

### 偏移策略 (Offset Strategy)

- 根據落點與場地中心位置，增加偏移 $offset = \pm 5$ 像素，以打出不同方向的球。
- 最終落點：
$$
target\_x \leftarrow target\_x + offset
$$

5. **板子移動指令**
   - 若板子中心小於 $target\_x - 3$ → `MOVE_RIGHT`
   - 若板子中心大於 $target\_x + 3$ → `MOVE_LEFT`
   - 否則 → `NONE`

---

## 💾 資料收集

### 特徵 (State)
| 索引 | 意義 | 正規化方式 | 範圍 |
| :--- | :--- | :--- | :--- |
| 0 | 球 X 座標 | $ball\_x / W$ | 0 ~ 1 |
| 1 | 球 Y 座標 | $ball\_y / H$ | 0 ~ 1 |
| 2 | 水平速度 | $V_x / 50$ | -1 ~ 1 |
| 3 | 垂直速度 | $V_y / 50$ | -1 ~ 1 |
| 4 | 板子 X 座標 | $plat\_x / W$ | 0 ~ 1 |

### 標籤 (Action)
| Label | 指令 |
| :---: | :--- |
| 0 | NONE (不移動) |
| 1 | MOVE_LEFT (向左) |
| 2 | MOVE_RIGHT (向右) |

### 額外資訊
- `incoming`: 球是否朝自己飛來
- `pred\_x`: 預測落點
- `offset`: 偏移策略值

---

## 🚀 使用方式

1. **檔案放置**
   - 將 `ml_play.py` 放到遊戲 `ml` 資料夾中。

2. **資料儲存**
   - 遊戲結束時自動存檔為 `game_data_<side>.pickle`。
   - 若檔案存在，舊資料會自動合併。
   - 每累積 1000 筆資料才存一次，避免記憶體爆掉。

3. **資料訓練**
```python
import pickle
with open("game_data_1P.pickle", "rb") as f:
    data = pickle.load(f)
print(f"總共收集 {len(data)} 筆資料")
