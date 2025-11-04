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

def get_router_ip_addresses(device_name, interfaces):
    """Chiede gli indirizzi IP per ogni interfaccia del router"""
    print(f"\n🌐 Configurazione indirizzi IP per router '{device_name}'")
    ip_config = {}
    
    for eth_num in sorted(interfaces.keys()):
        domain = interfaces[eth_num]
        print(f"\nInterfaccia eth{eth_num} (dominio {domain}):")
        
        while True:
            ip_input = input(f"Indirizzo IP per eth{eth_num} (formato: 10.0.0.1/24): ").strip()
            
            # Verifica formato base (contiene / e punto)
            if not ip_input:
                print("❌ L'indirizzo IP non può essere vuoto!")
                continue
            
            if '/' not in ip_input:
                print("❌ Formato non valido! Usa il formato: IP/NETMASK (es. 10.0.0.1/24)")
                continue
            
            # Split IP e netmask
            try:
                ip_part, netmask = ip_input.split('/')
                
                # Verifica che la netmask sia un numero
                netmask_int = int(netmask)
                if netmask_int < 0 or netmask_int > 32:
                    print("❌ La netmask deve essere tra 0 e 32!")
                    continue
                
                # Verifica formato IP (deve avere 4 ottetti)
                octets = ip_part.split('.')
                if len(octets) != 4:
                    print("❌ L'indirizzo IP deve avere 4 ottetti (es. 192.168.1.1)!")
                    continue
                
                # Verifica che ogni ottetto sia valido
                valid = True
                for octet in octets:
                    octet_int = int(octet)
                    if octet_int < 0 or octet_int > 255:
                        print(f"❌ Ottetto {octet} non valido! Deve essere tra 0 e 255.")
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Salva la configurazione
                ip_config[eth_num] = ip_input
                print(f"✅ eth{eth_num} → {ip_input}")
                break
                
            except ValueError:
                print("❌ Formato non valido! Usa il formato: IP/NETMASK (es. 10.0.0.1/24)")
                continue
    
    return ip_config

def get_host_server_ip_addresses(device_name, device_type, interfaces):
    """Chiede gli indirizzi IP per ogni interfaccia di host/server"""
    print(f"\n🌐 Configurazione indirizzi IP per {device_type} '{device_name}'")
    print("Vuoi configurare gli indirizzi IP per questo dispositivo?")
    
    configure_ips = input("Configura IP? (s/N): ").strip().lower()
    
    if configure_ips != 's':
        return {}
    
    ip_config = {}
    
    for eth_num in sorted(interfaces.keys()):
        domain = interfaces[eth_num]
        print(f"\nInterfaccia eth{eth_num} (dominio {domain}):")
        
        while True:
            ip_input = input(f"Indirizzo IP per eth{eth_num} (formato: 10.0.0.1/24 o invio per saltare): ").strip()
            
            # Permetti di saltare l'interfaccia
            if not ip_input:
                print(f"⏭️  eth{eth_num} saltata (verrà commentata nel file .startup)")
                break
            
            if '/' not in ip_input:
                print("❌ Formato non valido! Usa il formato: IP/NETMASK (es. 10.0.0.1/24)")
                continue
            
            # Split IP e netmask
            try:
                ip_part, netmask = ip_input.split('/')
                
                # Verifica che la netmask sia un numero
                netmask_int = int(netmask)
                if netmask_int < 0 or netmask_int > 32:
                    print("❌ La netmask deve essere tra 0 e 32!")
                    continue
                
                # Verifica formato IP (deve avere 4 ottetti)
                octets = ip_part.split('.')
                if len(octets) != 4:
                    print("❌ L'indirizzo IP deve avere 4 ottetti (es. 192.168.1.1)!")
                    continue
                
                # Verifica che ogni ottetto sia valido
                valid = True
                for octet in octets:
                    octet_int = int(octet)
                    if octet_int < 0 or octet_int > 255:
                        print(f"❌ Ottetto {octet} non valido! Deve essere tra 0 e 255.")
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Salva la configurazione
                ip_config[eth_num] = ip_input
                print(f"✅ eth{eth_num} → {ip_input}")
                break
                
            except ValueError:
                print("❌ Formato non valido! Usa il formato: IP/NETMASK (es. 10.0.0.1/24)")
                continue
    
    return ip_config

