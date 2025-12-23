import pickle
import os

class MLPlay:
    """
    PAIA 乒乓球 AI：1P 進階收集版 (最終優化 + 預測落點特徵)
    特徵數：6 
    特徵詳情：[球X, 球Y, 球速X, 球速Y, 板X, 預測落點X]
    """
    def __init__(self, ai_name, *args, **kwargs):
        print(f"[AI INIT] Side = {ai_name}")
        self.side = ai_name

        # 遊戲常數
        self.W = 200
        self.H = 500
        self.PLAT_W = 40
        self.PLAT_H = 30
        self.BALL_SIZE = 5

        # 內部狀態
        self.prev_ball = None
        self.prev_plat_x = None
        self.data_buffer = [] # 暫存區 
        self.all_data = []    # 累積存檔區 
        
        # 正規化因子
        self.SPEED_NORM = 50.0 
        self.MIN_DATA_SIZE = 1000 

    def update(self, scene_info, *args, **kwargs):
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"

        # ===== 取得資料 =====
        ball = scene_info.get("ball")
        platform = scene_info.get("platform") or \
                   scene_info.get(f"platform_{self.side}")

        if ball is None or platform is None:
            return "NONE"

        ball_x, ball_y = ball
        plat_x, plat_y = platform

        # ===== 1. 計算速度 =====
        if self.prev_ball is None:
            vx, vy = 0, 0
        else:
            vx = ball_x - self.prev_ball[0]
            vy = ball_y - self.prev_ball[1]
            
        self.prev_ball = (ball_x, ball_y)

        # ===== 2. 判斷方向 =====
        is_bottom = plat_y > self.H / 2
        is_top = not is_bottom
        incoming = (is_bottom and vy > 0) or (is_top and vy < 0)

        # ===== 3. 數學策略 (產生正確答案 & 第6特徵) =====
        # 這裡算出的 target_x 就是考慮了「牆壁反彈」後的最終落點
        if not incoming or vy == 0:
            target_x = self.W / 2
        else:
            # 計算球還需要幾步才會到板子的高度
            steps = (plat_y - ball_y) / vy
            
            # 預測沒牆壁時的落點
            pred_x = ball_x + vx * steps
            
            # 處理牆壁反彈 (Reflection Logic)
            cycle = int(pred_x // self.W)
            remain = pred_x % self.W
            # 奇數次反彈 vs 偶數次反彈
            target_x = remain if (cycle % 2 == 0) else self.W - remain
        
        # 動作控制 (引導 AI 去接這個 target_x)
        plat_center = plat_x + self.PLAT_W / 2
        if plat_center < target_x - 3:
            command = "MOVE_RIGHT"
            action_code = 2 
        elif plat_center > target_x + 3:
            command = "MOVE_LEFT"
            action_code = 1 
        else:
            command = "NONE"
            action_code = 0 

        # ===== 4. 收集訓練資料 (新增特徵) =====
        
        # 條件 A: 只收集 1P 且 球正在移動
        if self.side == "2P" and (vx != 0 or vy != 0):
            
            # 條件 B: 只收集「有移動」的數據，剔除發呆
            if action_code == 1 or action_code == 2:
                
                # ★ 6 個特徵 (新增：預測落點 target_x) ★
                state = [
                    ball_x / self.W,        # 1. 球 X
                    ball_y / self.H,        # 2. 球 Y
                    vx / self.SPEED_NORM,   # 3. 球速 X
                    vy / self.SPEED_NORM,   # 4. 球速 Y
                    plat_x / self.W,        # 5. 板 X
                    target_x / self.W       # 6. ★ 新增：預測落點 (包含反彈物理)
                ]
                self.data_buffer.append([state, action_code])
        
        # ===== 5. 結果判定 (條件 C: 只收成功打到的) =====
        
        # 判定高度與水平是否命中
        hit_y = (ball_y + self.BALL_SIZE >= plat_y)
        hit_x = (ball_x + self.BALL_SIZE >= plat_x) and (ball_x <= plat_x + self.PLAT_W)

        if hit_y and hit_x and incoming: 
            if len(self.data_buffer) > 0:
                self.all_data.extend(self.data_buffer)
                print(f"[DATA] 成功回擊！收集 {len(self.data_buffer)} 筆。總計: {len(self.all_data)}")
            self.data_buffer = [] 
        
        elif hit_y: # 漏接
             self.data_buffer = []

        return command

    def reset(self):
        # ===== 6. 存檔邏輯 =====
        if self.side == "2P":
            self.data_buffer = [] # 丟棄未完成的
            
            if len(self.all_data) >= self.MIN_DATA_SIZE:
                save_path = os.path.join(os.path.dirname(__file__), "game_data_2Pnew.pickle")
                
                old = []
                if os.path.exists(save_path):
                    try:
                        with open(save_path, "rb") as f:
                            old = pickle.load(f)
                    except:
                        pass

                self.all_data = old + self.all_data
                try:
                    with open(save_path, "wb") as f:
                        pickle.dump(self.all_data, f)
                    print(f"[SAVE] 存檔完畢，目前共 {len(self.all_data)} 筆 (含特徵6)")
                except Exception as e:
                    print(f"[SAVE ERROR] {e}")
                
                self.all_data = []
            
        self.prev_ball = None
        return "RESET"
