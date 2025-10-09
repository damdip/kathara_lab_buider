#!/usr/bin/env python3
"""
Kathara Lab Creator - Versione semplificata
Crea file lab.conf per laboratori Kathara

Passo 1: Gestione dispositivi e creazione lab.conf
Passo 2: Creazione file .startup per ogni dispositivo
"""

import os
from pathlib import Path

def welcome():
    """Mostra messaggio di benvenuto"""
    print("=" * 50)
    print("🌐 KATHARA LAB CREATOR")
    print("=" * 50)
    print("Creatore semplificato per laboratori Kathara")
    print("Questo strumento ti aiuterà a creare il file lab.conf")
    print("e i file .startup per ogni dispositivo")
    print("=" * 50)
    print()

def show_existing_labs():
    """Mostra i laboratori già creati"""
    created_labs_dir = Path("created_labs")
    
    if created_labs_dir.exists():
        labs = [d.name for d in created_labs_dir.iterdir() if d.is_dir()]
        if labs:
            print("\n📚 Laboratori esistenti in created_labs/:")
            for lab in sorted(labs):
                print(f"   • {lab}")
        else:
            print("\n📚 Nessun laboratorio trovato in created_labs/")
    else:
        print("\n📚 Directory created_labs/ non esistente (verrà creata)")

def get_lab_name():
    """Chiede il nome del laboratorio"""
    while True:
        lab_name = input("Nome del laboratorio: ").strip()
        if lab_name:
            return lab_name
        print("❌ Il nome del laboratorio non può essere vuoto!")

def get_devices():
    """Chiede il numero di dispositivi e i loro nomi"""
    devices = []
    
    # Chiedi numero di dispositivi
    while True:
        try:
            num_devices = int(input("Quanti dispositivi vuoi nel laboratorio? "))
            if num_devices > 0:
                break
            else:
                print("❌ Devi avere almeno 1 dispositivo!")
        except ValueError:
            print("❌ Inserisci un numero valido!")
    
    print(f"\nOra inserisci i nomi dei {num_devices} dispositivi:")
    
    # Chiedi nome di ogni dispositivo
    for i in range(num_devices):
        while True:
            device_name = input(f"Nome dispositivo {i+1}: ").strip()
            
            # Verifica che il nome sia valido
            if not device_name:
                print("❌ Il nome non può essere vuoto!")
                continue
            
            # Verifica che non sia duplicato
            if device_name in devices:
                print("❌ Nome già esistente! Scegli un nome diverso.")
                continue
            
            # Verifica caratteri validi (solo lettere, numeri, underscore)
            if not device_name.replace('_', '').replace('-', '').isalnum():
                print("❌ Il nome può contenere solo lettere, numeri, - e _")
                continue
            
            devices.append(device_name)
            print(f"✅ Dispositivo '{device_name}' aggiunto")
            break
    
    return devices

def choose_device_type(device_name):
    """Chiede il tipo di dispositivo per scegliere l'immagine Docker"""
    print(f"\nChe tipo di dispositivo è '{device_name}'?")
    print("1. Router (kathara/quagga)")
    print("2. Host/PC (kathara/base)")
    print("3. Server DNS (kathara/bind)")
    print("4. Server Web (kathara/apache)")
    print("5. Router FRR (kathara/frr)")
    print("6. Personalizzato")
    
    images = {
        "1": "kathara/quagga",
        "2": "kathara/base", 
        "3": "kathara/bind",
        "4": "kathara/apache",
        "5": "kathara/frr"
    }
    
    while True:
        choice = input("Scegli tipo (1-6): ").strip()
        
        if choice in images:
            return images[choice]
        elif choice == "6":
            custom_image = input("Inserisci nome immagine Docker personalizzata: ").strip()
            if custom_image:
                return custom_image
            else:
                print("❌ Nome immagine non valido!")
        else:
            print("❌ Scelta non valida!")

