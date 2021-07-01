trend-alert: 
	Retrieve today's tweets (reweets>=10, likes>=10) and initialize the tweet user's historical influence (retweet,like,reply),
	Constantly retrieve the tweets satisfying (reweets>=10, likes>=10), if the tweet's influence is greater than user's historical influence, make the alert.
	Constantly retrieve the popular trends all over the world, if it contains the user defined key word, make the alert.

Output-> data.txt
Format: tweet url / tweet date / user's influence / tweet influence / user name / content
