import fb_auth_token

fb_username = "hubid@vipepe.com"
fb_password = "tinderpigen"
fb_access_token = fb_auth_token.get_fb_access_token(fb_username, fb_password)
fb_user_id = fb_auth_token.get_fb_id(fb_access_token)

myTinderID = ''

dbHost = "46.101.137.45"
dbName ='TellersTinder'
dbCollection = 'MatchedPairs'
dbUser = 'tinderbot'
dbPass = 'iambot'


host = 'https://api.gotinder.com'

# Your real config file should simply be named "config.py"
# Just insert your fb_username and fb_password in string format
# and the fb_auth_token.py module will do the rest!
