# Заметки по языкам и сборке

Проект можно реализовать на Python, Java, Kotlin, C# или C++.

## Python

- Точка входа: `main.py` / `python -m your_package`.
- Зависимости: `requirements.txt`
- Запуск: `python main.py`.
- В README укажите версию Python.

## Java

- Сборка: Maven (`pom.xml`) или Gradle (`build.gradle`).
- Обязательно проверьте, что `mvn package` / `./gradlew build` собирается
  «с нуля».
- Запуск: `./gradlew run`.

## Kotlin

- Сборка: Gradle (`build.gradle.kts`).
- Оставьте **Gradle wrapper** (`gradlew`, `gradle/wrapper/…`) в репозитории.
- Запуск: `./gradlew run`.

## C#

- Проект: `dotnet new console`
- Сборка/запуск: `dotnet run`

## C++

- Сборка: `CMakeLists.txt` **или** `Makefile`
- **Не коммитьте** `build/`, `*.o`, `CMakeCache.txt`
