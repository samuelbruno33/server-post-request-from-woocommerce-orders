# POST request to a Server with filtering of the data through a JQ command and GET request via the REST API of Woocommerce
A python script that allows to make a POST request to a Server from a GET request of all orders of the day on my Woocommerce's website.

Initially the GET request is made to your website which will write in a file the entire response as a Json file. In particular I will take all the orders of the day using the REST API made available by Woocommerce. The request is divided into "chunks" so as not to weigh too much on servers that have little ram memory or have little capacity to process data, since the server response will be quite heavy.

This file will then be filtered through a JQ command that will only take the data I am really interested in. This data must then be manipulated in a way that makes the results consistent with how the servers accept these variables.

Finally, I will write the result of this call again in a file that will serve as debug in case something didn’t go as planned. The file contains both the Status Code and the Server response in the form of Json.

 
