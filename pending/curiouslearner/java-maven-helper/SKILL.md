---
name: java-maven-helper
description: Maven build system, dependency management, and Java project configuration assistance.
---

# Java Maven Dependency and Build Helper Skill

Maven build system, dependency management, and Java project configuration assistance.

## Instructions

You are a Maven and Java ecosystem expert. When invoked:

1. **Maven Project Management**:
   - Initialize and configure Maven projects
   - Manage pom.xml configuration
   - Handle project structure and organization
   - Configure multi-module projects
   - Use Maven archetypes

2. **Dependency Management**:
   - Add, update, and remove dependencies
   - Manage dependency scopes
   - Handle version conflicts
   - Use dependency management sections
   - Work with BOMs (Bill of Materials)

3. **Build Configuration**:
   - Configure plugins and goals
   - Set up build profiles
   - Manage build lifecycle
   - Configure properties and resources
   - Handle filtering and resource processing

4. **Troubleshooting**:
   - Fix dependency resolution errors
   - Debug build failures
   - Resolve plugin conflicts
   - Clean corrupted repositories
   - Handle version conflicts

5. **Best Practices**: Provide guidance on Maven project organization, dependency management, and build optimization

## Maven Basics

### Project Initialization
```bash
# Create from archetype (interactive)
mvn archetype:generate

# Create quickstart project (non-interactive)
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=my-app \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DarchetypeVersion=1.4 \
  -DinteractiveMode=false

# Create web application
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=my-webapp \
  -DarchetypeArtifactId=maven-archetype-webapp \
  -DinteractiveMode=false

# Create Spring Boot application
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=my-spring-app \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false
```

### Basic Commands
```bash
# Clean build artifacts
mvn clean

# Compile project
mvn compile

# Run tests
mvn test

# Package (create JAR/WAR)
mvn package

# Install to local repository
mvn install

# Deploy to remote repository
mvn deploy

# Skip tests
mvn package -DskipTests

# Run specific test
mvn test -Dtest=MyTest

# Show dependency tree
mvn dependency:tree

# Show effective POM
mvn help:effective-pom

# Run project (with exec plugin)
mvn exec:java -Dexec.mainClass="com.example.Main"
```

## Usage Examples

```
@java-maven-helper
@java-maven-helper --init-project
@java-maven-helper --add-dependency
@java-maven-helper --fix-dependencies
@java-maven-helper --multi-module
@java-maven-helper --troubleshoot
```

## pom.xml Configuration

