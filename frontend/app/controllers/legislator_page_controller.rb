class LegislatorPageController < ApplicationController
  def view
    @message = "Test! #{Legislator.first.name}"
  end
end