def get_host_routes(device_name):
    """Chiede le rotte da aggiungere per un host"""
    print(f"\n🛣️  Configurazione rotte per host '{device_name}'")
    print("Vuoi aggiungere rotte statiche per questo host?")
    
    add_routes = input("Aggiungi rotte? (s/N): ").strip().lower()
    
    if add_routes != 's':
        return []
    
    routes = []
    print("\nInserisci le rotte (lascia vuoto per terminare)")
    print("Formato rotta di default: default via GATEWAY (es. default via 192.168.1.1)")
    print("Formato rotta specifica: RETE/NETMASK via GATEWAY (es. 192.168.2.0/24 via 192.168.1.1)")
    
    while True:
        route_input = input(f"Rotta {len(routes) + 1} (o invio per terminare): ").strip()
        
        if not route_input:
            break
        
        # Verifica formato base
        if ' via ' not in route_input.lower():
            print("❌ Formato non valido! Usa: RETE/NETMASK via GATEWAY o default via GATEWAY")
            continue
        
        try:
            # Split in parti
            parts = route_input.lower().split(' via ')
            if len(parts) != 2:
                print("❌ Formato non valido! Usa: RETE/NETMASK via GATEWAY o default via GATEWAY")
                continue
            
            network, gateway = parts[0].strip(), parts[1].strip()
            
            # Verifica se è la rotta di default
            is_default = (network == 'default')
            
            if not is_default:
                # Verifica che la rete abbia la netmask
                if '/' not in network:
                    print("❌ La rete deve includere la netmask (es. 192.168.2.0/24) o usare 'default'")
                    continue
                
                # Verifica formato network
                net_part, netmask = network.split('/')
                netmask_int = int(netmask)
                if netmask_int < 0 or netmask_int > 32:
                    print("❌ La netmask deve essere tra 0 e 32!")
                    continue
                
                # Verifica formato IP della rete
                net_octets = net_part.split('.')
                if len(net_octets) != 4:
                    print("❌ La rete deve avere 4 ottetti!")
                    continue
                
                # Verifica validità ottetti della rete
                valid = True
                for octet in net_octets:
                    octet_int = int(octet)
                    if octet_int < 0 or octet_int > 255:
                        print(f"❌ Ottetto {octet} non valido! Deve essere tra 0 e 255.")
                        valid = False
                        break
                
                if not valid:
                    continue
            
            # Verifica formato IP del gateway
            gw_octets = gateway.split('.')
            if len(gw_octets) != 4:
                print("❌ Il gateway deve avere 4 ottetti!")
                continue
            
            # Verifica validità ottetti del gateway
            valid = True
            for octet in gw_octets:
                octet_int = int(octet)
                if octet_int < 0 or octet_int > 255:
                    print(f"❌ Ottetto {octet} non valido! Deve essere tra 0 e 255.")
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Salva la rotta
            routes.append({'network': network, 'gateway': gateway, 'is_default': is_default})
            if is_default:
                print(f"✅ Rotta di default aggiunta: via {gateway}")
            else:
                print(f"✅ Rotta aggiunta: {network} via {gateway}")
            
        except ValueError:
            print("❌ Formato non valido! Usa: RETE/NETMASK via GATEWAY o default via GATEWAY")
            continue
    
    return routes

def choose_routing_protocol(device_name):
    """Chiede quale protocollo di routing usa il router"""
    print(f"\n🔀 Configurazione routing per '{device_name}'")
    print("Quale protocollo di routing usa questo router?")
    print("1. OSPF (Open Shortest Path First)")
    print("2. RIP (Routing Information Protocol)")
    print("3. BGP (Border Gateway Protocol)")
    
    while True:
        choice = input("Scegli protocollo (1-3): ").strip()
        
        if choice == "1":
            return "ospf"
        elif choice == "2":
            return "rip"
        elif choice == "3":
            return "bgp"
        else:
            print("❌ Scelta non valida! Scegli 1, 2 o 3.")

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
    
    # Lista dei file da copiare
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

