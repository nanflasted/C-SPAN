class LegislatorPageController < ApplicationController
  def view
    @message = "Test!" + params[:id]
  end
end
