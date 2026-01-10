---
name: "@delon/form Dynamic Schema Forms"
description: "Create dynamic schema-based forms using @delon/form (SF component). Use this skill when building complex forms with validation, conditional rendering, async data loading, custom widgets, and multi-step workflows. Ensures forms follow JSON Schema standards, integrate with Angular reactive forms, support internationalization, and maintain consistent validation patterns across the application."
license: "MIT"
---

# @delon/form Dynamic Schema Forms Skill

This skill helps create dynamic forms using @delon/form's SF (Schema Form) component.

## Core Principles

### Schema-Driven Forms
- **JSON Schema**: Define forms declaratively with JSON Schema
- **Type Safety**: Full TypeScript support for schema definitions
- **Validation**: Built-in validation with custom validators
- **Dynamic Rendering**: Conditional fields based on form state

### Key Features
- Automatic form generation from schema
- Custom widgets for specialized inputs
- Async data loading (dropdowns, autocomplete)
- Multi-step forms (wizards)
- Responsive grid layouts
- Internationalization support

## Basic Schema Form

```typescript
import { Component, signal, output } from '@angular/core';
import { SFSchema, SFComponent, SFUISchema } from '@delon/form';
import { SHARED_IMPORTS } from '@shared';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [SHARED_IMPORTS, SFComponent],
  template: `
    <sf 
      [schema]="schema"
      [ui]="ui"
      [formData]="initialData()"
      [loading]="loading()"
      (formSubmit)="handleSubmit($event)"
      (formChange)="handleChange($event)"
      (formError)="handleError($event)"
    />
  `
})
export class UserFormComponent {
  loading = signal(false);
  initialData = signal<any>({});
  formSubmit = output<any>();
  
  schema: SFSchema = {
    properties: {
      name: {
        type: 'string',
        title: 'Full Name',
        maxLength: 100
      },
      email: {
        type: 'string',
        title: 'Email',
        format: 'email'
      },
      age: {
        type: 'number',
        title: 'Age',
        minimum: 18,
        maximum: 120
      },
      role: {
        type: 'string',
        title: 'Role',
        enum: ['admin', 'member', 'viewer'],
        default: 'member'
      }
    },
    required: ['name', 'email', 'role']
  };
  
  ui: SFUISchema = {
    '*': {
      spanLabel: 6,
      spanControl: 18,
      grid: { span: 24 }
    },
    $name: {
      placeholder: 'Enter full name',
      widget: 'string'
    },
    $email: {
      placeholder: 'user@example.com',
      widget: 'string'
    },
    $age: {
      widget: 'number'
    },
    $role: {
      widget: 'select',
      placeholder: 'Select role'
    }
  };
  
  handleSubmit(value: any): void {
    console.log('Form submitted:', value);
    this.formSubmit.emit(value);
  }
  
  handleChange(value: any): void {
    console.log('Form changed:', value);
  }
  
  handleError(errors: any): void {
    console.error('Form errors:', errors);
  }
}
```

## Common Widgets

### String Input
```typescript
{
  name: {
    type: 'string',
    title: 'Name',
    ui: {
      widget: 'string',
      placeholder: 'Enter name',
      prefix: 'User',
      suffix: '@',
      maxLength: 100
    }
  }
}
```

### Textarea
```typescript
{
  description: {
    type: 'string',
    title: 'Description',
    ui: {
      widget: 'textarea',
      autosize: { minRows: 3, maxRows: 6 },
      placeholder: 'Enter description'
    }
  }
}
```

### Number Input
```typescript
{
  amount: {
    type: 'number',
    title: 'Amount',
    minimum: 0,
    maximum: 1000000,
    ui: {
      widget: 'number',
      precision: 2,
      prefix: '$',
      formatter: (value: number) => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    }
  }
}
```

### Date Picker
```typescript
{
  birthDate: {
    type: 'string',
    title: 'Birth Date',
    format: 'date',
    ui: {
      widget: 'date',
      mode: 'date',
      displayFormat: 'yyyy-MM-dd',
      end: 'today' // Can't select future dates
    }
  }
}
```

### Date Range
```typescript
{
  dateRange: {
    type: 'string',
    title: 'Date Range',
    ui: {
      widget: 'date',
      mode: 'range',
      displayFormat: 'yyyy-MM-dd'
    }
  }
}
```

