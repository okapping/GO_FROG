import platform
# from js はEmscripten環境以外では例外発生するのでcatchして環境を判定する
try:
    from js import navigator
    is_web_launcher = True
except ImportError:
    is_web_launcher = False

class DeviceChecker:
    def __init__(self):
        if is_web_launcher:
            # Web launcherから起動している場合、js関数でOS判定する
            self.user_agent = navigator.userAgent.lower()
            self.os_pc = not ("android" in self.user_agent or "iphone" in self.user_agent or "ipad" in self.user_agent)
        else:
            # ローカルから起動している場合、platformから判定する
            self.os_name = platform.system()
            self.os_pc =  self.os_name == "Windows" or self.os_name == "Darwin" or self.os_name == "Linux"

    def is_pc(self):
        return self.os_pc

    def is_web_launcher(self):
        return is_web_launcher
