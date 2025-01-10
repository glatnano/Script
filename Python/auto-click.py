#!/usr/bin/env python
import pyautogui
import time
from pynput import keyboard
import os
import subprocess
import threading

# Global değişkenler
stop_macro = False  # Makroyu durdurma kontrolü


# Z tuşunu dinlemek için bir iş parçacığı oluştur
def start_stop_listener():
    global stop_macro

    def on_press(key):
        global stop_macro
        if key == keyboard.KeyCode.from_char('z'):  # z tuşu
            print("\nMakro durduruluyor...")
            stop_macro = True
            return False  # Dinleyiciyi durdur

    # Dinleyiciyi başlat
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# Hareketleri bir txt dosyasından yükleme
def load_from_file():
    print("\n1: $HOME/App/mac/ dizininde ara")
    print("2: Kodun çalıştığı dizinde ara")

    while True:
        choice = input("Seçiminiz (1 veya 2, çıkmak için 'q'): ")
        if choice == "q":
            return None, None  # Ana menüye dön
        elif choice == "1":
            search_dir = os.path.join(os.path.expanduser("~"), "App", "mac")
            break
        elif choice == "2":
            search_dir = os.getcwd()
            break
        else:
            print("Geçersiz seçim. Lütfen 1 veya 2 girin.")

    macro_name = input("Yüklemek istediğiniz makronun ismini girin (çıkmak için 'q'): ").strip()
    if macro_name == "q":
        return None, None

    filepath = os.path.join(search_dir, f"{macro_name}.txt")
    if not os.path.exists(filepath):
        print(f"'{macro_name}' adlı makro {search_dir} dizininde bulunamadı. Tekrar deneyin.")
        return None, None

    actions = []
    wait_times = []
    with open(filepath, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if parts[0] == "click":
                actions.append(("click", int(parts[1]), int(parts[2])))
                wait_times.append(float(parts[3]))
    print(f"Makro '{macro_name}' başarıyla yüklendi.")
    return actions, wait_times


# Hareketleri kaydetme
def record():
    actions = []  # Tıklama hareketlerini kaydetmek için
    wait_times = []  # Bekleme sürelerini kaydetmek için
    print("Shift tuşuna basarak fare konumlarını kaydedin. Süreyi ayarlamak için 'Tab' tuşuna basın. Çıkmak için 'Esc' tuşuna basın.")

    recording = True

    def on_press(key):
        nonlocal recording
        try:
            if key == keyboard.Key.shift:  # Shift tuşu
                x, y = pyautogui.position()
                actions.append(("click", x, y))
                print(f"Tıklama kaydedildi: ({x}, {y})")
                time.sleep(0.2)  # Birden fazla algılamayı önlemek için kısa bekleme

            elif key == keyboard.Key.tab:  # Tab tuşu
                for i, action in enumerate(actions):
                    if len(wait_times) <= i:  # Eğer bekleme süresi tanımlanmadıysa sor
                        while True:
                            wait_time_input = input(f"Tıklama {i + 1} ({action[1]}, {action[2]}) için bekleme süresi (saniye) girin (Varsayılan: 0.1): ")
                            try:
                                if wait_time_input == "":
                                    wait_time = 0.1
                                else:
                                    wait_time = float(wait_time_input)
                                wait_times.append(wait_time)
                                print(f"Tıklama {i + 1} için bekleme süresi ayarlandı: {wait_time} saniye")
                                break
                            except ValueError:
                                print("Lütfen geçerli bir sayı girin.")

            elif key == keyboard.Key.esc:  # Esc tuşu
                print("Kayıt işlemi durduruldu.")
                recording = False
                return False

        except AttributeError:
            pass

    # Klavye dinleyicisini başlat
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    return actions, wait_times


# Hareketleri kaydetme
def save_to_file(actions, wait_times):
    macro_name = input("Makro için bir isim girin (çıkmak için 'q'): ").strip()
    if macro_name == "q":
        return

    print("\n1: Dosyayı $HOME/App/mac/ dizinine kaydet")
    print("2: Dosyayı kodun çalıştığı dizine kaydet")

    while True:
        choice = input("Seçiminiz (1 veya 2, çıkmak için 'q'): ")
        if choice == "q":
            return
        elif choice == "1":
            save_dir = os.path.join(os.path.expanduser("~"), "App", "mac")
            os.makedirs(save_dir, exist_ok=True)
            break
        elif choice == "2":
            save_dir = os.getcwd()
            break
        else:
            print("Geçersiz seçim. Lütfen 1 veya 2 girin.")

    filename = os.path.join(save_dir, f"{macro_name}.txt")
    with open(filename, "w") as file:
        for i in range(len(actions)):
            action = actions[i]
            wait_time = wait_times[i]
            file.write(f"{action[0]},{action[1]},{action[2]},{wait_time}\n")
    print(f"Makro '{macro_name}' olarak '{filename}' dizinine kaydedildi.")


# Kaydedilen hareketleri oynatma
def play(actions, wait_times):
    global stop_macro
    stop_macro = False

    listener_thread = threading.Thread(target=start_stop_listener, daemon=True)
    listener_thread.start()

    while True:
        try:
            repeat_count = int(input("Makroyu kaç kez tekrarlamak istiyorsunuz? (1-999, çıkmak için 'q'): "))
            if 1 <= repeat_count <= 999:
                break
            else:
                print("Lütfen 1 ile 999 arasında bir sayı girin.")
        except ValueError:
            print("Geçersiz giriş.")

    print(f"Makro {repeat_count} kez oynatılıyor...")
    for repeat in range(repeat_count):
        if stop_macro:
            print("Makro oynatma durduruldu.")
            break
        print(f"\nTekrar {repeat + 1} / {repeat_count}")
        for i, action in enumerate(actions):
            if stop_macro:
                break
            if action[0] == "click":
                x, y = action[1], action[2]
                pyautogui.click(x, y)
                time.sleep(wait_times[i])
    print("Makro oynatma tamamlandı.")


# Ana menü
actions, wait_times = None, None
while True:
    subprocess.run("clear", shell=True)
    print("\n1: Kayıt Başlat\n2: Kaydedilenleri Oynat\n3: Makro Kaydet\n4: Makro Yükle\n5: Çıkış")
    choice = input("Seçiminiz: ")
    if choice == "1":
        actions, wait_times = record()
    elif choice == "2":
        if actions and wait_times:
            play(actions, wait_times)
        else:
            print("Önce bir makro kaydedin veya yükleyin.")
            time.sleep(2)
    elif choice == "3":
        if actions and wait_times:
            save_to_file(actions, wait_times)
        else:
            print("Önce bir makro kaydedin.")
            time.sleep(2)
    elif choice == "4":
        actions, wait_times = load_from_file()
    elif choice == "5":
        print("Çıkış yapılıyor...")
        break
    else:
        print("Geçersiz seçim.")
