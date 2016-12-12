require 'test_helper'

class LegislatorsControllerTest < ActionController::TestCase
  setup do
    @legislator = legislators(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:legislators)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create legislator" do
    assert_difference('Legislator.count') do
      post :create, legislator: { desc: @legislator.desc, ideology: @legislator.ideology, image: @legislator.image, name: @legislator.name, party: @legislator.party, role: @legislator.role, state: @legislator.state }
    end

    assert_redirected_to legislator_path(assigns(:legislator))
  end

  test "should show legislator" do
    get :show, id: @legislator
    assert_response :success
  end

  test "should get edit" do
    get :edit, id: @legislator
    assert_response :success
  end

  test "should update legislator" do
    patch :update, id: @legislator, legislator: { desc: @legislator.desc, ideology: @legislator.ideology, image: @legislator.image, name: @legislator.name, party: @legislator.party, role: @legislator.role, state: @legislator.state }
    assert_redirected_to legislator_path(assigns(:legislator))
  end

  test "should destroy legislator" do
    assert_difference('Legislator.count', -1) do
      delete :destroy, id: @legislator
    end

    assert_redirected_to legislators_path
  end
end
