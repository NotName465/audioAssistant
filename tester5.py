import subprocess


def is_sound_muted():
    """
    Проверяет, заглушен ли звук на ПК через PowerShell
    """
    try:
        # PowerShell команда для точной проверки mute статуса
        ps_command = """
        # Пробуем несколько способов определить mute статус
        $result = $false

        try {
            # Способ 1: Через AudioDevice командлет (если установлен)
            if (Get-Command Get-AudioDevice -ErrorAction SilentlyContinue) {
                $device = Get-AudioDevice -Playback
                if ($device.Mute -eq $true) {
                    $result = $true
                }
            }
        } catch {}

        if (-not $result) {
            try {
                # Способ 2: Через Windows API
                Add-Type -TypeDefinition @'
                using System;
                using System.Runtime.InteropServices;
                public class AudioMuteChecker {
                    [DllImport("winmm.dll")]
                    public static extern int waveOutGetVolume(IntPtr hwo, out uint dwVolume);

                    [DllImport("winmm.dll")] 
                    public static extern int waveOutSetVolume(IntPtr hwo, uint dwVolume);

                    public static bool IsSystemMuted() {
                        uint currentVolume;
                        int result = waveOutGetVolume(IntPtr.Zero, out currentVolume);

                        if (result == 0) {
                            // Сохраняем текущую громкость
                            uint savedVolume = currentVolume;

                            // Пробуем изменить громкость
                            uint testVolume = (savedVolume == 0) ? 0x50005000 : 0;
                            waveOutSetVolume(IntPtr.Zero, testVolume);

                            // Проверяем изменилась ли громкость
                            uint newVolume;
                            waveOutGetVolume(IntPtr.Zero, out newVolume);

                            // Восстанавливаем громкость
                            waveOutSetVolume(IntPtr.Zero, savedVolume);

                            // Если громкость не изменилась - вероятно muted
                            return newVolume == currentVolume;
                        }
                        return false;
                    }
                }
'@
                $result = [AudioMuteChecker]::IsSystemMuted()
            } catch {
                # Способ 3: Через реестр
                try {
                    $muteValue = Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Multimedia\\Audio" -Name "UserMute" -ErrorAction SilentlyContinue
                    if ($muteValue -ne $null) {
                        $result = [bool]$muteValue.UserMute
                    }
                } catch {}
            }
        }

        # Возвращаем результат
        if ($result) { "MUTED" } else { "UNMUTED" }
        """

        result = subprocess.run([
            "powershell", "-Command", ps_command
        ], capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            output = result.stdout.strip()
            return "MUTED" in output

        return False

    except Exception as e:
        print(f"Ошибка проверки mute: {e}")
        return False


# Альтернативная функция через анализ системных иконок
def is_sound_muted_icon():
    """
    Определяет mute статус по системной иконке звука (косвенный метод)
    """
    try:
        ps_command = """
        # Проверяем наличие иконки muted в системном трее
        Add-Type -TypeDefinition @'
        using System;
        using System.Runtime.InteropServices;
        using System.Diagnostics;
        public class SystemTrayChecker {
            [DllImport("user32.dll")]
            public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

            [DllImport("user32.dll")]
            public static extern IntPtr FindWindowEx(IntPtr hwndParent, IntPtr hwndChildAfter, string lpszClass, string lpszWindow);

            [DllImport("user32.dll", SetLastError = true)]
            public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);

            public static string CheckVolumeIcon() {
                try {
                    // Ищем окно системного трея
                    IntPtr systemTray = FindWindow("Shell_TrayWnd", null);
                    if (systemTray != IntPtr.Zero) {
                        IntPtr trayNotify = FindWindowEx(systemTray, IntPtr.Zero, "TrayNotifyWnd", null);
                        if (trayNotify != IntPtr.Zero) {
                            // Косвенный признак - если в названии процессов есть упоминание muted
                            Process[] processes = Process.GetProcesses();
                            foreach (Process p in processes) {
                                if (p.ProcessName.ToLower().Contains("audio") || 
                                    p.ProcessName.ToLower().Contains("sound") ||
                                    p.MainWindowTitle.ToLower().Contains("mute")) {
                                    return "MUTED";
                                }
                            }
                        }
                    }
                } catch {}
                return "UNMUTED";
            }
        }
'@
        [SystemTrayChecker]::CheckVolumeIcon()
        """

        result = subprocess.run([
            "powershell", "-Command", ps_command
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            output = result.stdout.strip()
            return "MUTED" in output

        return False

    except Exception as e:
        print(f"Ошибка проверки иконки: {e}")
        return False


# Универсальная функция
def check_mute_status():
    """
    Комбинированная проверка mute статуса
    """
    # Пробуем основной способ
    muted = is_sound_muted()

    # Если не уверены, пробуем альтернативный
    if not muted:
        muted_alt = is_sound_muted_icon()
        return muted_alt

    return muted


# Простой способ через тестовый звук
def is_sound_muted_simple():
    """
    Простая проверка через попытку воспроизведения звука
    """
    try:
        import winsound
        # Пробуем воспроизвести очень тихий звук
        winsound.Beep(37, 100)  # 37 Hz - почти неслышимый звук
        return False  # Если звук воспроизвелся - не muted
    except:
        return True  # Если ошибка - вероятно muted


# Использование
if __name__ == "__main__":
    print("=== Проверка статуса звука ===")

    print("1. Основной способ:", "🔇 MUTED" if is_sound_muted() else "🔊 UNMUTED")
    print("2. Через иконки:", "🔇 MUTED" if is_sound_muted_icon() else "🔊 UNMUTED")
    print("3. Тестовый звук:", "🔇 MUTED" if is_sound_muted_simple() else "🔊 UNMUTED")
    print("4. Комбинированный:", "🔇 MUTED" if check_mute_status() else "🔊 UNMUTED")