#!/usr/bin/env python3
"""
Kathara Lab Creator - Versione semplificata
Crea file lab.conf e startup e file di configurazione delle macchine
per laboratori Kathara
"""

import os
import shutil
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
            
            # Verifica caratteri validi (lettere, numeri, underscore, trattino)
            # Permette nomi come: r1, pc1, br1r, br2r, web-server, db_1, etc.
            valid_chars = all(c.isalnum() or c in ('_', '-') for c in device_name)
            if not valid_chars:
                print("❌ Il nome può contenere solo lettere, numeri, - e _")
                continue
            
            # Il nome deve iniziare con una lettera o numero (non con - o _)
            if not device_name[0].isalnum():
                print("❌ Il nome deve iniziare con una lettera o un numero")
                continue
            
            devices.append(device_name)
            print(f"✅ Dispositivo '{device_name}' aggiunto")
            break
    
    return devices

def choose_device_type(device_name):
    """Chiede il tipo di dispositivo per scegliere l'immagine Docker"""
    print(f"\nChe tipo di dispositivo è '{device_name}'?")
    print("1. Router (kathara/frr)")
    print("2. Host (kathara/base)")
    print("3. Server (kathara/base)")
    
    images = {
        "1": "kathara/frr",
        "2": "kathara/base", 
        "3": "kathara/base"
    }
    
    # Tipi considerati router (che necessitano configurazione routing)
    router_types = {"1"}
    server_types = {"3"}
    
    while True:
        choice = input("Scegli tipo (1-3): ").strip()
        
        if choice in images:
            is_router = choice in router_types
            is_server = choice in server_types
            return images[choice], is_router, is_server
        else:
            print("❌ Scelta non valida! Scegli 1, 2 o 3.")









def choose_routing_protocol(device_name):
    """Chiede quale protocollo di routing usa il router"""
    print(f"\n🔀 Configurazione routing per '{device_name}'")
    print("Quale protocollo di routing usa questo router?")
    print("1. OSPF (Open Shortest Path First)")
    print("2. RIP (Routing Information Protocol)")
    print("3. BGP (Border Gateway Protocol)")
    print("4. BGP-OSPF (BGP + OSPF)")
    print("5. BGP-RIP (BGP + RIP)")
    print("6. BGP Datacenter Leaf")
    print("7. BGP Datacenter Spine")
    print("8. BGP Datacenter ToF")
    
    while True:
        choice = input("Scegli protocollo (1-8): ").strip()
        
        if choice == "1":
            return "ospf"
        elif choice == "2":
            return "rip"
        elif choice == "3":
            return "bgp"
        elif choice == "4":
            return "bgp-ospf"
        elif choice == "5":
            return "bgp-rip"
        elif choice == "6":
            return "bgp-datacenter-leaf"
        elif choice == "7":
            return "bgp-datacenter-spine"
        elif choice == "8":
            return "bgp-datacenter-tof"
        else:
            print("❌ Scelta non valida! Scegli 1, 2, 3, 4, 5, 6, 7 o 8.")

def choose_startup_type(device_name):
    """Chiede quale tipo di file startup usare per il dispositivo"""
    print(f"\n📄 Configurazione file startup per '{device_name}'")
    print("Quale tipo di file startup vuoi usare?")
    print("1. File base (systemctl start frr/apache2)")
    print("2. Leaf startup (da fileStartup/leaf.startup)")
    print("3. Container startup (da fileStartup/container.startup)")
    print("4. Server startup (da fileStartup/server.startup)")
    print("5. Leaf Bond startup (da fileStartup/leafBond.startup)")
    print("6. Server Bond startup (da fileStartup/serverBond.startup)")
    
    while True:
        choice = input("Scegli tipo startup (1-6): ").strip()
        
        if choice == "1":
            return "base"
        elif choice == "2":
            return "leaf"
        elif choice == "3":
            return "container"
        elif choice == "4":
            return "server"
        elif choice == "5":
            return "leafBond"
        elif choice == "6":
            return "serverBond"
        else:
            print("❌ Scelta non valida! Scegli 1, 2, 3, 4, 5 o 6.")

