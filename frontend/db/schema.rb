# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20161204223452) do

  create_table "committee", force: :cascade do |t|
    t.text "floor"
    t.text "desc"
    t.text "name",  null: false
  end

  add_index "committee", ["id"], name: "sqlite_autoindex_committee_1", unique: true

  create_table "content", force: :cascade do |t|
    t.text    "content",   null: false
    t.integer "author",    null: false
    t.integer "committee"
    t.text    "time",      null: false
    t.text    "replyto"
    t.text    "memebg"
    t.text    "type",      null: false
  end

  add_index "content", ["id"], name: "sqlite_autoindex_content_1", unique: true

# Could not dump table "legislator" because of following NoMethodError
#   undefined method `[]' for nil:NilClass

  create_table "legislators", force: :cascade do |t|
    t.text     "name"
    t.text     "desc"
    t.text     "role"
    t.text     "party"
    t.text     "state"
    t.float    "ideology"
    t.text     "image"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "like", force: :cascade do |t|
    t.integer "lid", null: false
    t.integer "cid", null: false
  end

  add_index "like", ["id"], name: "sqlite_autoindex_like_1", unique: true

  create_table "participate", force: :cascade do |t|
    t.integer "lid",  null: false
    t.text    "role"
    t.integer "cid",  null: false
  end

  add_index "participate", ["id"], name: "sqlite_autoindex_participate_1", unique: true

  create_table "vote", force: :cascade do |t|
    t.integer "lid", null: false
    t.integer "cid", null: false
  end

  add_index "vote", ["id"], name: "sqlite_autoindex_vote_1", unique: true

end
