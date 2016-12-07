class LImgController < ApplicationController
  def view
     send_data Legislator.find(params[:id]).image, :type => 'image/jpg',:disposition => 'inline'
  end
end
