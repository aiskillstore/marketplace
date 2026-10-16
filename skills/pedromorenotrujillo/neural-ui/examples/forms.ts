import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { FormField, form, minLength, required } from '@angular/forms/signals';
import { NeuInputComponent } from '@neural-ui/core/input';
import { NeuSelectComponent } from '@neural-ui/core/select';
import { NeuButtonComponent } from '@neural-ui/core/button';

@Component({
  selector: 'example-forms',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [FormField, NeuInputComponent, NeuSelectComponent, NeuButtonComponent],
  template: `
    <section aria-labelledby="forms-heading">
      <h2 id="forms-heading">Signal Forms</h2>
      <neu-input label="Name" inputId="customer-name" [formField]="fields.name"
        [errorMessage]="fields.name().touched() && fields.name().invalid() ? 'Enter at least 3 characters' : ''" />
      <output data-testid="name-value">{{ model().name }}</output>
      <output data-testid="name-state">{{ fields.name().touched() }} / {{ fields.name().dirty() }} / {{ fields.name().valid() }}</output>
      <button neu-button type="button" (neuClick)="fields.name().reset('')">Reset name</button>
      <h3>Explicit model binding</h3>
      <neu-select label="Region" mode="single" [options]="regions" [optionLabel]="regionLabel"
        [optionValue]="regionValue" [value]="region()" (valueChange)="region.set($event)" />
      <output data-testid="region-value">{{ region() }}</output>
    </section>
  `,
})
export class FormsExample {
  readonly model = signal({ name: '' });
  readonly fields = form(this.model, schema => {
    required(schema.name);
    minLength(schema.name, 3);
  });
  readonly regions = [{ id: 'eu', name: 'Europe' }, { id: 'am', name: 'Americas' }];
  readonly regionLabel = (region: (typeof this.regions)[number]) => region.name;
  readonly regionValue = (region: (typeof this.regions)[number]) => region.id;
  readonly region = signal<string | null>(null);
}
