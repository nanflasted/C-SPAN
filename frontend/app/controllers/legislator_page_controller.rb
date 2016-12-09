require_relative "us_state"

class LegislatorPageController < ApplicationController
  helper_method :get_img_link
  helper_method :get_likes_subtext

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

  def get_likes_subtext(c)
    likers = Like.where(cid: c.id).map{ |l| Legislator.find(l.lid)}
    # now we have id's of all the people who like the content
    if likers.count == 0
        return "No one likes this post" 
    elsif likers.count == 1
        return "#{likers[0].name} likes this post"
    elsif likers.count == 2
        return "#{likers[0].name} and #{likers[1].name} like this post"
    else
        return "#{likers[0].name}, #{likers[1].name}, and {likers.count-2} more like this post"
    end
  end
    
end