def create_lab_conf(lab_name, devices_info, lab_path):
    """Crea il file lab.conf nella directory del laboratorio"""
    filename = lab_path / "lab.conf"
    
    print(f"\n📁 Creando file lab.conf...")
    
    with open(filename, 'w', encoding='utf-8') as f:
               
        # Per ogni dispositivo, scrivi la configurazione
        for device_name, device_data in devices_info.items():
            image = device_data['image']
            interfaces = device_data['interfaces']
            
            # Specifica sempre l'immagine (anche kathara/base per host e server)
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
        is_router = device_data.get('is_router', False)
        is_server = device_data.get('is_server', False)
        is_host = device_data.get('is_host', False)
        ip_addresses = device_data.get('ip_addresses', {})
        host_routes = device_data.get('host_routes', [])
        
        with open(startup_filename, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n\n")
            
            # Configurazione delle interfacce
            f.write("# Configurazione interfacce di rete\n")
            
            # Se ci sono IP configurati (router, host o server)
            if ip_addresses:
                for eth_num in sorted(interfaces.keys()):
                    domain = interfaces[eth_num]
                    if eth_num in ip_addresses:
                        ip_addr = ip_addresses[eth_num]
                        f.write(f"ip addr add {ip_addr} dev eth{eth_num}\n")
                    else:
                        # Interfaccia senza IP configurato
                        f.write(f"# eth{eth_num} collegata al dominio {domain}\n")
                        f.write(f"# ip addr add <INDIRIZZO_IP>/<NETMASK> dev eth{eth_num}\n")
            else:
                # Nessun IP configurato - commenta tutte le interfacce
                for eth_num, domain in interfaces.items():
                    f.write(f"# eth{eth_num} collegata al dominio {domain}\n")
                    f.write(f"# ip addr add <INDIRIZZO_IP>/<NETMASK> dev eth{eth_num}\n")
            
            if interfaces:
                f.write("\n")
            
            # Se è un host con rotte, aggiungile
            if is_host and host_routes:
                f.write("# Configurazione rotte statiche\n")
                for route in host_routes:
                    if route.get('is_default', False):
                        # Rotta di default
                        f.write(f"ip route add default via {route['gateway']}\n")
                    else:
                        # Rotta specifica
                        f.write(f"ip route add {route['network']} via {route['gateway']}\n")
                f.write("\n")
            
            # Se è un router, aggiungi il comando per avviare FRR
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
        is_router = device_data.get('is_router', False)
        routing_protocol = device_data.get('routing_protocol', None)
        ip_addresses = device_data.get('ip_addresses', {})
        
        print(f"  • {device_name} ({image})")
        
        if is_router and routing_protocol:
            print(f"    ├─ Protocollo: {routing_protocol.upper()}")
        
        if interfaces:
            for eth_num, domain in interfaces.items():
                ip_info = ""
                if eth_num in ip_addresses:
                    ip_info = f" - IP: {ip_addresses[eth_num]}"
                print(f"    └─ eth{eth_num} → {domain}{ip_info}")
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
        image, is_router, is_server = choose_device_type(device)
        is_host = not is_router and not is_server
        
        # Interfacce del dispositivo
        interfaces, device_domains = get_device_interfaces(device)
        
        # Configurazione IP e rotte in base al tipo
        routing_protocol = None
        ip_addresses = {}
        host_routes = []
        
        if is_router:
            # Router: chiedi protocollo di routing e IP
            routing_protocol = choose_routing_protocol(device)
            if interfaces:
                ip_addresses = get_router_ip_addresses(device, interfaces)
        elif is_host:
            # Host: chiedi IP e rotte
            if interfaces:
                ip_addresses = get_host_server_ip_addresses(device, "host", interfaces)
            host_routes = get_host_routes(device)
        elif is_server:
            # Server: chiedi solo IP
            if interfaces:
                ip_addresses = get_host_server_ip_addresses(device, "server", interfaces)
        
        # Salva informazioni dispositivo
        devices_info[device] = {
            'image': image,
            'interfaces': interfaces,
            'is_router': is_router,
            'is_server': is_server,
            'is_host': is_host,
            'routing_protocol': routing_protocol,
            'ip_addresses': ip_addresses,
            'host_routes': host_routes
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
        print(f"   • lab.conf")
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
        print("1. Modifica i file .startup per configurare gli IP")
        if router_configs_created:
            print("2. Personalizza i file di configurazione routing in <router>/etc/frr/")
            print("3. Entra nella directory del laboratorio:")
        else:
            print("2. Entra nella directory del laboratorio:")
        print(f"   cd created_labs/{lab_name}")
        print(f"{3 if router_configs_created else 2}. Avvia il laboratorio:")
        print("   kathara lstart")
        print(f"{4 if router_configs_created else 3}. Per fermarlo:")
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