### Select Dropdown
```typescript
{
  category: {
    type: 'string',
    title: 'Category',
    enum: [
      { label: 'Technology', value: 'tech' },
      { label: 'Business', value: 'business' },
      { label: 'Science', value: 'science' }
    ],
    ui: {
      widget: 'select',
      placeholder: 'Select category',
      allowClear: true,
      showSearch: true
    }
  }
}
```

### Multi-Select
```typescript
{
  tags: {
    type: 'array',
    title: 'Tags',
    items: {
      type: 'string',
      enum: ['angular', 'react', 'vue', 'typescript']
    },
    ui: {
      widget: 'select',
      mode: 'multiple',
      placeholder: 'Select tags'
    }
  }
}
```

### Autocomplete
```typescript
{
  city: {
    type: 'string',
    title: 'City',
    ui: {
      widget: 'autocomplete',
      asyncData: () => this.loadCities(),
      debounceTime: 300,
      placeholder: 'Search city'
    }
  }
}

private async loadCities(): Promise<any[]> {
  return [
    { label: 'New York', value: 'ny' },
    { label: 'Los Angeles', value: 'la' },
    { label: 'Chicago', value: 'chi' }
  ];
}
```

### Radio Buttons
```typescript
{
  priority: {
    type: 'string',
    title: 'Priority',
    enum: [
      { label: 'Low', value: 'low' },
      { label: 'Medium', value: 'medium' },
      { label: 'High', value: 'high' }
    ],
    default: 'medium',
    ui: {
      widget: 'radio',
      styleType: 'button' // or 'default'
    }
  }
}
```

### Checkbox
```typescript
{
  agree: {
    type: 'boolean',
    title: 'Agree to terms',
    ui: {
      widget: 'checkbox'
    }
  }
}
```

### Switch
```typescript
{
  isActive: {
    type: 'boolean',
    title: 'Active Status',
    ui: {
      widget: 'switch',
      checkedChildren: 'On',
      unCheckedChildren: 'Off'
    }
  }
}
```

### Slider
```typescript
{
  rating: {
    type: 'number',
    title: 'Rating',
    minimum: 0,
    maximum: 100,
    ui: {
      widget: 'slider',
      marks: {
        0: '0',
        50: '50',
        100: '100'
      }
    }
  }
}
```

### File Upload
```typescript
{
  avatar: {
    type: 'string',
    title: 'Avatar',
    ui: {
      widget: 'upload',
      action: '/api/upload',
      accept: 'image/*',
      limit: 1,
      listType: 'picture-card'
    }
  }
}
```

## Async Data Loading

### Dynamic Dropdown Options
```typescript
{
  assignee: {
    type: 'string',
    title: 'Assignee',
    ui: {
      widget: 'select',
      asyncData: () => this.loadUsers(),
      placeholder: 'Select user'
    }
  }
}

private async loadUsers(): Promise<any[]> {
  const users = await this.userService.getUsers();
  return users.map(u => ({
    label: u.name,
    value: u.id
  }));
}
```

### Cascading Selects
```typescript
{
  country: {
    type: 'string',
    title: 'Country',
    ui: {
      widget: 'select',
      asyncData: () => this.loadCountries(),
      change: (value: string) => this.onCountryChange(value)
    }
  },
  city: {
    type: 'string',
    title: 'City',
    ui: {
      widget: 'select',
      asyncData: () => this.loadCities(this.selectedCountry())
    }
  }
}

private selectedCountry = signal<string>('');

onCountryChange(value: string): void {
  this.selectedCountry.set(value);
}
```

## Conditional Fields

### Show/Hide Based on Value
```typescript
schema: SFSchema = {
  properties: {
    userType: {
      type: 'string',
      title: 'User Type',
      enum: ['individual', 'company']
    },
    // Show only for companies
    companyName: {
      type: 'string',
      title: 'Company Name',
      ui: {
        visibleIf: {
          userType: ['company']
        }
      }
    },
    // Show only for individuals
    firstName: {
      type: 'string',
      title: 'First Name',
      ui: {
        visibleIf: {
          userType: ['individual']
        }
      }
    }
  }
};
```

## Custom Validators

