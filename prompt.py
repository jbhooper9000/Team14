prompt = f'''

You are summarising documents for a departmental minister. 
Time is tight, so you need to pick the most important points. Your response should include the following: 


Include short extracts of the document where this is helpful. Only include the requested response. There will be no follow up.

The response should be in this format:

First section title: 'Summary'. 
Content:  summarise the document below by pulling out key themes. This should be within 3-7 bullet points. 

Second section title: 'To be aware'. 
Content: this section has a few components formatted in bullet points, it is aimed to raising anything that may be problematic for the Minister. 
 Point out:
 - anything in the document that may be of particular interest to the prime minister and why.
 - any policy which sounds like there is a lack of conviction or evidence, for instance with the phrasing 'you may wish to consider'. Flag which specific area this relates to. 
 - if and how the policies in the document does not align with the 2019 Conservative manifesto pledges. Specify the most relevant pledge to the document.
 - all other UK Government departments and agencies who may have an interest in this policy, or be responsible for delivering any part of the content. 


Here is the document:
"

'''

# Answer each part of the question only if you know the answer or can make a well-informed guess; otherwise tell me you don't know it.
# Third section title: 'Latest news'
#  - recent news articles relating to themes or policies in the document, with links provided.
