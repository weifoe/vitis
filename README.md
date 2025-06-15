# vitis 操作流程

## 1. create platform component (Name and Location)

   ![image](https://github.com/user-attachments/assets/fb6e22b8-06fc-4e48-8891-c07886457fe3)

### >設定好文件名字和資料夾

## 2. create platform component (Flow) 

![image](https://github.com/user-attachments/assets/38645eca-c555-4fb3-b3dd-d9820e4ae99d)



### >引入xsa檔案

## 3. create platform component (OS and Processor)

![image](https://github.com/user-attachments/assets/a01fd460-ff8f-4bdf-b8c7-3d2c672a752b)


### >設定處理器

## 4.create platform component (Summary)

![image](https://github.com/user-attachments/assets/459133e4-76c4-4651-900c-89f4aa66fedc)

### >finish

---
## 1. Empty Application

![image](https://github.com/user-attachments/assets/f3d2d093-30ea-40b5-a3be-c702ec490e81)

### >創建 Empty Application

## 2. Create Application Component (Name and Location)

![image](https://github.com/user-attachments/assets/bc06153f-857f-42f2-bd9e-401dd5492f5d)

### >創建文件

## 3. Create Application Component (Hardware)

![image](https://github.com/user-attachments/assets/1f8302cd-3af6-4c5f-94d4-29e335a0e8fd)


### >Select Platform(ego-xz7)


## 4. Create Application Component (Domain)

![image](https://github.com/user-attachments/assets/e35d0eb8-f48d-4d78-8b79-5ccb282f0bc2)

### > 選擇standalone_microblaze_riscv_0

## 5. Create Application Component (Source File)

![image](https://github.com/user-attachments/assets/79b12a81-5486-49af-bca3-68d833f324c9)


### > Next

## 6. Create Application Component (Summary)

![image](https://github.com/user-attachments/assets/f0557d06-379e-4b2f-a91f-53d580416d75)

### > Finish

---

# 編譯C程式碼

## 1. Build platform

![image](https://github.com/user-attachments/assets/8af069e8-2c0a-4d8d-84e9-c2f4945c849a)

## 1.1 build platform 成功

### output 畫面確認build成功

![image](https://github.com/user-attachments/assets/a927bcb6-8b5a-4bca-bb38-276f46b7b520)


### 確認 empty_application的include資料夾有產生.h檔案

![image](https://github.com/user-attachments/assets/23998ba8-c760-4e79-afda-b7e07cd472fd)

## 2 empty_application產生.c檔案

### 對src按右鍵->New File->輸入name.c(本說明手冊由於已產生hello.c所以已name.c舉例,以下說明都已hello.c為實作範例)->ok


![image](https://github.com/user-attachments/assets/1f48eef3-7ad4-45cd-94c0-bf4e7d4b70ca)

### 3 編寫 hello.c 

#### > 測試程式碼


```c
#include "xgpio.h"

#include "xparameters.h"

#define XPAR_AXI_GPIO_0_DEVICE_ID 0

#define GPIO_DEVICE_ID XPAR_AXI_GPIO_0_DEVICE_ID

int main() {

    XGpio Gpio;

    int status;

    int value = 0xAA;  // 初始燈光狀態（10101010）

    status = XGpio_Initialize(&Gpio, GPIO_DEVICE_ID);

    if (status != XST_SUCCESS) {
        return XST_FAILURE;
    }

    XGpio_SetDataDirection(&Gpio, 1, 0x00);  // 通道1為輸出

    while (1) {
        XGpio_DiscreteWrite(&Gpio, 1, value);  // 輸出當前燈光狀態
        value = ~value;                         // 將燈光狀態反轉，達到閃爍效果
        for (volatile int i = 0; i < 10000000; i++);  // 簡單延遲，視頻率調整
    }

    return 0;
}
```

### 3-1 將以上程式碼貼到hello.c

![image](https://github.com/user-attachments/assets/50cc35f3-706f-46f4-aa6b-a8da23ce1bdd)

> 對 empty_application執行build

![image](https://github.com/user-attachments/assets/624dac45-e0ff-4b88-a1fc-e727ec357600)

> 確認有產生.elf檔案(很重要)

![image](https://github.com/user-attachments/assets/b6e653c0-f2c1-41e5-a297-f631926c1441)

>按下run(右下角出現錯誤正常))

![image](https://github.com/user-attachments/assets/12ffb604-f9cc-4fe6-9ea4-a60a47ccf59f)

> 按下run確認板子有亮藍燈

![133242](https://github.com/user-attachments/assets/45d39ece-6814-429c-9a5d-c7b33371d66f)

### 3-2 啟動xsdb將.elf檔案載入到板子

![image](https://github.com/user-attachments/assets/69b7a054-30a2-4d36-bf77-c18e28ac4cab)

> vitis->XSDB console

#### XSDB 指令

```
xsdb% connect

```
![image](https://github.com/user-attachments/assets/7e029e67-fb61-4e0e-955c-19c877c151be)

```

xsdb% targets

```

![image](https://github.com/user-attachments/assets/c659222b-0805-48a2-b4ea-5fe48a0e0110)



```
xsdb% targets 7
xsdb% dow D:/xinlinx_205/project_3/newrisc(此專案資料夾名字)/empty_application/build/empty_application.elf(基本上elf檔案都在empty_application/build底下)

```
以上指令執行後

結果會像此影片

https://youtu.be/5ZMqT0NsJ04

           


































