from moviepy import VideoFileClip

# 載入影片
clip = VideoFileClip("6.mp4")

# 印出原始尺寸確認（可選）
print("原始尺寸：", clip.size)

# 裁切前 5 秒（可選）
clip = clip.subclipped(0, 5)

# 等比例縮放（可選）
new_width = 720
w, h = clip.size
new_height = int(h * new_width / w)
clip = clip.resized((new_width, new_height))

# 輸出為 GIF
clip.write_gif("output.gif", fps=10)
