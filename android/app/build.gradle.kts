import java.util.Properties
import java.io.FileInputStream
plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("com.chaquo.python") }
android {
    namespace = "br.lugh.or70"
    compileSdk = 34
    defaultConfig {
        applicationId = "br.lugh.or70"; minSdk = 24; targetSdk = 34
        versionCode = 1; versionName = "0.1.0-android"
        ndk { abiFilters += listOf("arm64-v8a", "x86_64") }
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    // Credenciais FORA do repo: caminho via env OR70_SIGNING (arquivo .properties). Sem ele, release sai sem assinatura.
    val sp = System.getenv("OR70_SIGNING")?.let { f -> Properties().apply { load(FileInputStream(f)) } }
    if (sp != null) signingConfigs { create("rel") { storeFile = file(sp["storeFile"] as String); storePassword = sp["storePassword"] as String; keyAlias = sp["keyAlias"] as String; keyPassword = sp["keyPassword"] as String } }
    buildTypes { getByName("release") { isMinifyEnabled = false; if (sp != null) signingConfig = signingConfigs.getByName("rel") } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
// Núcleo REAL: copia ../../or70 (sem reimplementar) para o fonte Python do APK.
val syncCore by tasks.registering(Sync::class) {
    from(rootProject.file("../or70")) { exclude("**/__pycache__/**") }
    into(layout.buildDirectory.dir("core-py/or70"))
}
chaquopy {
    defaultConfig { version = "3.13"; pyc { src = false } }
    sourceSets { getByName("main") { srcDir("src/main/python"); srcDir(layout.buildDirectory.dir("core-py")) } }
}
tasks.matching { it.name.startsWith("merge") && it.name.contains("PythonSources") }.configureEach { dependsOn(syncCore) }
tasks.named("preBuild") { dependsOn(syncCore) }
dependencies {
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test:runner:1.5.2")
}
