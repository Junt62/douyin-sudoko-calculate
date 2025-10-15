# 应用标题
appTitle = r"iphone镜像"

# 每隔多少秒更新一次ui
updateFramePerSecend = 0.2

# 每隔多少秒更新一次ocr
updateOcrPerSecend = 2

# 棋盘坐标
chessFivePos = {"X1": 75, "Y1": 408, "X2": 436, "Y2": 767}
chessTenPos = {"X1": 79, "Y1": 412, "X2": 436, "Y2": 767}
chessTwelvePos = {"X1": 76, "Y1": 414, "X2": 433, "Y2": 769}
chessFifteenPos = {"X1": 75, "Y1": 409, "X2": 435, "Y2": 767}

# 识别需要使用哪个坐标
chessPos = chessFifteenPos

# 横盘尺寸
POS_TO_SIZE = {
    id(chessFivePos): 5,
    id(chessTenPos): 10,
    id(chessTwelvePos): 12,
    id(chessFifteenPos): 15,
}
chessSize = POS_TO_SIZE.get(id(chessPos))

# 动态生成棋盘的数字提示坐标
chessPosNumTintRow = {
    "X1": chessPos["X1"],
    "Y1": chessPos["Y1"] - 65,
    "X2": chessPos["X2"] - 2,
    "Y2": chessPos["Y1"],
}
chessPosNumTintCol = {
    "X1": chessPos["X1"] - 70,
    "Y1": chessPos["Y1"],
    "X2": chessPos["X1"],
    "Y2": chessPos["Y2"],
}

# 棋盘数字提示坐标的偏移
chessPosNumTintRowOffset = (chessPosNumTintRow["X2"] - chessPosNumTintRow["X1"]) / chessSize
chessPosNumTintColOffset = (chessPosNumTintCol["Y2"] - chessPosNumTintCol["Y1"]) / chessSize

# 棋盘数字提示坐标的每一个格子
chessPosNumTintRowList = [
    {
        "X1": chessPosNumTintRow["X1"] + i * chessPosNumTintRowOffset,
        "Y1": chessPosNumTintRow["Y1"],
        "X2": chessPosNumTintRow["X1"] + chessPosNumTintRowOffset + i * chessPosNumTintRowOffset,
        "Y2": chessPosNumTintRow["Y2"],
    }
    for i in range(chessSize)
]
chessPosNumTintColList = [
    {
        "X1": chessPosNumTintCol["X1"],
        "Y1": chessPosNumTintCol["Y1"] + i * chessPosNumTintColOffset,
        "X2": chessPosNumTintCol["X2"],
        "Y2": chessPosNumTintCol["Y1"] + chessPosNumTintColOffset + i * chessPosNumTintColOffset,
    }
    for i in range(chessSize)
]

# 横盘内的每一个格子的位置
chessPosEveryBlockGrid = [
    [
        {
            "X1": chessPosNumTintRow["X1"] + j * chessPosNumTintRowOffset,
            "Y1": chessPosNumTintCol["Y1"] + i * chessPosNumTintColOffset,
            "X2": chessPosNumTintRow["X1"] + (j + 1) * chessPosNumTintRowOffset,
            "Y2": chessPosNumTintCol["Y1"] + (i + 1) * chessPosNumTintColOffset,
        }
        for j in range(chessSize)
    ]
    for i in range(chessSize)
]

# 绘制ui样式
appRangeBorderColor = (0.0, 1.0, 0.0)
appRangeBorderThickness = 4
appRangeBorderAlpha = 1
appRangeFillColor = (0.0, 1.0, 0.0)
appRangeFillAlpha = 0

# 绘制棋盘样式
chessRangeBorderColor = (0.0, 1.0, 0.0)
chessRangeBorderThickness = 1
chessRangeBorderAlpha = 1
chessRangeFillColor = (0.0, 1.0, 0.0)
chessRangeFillAlpha = 0

# 绘制棋盘数字提示样式
chessPosNumTintRangeBorderColor = (1.0, 0.0, 0.0)
chessPosNumTintRangeBorderThickness = 1
chessPosNumTintRangeBorderAlpha = 1

# 绘制棋盘数字提示坐标的每一个格子的样式
chessPosNumTintEveryRangeBorderColor = (0.0, 0.0, 1.0)
chessPosNumTintEveryRangeBorderThickness = 1
chessPosNumTintEveryRangeBorderAlpha = 1

# 绘制横盘内的每一个格子的样式
chessPosEveryBlockGridRangeBorderColor = (1, 1, 1)
chessPosEveryBlockGridRangeBorderColorTrue = (0, 1, 0)
chessPosEveryBlockGridRangeBorderColorFalse = (1, 0, 0)
chessPosEveryBlockGridRangeBorderThickness = 1
chessPosEveryBlockGridRangeBorderAlpha = 1
chessPosEveryBlockGridRangeFillColor = (1, 1, 1)
chessPosEveryBlockGridRangeFillColorTrue = (0, 1, 0)
chessPosEveryBlockGridRangeFillColorFalse = (1, 0, 0)
chessPosEveryBlockGridRangeFillAlpha = 0.3
