class CreateUsers < ActiveRecord::Migration[7.0]
  def change
    create_table :users, id: :uuid do |t|
      t.string :email, null: false
      t.string :name
      t.timestamps
    end

    add_index :users, :email, unique: true
  end

  # Alternative: Use up/down for non-reversible migrations
  # def up
  #   create_table :users, id: :uuid do |t|
  #     t.string :email, null: false
  #     t.string :name
  #     t.timestamps
  #   end
  #
  #   add_index :users, :email, unique: true
  #
  #   # Data migration example
  #   User.find_each do |user|
  #     user.update(name: user.name.titleize) if user.name.present?
  #   end
  # end
  #
  # def down
  #   drop_table :users
  # end
end

# Example: Add column migration
# class AddPhoneToUsers < ActiveRecord::Migration[7.0]
#   def change
#     add_column :users, :phone, :string
#   end
# end

# Example: Add reference/foreign key
# class AddUserRefToPosts < ActiveRecord::Migration[7.0]
#   def change
#     add_reference :posts, :user, type: :uuid, foreign_key: true, null: false
#   end
# end

# Example: Add index
# class AddIndexToUsersEmail < ActiveRecord::Migration[7.0]
#   def change
#     add_index :users, :email, unique: true
#   end
# end

# Example: Complex migration with data changes
# class MigrateUserStatus < ActiveRecord::Migration[7.0]
#   def up
#     add_column :users, :status, :integer, default: 0
#
#     User.where(active: true).update_all(status: 1)
#     User.where(active: false).update_all(status: 0)
#
#     remove_column :users, :active
#   end
#
#   def down
#     add_column :users, :active, :boolean, default: false
#
#     User.where(status: 1).update_all(active: true)
#     User.where(status: 0).update_all(active: false)
#
#     remove_column :users, :status
#   end
# end