### Complete Example
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- Project Coordinates -->
    <groupId>com.example</groupId>
    <artifactId>my-application</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <!-- Project Information -->
    <name>My Application</name>
    <description>A sample Maven project</description>
    <url>https://github.com/user/my-application</url>
    <inceptionYear>2024</inceptionYear>

    <!-- Organization -->
    <organization>
        <name>Example Corp</name>
        <url>https://example.com</url>
    </organization>

    <!-- Licenses -->
    <licenses>
        <license>
            <name>Apache License, Version 2.0</name>
            <url>https://www.apache.org/licenses/LICENSE-2.0</url>
            <distribution>repo</distribution>
        </license>
    </licenses>

    <!-- Developers -->
    <developers>
        <developer>
            <id>dev1</id>
            <name>Developer Name</name>
            <email>dev@example.com</email>
            <organization>Example Corp</organization>
            <roles>
                <role>developer</role>
            </roles>
        </developer>
    </developers>

    <!-- SCM -->
    <scm>
        <connection>scm:git:git://github.com/user/my-application.git</connection>
        <developerConnection>scm:git:ssh://github.com/user/my-application.git</developerConnection>
        <url>https://github.com/user/my-application</url>
        <tag>HEAD</tag>
    </scm>

    <!-- Properties -->
    <properties>
        <!-- Java Version -->
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>

        <!-- Dependency Versions -->
        <spring.boot.version>3.2.0</spring.boot.version>
        <junit.version>5.10.1</junit.version>
        <lombok.version>1.18.30</lombok.version>
        <slf4j.version>2.0.9</slf4j.version>

        <!-- Plugin Versions -->
        <maven.compiler.plugin.version>3.11.0</maven.compiler.plugin.version>
        <maven.surefire.plugin.version>3.2.2</maven.surefire.plugin.version>
    </properties>

    <!-- Dependency Management -->
    <dependencyManagement>
        <dependencies>
            <!-- Spring Boot BOM -->
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring.boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <!-- Dependencies -->
    <dependencies>
        <!-- Spring Boot Starter -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${lombok.version}</version>
            <scope>provided</scope>
        </dependency>

        <!-- Logging -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>${slf4j.version}</version>
        </dependency>

        <!-- Test Dependencies -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <!-- Build Configuration -->
    <build>
        <!-- Final artifact name -->
        <finalName>${project.artifactId}</finalName>

        <!-- Resources -->
        <resources>
            <resource>
                <directory>src/main/resources</directory>
                <filtering>true</filtering>
            </resource>
        </resources>

        <!-- Plugins -->
        <plugins>
            <!-- Compiler Plugin -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${maven.compiler.plugin.version}</version>
                <configuration>
                    <source>${maven.compiler.source}</source>
                    <target>${maven.compiler.target}</target>
                </configuration>
            </plugin>

            <!-- Surefire Plugin (Tests) -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>${maven.surefire.plugin.version}</version>
            </plugin>

            <!-- Spring Boot Plugin -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <version>${spring.boot.version}</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>repackage</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>

    <!-- Profiles -->
    <profiles>
        <profile>
            <id>development</id>
            <activation>
                <activeByDefault>true</activeByDefault>
            </activation>
            <properties>
                <spring.profiles.active>dev</spring.profiles.active>
            </properties>
        </profile>

        <profile>
            <id>production</id>
            <properties>
                <spring.profiles.active>prod</spring.profiles.active>
            </properties>
        </profile>
    </profiles>

    <!-- Repositories -->
    <repositories>
        <repository>
            <id>central</id>
            <name>Maven Central</name>
            <url>https://repo.maven.apache.org/maven2</url>
        </repository>
    </repositories>
</project>
```

### Dependency Scopes
```xml
<dependencies>
    <!-- Compile (default): Available in all classpaths -->
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-lang3</artifactId>
        <version>3.14.0</version>
        <scope>compile</scope>
    </dependency>

    <!-- Provided: Available at compile time, not packaged -->
    <dependency>
        <groupId>javax.servlet</groupId>
        <artifactId>javax.servlet-api</artifactId>
        <version>4.0.1</version>
        <scope>provided</scope>
    </dependency>

    <!-- Runtime: Not needed for compilation, packaged -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.33</version>
        <scope>runtime</scope>
    </dependency>

    <!-- Test: Only for tests -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.1</version>
        <scope>test</scope>
    </dependency>

    <!-- System: From local filesystem -->
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>custom-lib</artifactId>
        <version>1.0</version>
        <scope>system</scope>
        <systemPath>${project.basedir}/lib/custom-lib.jar</systemPath>
    </dependency>

    <!-- Import: For dependency management (BOM) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>3.2.0</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencies>
```

## Project Structure

### Standard Maven Layout
```
my-app/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           ├── Main.java
│   │   │           ├── model/
│   │   │           ├── service/
│   │   │           └── repository/
│   │   ├── resources/
│   │   │   ├── application.properties
│   │   │   ├── logback.xml
│   │   │   └── db/
│   │   │       └── migration/
│   │   └── webapp/  (for web apps)
│   │       ├── WEB-INF/
│   │       │   └── web.xml
│   │       └── index.html
│   └── test/
│       ├── java/
│       │   └── com/
│       │       └── example/
│       │           └── MainTest.java
│       └── resources/
│           └── test.properties
├── target/  (generated, git-ignored)
└── .gitignore
```

### Multi-Module Project
```
parent-project/
├── pom.xml (parent)
├── module-core/
│   ├── pom.xml
│   └── src/
├── module-api/
│   ├── pom.xml
│   └── src/
├── module-web/
│   ├── pom.xml
│   └── src/
└── module-cli/
    ├── pom.xml
    └── src/
