# Science Domain Profile

> For physics, chemistry, biology, mathematics, and related scientific topics.

---

## Search Strategy

### Primary Sources

1. **Research Papers**
   - arXiv (physics, math, CS)
   - PubMed (life sciences)
   - Google Scholar
   - ResearchGate

2. **Textbooks & References**
   - University-level textbooks
   - Reference handbooks
   - Online open textbooks (OpenStax, MIT OCW)

3. **Educational Platforms**
   - Khan Academy
   - Coursera/edX course materials
   - 3Blue1Brown (mathematics)
   - PhET Simulations

4. **Scientific Organizations**
   - NIST (standards, constants)
   - NASA (space science)
   - CERN (particle physics)
   - Korean science institutions (KIST, KAIST)

### Search Query Patterns

```
"{topic} textbook PDF"
"{topic} lecture notes"
"{topic} arXiv"
"{topic} derivation proof"
"{topic} experiment demonstration"
"{topic} simulation interactive"
"{topic} problem set solutions"
"{topic} Khan Academy"
"{topic} 대학 강의"
```

### Quality Indicators

- Peer-reviewed sources
- Clear mathematical rigor
- Reproducible experiments
- Recent for cutting-edge topics
- Foundational for classic topics

---

## Special Fields

### Equations

| Field                 | Description               | Example             |
| --------------------- | ------------------------- | ------------------- |
| `equation_format`     | Notation system           | LaTeX               |
| `key_equations`       | Important formulas        | E = mc², F = ma     |
| `notation_style`      | Notation conventions      | SI units, bra-ket   |
| `computational_tools` | Software for calculations | Python, Mathematica |

### Lab Requirements

| Field                  | Description         | Example              |
| ---------------------- | ------------------- | -------------------- |
| `lab_type`             | Type of experiments | 화학 실험, 물리 측정 |
| `equipment`            | Required equipment  | 분광기, 오실로스코프 |
| `safety_protocols`     | Safety requirements | 보호 장비, 환기      |
| `virtual_alternatives` | Online simulations  | PhET, ChemCollective |

### Prerequisites

| Field             | Description             | Example                  |
| ----------------- | ----------------------- | ------------------------ |
| `math_prereqs`    | Required math           | 미적분, 선형대수         |
| `science_prereqs` | Prior science knowledge | 고전역학, 일반화학       |
| `skill_prereqs`   | Practical skills        | 그래프 해석, 데이터 분석 |

---

## Terminology Policy

### Language Handling

| Type             | Policy                   | Example                |
| ---------------- | ------------------------ | ---------------------- |
| Scientific terms | 한국어 + English         | 운동량(momentum)       |
| Equations        | Universal notation       | $$\vec{F} = m\vec{a}$$ |
| Units            | SI 단위 + CGS 병기       | 10 N (= 10⁶ dyne)      |
| Greek letters    | Spelled out on first use | 람다(λ, lambda)        |

### First Occurrence Format

```markdown
## 슈뢰딩거 방정식 (Schrödinger Equation)

슈뢰딩거 방정식은 양자역학에서 파동함수의 시간 변화를 기술합니다:

$$i\hbar\frac{\partial}{\partial t}\Psi = \hat{H}\Psi$$

여기서 $\Psi$는 파동함수(wave function), $\hat{H}$는 해밀토니안 연산자(Hamiltonian operator)입니다.
```

### Citation Format

```markdown
> Griffiths, D. J. (2018). _Introduction to Quantum Mechanics_ (3rd ed.). Cambridge University Press.

> arXiv:2301.12345 [physics.quant-ph]
```

---

## Content Structure

### Recommended Organization

```
1. 개념 도입
   - 역사적 배경과 동기
   - 핵심 질문/문제
   - 직관적 설명

2. 수학적 형식화
   - 기본 정의와 공리
   - 주요 정리와 증명
   - 유도 과정

3. 예제와 문제 풀이
   - 단순화된 예제
   - 점진적 복잡도
   - 풀이 전략

4. 실험/응용
   - 실험적 검증
   - 실생활 응용
   - 현대 연구 동향

5. 연습 문제
   - 개념 확인 문제
   - 계산 문제
   - 심화 문제
```

### Equation Format

Using LaTeX for mathematical expressions:

```markdown
## 인라인 수식

뉴턴의 제2법칙은 $F = ma$로 표현됩니다.

## 블록 수식

운동에너지와 위치에너지의 관계:

$$E_{total} = \frac{1}{2}mv^2 + mgh$$

## 정렬된 수식

미분 과정:

$$
\begin{align}
\frac{d}{dt}(mv) &= F \\
m\frac{dv}{dt} &= F \\
ma &= F
\end{align}
$$
```

### Problem Set Format

```markdown
## 연습문제

### 문제 1 (기초)

질량 2 kg인 물체에 10 N의 힘이 작용할 때 가속도를 구하시오.

<details>
<summary>풀이 보기</summary>

$$a = \frac{F}{m} = \frac{10\,\text{N}}{2\,\text{kg}} = 5\,\text{m/s}^2$$

</details>

### 문제 2 (심화)

포물선 운동에서 최대 높이와 수평 도달 거리의 관계를 유도하시오.
```

---

## Diagram Requirements

Scientific diagrams should include:

```markdown
<!-- 다이어그램 설명 -->

![자유물체도](diagrams/free-body-diagram.svg)

**그림 1**: 경사면 위 물체의 자유물체도

- 중력 $mg$는 아래 방향
- 수직항력 $N$은 경사면에 수직
- 마찰력 $f$는 운동 반대 방향
```

---

## Safety Notes

For laboratory-related content:

```markdown
> ⚠️ **안전 주의사항**
>
> 이 실험에서는 다음 안전 수칙을 준수해야 합니다:
>
> - 보안경 착용 필수
> - 환기가 잘 되는 곳에서 실험
> - 산/염기 취급 시 장갑 착용
> - 비상 샤워 및 세안 시설 위치 확인
```

---

## Review Criteria

Review criteria for the reviewer agent when evaluating science domain documents.

### Critical Checks (ERROR if failed)

These issues trigger `NEEDS_REVISION` status:

| Check | Detection | Example |
|-------|-----------|---------|
| Equation format errors | Malformed LaTeX | Unbalanced `$$`, missing `\` for commands |
| Unit inconsistency | Mixed SI/CGS without conversion | Using both N and dyne without relationship |
| Mathematical errors | Incorrect derivations | Wrong integration/differentiation steps |
| Safety omissions | Missing lab safety notes | Dangerous procedures without warnings |

### Quality Checks (WARN if issues)

These issues are noted but don't block publication:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Variable definitions | All symbols defined on first use | $\Psi$ is wave function |
| Step-by-step derivations | Key steps shown, not skipped | Major algebraic steps included |
| Worked examples | 2+ examples per concept | Increasing difficulty progression |
| Prerequisite references | Prior knowledge stated | "미적분 기초 필요" |

### Style Checks (INFO)

Minor issues for optional improvement:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Bilingual terminology | 한국어(English) format | 운동량(momentum) |
| SI unit preference | SI primary, others secondary | 10 N (= 10⁶ dyne) |
| Greek letter spelling | First use spelled out | 람다(λ, lambda) |
| Equation numbering | Numbered for reference | Eq. (1), (2) style |

### Equation Format Validation

```markdown
# LaTeX format checklist:

□ Inline math: Single $ delimiters - $E = mc^2$
□ Block math: Double $$ or equation environment
□ Aligned equations: \begin{align} for multi-line
□ Units: \text{} for unit names - $v = 10\,\text{m/s}$
□ Vectors: \vec{} notation - $\vec{F} = m\vec{a}$
```

---

## Domain-Specific Sections for persona.md

```markdown
## Domain Guidelines: Science

**Equation Format**: LaTeX ($$..$$ 블록, $..$$ 인라인)
**Lab Safety**: {LAB_SAFETY_REQUIRED} 필수 포함
**Prerequisites**: {MATH_PREREQS} 기초 가정

**Mathematical Rigor**:

- 정의와 정리 명확히 구분
- 증명 과정 단계별 제시
- 수식 유도 과정 포함

**Experimental Approach**:

- 실험 목적과 원리 설명
- 측정 불확도 고려
- 데이터 분석 방법 제시

**Problem-Based Learning**:

- 개념당 2-3개 예제 문제
- 난이도별 연습문제 제공
- 풀이 과정 상세 설명
```