def create_router_config_directories(device_name, routing_protocol, lab_path):
    """
    Crea la directory nomerouter/etc/frr/ e copia i file di configurazione
    dal protocollo di routing specificato
    """
    # Path della directory di destinazione
    router_dir = lab_path / device_name / "etc" / "frr"
    router_dir.mkdir(parents=True, exist_ok=True)
    
    # Path della directory sorgente
    config_source_dir = Path("fileConfigurazione") / routing_protocol
    
    # Verifica che la directory sorgente esista
    if not config_source_dir.exists():
        print(f"⚠️  Directory di configurazione {config_source_dir} non trovata!")
        return False
    
    # Lista dei file da copiare (dipende dal tipo di protocollo)
    # Per datacenter (leaf/spine/tof) usa bgpd.conf, per gli altri usa frr.conf
    if "datacenter" in routing_protocol:
        config_files = ["daemons", "bgpd.conf"]
    else:
        config_files = ["daemons", "frr.conf", "vtysh.conf"]
    
    # Copia ogni file
    copied_files = []
    for config_file in config_files:
        source_file = config_source_dir / config_file
        dest_file = router_dir / config_file
        
        if source_file.exists():
            shutil.copy2(source_file, dest_file)
            copied_files.append(config_file)
        else:
            print(f"⚠️  File {config_file} non trovato in {config_source_dir}")
    
    if copied_files:
        print(f"✅ Creata directory {device_name}/etc/frr/ con file: {', '.join(copied_files)}")
        return True
    else:
        print(f"❌ Nessun file di configurazione copiato per {device_name}")
        return False

def create_server_config_directories(device_name, lab_path):
    """
    Crea la directory nome_server/var/www/html/ e copia il file index.html
    dalla directory fileConfigurazione/server/
    """
    # Path della directory di destinazione
    server_dir = lab_path / device_name / "var" / "www" / "html"
    server_dir.mkdir(parents=True, exist_ok=True)
    
    # Path della directory sorgente
    config_source_dir = Path("fileConfigurazione") / "server" / "var" / "www" / "html"
    
    # Verifica che la directory sorgente esista
    if not config_source_dir.exists():
        print(f"⚠️  Directory di configurazione {config_source_dir} non trovata!")
        return False
    
    # File da copiare
    source_file = config_source_dir / "index.html"
    dest_file = server_dir / "index.html"
    
    if source_file.exists():
        shutil.copy2(source_file, dest_file)
        print(f"✅ Creata directory {device_name}/var/www/html/ con file: index.html")
        return True
    else:
        print(f"⚠️  File index.html non trovato in {config_source_dir}")
        return False


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

def create_startup_files(devices_info, lab_path):
    """Crea i file .startup per ogni dispositivo"""
    print(f"\n🚀 Creando file .startup...")
    
    startup_files = []
    
    for device_name, device_data in devices_info.items():
        startup_filename = lab_path / f"{device_name}.startup"
        startup_type = device_data.get('startup_type', 'base')
        is_router = device_data.get('is_router', False)
        is_server = device_data.get('is_server', False)
        
        # Se il tipo è diverso da "base", copia il template
        if startup_type != 'base':
            template_file = Path("fileStartup") / f"{startup_type}.startup"
            
            if template_file.exists():
                shutil.copy2(template_file, startup_filename)
                # Rendi il file eseguibile
                startup_filename.chmod(0o755)
                startup_files.append(startup_filename)
                print(f"✅ Creato {device_name}.startup (template: {startup_type}.startup)")
            else:
                print(f"⚠️  Template {template_file} non trovato! Creo file base.")
                # Fallback al file base
                startup_type = 'base'
        
        # Se il tipo è "base", genera il file standard
        if startup_type == 'base':
            with open(startup_filename, 'w', encoding='utf-8') as f:
                f.write("#!/bin/bash\n\n")
                
                # Se è un router, aggiungi solo il comando per avviare FRR
                if is_router:
                    f.write("# Avvio servizio FRR\n")
                    f.write("systemctl start frr\n")
                
                # Se è un server, aggiungi il comando per avviare Apache2
                if is_server:
                    f.write("# Avvio servizio Apache2\n")
                    f.write("systemctl start apache2\n")
            
            # Rendi il file eseguibile
            startup_filename.chmod(0o755)
            startup_files.append(startup_filename)
            print(f"✅ Creato {device_name}.startup (file base)")
    
    return startup_files