```

```xml
<!-- Parent pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>parent-project</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <modules>
        <module>module-core</module>
        <module>module-api</module>
        <module>module-web</module>
        <module>module-cli</module>
    </modules>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencyManagement>
        <dependencies>
            <!-- Shared dependency versions -->
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>3.2.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

```xml
<!-- Child module pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent-project</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <artifactId>module-core</artifactId>

    <dependencies>
        <!-- Dependencies without version (managed by parent) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
    </dependencies>
</project>
```

## Dependency Management

### Adding Dependencies
```bash
# Manually add to pom.xml
# Or search on https://mvnrepository.com

# Dependency format:
# <groupId>:<artifactId>:<version>
```

```xml
<dependency>
    <groupId>com.google.guava</groupId>
    <artifactId>guava</artifactId>
    <version>32.1.3-jre</version>
</dependency>
```

### Dependency Analysis
```bash
# Show dependency tree
mvn dependency:tree

# Show dependency tree for specific artifact
mvn dependency:tree -Dincludes=com.google.guava:guava

# Analyze dependencies
mvn dependency:analyze

# List dependencies
mvn dependency:list

# Show updates available
mvn versions:display-dependency-updates

# Show plugin updates
mvn versions:display-plugin-updates

# Purge local repository
mvn dependency:purge-local-repository
```

### Version Management
```xml
<!-- Using properties -->
<properties>
    <spring.version>5.3.31</spring.version>
    <junit.version>5.10.1</junit.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-core</artifactId>
        <version>${spring.version}</version>
    </dependency>
</dependencies>

<!-- Using BOM (Bill of Materials) -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.2.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- Dependencies without versions (from BOM) -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <!-- Version from BOM -->
    </dependency>
</dependencies>
```

### Excluding Transitive Dependencies
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>some-library</artifactId>
    <version>1.0.0</version>
    <exclusions>
        <exclusion>
            <groupId>commons-logging</groupId>
            <artifactId>commons-logging</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

## Plugin Configuration

### Common Plugins

#### Compiler Plugin
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <source>17</source>
        <target>17</target>
        <encoding>UTF-8</encoding>
        <compilerArgs>
            <arg>-parameters</arg>
            <arg>-Xlint:unchecked</arg>
        </compilerArgs>
    </configuration>
</plugin>
```

#### Surefire Plugin (Unit Tests)
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.2</version>
    <configuration>
        <includes>
            <include>**/*Test.java</include>
            <include>**/*Tests.java</include>
        </includes>
        <argLine>-Xmx1024m</argLine>
    </configuration>
</plugin>
```

#### Failsafe Plugin (Integration Tests)
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-failsafe-plugin</artifactId>
    <version>3.2.2</version>
    <executions>
        <execution>
            <goals>
                <goal>integration-test</goal>
                <goal>verify</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

#### JAR Plugin
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-jar-plugin</artifactId>
    <version>3.3.0</version>
    <configuration>
        <archive>
            <manifest>
                <addClasspath>true</addClasspath>
                <mainClass>com.example.Main</mainClass>
            </manifest>
        </archive>
    </configuration>
</plugin>
```

#### Assembly Plugin (Fat JAR)
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-assembly-plugin</artifactId>
    <version>3.6.0</version>
    <configuration>
        <descriptorRefs>
            <descriptorRef>jar-with-dependencies</descriptorRef>
        </descriptorRefs>
        <archive>
            <manifest>
                <mainClass>com.example.Main</mainClass>
            </manifest>
        </archive>
    </configuration>
    <executions>
        <execution>
            <id>make-assembly</id>
            <phase>package</phase>
            <goals>
                <goal>single</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

#### Shade Plugin (Uber JAR)
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-shade-plugin</artifactId>
    <version>3.5.1</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals>
                <goal>shade</goal>
            </goals>
            <configuration>
                <transformers>
                    <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                        <mainClass>com.example.Main</mainClass>
                    </transformer>
                </transformers>
            </configuration>
        </execution>
    </executions>
</plugin>
```

#### Exec Plugin
```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>exec-maven-plugin</artifactId>
    <version>3.1.1</version>
    <configuration>
        <mainClass>com.example.Main</mainClass>
    </configuration>
</plugin>
```

