from pycaw.pycaw import AudioUtilities


def set_volume_simple(percent):
    """Упрощенная установка громкости через сессии"""
    try:
        sessions = AudioUtilities.GetAllSessions()

        for session in sessions:
            # Устанавливаем громкость для всех сессий
            if hasattr(session, 'SimpleAudioVolume'):
                volume_level = percent / 100.0
                session.SimpleAudioVolume.SetMasterVolume(volume_level, None)

        print(f"Громкость установлена на {percent}%")
        return True

    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def get_volume_simple():
    """Упрощенное получение громкости"""
    try:
        sessions = AudioUtilities.GetAllSessions()
        ses = AudioUtilities.GetAudioSessionManager()
        print(ses)
        for session in sessions:
            print(session)
            if hasattr(session, 'SimpleAudioVolume'):
                volume = session.SimpleAudioVolume.GetMasterVolume()
                return int(volume * 100)

        return None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None
print(get_volume_simple())