```typescript
import { SFSchema } from '@delon/form';

schema: SFSchema = {
  properties: {
    password: {
      type: 'string',
      title: 'Password',
      ui: {
        type: 'password',
        validator: (value: string, formProperty: any, form: any) => {
          if (value.length < 8) {
            return [{ keyword: 'minLength', message: 'Password must be at least 8 characters' }];
          }
          if (!/[A-Z]/.test(value)) {
            return [{ keyword: 'uppercase', message: 'Password must contain uppercase letter' }];
          }
          return [];
        }
      }
    },
    confirmPassword: {
      type: 'string',
      title: 'Confirm Password',
      ui: {
        type: 'password',
        validator: (value: string, formProperty: any, form: any) => {
          if (value !== form.value.password) {
            return [{ keyword: 'match', message: 'Passwords must match' }];
          }
          return [];
        }
      }
    }
  }
};
```

## Multi-Step Forms (Wizards)

```typescript
import { Component, signal } from '@angular/core';
import { SFSchema } from '@delon/form';

@Component({
  selector: 'app-wizard-form',
  template: `
    <nz-steps [nzCurrent]="currentStep()">
      <nz-step nzTitle="Basic Info" />
      <nz-step nzTitle="Address" />
      <nz-step nzTitle="Confirmation" />
    </nz-steps>
    
    @switch (currentStep()) {
      @case (0) {
        <sf [schema]="basicInfoSchema" (formSubmit)="nextStep($event)" />
      }
      @case (1) {
        <sf [schema]="addressSchema" (formSubmit)="nextStep($event)" />
      }
      @case (2) {
        <div class="confirmation">
          <h3>Review Your Information</h3>
          <pre>{{ formData() | json }}</pre>
          <button nz-button nzType="primary" (click)="submit()">Submit</button>
        </div>
      }
    }
  `
})
export class WizardFormComponent {
  currentStep = signal(0);
  formData = signal<any>({});
  
  basicInfoSchema: SFSchema = {
    properties: {
      name: { type: 'string', title: 'Name' },
      email: { type: 'string', title: 'Email', format: 'email' }
    },
    required: ['name', 'email']
  };
  
  addressSchema: SFSchema = {
    properties: {
      street: { type: 'string', title: 'Street' },
      city: { type: 'string', title: 'City' },
      zipCode: { type: 'string', title: 'Zip Code' }
    },
    required: ['street', 'city']
  };
  
  nextStep(value: any): void {
    this.formData.update(data => ({ ...data, ...value }));
    this.currentStep.update(step => step + 1);
  }
  
  submit(): void {
    console.log('Final data:', this.formData());
  }
}
```

## Grid Layout

```typescript
ui: SFUISchema = {
  '*': {
    spanLabel: 4,
    spanControl: 20,
    grid: { span: 12 } // 2 columns (24 / 12 = 2)
  },
  $description: {
    grid: { span: 24 } // Full width
  }
};
```

## Responsive Layout

```typescript
ui: SFUISchema = {
  '*': {
    grid: {
      xs: 24,  // Mobile: full width
      sm: 12,  // Tablet: 2 columns
      md: 8,   // Desktop: 3 columns
      lg: 6    // Large: 4 columns
    }
  }
};
```

## Form Actions

```typescript
@Component({
  template: `
    <sf [schema]="schema" [button]="button">
      <ng-template sf-template="button" let-btn>
        <button 
          nz-button 
          [nzType]="btn.submit ? 'primary' : 'default'"
          (click)="btn.submit ? handleSubmit() : handleReset()"
        >
          {{ btn.submit ? 'Submit' : 'Reset' }}
        </button>
      </ng-template>
    </sf>
  `
})
export class CustomButtonFormComponent {
  button = {
    submit_text: 'Submit',
    reset_text: 'Reset',
    submit_type: 'primary' as const,
    reset_type: 'default' as const
  };
}
```

## Checklist

When creating SF forms:

- [ ] Use proper JSON Schema types
- [ ] Define required fields
- [ ] Set validation rules (min/max, format, pattern)
- [ ] Use appropriate widgets for data types
- [ ] Handle async data loading
- [ ] Implement conditional field visibility
- [ ] Add custom validators when needed
- [ ] Configure responsive grid layout
- [ ] Handle form submission and errors
- [ ] Provide loading states
- [ ] Test form validation
- [ ] Ensure accessibility (labels, ARIA)

## References

- [@delon/form Documentation](https://ng-alain.com/form)
- [JSON Schema Specification](https://json-schema.org/)
- [SF Component API](https://ng-alain.com/components/sf)
- [ng-alain Component Skill](./ng-alain-component/SKILL.md)
