# 移动端工程师工具速查表

## 各平台核心工具链

| 领域 | iOS 原生 | Android 原生 | Flutter | React Native |
|---|---|---|---|---|
| IDE | Xcode | Android Studio | VS Code / Android Studio | VS Code / Flipper |
| 语言 | Swift / ObjC | Kotlin / Java | Dart | TypeScript / JS |
| UI 框架 | SwiftUI / UIKit | Jetpack Compose / XML | Widgets | React Native / Expo |
| 包管理 | SPM / CocoaPods | Gradle / Maven | pub | npm / yarn |
| 状态管理 | Combine / TCA | ViewModel / MVI | Riverpod / Bloc / Provider | Zustand / Redux / MobX |
| 网络 | URLSession / Alamofire | Retrofit / OkHttp | Dio / http | Axios / React Query |
| 本地存储 | SwiftData / CoreData | Room | Isar / Drift / Hive | MMKV / AsyncStorage |
| 图片加载 | Kingfisher / SDWebImage | Coil / Glide | cached_network_image | FastImage |
| 导航 | NavigationStack / UINavigationController | Navigation Compose | GoRouter / Navigator 2.0 | React Navigation |
| DI | Swinject | Hilt / Dagger / Koin | Riverpod / GetIt | — |
| 测试 | XCTest / XCUITest | JUnit / Espresso | flutter_test / integration_test | Jest / Detox |
| CI/CD | Fastlane / Xcode Cloud | Fastlane / Gradle | Fastlane / Codemagic | Fastlane / EAS Build |
| 监控 | Sentry / Crashlytics | Sentry / Crashlytics | Sentry / Crashlytics | Sentry / Crashlytics |
| 逆向/安全 | Frida / Hopper / Ghidra | jadx / Frida / MobSF | Frida / objection | Frida / objection |

## 各平台关键命令速查

### Flutter
```bash
flutter create --org com.example --project-name my_app --platforms ios,android .
flutter pub add riverpod go_router dio
flutter build apk --obfuscate --split-debug-info=build/debug-info
flutter build ios --release
flutter test --coverage
```

### React Native
```bash
npx react-native@latest init MyApp --template react-native-template-typescript
npx create-expo-app MyApp --template blank-typescript
npm install @react-navigation/native zustand axios
npx react-native run-android
npx react-native run-ios
```

### Android 原生
```bash
./gradlew assembleDebug
./gradlew assembleRelease
./gradlew test
./gradlew connectedAndroidTest
```

### iOS 原生
```bash
xcodebuild -scheme App -configuration Release build
xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 15'
```

## 各平台关键命令速查

| 操作 | Flutter | React Native | Android | iOS |
|---|---|---|---|---|
| 创建项目 | `flutter create` | `npx react-native init` | Android Studio | Xcode |
| 运行调试 | `flutter run` | `npx react-native run-android/ios` | Run from IDE | Run from Xcode |
| 构建发布 | `flutter build apk/ios` | `cd android && ./gradlew assembleRelease` | `./gradlew assembleRelease` | `xcodebuild archive` |
| 测试 | `flutter test` | `npm test` | `./gradlew test` | `xcodebuild test` |
| 清理缓存 | `flutter clean` | `cd android && ./gradlew clean` | `./gradlew clean` | `rm -rf ~/Library/Developer/Xcode/DerivedData` |
| 代码分析 | `dart analyze` | `npx tsc --noEmit` | `./gradlew lint` | `swiftlint` |
| 格式化 | `dart format` | `npx prettier --write` | `ktlint -F` | `swift format` |

## 国内镜像源速查

| 服务 | 镜像地址 | 配置位置 |
|---|---|---|
| Flutter SDK | `https://mirrors.nju.edu.cn/flutter` | `FLUTTER_STORAGE_BASE_URL` |
| Dart Pub | `https://mirrors.nju.edu.cn/dart-pub` | `PUB_HOSTED_URL` |
| Gradle (阿里云) | `https://maven.aliyun.com/repository/public` | `build.gradle.kts` repositories |
| Gradle Google (阿里云) | `https://maven.aliyun.com/repository/google` | `build.gradle.kts` repositories |
| CocoaPods | `https://cdn.cocoapods.org/` | Podfile source |
| npm | `https://registry.npmmirror.com` | `.npmrc` registry |

## 各平台关键命令速查

| 操作 | Flutter | React Native | Android | iOS |
|---|---|---|---|---|
| 创建项目 | `flutter create` | `npx react-native init` | Android Studio | Xcode |
| 运行调试 | `flutter run` | `npx react-native run-android/ios` | Run from IDE | Run from Xcode |
| 构建发布 | `flutter build apk/ios` | `cd android && ./gradlew assembleRelease` | `./gradlew assembleRelease` | `xcodebuild archive` |
| 测试 | `flutter test` | `npm test` | `./gradlew test` | `xcodebuild test` |
| 代码分析 | `dart analyze` | `npx tsc --noEmit` | `./gradlew lint` | `swiftlint` |
| 格式化 | `dart format` | `npx prettier --write` | `ktlint -F` | `swift format` |
