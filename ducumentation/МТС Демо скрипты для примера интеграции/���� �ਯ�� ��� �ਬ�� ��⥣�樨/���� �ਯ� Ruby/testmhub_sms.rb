require 'net/http'
require 'json'
require 'net/https'
require 'uri'



uri = URI('https://api.connect.mts.by/8/json2/simple')
#8 - client id

#uri = URI.parse("https://api.br.mts.by/14/json2/simple")

#uri = URI.parse("https://api.br.mts.by/31/json2/simple")

https = Net::HTTP.new(uri.host,uri.port)
https.use_ssl=true
https.verify_mode = OpenSSL::SSL::VERIFY_NONE
#req = Net::HTTP::Post.new(uri.path)
req = Net::HTTP::Post.new(uri.path, initheader = {'Content-Type' =>'application/json'})

req.basic_auth 'login', 'password'


re111 = {
    "phone_number": 375298766719,
    "extra_id": "4232j4h89932kjhs",
    "callback_url": "https://send-dr-here.com",
    #"start_time": "2019-08-16 09:59:10",
    "tag": "Campaign name",
    "channels": [
        "sms"
#        "viber"
    ],
    "channel_options": {
        "sms": {
            "text": "privet",
            "alpha_name": "TEST",
            "ttl": 600
        }


#        "viber": {
#            "text": "Text for Viber",
#            "ttl": 60,
        #    "img": "http://olddogs.org/logo.png",
##            "caption": "Old Dogs need you!",
#            "action": "http://olddogs.org",
#        },
    }
}


req.body = re111.to_json

res = https.request(req)
#puts "Response #{res.code} #{res.message}: #{res.body}"

#res = Net::HTTP.start(uri.hostname, uri.port) do |http|
#  http.request(req)
#end

p res.body
p res.code



