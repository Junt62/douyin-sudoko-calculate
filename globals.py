from types import MappingProxyType
from AppKit import NSScreen


class Globals:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Globals, cls).__new__(cls)
            cls._instance._initialize_constants()
            return cls._instance

    def _initialize_constants(self):
        # 应用标题
        self.APP_TITLE = r"iphone镜像"

        # 每隔多少秒更新一次ui
        self.UPDATE_UI_FPS = 0.2

        # 每隔多少秒更新一次ocr
        self.UPDATE_OCR_FPS = 5

        # 显示器缩放比例
        self.scale_factor = NSScreen.mainScreen().backingScaleFactor()
        self.scale_factor = 1

        # 棋盘逻辑坐标
        self.CHESS_POS_FIVE_LOGIC = MappingProxyType(
            {"X": 75, "Y": 408, "W": 436, "H": 767}
        )
        self.CHESS_POS_TEN_LOGIC = MappingProxyType(
            {"X": 79, "Y": 412, "W": 436, "H": 767}
        )
        self.CHESS_POS_TWELVE_LOGIC = MappingProxyType(
            {"X": 76, "Y": 414, "W": 433, "H": 769}
        )
        self.CHESS_POS_FIFTEEN_LOGIC = MappingProxyType(
            {"X": 75, "Y": 409, "W": 435, "H": 767}
        )

        # 棋盘真实坐标
        self.CHESS_POS_FIVE_REALITY = MappingProxyType(
            {
                key: value * self.scale_factor
                for key, value in self.CHESS_POS_FIVE_LOGIC.items()
            }
        )
        self.CHESS_POS_TEN_REALITY = MappingProxyType(
            {
                key: value * self.scale_factor
                for key, value in self.CHESS_POS_TEN_LOGIC.items()
            }
        )
        self.CHESS_POS_TWELVE_REALITY = MappingProxyType(
            {
                key: value * self.scale_factor
                for key, value in self.CHESS_POS_TWELVE_LOGIC.items()
            }
        )
        self.CHESS_POS_FIFTEEN_REALITY = MappingProxyType(
            {
                key: value * self.scale_factor
                for key, value in self.CHESS_POS_FIFTEEN_LOGIC.items()
            }
        )

        # 棋盘格子的行列数
        self.CHESS_GRID_NUM_GROUP = MappingProxyType(
            {
                id(self.CHESS_POS_FIVE_LOGIC): 5,
                id(self.CHESS_POS_FIVE_REALITY): 5,
                id(self.CHESS_POS_TEN_LOGIC): 10,
                id(self.CHESS_POS_TEN_REALITY): 10,
                id(self.CHESS_POS_TWELVE_LOGIC): 12,
                id(self.CHESS_POS_TWELVE_REALITY): 12,
                id(self.CHESS_POS_FIFTEEN_LOGIC): 15,
                id(self.CHESS_POS_FIFTEEN_REALITY): 15,
            }
        )

        # 识别棋盘尺寸
        self.chess_size = self.CHESS_POS_FIFTEEN_REALITY

        # 从棋盘尺寸获棋盘位置
        self.chess_grid_pos = self.chess_size

        # 棋盘尺寸获棋盘行数与列数
        self.chess_grid_num = self.CHESS_GRID_NUM_GROUP.get(id(self.chess_size))

        # 棋盘提示数字的坐标
        self.mark_row_pos = {
            "X": self.chess_grid_pos["X"] - 70,
            "Y": self.chess_grid_pos["Y"],
            "W": self.chess_grid_pos["X"],
            "H": self.chess_grid_pos["H"],
        }

        self.mark_col_pos = {
            "X": self.chess_grid_pos["X"],
            "Y": self.chess_grid_pos["Y"] - 52,
            "W": self.chess_grid_pos["W"] - 2,
            "H": self.chess_grid_pos["Y"],
        }

        # 棋盘提示数字的坐标的列表的偏移
        self.mark_row_pos_list_offset = (
            self.mark_row_pos["H"] - self.mark_row_pos["Y"]
        ) / self.chess_grid_num
        self.mark_col_pos_list_offset = (
            self.mark_col_pos["W"] - self.mark_col_pos["X"]
        ) / self.chess_grid_num

        # 棋盘提示数字的坐标的列表
        self.mark_row_pos_list = [
            {
                "X": int(self.mark_row_pos["X"]) * self.scale_factor,
                "Y": int(self.mark_row_pos["Y"] + i * self.mark_row_pos_list_offset)
                * self.scale_factor,
                "W": int(self.mark_row_pos["W"]) * self.scale_factor,
                "H": int(
                    self.mark_row_pos["Y"]
                    + self.mark_row_pos_list_offset
                    + i * self.mark_row_pos_list_offset
                )
                * self.scale_factor,
            }
            for i in range(self.chess_grid_num)
        ]

        self.mark_col_pos_list = [
            {
                "X": int(self.mark_col_pos["X"] + i * self.mark_col_pos_list_offset)
                * self.scale_factor,
                "Y": int(self.mark_col_pos["Y"]) * self.scale_factor,
                "W": int(
                    self.mark_col_pos["X"]
                    + self.mark_col_pos_list_offset
                    + i * self.mark_col_pos_list_offset
                )
                * self.scale_factor,
                "H": int(self.mark_col_pos["H"]) * self.scale_factor,
            }
            for i in range(self.chess_grid_num)
        ]

        # 棋盘内的每一个格子的位置
        self.chess_block_pos = [
            [
                {
                    "X": self.mark_col_pos["X"] + j * self.mark_col_pos_list_offset,
                    "Y": self.mark_row_pos["Y"] + i * self.mark_row_pos_list_offset,
                    "W": self.mark_col_pos["X"]
                    + (j + 1) * self.mark_col_pos_list_offset,
                    "H": self.mark_row_pos["Y"]
                    + (i + 1) * self.mark_row_pos_list_offset,
                }
                for j in range(self.chess_grid_num)
            ]
            for i in range(self.chess_grid_num)
        ]

    # 绘制ui样式
    APP_BORDER_COLOR = (0.0, 1.0, 0.0)
    APP_BORDER_THICKNESS = 4
    APP_BORDER_ALPHA = 1
    APP_FILL_COLOR = (0.0, 1.0, 0.0)
    APP_FILL_ALPHA = 0

    # 绘制棋盘样式
    CHESS_BORDER_COLOR = (0.0, 1.0, 0.0)
    CHESS_BORDER_THICKNESS = 1
    CHESS_BORDER_ALPHA = 1
    CHESS_FILL_COLOR = (0.0, 1.0, 0.0)
    CHESS_FILL_ALPHA = 0

    # 绘制棋盘数字提示样式
    MARK_BORDER_COLOR = (1.0, 0.0, 0.0)
    MARK_BORDER_THICKNESS = 1
    MARK_BORDER_ALPHA = 1

    # 绘制棋盘数字提示坐标的每一个格子的样式
    MARK_BLOCK_BORDER_COLOR = (0.0, 0.0, 1.0)
    MARK_BLOCK_BORDER_THICKNESS = 1
    MARK_BLOCK_BORDER_ALPHA = 1

    # 绘棋盘内的每一个格子的样式
    CHESS_BLOCK_BORDER_COLOR = (1, 1, 1)
    CHESS_BLOCK_BORDER_COLOR_TRUE = (0, 1, 0)
    CHESS_BLOCK_BORDER_COLOR_FALSE = (1, 0, 0)
    CHESS_BLOCK_BORDER_THICKNESS = 1
    CHESS_BLOCK_BORDER_ALPHA = 1
    CHESS_BLOCK_FILL_COLOR = (1, 1, 1)
    CHESS_BLOCK_FILL_COLOR_TRUE = (0, 1, 0)
    CHESS_BLOCK_FILL_COLOR_FALSE = (1, 0, 0)
    CHESS_BLOCK_ALPHA = 0.3
