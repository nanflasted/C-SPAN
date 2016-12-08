require_relative "us_state"

class LegislatorPageController < ApplicationController
  helper_method :get_img_link

  def view
    @legislator = Legislator.find(params[:id])
    # Get name
    @name = @legislator.name
    # Get description, i.e. "Senator from New York"
    party = @legislator.party.capitalize + (@legislator.party.include?("Demo") ? "ic" : "")
    @description = "#{party} #{@legislator.role.capitalize} from #{US_State.abbreviation_to_full(@legislator.state)}"
    # CODING HORROR here but that's ok
    @profile_pic = get_img_link(params[:id])
    @contents = Content.where(author: @legislator.id)
    puts "COUNT #{@contents.length}"
    @contents.each do |c|
      puts "#{c.type}"
    end
  end

  def get_img_link(id)
    return "http://localhost:3000/l_img/#{id}"
  end
end
