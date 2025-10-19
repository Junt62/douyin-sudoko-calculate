def nums_sort(data, direction="x"):
    """
    字典数组排序与合并

    Args:
        data: 字典数组，每个字典包含 name, X, Y, W, H
        direction: 'x' 或 'y'，指定排序方向（默认'x'）

    Returns:
        处理后的字典数组

    规则：
        X方向：
            1. 按X排序
            2. 用X+W判断合并
            3. 合并时：name拼接，X,Y用前一个，W,H使用合并后的W,H

        Y方向：
            1. 先按Y排序
            2. 判断Y值差距在±15以内，且X+W重叠，才合并
            3. 合并后，再按Y排序
            4. 合并时：name拼接，X,Y用前一个，W,H使用合并后的W,H
    """
    # 边界情况
    if not data or len(data) <= 1:
        return data

    # 标准化方向
    direction = direction.lower()
    if direction not in ["x", "y"]:
        raise ValueError("direction 必须是 'x' 或 'y'")

    # 设置排序键
    sort_key = "X" if direction == "x" else "Y"

    # 排序
    if direction == "x":
        sorted_data = sorted(data, key=lambda d: d[sort_key])
        # 合并（name拼接，被合并的元素删除）
        result = [sorted_data[0].copy()]
        # 确保 name 是字符串
        result[0]["name"] = str(result[0]["name"])

        for i in range(1, len(sorted_data)):
            current = sorted_data[i]
            previous = result[-1]

            # 判断是否重叠
            if current["X"] < previous["X"] + previous["W"]:
                result[-1] = {
                    "name": previous["name"] + str(current["name"]),  # 拼接 name
                    "X": previous["X"],
                    "Y": previous["Y"],
                    "W": current["X"] + current["W"] - previous["X"],
                    "H": current["Y"] + current["H"] - previous["Y"],
                }
                # 被合并的元素自动不会加入 result，相当于被删除
            else:
                # 不重叠，添加新元素
                new_item = current.copy()
                new_item["name"] = str(new_item["name"])  # 确保是字符串
                result.append(new_item)

        return result

    else:  # direction == 'y'
        # Y方向：先按Y排序，判断Y差距±15且X+W重叠才合并，合并后再按Y排序

        # 步骤1：按Y排序
        sorted_data = sorted(data, key=lambda d: d["X"])
        # 步骤2：合并（Y差距±15以内 且 X+W重叠）
        result = [sorted_data[0].copy()]
        # 确保 name 是字符串
        result[0]["name"] = str(result[0]["name"])

        for i in range(1, len(sorted_data)):
            current = sorted_data[i]
            previous = result[-1]

            # 计算Y值差距
            y_diff = abs(current["Y"] - previous["Y"])

            # 判断X+W是否重叠
            x_overlap = current["X"] < previous["X"] + previous["W"]

            # Y差距在15以内 且 X重叠，才合并
            if y_diff <= 15 and x_overlap:
                result[-1] = {
                    "name": previous["name"] + str(current["name"]),
                    "X": previous["X"],
                    "Y": previous["Y"],
                    "W": current["X"] + current["W"] - previous["X"],
                    "H": current["Y"] + current["H"] - previous["Y"],
                }
            else:
                new_item = current.copy()
                new_item["name"] = str(new_item["name"])
                result.append(new_item)

        # 步骤3：合并后再按Y排序
        result = sorted(result, key=lambda d: d["Y"])

        return result


def dict2list(dict_list, key):
    """
    将字典列表中指定键的逗号分隔字符串转换为二维整数数组

    参数:
        dict_list: 字典列表
        key: 要提取的键名

    返回:
        二维整数列表
    """
    return [[int(item[key]) for item in row] for row in dict_list]
