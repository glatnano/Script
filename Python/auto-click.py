# Hareketleri kaydetme
def record():
    actions = []  # Tıklama hareketlerini kaydetmek için
    wait_times = []  # Bekleme sürelerini kaydetmek için
    print("Shift tuşuna basarak fare konumlarını kaydedin. Bekleme sürelerini ayarlamak için 'Tab' tuşuna basın. Çıkmak için 'Esc' tuşuna basın.")

    recording = True

    def on_press(key):
        nonlocal recording
        try:
            if key == keyboard.Key.shift:  # shift tuşu
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
                                    if wait_time < 0.1 or wait_time > 99999:
                                        print("Geçersiz değer, bekleme süresi 0.1 olarak ayarlandı.")
                                        wait_time = 0.1
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

# Hareketleri bir txt dosyasına kaydetme
def save_to_file(actions, wait_times):
    macro_name = input("Makro için bir isim girin (örn. macro1): ")

    # Kullanıcıya dosyanın nereye kaydedileceğini seçtirme
    print("\n1: Dosyayı $HOME/App/mac/ dizinine kaydet")
    print("2: Dosyayı kodun çalıştığı dizine kaydet")
    
    while True:
        choice = input("Seçiminiz (1 veya 2): ")
        if choice == "1":
            # $HOME/App/mac/ dizinine kaydetme
            home_dir = os.path.expanduser("~")  # Kullanıcının ev dizinini al
            save_dir = os.path.join(home_dir, "App", "mac")
            os.makedirs(save_dir, exist_ok=True)  # Dizini oluştur, zaten varsa hata verme
            break
        elif choice == "2":
            # Kodun çalıştığı dizine kaydetme
            save_dir = os.getcwd()  # Geçerli çalışma dizinini al
            break
        else:
            print("Geçersiz seçim. Lütfen 1 veya 2 girin.")
    
    # Dosya yolunu oluştur
    filename = os.path.join(save_dir, f"{macro_name}.txt")

    # Dosyayı yazma
    try:
        with open(filename, "w") as file:
            for i in range(len(actions)):
                action = actions[i]
                wait_time = wait_times[i]
                file.write(f"{action[0]},{action[1]},{action[2]},{wait_time}\n")
        print(f"Makro '{macro_name}' olarak '{filename}' dizinine kaydedildi.")
    except Exception as e:
        print(f"Dosya kaydedilirken bir hata oluştu: {e}")
# Kaydedilen hareketleri oynatma
def play(actions, wait_times):
    global stop_macro
    stop_macro = False  # Makroyu durdurma kontrolünü sıfırla

    # Z dinleyici iş parçacığını başlat
    listener_thread = threading.Thread(target=start_stop_listener, daemon=True)
    listener_thread.start()

    # Kullanıcı dan tekrar sayısını al
    while True:
        try:
            repeat_count = int(input("Makroyu kaç kez tekrarlamak istiyorsunuz? (1-999): "))
            if 1 <= repeat_count <= 999:
                break
            else:
                print("Lütfen 1 ile 999 arasında bir sayı girin.")
        except ValueError:
            print("Geçersiz giriş. Lütfen bir sayı girin.")

    # Makroyu tekrarlama
    print(f"Makro {repeat_count} kez oynatılıyor...")
    for repeat in range(repeat_count):
        if stop_macro:  # Durdurma kontrolü
            print("Makro oynatma durduruldu.")
            break
        print(f"\nTekrar {repeat + 1} / {repeat_count}")
        for i, action in enumerate(actions):
            if stop_macro:  # Durdurma kontrolü
                print("Makro oynatma durduruldu.")
                break
            if action[0] == "click":
                x, y = action[1], action[2]
                pyautogui.click(x, y)
                print(f"Tıklama {i + 1}: ({x}, {y}) | Bekleme süresi: {wait_times[i]} saniye")
                time.sleep(wait_times[i])
    print("Makro oynatma tamamlandı.")

# Kullanıcıya seçenek sun
while True:
    subprocess.run("clear", shell=True)
    print("\n1: Kayıt Başlat\n2: Kaydedilenleri Oynat\n3: Makroyu Kaydet (isimle kaydet)\n4: Çıkış")
    choice = input("Seçiminiz: ")
    if choice == '1':
        actions, wait_times = record()
    elif choice == '2':
        try:
            play(actions, wait_times)
        except NameError:
            print("Önce bir kayıt başlatmalısınız.")
            time.sleep(2)
    elif choice == '3':
        try:
            save_to_file(actions, wait_times)
        except NameError:
            print("Önce bir kayıt başlatmalısınız.")
            time.sleep(2)
    elif choice == '4':
        print("Çıkış yapılıyor...")
        break
    else:
        print("Geçersiz seçim.")
