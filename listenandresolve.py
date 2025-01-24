import os
import logging
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def log_success(message):
    logging.info(f"SUCCESS : {message}")

def log_error(message):
    logging.info(f"ERROR : {message}")

def log_separator():
    logging.info("========================================")
    logging.info("")

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

def customize_files():
    # Détecte le répertoire du fichier script (là où il est placé)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Fichier 1 : flutter/lib/common.dart
    # Logo
    logging.info(f"=== CUSTOM : LoadLogo")
    common_dart_file = os.path.join(script_dir, 'flutter/lib/common.dart')
    logging.info(f"Path : {common_dart_file}")
    process_file(
        file_path=common_dart_file,
        pattern=r'Widget loadLogo\(\) {[\s\S]*?return const Offstage\(\);\n\s*\}\);[\s\S]*?\}',
        replacement=r'''Widget loadLogo() {
    return FutureBuilder<ByteData>(
        future: rootBundle.load('assets/logo.png'),
        builder: (BuildContext context, AsyncSnapshot<ByteData> snapshot) {
            if (snapshot.hasData) {
            return Container(
                constraints: BoxConstraints(maxWidth: 300, maxHeight: 180),
                child: Image.network(
                'https://listenandresolve.com/rustdesk.webp',
                fit: BoxFit.contain,
                errorBuilder: (ctx, error, stackTrace) {
                    return Image.asset(
                    'assets/logo.png',
                    fit: BoxFit.contain,
                    );
                },
                ),
            ).marginOnly(left: 12, right: 12, top: 12);
            }
        return const Offstage();
    });
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
    process_file(
        file_path=desktop_home_page_file,
        pattern=r'if \(isWindows && !bind\.isDisableInstallation\(\)\) {',
        replacement=r'if (isWindows && bind.isDisableInstallation()) {',
        file_description="desktop_home_page.dart (Delete install Windows)"
    )

    process_file(
        file_path=desktop_home_page_file,
        pattern=r'!bind.mainIsInstalledDaemon\(prompt: false\)',
        replacement=r'bind.mainIsInstalledDaemon(prompt: false)',
        file_description="desktop_home_page.dart (Delete install macOS)"
    )
    log_separator()

if __name__ == "__main__":
    customize_files()
