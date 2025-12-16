import pickle
import os

class MLPlay:
    """
    PAIA 乒乓球 AI：精確落點預測 + 成功軌跡數據收集
    目標：收集 (球位置/速度, 板子位置/速度) -> (板子動作) 的訓練數據。
    """
    def __init__(self, ai_name, *args, **kwargs):
        print(f"[AI INIT] Side = {ai_name}")
        self.side = ai_name

        # 遊戲常數 (依據 MLGame 標準設定)
        self.W = 200
        self.H = 500
        self.PLAT_W = 40
        self.PLAT_H = 30
        self.BALL_SIZE = 5

        # 內部狀態
        self.prev_ball = None # 上一幀的球位置 (x, y)
        self.prev_plat_x = None # 上一幀的板子 X 座標
        self.data_buffer = [] # 暫存「目前這一顆球」的軌跡 (成功接住才會被儲存)
        self.all_data = []    # 累積「確定有接到」的成功軌跡
        self.SPEED_NORM = 50.0 # 球速歸一化因子 (假設最大速度為 50)
        self.PLAT_SPEED_NORM = 10.0 # 板速歸一化因子 (假設板子最大移動速度)
        self.MIN_DATA_SIZE = 1000 # 數據寫入硬碟的閾值

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

        # ===== 1. 計算球速 (vx, vy) 與板速 (v_plat_x) =====
        if self.prev_ball is None or self.prev_plat_x is None:
            vx, vy, v_plat_x = 0, 0, 0
        else:
            vx = ball_x - self.prev_ball[0]
            vy = ball_y - self.prev_ball[1]
            v_plat_x = plat_x - self.prev_plat_x
            
        self.prev_ball = (ball_x, ball_y)
        self.prev_plat_x = plat_x # 記錄當前板子位置供下一幀計算

        # ===== 2. 判斷上下板與球路方向 =====
        is_bottom = plat_y > self.H / 2
        is_top = not is_bottom
        incoming = (is_bottom and vy > 0) or (is_top and vy < 0)

        # ===== 3. 策略與動作控制 (使用您原有的精確預測策略) =====
        if not incoming or vy == 0:
            target_x = self.W / 2
        else:
            steps = (plat_y - ball_y) / vy
            pred_x = ball_x + vx * steps
            
            # 牆壁反彈補償
            cycle = int(pred_x // self.W)
            remain = pred_x % self.W
            target_x = remain if (cycle % 2 == 0) else self.W - remain
        
        # 動作控制
        plat_center = plat_x + self.PLAT_W / 2
        if plat_center < target_x - 3:
            command = "MOVE_RIGHT"
            action_code = 2  # 動作標籤: 右移
        elif plat_center > target_x + 3:
            command = "MOVE_LEFT"
            action_code = 1  # 動作標籤: 左移
        else:
            command = "NONE"
            action_code = 0  # 動作標籤: 不移動 (或發射/停止)

        # ===== 4. 收集訓練資料 (重點優化部分) =====
        if vx != 0 or vy != 0:
            # 訓練輸入狀態 (State Vector):
            # [球 X/W, 球 Y/H, 球 VX/NORM, 球 VY/NORM, 板子 X/W, 板子 VX/PLAT_NORM]
            state = [
                ball_x / self.W,
                ball_y / self.H,
                vx / self.SPEED_NORM,
                vy / self.SPEED_NORM,
                plat_x / self.W,
                v_plat_x / self.PLAT_SPEED_NORM,
            ]
            
            # 訓練輸出標籤 (Action Label):
            # [action_code]
            
            self.data_buffer.append([state, action_code])
        
        # ===== 5. 偵測「接到球」並存入成功資料 =====
        # 這裡的邏輯是為了確保只收集「成功」的軌跡。
        hit_x = (ball_x + self.BALL_SIZE >= plat_x) and (ball_x <= plat_x + self.PLAT_W)
        
        # Y 軸接觸判定: 判斷球是否在板子的厚度範圍內
        if is_bottom:
            # 下板: 球的底部 (y + size) 觸碰到板子的頂部 (plat_y)
            hit_y = (ball_y + self.BALL_SIZE >= plat_y) and (ball_y <= plat_y + self.PLAT_H)
        else:
            # 上板: 球的頂部 (y) 觸碰到板子的底部 (plat_y + plat_H)
            hit_y = (ball_y >= plat_y) and (ball_y <= plat_y + self.PLAT_H)

        if hit_x and hit_y and incoming: # 確保是在球朝向板子時發生碰撞
            # 將暫存區這一段成功的軌跡，正式加入訓練資料
            if len(self.data_buffer) > 0:
                self.all_data.extend(self.data_buffer)
                print(f"[DATA] 接到球並存入 {len(self.data_buffer)} 幀成功軌跡。累積: {len(self.all_data)}")
            
            self.data_buffer = [] # 清空暫存，準備記錄下一段軌跡

        return command

    def reset(self):
        print(f"[RESET] Game Ended. 丟棄 {len(self.data_buffer)} 幀失敗軌跡。")

        # 遊戲結束時，data_buffer 裡的是漏接的軌跡，全部丟棄
        self.data_buffer = []
        self.prev_ball = None
        self.prev_plat_x = None

        # ==== 存檔 (只存 all_data 裡確定成功的資料) ====
        if len(self.all_data) >= self.MIN_DATA_SIZE:
            # 建議將檔案命名加入 side，避免 1P 和 2P 互相覆蓋
            save_path = os.path.join(os.path.dirname(__file__), f"game_data_{self.side}.pickle")
            
            old = []
            if os.path.exists(save_path):
                try:
                    with open(save_path, "rb") as f:
                        old = pickle.load(f)
                except:
                    pass

            # 合併舊檔並寫入
            self.all_data = old + self.all_data
            try:
                with open(save_path, "wb") as f:
                    pickle.dump(self.all_data, f)
                print(f"[SAVE] 成功寫入 {len(self.all_data)} 筆資料到 {save_path}")
            except Exception as e:
                print(f"[SAVE ERROR] {e}")
            
            self.all_data = []
