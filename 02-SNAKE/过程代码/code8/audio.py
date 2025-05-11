import threading
import time
import traceback
import pyaudio
import audioop
from config import *

class AudioInput:
    def __init__(self):
        self.audio = None
        self.stream = None
        self.is_running = False
        self.current_volume = 0
        if AUDIO_AVAILABLE:
            self.setup_stream()

    def setup_stream(self):
        try:
            import pyaudio
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_RATE,
                input=True,
                frames_per_buffer=AUDIO_CHUNK
            )
            self.is_running = True
            threading.Thread(target=self.audio_loop, daemon=True).start()
            print("音频输入初始化成功")
        except Exception as e:
            print(f"音频输入初始化失败: {e}")
            print(traceback.format_exc())
            self.is_running = False
            if self.audio:
                self.audio.terminate()

    def audio_loop(self):
        while self.is_running:
            try:
                if self.stream and not self.stream.is_stopped():
                    data = self.stream.read(AUDIO_CHUNK, exception_on_overflow=False)
                    # 使用 audioop 计算音量
                    self.current_volume = audioop.rms(data, 2)  # 2 表示 2 字节采样
            except Exception as e:
                print(f"音频读取错误: {e}")
                time.sleep(0.1)

    def get_is_loud(self):
        """返回当前音量是否超过阈值"""
        if not self.is_running:
            return False
        return self.current_volume > AUDIO_THRESHOLD

    def cleanup(self):
        print("正在清理音频资源...")
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"关闭音频流时出错: {e}")
        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                print(f"终止音频系统时出错: {e}")
