/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = function(knex) {
  return knex.schema
    .createTable('users', function(table) {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
      table.string('email').notNullable().unique();
      table.string('name');
      table.timestamps(true, true); // created_at, updated_at
    })
    .then(() => {
      // Add indexes after table creation
      return knex.schema.table('users', function(table) {
        table.index('email', 'users_email_idx');
      });
    });

  // Alternative: Add column to existing table
  // return knex.schema.table('users', function(table) {
  //   table.string('phone');
  // });

  // Add foreign key
  // return knex.schema.table('posts', function(table) {
  //   table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
  // });
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.down = function(knex) {
  return knex.schema.dropTableIfExists('users');

  // Rollback column addition
  // return knex.schema.table('users', function(table) {
  //   table.dropColumn('phone');
  // });

  // Rollback foreign key
  // return knex.schema.table('posts', function(table) {
  //   table.dropForeign('user_id');
  //   table.dropColumn('user_id');
  // });
};
