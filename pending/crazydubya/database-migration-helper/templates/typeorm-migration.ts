import { MigrationInterface, QueryRunner, Table, TableIndex, TableForeignKey } from 'typeorm';

export class CreateUsersTable1234567890123 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    // Create table
    await queryRunner.createTable(
      new Table({
        name: 'users',
        columns: [
          {
            name: 'id',
            type: 'uuid',
            isPrimary: true,
            generationStrategy: 'uuid',
            default: 'uuid_generate_v4()',
          },
          {
            name: 'email',
            type: 'varchar',
            isNullable: false,
            isUnique: true,
          },
          {
            name: 'name',
            type: 'varchar',
            isNullable: true,
          },
          {
            name: 'created_at',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
          },
          {
            name: 'updated_at',
            type: 'timestamp',
            default: 'CURRENT_TIMESTAMP',
            onUpdate: 'CURRENT_TIMESTAMP',
          },
        ],
      }),
      true,
    );

    // Create index
    await queryRunner.createIndex(
      'users',
      new TableIndex({
        name: 'IDX_USERS_EMAIL',
        columnNames: ['email'],
      }),
    );

    // Add column to existing table (example)
    // await queryRunner.addColumn('users', new TableColumn({
    //   name: 'phone',
    //   type: 'varchar',
    //   isNullable: true,
    // }));

    // Add foreign key (example)
    // await queryRunner.createForeignKey('posts', new TableForeignKey({
    //   columnNames: ['user_id'],
    //   referencedColumnNames: ['id'],
    //   referencedTableName: 'users',
    //   onDelete: 'CASCADE',
    // }));
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // Drop in reverse order
    // await queryRunner.dropForeignKey('posts', 'FK_...');
    // await queryRunner.dropColumn('users', 'phone');
    await queryRunner.dropIndex('users', 'IDX_USERS_EMAIL');
    await queryRunner.dropTable('users');
  }
}
