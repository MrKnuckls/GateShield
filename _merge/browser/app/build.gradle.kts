plugins { id("com.android.application") }
android {
    namespace = "com.knuckls.gateshield.browser"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.knuckls.gateshield.browser"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }
    buildTypes { release { isMinifyEnabled = false } }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
dependencies {
    implementation("androidx.appcompat:appcompat:1.7.0")
    constraints {
        implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.8.22") {
            because("kotlin-stdlib 1.8.22 includes the jdk7/jdk8 classes")
        }
    }
}
