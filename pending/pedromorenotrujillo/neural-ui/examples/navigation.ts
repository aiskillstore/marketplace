import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { NeuTabsComponent, NeuTabPanelComponent, type NeuTab } from '@neural-ui/core/tabs';

@Component({
  selector: 'example-navigation',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NeuTabsComponent, NeuTabPanelComponent],
  template: `
    <section aria-labelledby="navigation-heading">
      <h2 id="navigation-heading">Navigation</h2>
      <neu-tabs [tabs]="tabs" [activeId]="active()" (activeIdChange)="active.set($event)" ariaLabel="Customer sections">
        <neu-tab-panel tabId="overview"><p>Customer overview</p></neu-tab-panel>
        <neu-tab-panel tabId="activity"><p>Customer activity</p></neu-tab-panel>
      </neu-tabs>
      <output data-testid="active-tab">{{ active() }}</output>
    </section>
  `,
})
export class NavigationExample {
  readonly tabs: readonly NeuTab[] = [{ id: 'overview', label: 'Overview' }, { id: 'activity', label: 'Activity' }];
  readonly active = signal<string | null>('overview');
}
