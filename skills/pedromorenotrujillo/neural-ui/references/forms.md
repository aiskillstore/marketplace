# Forms and Signal Forms

Neural v2 signal controls implement Angular's Signal Forms control contracts. They do not implement ControlValueAccessor. Do not attach ngModel, formControl or formControlName to them. An application can retain reactive forms elsewhere; do not force the old binding onto a Neural signal control.

Start from the compiled [forms.ts](../examples/forms.ts). It imports FormField, form, required and minLength from @angular/forms/signals and NeuInputComponent from /input. The application signal owns the data; form creates a stable field tree; [formField] connects the Neural control to the field.

Use one value owner for a control: FormField or its documented model binding. Never add [value]/valueChange on the same control already owned by FormField. The example's separate Select illustrates explicit model binding instead.

Keep the field tree stable. Declare it once, not in a getter or template expression. Apply validation through the schema. Distinguish invalid, pending, touched and dirty: an empty required control can be invalid before interaction. Choose application error text based on the actual field errors and the intended display policy. The sample's single text message is deliberately simple.

Reset through the field state API when interaction state must reset too. Merely replacing the model's data does not express the same reset. A reset required field remains invalid if its reset value is empty. In the sample, fields.name().reset('') resets both value and touched/dirty state.

For disabled and readonly behavior, check Angular's Signal Forms schema rules and the individual Neural control's inputs. Do not equate readonly with disabled or attach competing owners for the same state. Model value types vary: inspect [input](api/input.md), [checkbox](api/checkbox.md), [switch](api/switch.md), [select](api/select.md), [date-input](api/date-input.md) and [option-api](api/option-api.md) for the specific control. Never assume all controls expose value or the same nullability.

For Select, use typed optionLabel/optionValue accessors and an explicit mode. Single mode emits a scalar or null; multiple mode uses a readonly value array. Preserve the application's domain identity and compareWith rules when objects are used. Do not copy v1 optionLabel strings into function-based APIs without checking the current declaration.

For a custom native input in a Neural form shell, connect label and input IDs using NeuFormFieldComponent's forId and the native input id. The shell does not turn an arbitrary control into a Signal Forms control.

Sources: [Neural v2 Signal Forms](https://ui.neuralui.org/v2/en/foundations/signal-forms), [Angular Signal Forms](https://angular.dev/guide/forms/signals/overview).
