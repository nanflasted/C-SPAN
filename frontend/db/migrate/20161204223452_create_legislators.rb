class CreateLegislators < ActiveRecord::Migration
  def change
    create_table :legislators do |t|
      t.text :name
      t.text :desc
      t.text :role
      t.text :party
      t.text :state
      t.float :ideology
      t.text :image

      t.timestamps null: false
    end
  end
end
