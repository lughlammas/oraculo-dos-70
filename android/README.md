# Oráculo dos 70 — Android (v0, teste)
Núcleo Python real (`../or70`) embarcado via Chaquopy. Offline, sem permissões, sem rede.

Build (box): JDK 17, Android SDK 34.
    export ANDROID_HOME=~/android/sdk JAVA_HOME=~/android/jdk-17.0.21+9
    ./gradlew assembleDebug                      # APK debug
    OR70_SIGNING=/caminho/fora/do/repo/signing.properties ./gradlew assembleRelease bundleRelease
`signing.properties`: storeFile, storePassword, keyAlias, keyPassword. **Nunca** commitar. A chave de teste atual é só teste; para a Play gerar chave nova (ou Play App Signing).
Testes: `../.venv/bin/python -m pytest -q` (host) · `./gradlew connectedDebugAndroidTest` (emulador/aparelho).
Instalar: `adb install app-release.apk` ou abrir o APK no celular (permitir fontes desconhecidas).
