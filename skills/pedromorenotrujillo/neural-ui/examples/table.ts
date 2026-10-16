import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { NeuTableComponent, type NeuTableColumn, type NeuTableQuery, type NeuTableSelection, type NeuTableSelectionOptions } from '@neural-ui/core/table';

interface Customer { id: number; name: string; }
type Field = 'name';

@Component({
  selector: 'example-table',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NeuTableComponent],
  template: `
    <section aria-labelledby="table-heading">
      <h2 id="table-heading">Customers</h2>
      <neu-table [data]="customers" [columns]="columns" [rowKey]="rowKey"
        [query]="query()" (queryChange)="query.set($event)"
        [selection]="selection()" (selectionChange)="selection.set($event.next)"
        [selectionOptions]="selectionOptions" />
      <output data-testid="table-sort">{{ query().sort[0]?.direction ?? 'none' }}</output>
      <output data-testid="table-selected">{{ selectedKeys() }}</output>
    </section>
  `,
})
export class TableExample {
  readonly customers: readonly Customer[] = [{ id: 1, name: 'Zoe' }, { id: 2, name: 'Ana' }, { id: 3, name: 'Leo' }];
  readonly rowKey = (row: Customer) => row.id;
  readonly columns: readonly NeuTableColumn<Customer, Field>[] = [
    { id: 'name', header: 'Customer', field: 'name', sort: { field: 'name' } },
  ];
  readonly query = signal<NeuTableQuery<Field>>({ page: 0, pageSize: 10, search: '', sort: [], filters: null });
  readonly selection = signal<NeuTableSelection<number, Field>>({ kind: 'keys', keys: [] });
  readonly selectionOptions: NeuTableSelectionOptions<Customer> = {
    mode: 'single', indicator: 'radio', selectOnRowClick: true, allowClear: true,
  };
  selectedKeys(): string {
    const value = this.selection();
    return value.kind === 'keys' ? value.keys.join(',') : 'all-matching';
  }
}
