---
name: allra-database-schema
description: Allra 데이터베이스 설계 및 QueryDSL 사용 규칙. Use when creating JPA entities, writing QueryDSL queries, or adding @Transactional annotations.
---

# Allra Database 설계 및 QueryDSL 규칙

Allra 백엔드 팀의 데이터베이스 설계, JPA, QueryDSL, 트랜잭션 관리 표준을 정의합니다.

## 프로젝트 기본 정보

이 가이드는 다음 환경을 기준으로 작성되었습니다:

- **Java**: 17 이상
- **Spring Boot**: 3.2 이상
- **ORM**: JPA/Hibernate
- **Query Library**: QueryDSL (선택 사항)
- **Testing**: Testcontainers (선택 사항)

**참고**: 프로젝트별로 사용하는 데이터베이스(MariaDB, PostgreSQL, MySQL 등)와 라이브러리가 다를 수 있습니다.

## QueryDSL 사용 규칙

### 1. Repository 구조 (Allra 권장 패턴)

JPA Repository와 Support 인터페이스를 함께 사용:

```java
// JPA Repository 인터페이스
public interface UserRepository extends JpaRepository<User, Long>, UserRepositorySupport {
}

// QueryDSL Support 인터페이스
public interface UserRepositorySupport {
    List<UserSummaryDto> findUserSummaries(UserSearchCondition condition);
}

// QueryDSL Support 구현체
@Repository
public class UserRepositoryImpl implements UserRepositorySupport {

    private final JPAQueryFactory queryFactory;

    @Override
    public List<UserSummaryDto> findUserSummaries(UserSearchCondition condition) {
        return queryFactory
            .select(new QUserSummaryDto(
                user.id,
                user.email,
                user.name
            ))
            .from(user)
            .where(
                emailContains(condition.email()),
                nameContains(condition.name())
            )
            .fetch();
    }

    private BooleanExpression emailContains(String email) {
        return email != null ? user.email.contains(email) : null;
    }
}
```

**참고**: Support 패턴은 선택 사항입니다. 프로젝트에 따라 `@Query` 어노테이션이나 다른 방식을 사용할 수 있습니다.

### 2. QueryDSL DTO Projection

Record와 `@QueryProjection` 사용:

```java
public record UserSummaryDto(
    Long id,
    String email,
    String name
) {
    @QueryProjection
    public UserSummaryDto {}
}
```

**빌드 설정**:

Gradle:
```gradle
annotationProcessor "com.querydsl:querydsl-apt:${queryDslVersion}:jakarta"
```

Maven:
```xml
<plugin>
    <groupId>com.mysema.maven</groupId>
    <artifactId>apt-maven-plugin</artifactId>
    <version>1.1.3</version>
    <executions>
        <execution>
            <goals>
                <goal>process</goal>
            </goals>
            <configuration>
                <outputDirectory>target/generated-sources/java</outputDirectory>
                <processor>com.querydsl.apt.jpa.JPAAnnotationProcessor</processor>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### 3. From 절에 맞는 Repository 위치

From절에 해당하는 Repository에 정의하는 것을 권장:

```java
// ❌ 피하기: Order에서 User를 조회
public interface OrderRepositorySupport {
    List<UserDto> findUsersByOrderDate(LocalDate date); // From user
}

// ✅ 권장: User에서 Order를 조인
public interface UserRepositorySupport {
    List<UserOrderDto> findUsersWithOrders(LocalDate date); // From user
}
```

### 4. 데이터베이스 호환성

QueryDSL 작성 시 사용 중인 데이터베이스의 특성을 고려:

```java
// 일반적인 쿼리
queryFactory
    .selectFrom(user)
    .where(user.createdAt.between(startDate, endDate))
    .fetch();

// LIMIT/OFFSET
queryFactory
    .selectFrom(user)
    .limit(10)
    .offset(0)
    .fetch();
```

**참고**: 윈도우 함수나 특정 DB 함수는 데이터베이스 버전에 따라 지원 여부가 다를 수 있습니다.

### 5. xxxRepositorySupport 직접 의존 금지

**반드시** JPA Repository 인터페이스를 통해 사용:

```java
// ❌ 잘못된 예
@Service
public class UserService {
    private final UserRepositoryImpl userRepositoryImpl; // 구현체 직접 주입
}

// ✅ 올바른 예
@Service
public class UserService {
    private final UserRepository userRepository; // 인터페이스 주입
}
```

## @Transactional 사용 가이드

### 필수 규칙

각 서비스 메서드에 명시적으로 선언:

1. **조회 쿼리만**: `@Transactional(readOnly = true)`
2. **변경 쿼리 포함**: `@Transactional`

### 예제

```java
@Service
public class UserService {

    private final UserRepository userRepository;

    // 읽기 전용 트랜잭션
    @Transactional(readOnly = true)
    public List<User> findAllUsers() {
        return userRepository.findAll();
    }

    // 쓰기 트랜잭션
    @Transactional
    public User createUser(SignUpRequest request) {
        User user = User.create(request.email(), request.password());
        return userRepository.save(user);
    }

    // 조회 + 변경
    @Transactional
    public User activateUser(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
        user.activate(); // 변경
        return user;
    }
}
```

**참고**: 트랜잭션 전파(Propagation)는 기본값(`REQUIRED`)을 사용하며, 특수한 경우에만 명시합니다.

## JPA Entity 설계 가이드

### 기본 구조

```java
@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 100)
    private String name;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private UserStatus status;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    // 정적 팩토리 메서드
    public static User create(String email, String password, String name) {
        User user = new User();
        user.email = email;
        user.password = password;
        user.name = name;
        user.status = UserStatus.ACTIVE;
        return user;
    }

    // 비즈니스 메서드
    public void activate() {
        this.status = UserStatus.ACTIVE;
    }
}
```

### 연관관계 매핑

```java
@Entity
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // ManyToOne - 지연 로딩 권장
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    // OneToMany - 지연 로딩, Cascade 설정
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    // 연관관계 편의 메서드
    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }
}
```

**참고**: 연관관계는 지연 로딩(LAZY)을 기본으로 사용하는 것을 권장합니다.

## When to Use This Skill

이 skill은 다음 상황에서 자동으로 적용됩니다:

- JPA Entity 생성 및 수정
- QueryDSL 쿼리 작성
- Repository 인터페이스 및 구현체 작성
- Service 메서드에 @Transactional 추가
- DTO Projection 작성

## Checklist

데이터베이스 관련 코드 작성 시 확인사항:

- [ ] QueryDSL Support가 JPA Repository에 상속되어 있는가? (Support 패턴 사용 시)
- [ ] QueryDSL 구현체가 From절에 맞는 Repository에 있는가?
- [ ] DTO Projection에 @QueryProjection이 적용되었는가? (QueryDSL 사용 시)
- [ ] Service의 모든 public 메서드에 @Transactional이 명시되었는가?
- [ ] 읽기 전용 메서드에 readOnly = true가 적용되었는가?
- [ ] MariaDB 호환성을 고려했는가?
- [ ] Entity의 연관관계가 지연 로딩(LAZY)으로 설정되었는가?
- [ ] xxxRepositorySupport 구현체를 직접 주입하지 않았는가?
