import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { NeuButtonComponent } from '@neural-ui/core/button';
import { NeuDialogComponent } from '@neural-ui/core/modal';

@Component({
  selector: 'example-overlays',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NeuButtonComponent, NeuDialogComponent],
  template: `
    <section aria-labelledby="overlay-heading">
      <h2 id="overlay-heading">Dialog ownership</h2>
      <label><input type="checkbox" [checked]="acceptClose()" (change)="acceptClose.set(!acceptClose())" /> Accept close requests</label>
      <button neu-button type="button" (neuClick)="open.set(true)">Edit customer</button>
      <neu-dialog [open]="open()" title="Edit customer" (closeRequested)="requestClose()"
        (opened)="opened.update(increment)" (closed)="closed.update(increment)">
        <p>Changes belong to the application.</p>
        <button neu-button type="button" (neuClick)="open.set(false)">Finish editing</button>
      </neu-dialog>
      <output data-testid="dialog-state">{{ open() }} / {{ requests() }} / {{ opened() }} / {{ closed() }}</output>
    </section>
  `,
})
export class OverlaysExample {
  readonly open = signal(false);
  readonly acceptClose = signal(true);
  readonly requests = signal(0);
  readonly opened = signal(0);
  readonly closed = signal(0);
  readonly increment = (value: number) => value + 1;
  requestClose(): void {
    this.requests.update(this.increment);
    if (this.acceptClose()) this.open.set(false);
  }
}
