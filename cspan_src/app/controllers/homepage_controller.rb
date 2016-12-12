class HomepageController < ApplicationController
  helper_method :get_img_link
  helper_method :rlink
    def view
       @legislators = Legislator.where(" ").order("name ASC")
    end

  def get_img_link(id)
    return "/l_img/#{id}"
  end

  def rlink(pid)
    return "/legislator_page/#{pid}"
  end
end
