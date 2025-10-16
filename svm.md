# 🌟 SVM 與 MLP 權重／偏差更新原理解說

---

## 🧩 一、SVM（線性 SVM，soft-margin）

### 1️⃣ 目標函數

SVM 的目標是最大化邊界距離並減少分類錯誤。  
損失函數定義如下：

$$
L(W,b) = \frac{1}{2} \|W\|^2 + C \sum_{i=1}^n \max(0, 1 - y_i (W^T x_i + b))
$$

---

### 2️⃣ 梯度計算

對單一樣本 \(i\)：

- **正確且位於 margin 外**（\(y_i(W^T x_i + b) \ge 1\)）：

$$
\frac{\partial L}{\partial W} = W, \qquad
\frac{\partial L}{\partial b} = 0
$$

- **錯誤或位於 margin 內**（\(y_i(W^T x_i + b) < 1\)）：

$$
\frac{\partial L}{\partial W} = W - C\,y_i x_i, \qquad
\frac{\partial L}{\partial b} = -C\,y_i
$$

---

### 3️⃣ 梯度下降更新

設定學習率 \(\eta\)，參數更新規則：

$$
W \leftarrow W - \eta\,\frac{\partial L}{\partial W}, \qquad
b \leftarrow b - \eta\,\frac{\partial L}{\partial b}
$$

> ✅ **直覺**：SVM 只針對「違反邊界條件的樣本」進行修正；  
> 其他樣本僅受正則化項影響。

---

## 🤖 二、MLP（多層感知機）

### 1️⃣ 前向傳播

第 \(l\) 層神經元的運算：

$$
z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]}, \qquad
a^{[l]} = f(z^{[l]})
$$

其中：

- \(a^{[l-1]}\)：前一層輸出  
- \(f(\cdot)\)：激活函數（ReLU, Sigmoid, Tanh 等）

---

### 2️⃣ 損失函數與誤差傳遞

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

---

### 3️⃣ 梯度計算與更新

每層權重與偏差的梯度：

$$
\frac{\partial L}{\partial W^{[l]}} = \delta^{[l]} (a^{[l-1]})^T, \qquad
\frac{\partial L}{\partial b^{[l]}} = \delta^{[l]}
$$

更新規則：

$$
W^{[l]} \leftarrow W^{[l]} - \eta\,\frac{\partial L}{\partial W^{[l]}}, \qquad
b^{[l]} \leftarrow b^{[l]} - \eta\,\frac{\partial L}{\partial b^{[l]}}
$$

> ✅ **直覺**：MLP 透過反向傳播將誤差分配到每層，  
> 調整權重與偏差，使網路輸出逐步逼近標籤。

---

## ⚖️ 三、快速比較表

| 項目 | 🧠 SVM | 🔗 MLP |
|------|---------|---------|
| 損失函數 | Hinge Loss | MSE / Cross-Entropy |
| 參數更新 | 僅針對違反 margin 樣本 | 反向傳播更新所有層 |
| 非線性能力 | 線性（可用 kernel 擴展） | 具非線性映射能力 |
| 激活函數 | 無 | 有（ReLU, Sigmoid, Tanh） |
| 更新直覺 | 調整邊界以滿足 margin | 誤差反傳 → 調整各層權重 |

---

## 📘 總結

- **SVM**：核心為「邊界最大化」，僅修正違規樣本。  
- **MLP**：核心為「整體誤差最小化」，利用反向傳播修正所有層參數。  
- **共通點**：皆以「損失微分 → 梯度下降 → 更新參數」為核心訓練流程。

---

> 🧾 **提示**：  
> 若要在 GitHub 正確顯示 LaTeX 公式，可在設定中啟用 `math rendering`（GitHub 支援 $\LaTeX$ via MathJax）。
