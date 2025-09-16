import exifread

class deal_data:
    @staticmethod
    def photo(file_path):
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)

                # 检查是否存在GPS信息
                if 'GPS GPSLatitude' not in tags or 'GPS GPSLongitude' not in tags:
                    return {'error': '图片中未包含GPS信息'}

                def getLatOrLng(tags, refKey, tudeKey):
                    try:
                        # 获取方向（N/S/E/W）
                        ref = tags[refKey].printable

                        # 获取坐标值
                        tude = tags[tudeKey]

                        # 将坐标值转换为度分秒格式
                        degrees = float(tude.values[0].num) / float(tude.values[0].den)
                        minutes = float(tude.values[1].num) / float(tude.values[1].den)
                        seconds = float(tude.values[2].num) / float(tude.values[2].den)

                        # 计算十进制度数
                        LatOrLng = degrees + minutes / 60 + seconds / 3600

                        # 根据方向调整正负
                        if refKey == 'GPS GPSLatitudeRef' and ref != "N":
                            LatOrLng = LatOrLng * (-1)
                        if refKey == 'GPS GPSLongitudeRef' and ref != "E":
                            LatOrLng = LatOrLng * (-1)

                        return LatOrLng
                    except Exception as e:
                        print(f"Error processing {tudeKey}: {str(e)}")
                        return None

                lat = getLatOrLng(tags, 'GPS GPSLatitudeRef', 'GPS GPSLatitude')
                lng = getLatOrLng(tags, 'GPS GPSLongitudeRef', 'GPS GPSLongitude')

                if lat is None or lng is None:
                    return {'error': 'GPS坐标解析失败'}

                return {
                    'latitude': lat,
                    'longitude': lng
                }
        except Exception as e:
            return {'error': str(e)}