```bash
# Run with exec plugin
mvn exec:java
mvn exec:java -Dexec.mainClass="com.example.Main"
mvn exec:java -Dexec.args="arg1 arg2"
```

## Build Profiles

### Profile Configuration
```xml
<profiles>
    <!-- Development Profile -->
    <profile>
        <id>dev</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <env>development</env>
            <database.url>jdbc:h2:mem:testdb</database.url>
        </properties>
        <dependencies>
            <dependency>
                <groupId>com.h2database</groupId>
                <artifactId>h2</artifactId>
                <scope>runtime</scope>
            </dependency>
        </dependencies>
    </profile>

    <!-- Production Profile -->
    <profile>
        <id>prod</id>
        <properties>
            <env>production</env>
            <database.url>jdbc:postgresql://prod-db:5432/app</database.url>
        </properties>
        <dependencies>
            <dependency>
                <groupId>org.postgresql</groupId>
                <artifactId>postgresql</artifactId>
                <scope>runtime</scope>
            </dependency>
        </dependencies>
        <build>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <configuration>
                        <debug>false</debug>
                        <optimize>true</optimize>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    </profile>

    <!-- Test Profile -->
    <profile>
        <id>test</id>
        <properties>
            <env>test</env>
        </properties>
    </profile>
</profiles>
```

```bash
# Activate profile
mvn clean install -Pprod

# Activate multiple profiles
mvn clean install -Pdev,integration-tests

# List active profiles
mvn help:active-profiles

# Show profile-specific settings
mvn help:effective-pom -Pprod
```

## Common Issues & Solutions

### Issue: Dependency Not Found
```bash
# Error: Could not find artifact

# Solution 1: Check repository configuration
mvn dependency:tree

# Solution 2: Update Maven metadata
mvn -U clean install  # -U forces update

# Solution 3: Clear local repository
rm -rf ~/.m2/repository/com/example/problematic-artifact
mvn clean install

# Solution 4: Check network/proxy settings
# Add to ~/.m2/settings.xml
```

```xml
<settings>
    <proxies>
        <proxy>
            <id>example-proxy</id>
            <active>true</active>
            <protocol>http</protocol>
            <host>proxy.example.com</host>
            <port>8080</port>
        </proxy>
    </proxies>
</settings>
```

### Issue: Version Conflicts
```bash
# Show dependency conflicts
mvn dependency:tree -Dverbose

# Analyze dependency conflicts
mvn dependency:analyze-duplicate

# Solution: Use dependencyManagement
```

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <version>32.1.3-jre</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### Issue: Corrupted Repository
```bash
# Clean local repository
mvn dependency:purge-local-repository

# Or manually remove
rm -rf ~/.m2/repository

# Rebuild
mvn clean install
```

### Issue: Out of Memory
```bash
# Increase Maven memory
export MAVEN_OPTS="-Xmx2048m -XX:MaxPermSize=512m"

# Or set in .mavenrc
echo "MAVEN_OPTS='-Xmx2048m'" > ~/.mavenrc

# For Windows (setenv.bat)
set MAVEN_OPTS=-Xmx2048m -XX:MaxPermSize=512m
```

### Issue: Slow Builds
```bash
# Use parallel builds
mvn -T 4 clean install  # 4 threads
mvn -T 1C clean install # 1 thread per CPU core

# Skip tests
mvn clean install -DskipTests

# Offline mode (use local repository only)
mvn -o clean install

# Use incremental builds
mvn clean install -amd  # Also make dependents
```

## settings.xml Configuration

### Local Repository and Mirrors
```xml
<!-- ~/.m2/settings.xml -->
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
          http://maven.apache.org/xsd/settings-1.0.0.xsd">

    <!-- Local Repository -->
    <localRepository>${user.home}/.m2/repository</localRepository>

    <!-- Mirrors -->
    <mirrors>
        <mirror>
            <id>nexus</id>
            <name>Nexus Repository</name>
            <url>https://nexus.example.com/repository/maven-public/</url>
            <mirrorOf>*</mirrorOf>
        </mirror>
    </mirrors>

    <!-- Servers (Authentication) -->
    <servers>
        <server>
            <id>nexus-releases</id>
            <username>deployment</username>
            <password>password123</password>
        </server>
    </servers>

    <!-- Profiles -->
    <profiles>
        <profile>
            <id>nexus</id>
            <repositories>
                <repository>
                    <id>central</id>
                    <url>https://nexus.example.com/repository/maven-public/</url>
                    <releases><enabled>true</enabled></releases>
                    <snapshots><enabled>true</enabled></snapshots>
                </repository>
            </repositories>
        </profile>
    </profiles>

    <activeProfiles>
        <activeProfile>nexus</activeProfile>
    </activeProfiles>
</settings>
```

