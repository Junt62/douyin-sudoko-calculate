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
        # 步骤1：先按Y排序，将Y值接近的分组
        sorted_by_y = sorted(data, key=lambda d: d["Y"])

        # 步骤2：按Y值分组（Y差距超过阈值就新建一组）
        y_threshold = 15  # Y值差距阈值
        groups = []
        current_group = [sorted_by_y[0]]

        for i in range(1, len(sorted_by_y)):
            current = sorted_by_y[i]
            previous = sorted_by_y[i - 1]

            # 如果Y值差距过大，创建新组
            if abs(current["Y"] - previous["Y"]) > y_threshold:
                groups.append(current_group)
                current_group = [current]
            else:
                current_group.append(current)

        # 添加最后一组
        groups.append(current_group)

        # 步骤3：在每组内按X排序并合并
        result = []
        for group in groups:
            # 组内按X排序
            sorted_group = sorted(group, key=lambda d: d["X"])

            # 组内合并（X+W重叠的合并）
            group_result = [sorted_group[0].copy()]
            group_result[0]["name"] = str(group_result[0]["name"])

            for i in range(1, len(sorted_group)):
                current = sorted_group[i]
                previous = group_result[-1]

                # 判断X+W是否重叠
                x_overlap = current["X"] - 8 < previous["X"] + previous["W"]

                # 同组内且X重叠，才合并
                if x_overlap:
                    group_result[-1] = {
                        "name": previous["name"] + str(current["name"]),
                        "X": previous["X"],
                        "Y": previous["Y"],
                        "W": current["X"] + current["W"] - previous["X"],
                        "H": max(
                            previous["Y"] + previous["H"], current["Y"] + current["H"]
                        )
                        - previous["Y"],
                    }
                else:
                    new_item = current.copy()
                    new_item["name"] = str(new_item["name"])
                    group_result.append(new_item)

            result.extend(group_result)

        # 步骤4：最终按Y排序（保持组的顺序）
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