def get_device_interfaces(device_name):
    """Chiede quante interfacce ha il dispositivo e i domini di collisione"""
    print(f"\n🔌 Configurazione interfacce per '{device_name}'")
    
    # Chiedi numero di interfacce
    while True:
        try:
            num_interfaces = int(input(f"Quante porte ethernet ha '{device_name}'? "))
            if num_interfaces >= 0:
                break
            else:
                print("❌ Il numero di interfacce non può essere negativo!")
        except ValueError:
            print("❌ Inserisci un numero valido!")
    
    interfaces = {}
    used_domains = set()
    
    # Per ogni interfaccia, chiedi il dominio di collisione
    for i in range(num_interfaces):
        print(f"\nInterfaccia eth{i} di '{device_name}':")
        
        while True:
            domain = input(f"Dominio di collisione per eth{i} (es. A, B, C...): ").strip().upper()
            
            # Verifica che non sia vuoto
            if not domain:
                print("❌ Il dominio di collisione non può essere vuoto!")
                continue
            
            # Verifica che sia un nome valido (lettere e numeri)
            if not domain.replace('_', '').replace('-', '').isalnum():
                print("❌ Il dominio può contenere solo lettere, numeri, - e _")
                continue
            
            # Suggerimento se non è una lettera maiuscola singola
            if len(domain) > 1 or not domain.isalpha():
                confirm = input(f"⚠️  Di solito si usano lettere singole (A, B, C...). Confermi '{domain}'? (s/N): ").strip().lower()
                if confirm != 's':
                    continue
            
            interfaces[i] = domain
            used_domains.add(domain)
            print(f"✅ eth{i} → {domain}")
            break
    
    return interfaces, used_domains

def create_lab_directory(lab_name):
    """Crea la directory del laboratorio dentro created_labs"""
    # Crea prima la directory principale created_labs se non esiste
    base_dir = Path("created_labs")
    base_dir.mkdir(exist_ok=True)
    
    # Crea il path completo del laboratorio
    lab_path = base_dir / lab_name
    
    # Se la directory esiste, chiedi conferma per sovrascriverla
    if lab_path.exists():
        print(f"⚠️  Directory 'created_labs/{lab_name}' già esistente!")
        overwrite = input("Vuoi sovrascriverla? (s/N): ").strip().lower()
        if overwrite != 's':
            print("❌ Operazione annullata.")
            return None
        
        # Rimuovi contenuto esistente
        import shutil
        shutil.rmtree(lab_path)
    
    # Crea la directory
    lab_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory 'created_labs/{lab_name}' creata")
    return lab_path

def create_lab_conf(lab_name, devices_info, lab_path):
    """Crea il file lab.conf nella directory del laboratorio"""
    filename = lab_path / "lab.conf"
    
    print(f"\n📁 Creando file lab.conf...")
    
    with open(filename, 'w', encoding='utf-8') as f:
               
        # Per ogni dispositivo, scrivi la configurazione
        for device_name, device_data in devices_info.items():
            image = device_data['image']
            interfaces = device_data['interfaces']
            
            # Se non è l'immagine di default, specificala
            if image != "kathara/base":
                f.write(f'{device_name}[image]="{image}"\n')
            
            # Configura le interfacce
            for eth_num, domain in interfaces.items():
                f.write(f'{device_name}[{eth_num}]="{domain}"\n')
            
            if interfaces:
                f.write(f"# {device_name} - Interfacce configurate\n")
            else:
                f.write(f"# {device_name} - Nessuna interfaccia configurata\n")
            f.write("\n")
    
    print(f"✅ File lab.conf creato!")
    return filename

def create_startup_files(devices_info, lab_path):
    """Crea i file .startup per ogni dispositivo"""
    print(f"\n🚀 Creando file .startup...")
    
    startup_files = []
    
    for device_name, device_data in devices_info.items():
        startup_filename = lab_path / f"{device_name}.startup"
        image = device_data['image']
        interfaces = device_data['interfaces']
        
        with open(startup_filename, 'w', encoding='utf-8') as f:
                        
            # Configurazione di base delle interfacce
            f.write("# Configurazione interfacce di rete\n")
            for eth_num, domain in interfaces.items():
                f.write(f"# eth{eth_num} collegata al dominio {domain}\n")
                f.write(f"# ip addr add <INDIRIZZO_IP>/<NETMASK> dev eth{eth_num}\n")
            
            if interfaces:
                f.write("\n")
        
        # Rendi il file eseguibile
        startup_filename.chmod(0o755)
        startup_files.append(startup_filename)
        print(f"✅ Creato {device_name}.startup")
    
    return startup_files