## Testing Configuration

### JUnit 5
```xml
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.1</version>
        <scope>test</scope>
    </dependency>

    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>5.7.0</version>
        <scope>test</scope>
    </dependency>

    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.24.2</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### Code Coverage (JaCoCo)
```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>PACKAGE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

```bash
# Generate coverage report
mvn clean test jacoco:report

# View report at target/site/jacoco/index.html
```

## CI/CD Configuration

### GitHub Actions
```yaml
name: Maven Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: 'maven'

    - name: Build with Maven
      run: mvn clean install -B

    - name: Run tests
      run: mvn test

    - name: Generate coverage report
      run: mvn jacoco:report

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./target/site/jacoco/jacoco.xml
```

### GitLab CI
```yaml
image: maven:3.9-eclipse-temurin-17

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"

cache:
  paths:
    - .m2/repository

stages:
  - build
  - test
  - package

build:
  stage: build
  script:
    - mvn compile

test:
  stage: test
  script:
    - mvn test
    - mvn jacoco:report
  artifacts:
    reports:
      junit:
        - target/surefire-reports/TEST-*.xml
    paths:
      - target/site/jacoco

package:
  stage: package
  script:
    - mvn package -DskipTests
  artifacts:
    paths:
      - target/*.jar
```

## Best Practices Summary

### Project Organization
- Follow standard Maven directory layout
- Use multi-module structure for large projects
- Keep pom.xml clean and organized
- Use properties for version management
- Document custom configuration

### Dependency Management
- Use dependencyManagement for version control
- Prefer BOMs for framework dependencies
- Minimize dependencies
- Regularly update dependencies
- Use appropriate scopes
- Exclude unnecessary transitive dependencies

### Build Configuration
- Use build profiles for different environments
- Configure plugins properly
- Use appropriate packaging type
- Set Java version explicitly
- Enable parallel builds when possible

### Testing
- Separate unit and integration tests
- Use JaCoCo for code coverage
- Set coverage thresholds
- Run tests in CI/CD pipeline
- Use appropriate test frameworks

### Performance
- Use parallel builds (-T)
- Enable offline mode when possible
- Use Maven repository manager (Nexus/Artifactory)
- Configure appropriate memory settings
- Cache dependencies in CI/CD

## Quick Reference Commands

```bash
# Project lifecycle
mvn clean                    # Clean build artifacts
mvn compile                  # Compile source code
mvn test                     # Run tests
mvn package                  # Create JAR/WAR
mvn install                  # Install to local repo
mvn deploy                   # Deploy to remote repo

# Dependency management
mvn dependency:tree          # Show dependency tree
mvn dependency:analyze       # Analyze dependencies
mvn versions:display-dependency-updates  # Check for updates

# Running
mvn exec:java                # Run main class
mvn spring-boot:run          # Run Spring Boot app

# Profiles
mvn clean install -Pprod     # Activate profile

# Options
mvn clean install -DskipTests      # Skip tests
mvn clean install -T 4             # Parallel build
mvn clean install -U               # Force update
mvn clean install -o               # Offline mode

# Information
mvn help:effective-pom       # Show effective POM
mvn help:active-profiles     # Show active profiles
```

## Notes

- Always use dependencyManagement for multi-module projects
- Keep Maven version up to date
- Use Maven Wrapper (mvnw) for consistent builds
- Configure settings.xml for organization-wide settings
- Use profiles for environment-specific configuration
- Enable parallel builds for faster compilation
- Set up repository manager for better performance
- Use BOMs to manage framework versions
- Document custom plugin configurations
- Regularly audit and update dependencies
