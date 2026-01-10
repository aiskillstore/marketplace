'use strict';

/** @type {import('sequelize-cli').Migration} */
module.exports = {
  async up(queryInterface, Sequelize) {
    // Create table example
    await queryInterface.createTable('users', {
      id: {
        type: Sequelize.UUID,
        defaultValue: Sequelize.UUIDV4,
        primaryKey: true,
      },
      email: {
        type: Sequelize.STRING,
        allowNull: false,
        unique: true,
      },
      name: {
        type: Sequelize.STRING,
        allowNull: true,
      },
      created_at: {
        type: Sequelize.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
      updated_at: {
        type: Sequelize.DATE,
        allowNull: false,
        defaultValue: Sequelize.literal('CURRENT_TIMESTAMP'),
      },
    });

    // Add index example
    await queryInterface.addIndex('users', ['email'], {
      name: 'users_email_idx',
      unique: true,
    });

    // Add column example
    // await queryInterface.addColumn('users', 'phone', {
    //   type: Sequelize.STRING,
    //   allowNull: true,
    // });

    // Add foreign key example
    // await queryInterface.addConstraint('posts', {
    //   fields: ['user_id'],
    //   type: 'foreign key',
    //   name: 'posts_user_id_fkey',
    //   references: {
    //     table: 'users',
    //     field: 'id',
    //   },
    //   onDelete: 'CASCADE',
    //   onUpdate: 'CASCADE',
    // });
  },

  async down(queryInterface, Sequelize) {
    // Rollback operations in reverse order
    // await queryInterface.removeConstraint('posts', 'posts_user_id_fkey');
    // await queryInterface.removeColumn('users', 'phone');
    await queryInterface.removeIndex('users', 'users_email_idx');
    await queryInterface.dropTable('users');
  },
};
