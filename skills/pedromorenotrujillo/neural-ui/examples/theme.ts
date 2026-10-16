import { DOCUMENT } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { defineNeuPreset } from '@neural-ui/core';
import { NeuButtonComponent } from '@neural-ui/core/button';

export const neuralAiPreset = defineNeuPreset({
  name: 'neural-ai',
  light: { '--neu-primary': '#166534', '--neu-bg': '#f0fdf4', '--neu-text': '#142d20' },
  dark: { '--neu-primary': '#86efac', '--neu-bg': '#081a10', '--neu-text': '#f0fdf4' },
});

@Component({
  selector: 'example-theme',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NeuButtonComponent],
  template: `<button neu-button type="button" (neuClick)="toggle()">Toggle theme</button><output data-testid="theme-mode">{{ mode() }}</output>`,
})
export class ThemeExample {
  private readonly document = inject(DOCUMENT);
  readonly mode = signal<'light' | 'dark'>('light');
  toggle(): void {
    this.mode.update(value => value === 'light' ? 'dark' : 'light');
    this.document.documentElement.setAttribute('data-theme', this.mode());
  }
}
