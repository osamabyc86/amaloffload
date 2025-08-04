import json
import os
import platform
from pathlib import Path

class AutoStartManager:
    def __init__(self, app_name="DistributedTaskSystem"):
        self.app_name = app_name
        self.config_file = Path.home() / f".{app_name}_autostart.json"
        self.load_config()
    
    def load_config(self):
        """تحميل إعدادات التشغيل التلقائي"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                'enabled': False,
                'startup_script': str(Path(__file__).parent / "startup.py")
            }
    
    def save_config(self):
        """حفظ الإعدادات"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def enable_autostart(self):
        """تفعيل التشغيل التلقائي"""
        self.config['enabled'] = True
        self._setup_autostart()
        self.save_config()
    
    def disable_autostart(self):
        """تعطيل التشغيل التلقائي"""
        self.config['enabled'] = False
        self._remove_autostart()
        self.save_config()
    
    def _setup_autostart(self):
        """إعداد التشغيل التلقائي حسب نظام التشغيل"""
        system = platform.system()
        
        if system == "Windows":
            self._setup_windows()
        elif system == "Linux":
            self._setup_linux()
        elif system == "Darwin":
            self._setup_mac()
    
    def _setup_windows(self):
        """إعداد التشغيل التلقائي لـ Windows"""
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(
            key, self.app_name, 0, winreg.REG_SZ,
            f'python "{self.config["startup_script"]}"'
        )
        winreg.CloseKey(key)
    
    def _setup_linux(self):
        """إعداد التشغيل التلقائي لـ Linux"""
        autostart_dir = Path.home() / ".config/autostart"
        autostart_dir.mkdir(exist_ok=True)
        
        desktop_file = autostart_dir / f"{self.app_name}.desktop"
        desktop_file.write_text(f"""
        [Desktop Entry]
        Type=Application
        Name={self.app_name}
        Exec=python3 {self.config['startup_script']}
        Terminal=false
        """)
    
    def _setup_mac(self):
        """إعداد التشغيل التلقائي لـ macOS"""
        plist_dir = Path.home() / "Library/LaunchAgents"
        plist_dir.mkdir(exist_ok=True)
        
        plist_file = plist_dir / f"com.{self.app_name.lower()}.plist"
        plist_file.write_text(f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.{self.app_name.lower()}</string>
            <key>ProgramArguments</key>
            <array>
                <string>python</string>
                <string>{self.config['startup_script']}</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
        </dict>
        </plist>
        """)
    
    def _remove_autostart(self):
        """إزالة التشغيل التلقائي"""
        system = platform.system()
        
        if system == "Windows":
            import winreg
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.DeleteValue(key, self.app_name)
                winreg.CloseKey(key)
            except WindowsError:
                pass
        
        elif system == "Linux":
            autostart_file = Path.home() / f".config/autostart/{self.app_name}.desktop"
            if autostart_file.exists():
                autostart_file.unlink()
        
        elif system == "Darwin":
            plist_file = Path.home() / f"Library/LaunchAgents/com.{self.app_name.lower()}.plist"
            if plist_file.exists():
                plist_file.unlink()