def show_generated_files(lab_path, devices_info):
    """Mostra il contenuto dei file generati"""
    print("\n" + "=" * 70)
    print("📄 CONTENUTO FILE GENERATI")
    print("=" * 70)
    
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

def show_summary(lab_name, devices_info):
    """Mostra un riassunto del laboratorio"""
    print("\n📊 RIASSUNTO LABORATORIO")
    print("=" * 50)
    print(f"Nome: {lab_name}")
    print(f"Numero dispositivi: {len(devices_info)}")
    print("\nDispositivi:")
    
    for device_name, device_data in devices_info.items():
        image = device_data['image']
        is_router = device_data.get('is_router', False)
        routing_protocol = device_data.get('routing_protocol', None)
        startup_type = device_data.get('startup_type', 'base')
        
        print(f"  • {device_name} ({image})")
        
        if is_router and routing_protocol:
            print(f"    ├─ Protocollo: {routing_protocol.upper()}")
        
        print(f"    └─ Startup: {startup_type}")
    
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
    
    # Per ogni dispositivo, chiedi il tipo e protocollo
    devices_info = {}
    
    print(f"\n🖥️  CONFIGURAZIONE DISPOSITIVI")
    print("-" * 35)
    
    for device in devices:
        print(f"\n--- Configurazione {device} ---")
        
        # Tipo di dispositivo
        image, is_router, is_server = choose_device_type(device)
        is_host = not is_router and not is_server
        
        # Protocollo di routing
        routing_protocol = None
        if is_router:
            routing_protocol = choose_routing_protocol(device)
        
        # Tipo di file startup
        startup_type = choose_startup_type(device)
        
        # Salva informazioni dispositivo
        devices_info[device] = {
            'image': image,
            'is_router': is_router,
            'is_server': is_server,
            'is_host': is_host,
            'routing_protocol': routing_protocol,
            'startup_type': startup_type
        }
    
    # Mostra riassunto
    show_summary(lab_name, devices_info)
    
    # Genera sempre i file (nessuna conferma)
    print("\n⚙️  Generazione file in corso...")
    
    # Crea file .startup
    startup_files = create_startup_files(devices_info, lab_path)
    
    # Crea directory di configurazione per i router
    router_configs_created = []
    for device_name, device_data in devices_info.items():
        if device_data.get('is_router') and device_data.get('routing_protocol'):
            success = create_router_config_directories(
                device_name, 
                device_data['routing_protocol'], 
                lab_path
            )
            if success:
                router_configs_created.append(device_name)
    
    # Crea directory di configurazione per i server
    server_configs_created = []
    for device_name, device_data in devices_info.items():
        if device_data.get('is_server'):
            success = create_server_config_directories(
                device_name,
                lab_path
            )
            if success:
                server_configs_created.append(device_name)
    
    print(f"\n🎉 Laboratorio '{lab_name}' creato!")
    print(f"📁 Directory: {lab_path.absolute()}")
    print("📄 File generati:")
    print(f"   • {len(startup_files)} file .startup")
    if router_configs_created:
        print(f"   • {len(router_configs_created)} directory di configurazione router:")
        for router in router_configs_created:
            print(f"     - {router}/etc/frr/")
    if server_configs_created:
        print(f"   • {len(server_configs_created)} directory di configurazione server:")
        for server in server_configs_created:
            print(f"     - {server}/var/www/html/")
    
    print("\nProssimi passi:")
    print("1. Personalizza i file di configurazione routing in <router>/etc/frr/")
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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Uscita dal programma. Arrivederci!")
    except Exception as e:
        print(f"\n❌ Errore: {e}")