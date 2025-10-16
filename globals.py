# 应用标题
appTitle = r"iphone镜像"

# 每隔多少秒更新一次ui
updateFramePerSecend = 0.2

# 每隔多少秒更新一次ocr
updateOcrPerSecend = 5

# 棋盘坐标
chessFivePos = {"X": 75, "Y": 408, "W": 436, "H": 767}
chessTenPos = {"X": 79, "Y": 412, "W": 436, "H": 767}
chessTwelvePos = {"X": 76, "Y": 414, "W": 433, "H": 769}
chessFifteenPos = {"X": 75, "Y": 409, "W": 435, "H": 767}

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
    "X": chessPos["X"] - 70,
    "Y": chessPos["Y"],
    "W": chessPos["X"],
    "H": chessPos["H"],
}
chessPosNumTintCol = {
    "X": chessPos["X"],
    "Y": chessPos["Y"] - 65,
    "W": chessPos["W"] - 2,
    "H": chessPos["Y"],
}

# 棋盘数字提示坐标的偏移
chessPosNumTintRowOffset = (
    chessPosNumTintRow["H"] - chessPosNumTintRow["Y"]
) / chessSize
chessPosNumTintColOffset = (
    chessPosNumTintCol["W"] - chessPosNumTintCol["X"]
) / chessSize

# 棋盘数字提示坐标的每一个格子
chessPosNumTintRowList = [
    {
        "X": chessPosNumTintRow["X"],
        "Y": chessPosNumTintRow["Y"] + i * chessPosNumTintRowOffset,
        "W": chessPosNumTintRow["W"],
        "H": chessPosNumTintRow["Y"]
        + chessPosNumTintRowOffset
        + i * chessPosNumTintRowOffset,
    }
    for i in range(chessSize)
]
chessPosNumTintColList = [
    {
        "X": chessPosNumTintCol["X"] + i * chessPosNumTintColOffset,
        "Y": chessPosNumTintCol["Y"],
        "W": chessPosNumTintCol["X"]
        + chessPosNumTintColOffset
        + i * chessPosNumTintColOffset,
        "H": chessPosNumTintCol["H"],
    }
    for i in range(chessSize)
]

# 横盘内的每一个格子的位置
chessPosEveryBlockGrid = [
    [
        {
            "X": chessPosNumTintCol["X"] + j * chessPosNumTintColOffset,
            "Y": chessPosNumTintRow["Y"] + i * chessPosNumTintRowOffset,
            "W": chessPosNumTintCol["X"] + (j + 1) * chessPosNumTintColOffset,
            "H": chessPosNumTintRow["Y"] + (i + 1) * chessPosNumTintRowOffset,
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
