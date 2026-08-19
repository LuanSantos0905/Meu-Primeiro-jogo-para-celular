[app]

# (str) Título do seu aplicativo
title = Meu Jogo

# (str) Nome do pacote
package.name = meujogo

# (str) Domínio do pacote (necessário para empacotamento android/ios)
package.domain = org.luan

# (str) Diretório do código fonte onde o main.py está
source.dir = .

# (list) Extensões de arquivos a serem incluídos
source.include_exts = py,png,jpg,kv,atlas

# (str) Versão do aplicativo
version = 0.1

# (list) Requisitos do aplicativo (AQUI ESTÁ A CORREÇÃO DO KIVY)
requirements = python3,kivy>=2.3.1

# (str) Orientação suportada (landscape, sensorLandscape, portrait ou all)
orientation = portrait

#
# Configurações específicas do Android
#

# (bool) Indicar se o aplicativo deve ser em tela cheia (fullscreen)
fullscreen = 0

# (list) Permissões (descomente e adicione se seu jogo precisar de internet, etc)
#android.permissions = INTERNET

# (int) Target Android API (AQUI ESTÃO AS CORREÇÕES DE API E NDK)
android.api = 33

# (int) Minimum API
android.minapi = 24

# (str) Versão do Android NDK
android.ndk = 25b

# (str) Variáveis de ambiente para forçar o compilador a achar o OpenGL no NDK
android.env_vars = CFLAGS="-I$(ANDROID_NDK_ROOT)/sysroot/usr/include"

# (bool) Aceitar automaticamente as licenças do SDK (Fundamental para o GitHub Actions não travar)
android.accept_sdk_license = True

# (str) Arquitetura alvo para a compilação
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Nível de log (0 = apenas erro, 1 = info, 2 = debug com saída do comando)
log_level = 2

# (int) Mostrar aviso se o buildozer for executado como root
warn_on_root = 1
