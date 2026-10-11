import os
import subprocess

desktop = os.path.expanduser("~/Desktop")
ps_content = f'''$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{desktop}\\Amar Hisab.lnk")
$Shortcut.TargetPath = "C:\\xampp\\htdocs\\amar-hisab\\Amar_Hisab.bat"
$Shortcut.WorkingDirectory = "C:\\xampp\\htdocs\\amar-hisab"
$Shortcut.Description = "Amar Hisab Billing Software"
$Shortcut.Save()
'''

ps_file = os.path.abspath("make_shortcut.ps1")
with open(ps_file, "w", encoding="utf-8-sig") as f:
    f.write(ps_content)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file], capture_output=True, text=True)
if os.path.exists(ps_file):
    os.remove(ps_file)

lnk_file = os.path.join(desktop, "Amar Hisab.lnk")
print("Shortcut created:", os.path.exists(lnk_file))
