require_relative "us_state"
require "time"
include ActionView::Helpers::DateHelper

class LegislatorPageController < ApplicationController
  helper_method :get_img_link
  helper_method :get_likes_subtext
  helper_method :get_replies
  helper_method :rlink
  helper_method :get_bill_committee
  helper_method :get_yea
  helper_method :get_nay
  helper_method :top_meme_text
  helper_method :bottom_meme_text
  helper_method :post_time

  def view
    
    begin
        @legislator = Legislator.find(params[:id])
    rescue
        redirect_to "/"
        return
    end
    # Get name
    @name = @legislator.name
    # Get description, i.e. "Senator from New York"
    party = @legislator.party.capitalize + (@legislator.party.include?("Demo") ? "ic" : "")
    @description = "#{party} #{@legislator.role.capitalize} from #{US_State.abbreviation_to_full(@legislator.state)}"
    # CODING HORROR here but that's ok
    @profile_pic = get_img_link(params[:id])
    @contents = Content.where(author: @legislator.id).reverse
    puts "COUNT #{@contents.length}"
    @contents.each do |c|
      puts "#{c.type}"
    end
  end

  def get_img_link(id)


    return "http://localhost:3000/l_img/#{id}"
  end

  def rlink(pid)
    return "/legislator_page/#{pid}"
  end

  def get_likes_subtext(c2)
   out = "SELECT G.name FROM LIKES L, LEGISLATORS G WHERE G.id = L.lid AND L.cid = \"#{c2.id}\";" 
   likes = ActiveRecord::Base.connection_pool.with_connection { |con| con.exec_query(out ) }.rows

    # now we have id's of all the people who like the content
    if likes.count == 0
        return "No one likes this post" 
    elsif likes.count == 1
        return "#{likes[0][0]} likes this post"
    elsif likes.count == 2
        return "#{likes[0][0]} and #{likes[1][0]} like this post"
    else 
       return "#{likes[0][0]}, #{likes[1][0]}, and #{likes.count - 2} others like this post"
    end
  end

  def get_replies(c2)
   return Content.where(type: "reply", replyto: c2.id)
  end

  def get_bill_committee(bill)
    out = "SELECT C.NAME FROM COMMITTEES C WHERE C.id = \"#{bill.committees}\";" 
    res = ActiveRecord::Base.connection_pool.with_connection { |con| con.exec_query(out ) }.rows
    puts "RES: #{res}"
    return res[0][0]
  end

  def get_yea(bill)
    out = "SELECT COUNT(V.LID) FROM VOTES V WHERE V.cid = \"#{bill.id}\" AND V.VOTES = \"yea\"";
    res = ActiveRecord::Base.connection_pool.with_connection { |con| con.exec_query(out ) }.rows
    return res[0][0].to_s
  end

  def get_nay(bill)
    out = "SELECT COUNT(V.LID) FROM VOTES V WHERE V.cid = \"#{bill.id}\" AND V.VOTES = \"nay\"";
    res = ActiveRecord::Base.connection_pool.with_connection { |con| con.exec_query(out ) }.rows
    return res[0][0].to_s
  end
   
  def top_meme_text(c)
       c.contents.split("<MEME>")[0]
  end

  def bottom_meme_text(c)
       c.contents.split("<MEME>")[1]
  end

  def post_time(c)
     time_ago_in_words(Time.parse(c.time)) + " ago"
  end

end
