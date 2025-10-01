# 🌟 SVM 與 MLP 權重/偏差更新原理解說

本檔案說明 SVM 與 MLP 在訓練過程中如何更新權重 `W` 與偏差 `b`，並附公式與簡單說明。  

> ⚠️ 注意：GitHub Markdown 對 LaTeX 公式的支援有限，inline `$...$` 與 display `$$...$$` 在 repo README 或 Issues/Discussions 頁面通常能顯示。若無法渲染，可使用公式圖片替代。

---

## 一、SVM (線性 SVM, soft-margin)

### 1️⃣ 目標函數

SVM 目標：最大化邊界距離並減少分類錯誤。損失函數為：

$$
L(W,b) = \frac{1}{2} \|W\|^2 + C \sum_{i=1}^n \max(0, 1 - y_i (W^T x_i + b))
$$

### 2️⃣ 梯度計算

對單樣本 \(i\) 分情況：

- **正確且 margin 外** (\(y_i(W^T x_i + b) \ge 1\))：

$$
\frac{\partial L}{\partial W} = W, \qquad
\frac{\partial L}{\partial b} = 0
$$

- **錯誤或 margin 內** (\(y_i(W^T x_i + b) < 1\))：

$$
\frac{\partial L}{\partial W} = W - C\,y_i x_i, \qquad
\frac{\partial L}{\partial b} = -C\,y_i
$$

### 3️⃣ 梯度下降更新

學習率 \(\eta\) 下更新公式：

$$
W \leftarrow W - \eta\,\frac{\partial L}{\partial W}, \qquad
b \leftarrow b - \eta\,\frac{\partial L}{\partial b}
$$

> ✅ 直覺：SVM 只針對「違反邊界條件的樣本」進行修正，其餘樣本只受正則化影響。

---

## 二、MLP (多層感知機)

### 1️⃣ 前向傳播

第 \(l\) 層神經元計算：

$$
z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]}, \qquad
a^{[l]} = f(z^{[l]})
$$

其中：
- \(a^{[l-1]}\)：前一層輸出  
- \(f(\cdot)\)：激活函數（ReLU, Sigmoid, Tanh 等）

### 2️⃣ 損失函數

以 MSE 為例：

$$
L = \frac{1}{2} \| a^{[L]} - y \|^2
$$

輸出層誤差：

$$
\delta^{[L]} = (a^{[L]} - y) \odot f'(z^{[L]})
$$

隱藏層誤差：

$$
\delta^{[l]} = (W^{[l+1]})^T \delta^{[l+1]} \odot f'(z^{[l]})
$$

### 3️⃣ 梯度計算與更新

每層梯度：

$$
\frac{\partial L}{\partial W^{[l]}} = \delta^{[l]} (a^{[l-1]})^T, \qquad
\frac{\partial L}{\partial b^{[l]}} = \delta^{[l]}
$$

梯度下降更新：

$$
W^{[l]} \leftarrow W^{[l]} - \eta\,\frac{\partial L}{\partial W^{[l]}}, \qquad
b^{[l]} \leftarrow b^{[l]} - \eta\,\frac{\partial L}{\partial b^{[l]}}
$$

> ✅ 直覺：MLP 利用反向傳播把誤差沿每層分配，並依梯度調整權重與偏差，使網路逐步逼近正確輸出。

---

## 三、快速比較

| 項目 | SVM | MLP |
|------|-----|-----|
| 損失函數 | Hinge Loss | MSE / Cross-Entropy |
| 參數更新 | 梯度下降只針對違反 margin 的樣本 | 反向傳播對每層參數都更新 |
| 非線性能力 | 線性（可加 kernel） | 非線性映射能力 |
| 激活函數 | 無 | 有（ReLU, Sigmoid, Tanh 等） |
| 更新直覺 | 調整邊界使支持向量滿足 margin | 誤差反傳 → 調整每層權重，使輸出逼近標籤 |

---

📘 **總結**

- **SVM**：重點是「邊界最大化」，梯度只針對違規樣本修正。  
- **MLP**：重點是「整體誤差最小化」，透過鏈式法則把誤差分配給每層權重與偏差。  
- **核心共通點**：都是「損失微分 → 梯度下降 → 更新參數」。