def show_generated_files(lab_path, devices_info):
    """Mostra il contenuto dei file generati"""
    print("\n" + "=" * 70)
    print("📄 CONTENUTO FILE GENERATI")
    print("=" * 70)
    
    # Mostra lab.conf
    lab_conf_path = lab_path / "lab.conf"
    if lab_conf_path.exists():
        print("\n🔧 CONTENUTO lab.conf:")
        print("-" * 50)
        with open(lab_conf_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        print("-" * 50)
    
    # Mostra i file .startup
    print("\n🚀 CONTENUTO FILE .startup:")
    print("-" * 50)
    
    for device_name in devices_info.keys():
        startup_path = lab_path / f"{device_name}.startup"
        if startup_path.exists():
            print(f"\n📄 File: {device_name}.startup")
            print("─" * 30)
            with open(startup_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
            print("─" * 30)
    
    print("\n" + "=" * 70)

def show_summary(lab_name, devices_info, all_domains):
    """Mostra un riassunto del laboratorio"""
    print("\n📊 RIASSUNTO LABORATORIO")
    print("=" * 50)
    print(f"Nome: {lab_name}")
    print(f"Numero dispositivi: {len(devices_info)}")
    print(f"Domini di collisione: {len(all_domains)}")
    print("\nDispositivi:")
    
    for device_name, device_data in devices_info.items():
        image = device_data['image']
        interfaces = device_data['interfaces']
        print(f"  • {device_name} ({image})")
        
        if interfaces:
            for eth_num, domain in interfaces.items():
                print(f"    └─ eth{eth_num} → {domain}")
        else:
            print(f"    └─ Nessuna interfaccia")
    
    if all_domains:
        print(f"\n📡 DOMINI DI COLLISIONE UTILIZZATI")
        print("-" * 35)
        for domain in sorted(all_domains):
            print(f"  • {domain}")
        print()
        print("💡 Ogni dominio di collisione rappresenta un segmento di rete")
        print("   Dispositivi nello stesso dominio possono comunicare direttamente")
    else:
        print("\n📡 Nessun dominio di collisione configurato")
        print("   (Tutti i dispositivi sono isolati)")
    
    print("=" * 50)

def main():
    """Funzione principale"""
    welcome()
    
    # Ottieni nome laboratorio
    lab_name = get_lab_name()
    
    # Crea directory del laboratorio
    lab_path = create_lab_directory(lab_name)
    if lab_path is None:
        return
    
    # Ottieni lista dispositivi
    devices = get_devices()
    
    # Per ogni dispositivo, chiedi il tipo e le interfacce
    devices_info = {}
    all_domains = set()
    
    print(f"\n🖥️  CONFIGURAZIONE DISPOSITIVI")
    print("-" * 35)
    
    for device in devices:
        print(f"\n--- Configurazione {device} ---")
        
        # Tipo di dispositivo
        image = choose_device_type(device)
        
        # Interfacce del dispositivo
        interfaces, device_domains = get_device_interfaces(device)
        
        # Salva informazioni dispositivo
        devices_info[device] = {
            'image': image,
            'interfaces': interfaces
        }
        
        # Aggiungi domini utilizzati
        all_domains.update(device_domains)
    
    # Mostra riassunto
    show_summary(lab_name, devices_info, all_domains)
    
    # Chiedi conferma
    confirm = input("\nVuoi creare i file del laboratorio? (S/n): ").strip().lower()
    if confirm != 'n':
        # Crea file lab.conf
        lab_conf_file = create_lab_conf(lab_name, devices_info, lab_path)
        
        # Crea file .startup
        startup_files = create_startup_files(devices_info, lab_path)
        
        
        print(f"\n🎉 Laboratorio '{lab_name}' creato!")
        print(f"📁 Directory: {lab_path.absolute()}")
        print("📄 File generati:")
        print(f"   • lab.conf")
        print(f"   • {len(startup_files)} file .startup")
        
        print("\nProssimi passi:")
        print("1. Modifica i file .startup per configurare gli IP")
        print("2. Entra nella directory del laboratorio:")
        print(f"   cd created_labs/{lab_name}")
        print("3. Avvia il laboratorio:")
        print("   kathara lstart")
        print("4. Per fermarlo:")
        print("   kathara lclean")
        
        # Chiedi se mostrare il contenuto dei file
        show_files = input("\nVuoi vedere il contenuto dei file generati? (S/n): ").strip().lower()
        if show_files != 'n':
            show_generated_files(lab_path, devices_info)
        
    else:
        print("\n👋 Operazione annullata.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Uscita dal programma. Arrivederci!")
    except Exception as e:
        print(f"\n❌ Errore: {e}")