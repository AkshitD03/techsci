# from gnews import GNews

# google_news = GNews()
# news = google_news.get_news_by_topic('TECHNOLOGY')
# print(news[0])
# # TECHNOLOGY and SCIENCE

# from gnews import GNews
# from openai import OpenAI


# # Fetch technology news
# google_news = GNews()
# news = google_news.get_news_by_topic('TECHNOLOGY')

# # Use only the first article
# if news:
#     article = news[0]
#     title = article.get('title')
#     des = article.get('description', '')

#     # Define the prompt with placeholders for title and description
#     prompt_template = """You are an experienced content writer and SEO specialist with a strong background in crafting engaging articles that rank well on search engines. Your expertise lies in producing high-quality, SEO-friendly content that captures readers' attention and drives traffic.
# Your task is to generate an article on the topic of: {title}. Change the title and make it attractive. A brief description about it is - "{des}". Also give me the description but in 1 line.
# Please ensure the article is engaging, informative, and optimized for SEO, incorporating relevant keywords seamlessly. Additionally, suggest a visual element that complements the article, such as an infographic, chart, or relevant stock photo, which can enhance the reader's understanding and engagement.
# For reference, I prefer articles that include a captivating introduction, clear subheadings, and a strong conclusion that encourages reader interaction.
# Make each part of the answer in JSON format like this - 
# {{
#   "title": "",
#   "cover-image": "",
#   "description": "",
#    "part1": {{
#     "heading": "",
#     "content": "",
#     "visual": ""  
#   }},
#    "part2": {{
#     "heading": "",
#     "content": "",
#     "visual": ""  
#   }},
#    "part3": {{
#     "heading": "",
#     "content": "",
#     "visual": ""  
#   }},
#   "part4": {{
#     "heading": "",
#     "content": "",
#     "visual": ""  
#   }},
#   "part5": {{
#     "heading": "",
#     "content": "",
#     "visual": ""
#   }}
# }}
# Stick to the formt of json file as you are part of a python program. Do not modify the json file a bit. Give me vodual for it it is cumpulsory. """

#     formatted_prompt = prompt_template.format(title=title, des=des)

#     # Initialize the OpenAI client (using the OpenRouter API)
#     client = OpenAI(
#       base_url="https://openrouter.ai/api/v1",
#       api_key="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",
#     )

#     completion = client.chat.completions.create(
#       model="google/gemini-2.0-pro-exp-02-05:free",
#       messages=[
#         {
#           "role": "user",
#           "content": formatted_prompt
#         }
#       ]
#     )

#     print(completion.choices[0].message.content)
# else:
#     print("No news articles found.")

from gnews import GNews
from openai import OpenAI
import re
import json
import pollinations  # Add pollinations import

def generate_pollinations_image(prompt: str, filename: str) -> None:
    """Helper function to generate and save images using Pollinations.ai"""
    image_model = pollinations.Image(
        width=1024,
        height=720,
    )
    image = image_model(prompt=prompt)
    image.save(file=filename)


# Fetch technology news
google_news = GNews()
news = google_news.get_news_by_topic('TECHNOLOGY')

# Use only the first article
if news:
    article = news[0]
    title = article.get('title')
    des = article.get('description', '')

    # Define the prompt with placeholders for title and description
    prompt_template = """You are an experienced content writer and SEO specialist with a strong background in crafting engaging articles that rank well on search engines. Your expertise lies in producing high-quality, SEO-friendly content that captures readers' attention and drives traffic.
Your task is to generate an article on the topic of: {title}. Change the title and make it attractive. A brief description about it is - "{des}". Also give me the description but in 1 line.
Please ensure the article is engaging, informative, and optimized for SEO, incorporating relevant keywords seamlessly. Additionally, suggest a visual element that complements the article, such as an infographic, chart, or relevant stock photo, which can enhance the reader's understanding and engagement.
For reference, I prefer articles that include a captivating introduction, clear subheadings, and a strong conclusion that encourages reader interaction.
Make each part of the answer in JSON format like this - 
{{
  "title": "",
  "cover-image": "",
  "description": "",
   "part1": {{
    "heading": "",
    "content": "",
    "visual1": ""  
  }},
   "part2": {{
    "heading": "",
    "content": "",
    "visual2": ""  
  }},
   "part3": {{
    "heading": "",
    "content": "",
    "visual3": ""  
  }},
  "part4": {{
    "heading": "",
    "content": "",
    "visual4": ""  
  }},
  "part5": {{
    "heading": "",
    "content": "",
    "visual5": ""
  }}
}}
Stick to the formt of json file as you are part of a python program. ALSO GIVE ME VISUAL FOR EACH OF THE THOING IT IS NESSARY I WNAT 65 VISUALS!!! do not modify the json file a bit. """

    formatted_prompt = prompt_template.format(title=title, des=des)

    # Initialize the OpenAI client (using the OpenRouter API)
    client = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key="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",
    )

    completion = client.chat.completions.create(
      model="google/gemini-2.0-pro-exp-02-05:free",
      messages=[
        {
          "role": "user",
          "content": formatted_prompt
        }
      ]
    )

    output = completion.choices[0].message.content

    # If a JSON code block exists in the output, extract its content
    if "```json" in output:
        match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if match:
            json_content = match.group(1)
            print(json_content)
            json_content = json.loads(json_content)
            
            # Generate images for all visuals
            generate_pollinations_image(json_content["cover-image"], "cover-image.png")
            generate_pollinations_image(json_content["part1"]["visual1"], "visual1.png")
            generate_pollinations_image(json_content["part2"]["visual2"], "visual2.png")
            generate_pollinations_image(json_content["part3"]["visual3"], "visual3.png")
            generate_pollinations_image(json_content["part4"]["visual4"], "visual4.png")
            generate_pollinations_image(json_content["part5"]["visual5"], "visual5.png")
            
            # Extracting values into separate variables
            cover_image = json_content["cover-image"]
            visual1 = json_content["part1"]["visual1"]
            visual2 = json_content["part2"]["visual2"]
            visual3 = json_content["part3"]["visual3"]
            visual4 = json_content["part4"]["visual4"]
            visual5 = json_content["part5"]["visual5"]
          
            
        else:
            print(output)
    else:
        print(output)
else:
    print("No news articles found.")
