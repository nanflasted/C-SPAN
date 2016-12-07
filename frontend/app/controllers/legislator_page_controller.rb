require_relative "us_state"
class LegislatorPageController < ApplicationController
  def view
    @legislator = Legislator.find(params[:id])
    # Get name
    @name = @legislator.name
    # Get description, i.e. "Senator from New York"
    party = @legislator.party.capitalize + (@legislator.party.include?("Demo") ? "ic" : "")
    @description = "#{party} #{@legislator.role.capitalize} from #{US_State.abbreviation_to_full(@legislator.state)}"
    # CODING HORROR here but that's ok
    @profile_pic="http://localhost:3000/l_img/#{@legislator.id}"
  end
end
