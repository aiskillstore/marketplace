# Типы вопросов WebAsk и их поля

Справочник к навыку `webask-quiz-from-brief`. Открывать, когда нужного типа нет в
таблице подбора внутри `SKILL.md` или когда нужно настроить поведение вопроса
точнее.

Поля перечислены основные — те, что действительно меняют поведение. Полная схема
приходит в ответе `get_quiz_structure` у уже существующего опроса: если сомневаешься
в имени поля, посмотри там на живом примере.

## Ответ текстом и числом

| Тип | Что это | Основные поля |
|---|---|---|
| `input` | однострочный или многострочный ответ | `inputPlaceholder`, `inputIsTextarea`, `inputLimitMin`, `inputLimitMax` |
| `number` | число | `numberMin`, `numberMax`, `inputPlaceholder` |
| `fio` | имя с разбором на части | `fioWithPatronymic`, `fioSurnamePlaceholder`, `fioNamePlaceholder` |
| `email` | почта с проверкой формата | `emailPlaceholder`, `emailWidth` |
| `phone` | телефон с выбором страны | `phoneDefaultCountry`, `phoneStrictValidation`, `phoneAllowedCountries`, `phoneHideCountrySelector` |
| `datetime` | дата и время | `dateTimeType`, `dateTimeFormatOfDate`, `dateTimeFormatOfTime` |

## Выбор

| Тип | Что это | Основные поля |
|---|---|---|
| `dropdown` | выбор из списка, одиночный или множественный | `dropdownMultiple`, `dropdownOther`, `dropdownRandomize`, `dropdownEntities`, `dropdownScores`, `noneOfAbove` |
| `yesno` | да или нет | `yesNoIcon`, `yesNoTextEntities` |
| `ranking` | расставить по порядку | `rankingEntities`, `rankingRandomize`, `rankingWithImages` |
| `pair` | попарное сравнение | `pairItemEntities`, `pairShowImages`, `pairStepByStep` |

`carryForward` у `dropdown` и `ranking` переносит в вопрос варианты, выбранные
респондентом раньше.

## Оценки и шкалы

| Тип | Что это | Основные поля |
|---|---|---|
| `rating` | звёзды, сердечки, смайлы | `ratingCount`, `ratingFigure`, `ratingStartValue`, `ratingScores` |
| `scale` | числовая шкала с подписями краёв | `scaleCount`, `scaleStartValue`, `scaleLabelLeft`, `scaleLabelRight`, `scaleScores` |
| `nps` | шкала готовности рекомендовать | те же поля, что у `scale` |
| `slider` | ползунок | `sliderMin`, `sliderMax`, `sliderStep` |
| `matrix` | набор оценок по одному списку критериев | `matrixChoiceType`, `matrixRowEntities`, `matrixColEntities`, `matrixIsAllRequired` |

`nps` — не то же самое, что `scale` с десятью делениями: у него своя аналитика в
отчётах. Для «насколько вероятно, что порекомендуете» брать именно `nps`.

## Файлы, карта, встроенное

| Тип | Что это | Основные поля |
|---|---|---|
| `file` | загрузка файла или фото | `fileFormats` |
| `map` | метка на карте | `mapCenterLat`, `mapCenterLng`, `mapZoom`, `mapTheme`, `mapMinMarks`, `mapMaxMarks` |
| `html` | свой блок разметки | `htmlCode`, `htmlIsEmbedded` |
| `booking` | запись на встречу по расписанию | `bookingSchedulerId`, `bookingNameWidgetId`, `bookingPhoneWidgetId` |
| `payment` | оплата внутри опроса | `paymentFixedAmount`, `paymentTypes`, `paymentYookassaAccountId` |

`booking` и `payment` требуют настроек, которые заводят в кабинете: расписание и
счёт продавца. Без них вопрос не заработает — предупредить об этом человека, а не
добавлять молча.

## Экраны без вопроса

| Тип | Что это | Основные поля |
|---|---|---|
| `welcome` | приветственный экран | `welcomeLabel`, `welcomeWithQuestionCount`, `welcomeWithResponseTime` |
| `message` | текстовый экран между вопросами | `messageLabel`, `messageWithButton` |
| `submit` | экран отправки с согласием на обработку | `submitTerms`, `submitTermsText`, `submitLabel` |
| `finish` | страница благодарности | `finishLabel`, `finishAnswerText`, `finishNextUrl`, `promoCode`, `maxScore` |
| `screenout` | отсев: конец для неподходящих респондентов | `finishLabel`, `finishNextUrl` |

`finish` обязателен: без него респондент после последнего вопроса упирается в
пустую страницу.

`screenout` нужен, когда часть людей не подходит под исследование — их правильнее
вежливо остановить, чем гнать до конца и потом чистить ответы.

## Что часто путают

- **Оценку не собирают текстом.** `input` с просьбой «поставьте оценку от 1 до 5»
  ломает всю аналитику: в отчёте будет список строк вместо среднего.
- **Список вариантов не собирают текстом.** Свободные ответы не сгруппировать, и
  «Москва», «москва» и «мск» станут тремя разными вариантами.
- **Телефон и почта — свои типы.** У них проверка формата; собранные через `input`
  контакты наполовину нерабочие.
- **Десять однотипных оценок — это `matrix`,** а не десять `rating` подряд: так
  короче для респондента и нагляднее в отчёте.
