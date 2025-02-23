import os
import logging
import re
import urllib.request
import shutil

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def log_success(message):
    logging.info(f"SUCCESS : {message}")

def log_error(message):
    logging.info(f"ERROR : {message}")

def log_separator():
    logging.info("========================================")
    logging.info("")

def download_and_replace_file(url, destination_path, file_description):
    """
    Télécharge un fichier depuis une URL et le place à la destination spécifiée
    """
    try:
        # S'assurer que le répertoire de destination existe
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Créer une requête avec un User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        # Télécharger le fichier
        with urllib.request.urlopen(req) as response, open(destination_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        log_success(f"{file_description} downloaded and replaced successfully at {destination_path}")
        return True
    except Exception as e:
        log_error(f"Error downloading/replacing {file_description}: {e}")
        return False

def process_file(file_path, pattern, replacement, file_description):
    if not os.path.exists(file_path):
        log_error(f"{file_description} NOT FOUND : {file_path}")
        return

    try:
        with open(file_path, 'r+') as f:
            content = f.read()
            
            # Vérifier si le motif est trouvé
            if not re.search(pattern, content, re.DOTALL):
                log_error(f"'{pattern}' --- NOT FOUND --- in {file_description}")
            else:
                # Remplacement
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                
                if content == new_content:
                    log_error(f"Nothing to change to {file_description}.")
                else:
                    # Écriture des modifications
                    f.seek(0)
                    f.write(new_content)
                    f.truncate()
                    log_success(f"{file_description} updated.")
    except Exception as e:
        log_error(f"Erreur lors du traitement de {file_description} : {e}")

def download_resources():
    """
    Télécharge et remplace les ressources (icônes et logo)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Définition des ressources à télécharger
    resources = [
        {
            'url': 'https://listenandresolve.com/rustdesk/icon.ico',
            'path': os.path.join(script_dir, 'res/icon.ico'),
            'description': 'Windows icon 1'
        },
        {
            'url': 'https://listenandresolve.com/rustdesk/icon.ico',
            'path': os.path.join(script_dir, 'flutter/windows/runner/resources/app-icon.ico'),
            'description': 'Windows icon 2'
        },
        {
            'url': 'https://listenandresolve.com/rustdesk/icon.svg',
            'path': os.path.join(script_dir, 'flutter/assets/icon.svg'),
            'description': 'Windows icon 3'
        },
        {
            'url': 'https://listenandresolve.com/rustdesk/AppIcon.icns',
            'path': os.path.join(script_dir, 'flutter/macos/Runner/AppIcon.icns'),
            'description': 'macOS icon'
        },
        {
            'url': 'https://listenandresolve.com/rustdesk/logo.png',
            'path': os.path.join(script_dir, 'flutter/assets/logo.png'),
            'description': 'Logo image'
        }
    ]
    
    logging.info("=== CUSTOM : Downloading resources")
    for resource in resources:
        download_and_replace_file(
            resource['url'],
            resource['path'],
            resource['description']
        )
    log_separator()

def customize_files():
    # Détecte le répertoire du fichier script (là où il est placé)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Télécharger les ressources en premier
    download_resources()

    # Fichier 1 : flutter/lib/common.dart
    # Logo
    logging.info(f"=== CUSTOM : LoadLogo")
    common_dart_file = os.path.join(script_dir, 'flutter/lib/common.dart')
    logging.info(f"Path : {common_dart_file}")
    process_file(
        file_path=common_dart_file,
        pattern=r'Widget loadLogo\(\) {[\s\S]*?return const Offstage\(\);\n\s*\}\);[\s\S]*?\}',
        replacement=r'''Widget loadLogo() {
    return Container(
    width: 300,
    height: 100,
    margin: EdgeInsets.only(left: 12, right: 12, top: 12),
    child: FadeInImage.assetNetwork(
      placeholder: 'assets/logo.png', // Placeholder image while loading
      image: 'https://listenandresolve.com/rustdesk/client.gif', // URL of the logo
      fit: BoxFit.contain,
      imageErrorBuilder: (context, error, stackTrace) {
        return Container(); // Handle image loading error
      },
    ),
  );
}''',
        file_description="common.dart"
    )
    log_separator()

    # Fichier 2 : src/lang/en.rs
    # Aide pour macOS
    logging.info(f"=== CUSTOM : Link for help")
    en_rs_file = os.path.join(script_dir, 'src/lang/en.rs')
    logging.info(f"Path : {en_rs_file}")
    process_file(
        file_path=en_rs_file,
        pattern=r'("doc_mac_permission",\s*"[^"]*")',
        replacement=r'("doc_mac_permission", "https://listenandresolve.com/rustdesk")',
        file_description="en.rs"
    )
    log_separator()

    # Fichier 3 : libs/hbb_common/src/config.rs
    # Incoming only
    logging.info(f"=== CUSTOM : Incoming Mode Only")
    config_rs_file = os.path.join(script_dir, 'libs/hbb_common/src/config.rs')
    logging.info(f"Path : {config_rs_file}")
    process_file(
        file_path=config_rs_file,
        pattern=r'pub static ref HARD_SETTINGS:\s*RwLock<HashMap<String,\s*String>>\s*=\s*Default::default\(\);',
        replacement=r'''pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = {
        let mut m = HashMap::new();
        m.insert("conn-type".to_string(), "incoming".to_string());
        RwLock::new(m)
    };''',
        file_description="config.rs"
    )
    # Modification du serveur Rendezvous
    logging.info(f"=== CUSTOM : Rendezvous Server")
    process_file(
        file_path=config_rs_file,
        pattern=r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\["[^"]*"\];',
        replacement=r'pub const RENDEZVOUS_SERVERS: &[&str] = &["${{ secrets.RENDEZVOUS_SERVER }}"];',
        file_description="config.rs (Rendezvous Server)"
    )
    
    # Modification de la clé publique RS
    logging.info(f"=== CUSTOM : RS Public Key")
    process_file(
        file_path=config_rs_file,
        pattern=r'pub const RS_PUB_KEY: &str = "[^"]*";',
        replacement=r'pub const RS_PUB_KEY: &str = "${{ secrets.RS_PUB_KEY }}";',
        file_description="config.rs (Public Key)"
    )
    log_separator()

    # Fichier 4 : libs/hbb_common/src/lib.rs
    # Désactiver les mises à jour
    logging.info(f"=== CUSTOM : Disable check update")
    lib_rs_file = os.path.join(script_dir, 'libs/hbb_common/src/lib.rs')
    logging.info(f"Path : {lib_rs_file}")
    process_file(
        file_path=lib_rs_file,
        pattern=r'const URL: &str = "https://api\.rustdesk\.com/version/latest";',
        replacement=r'const URL: &str = "";',
        file_description="lib.rs"
    )
    log_separator()
    
    # Fichier 5 : flutter/lib/desktop/pages/desktop_home_page.dart
    # Désactiver les cartes d'aides
    logging.info(f"=== CUSTOM : Help Cards")
    desktop_home_page_file = os.path.join(script_dir, 'flutter/lib/desktop/pages/desktop_home_page.dart')
    logging.info(f"Path : {desktop_home_page_file}")
    process_file( # Désactiver l'installation Windows
        file_path=desktop_home_page_file,
        pattern=r'if \(isWindows && !bind\.isDisableInstallation\(\)\) {',
        replacement=r'if (isWindows && bind.isDisableInstallation()) {',
        file_description="desktop_home_page.dart (Delete install Windows)"
    )

    process_file( # Désactiver l'installation macoS
        file_path=desktop_home_page_file,
        pattern=r'!bind.mainIsInstalledDaemon\(prompt: false\)',
        replacement=r'bind.mainIsInstalledDaemon(prompt: false)',
        file_description="desktop_home_page.dart (Delete install macOS)"
    )
    log_separator()

if __name__ == "__main__":
    customize_files()
