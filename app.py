from flask import Flask, render_template, request, redirect, url_for, session, flash
import logging
import json
import re
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from gnews import GNews
from openai import OpenAI
import pollinations  # Pollinations.ai library

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Setup logging and global storage for logs and blogs
logging.basicConfig(level=logging.INFO)
logs = []   # Global log list
blogs = []  # Global list to store generated blog posts

def log_event(message):
    """Log events both in-memory and in the console."""
    logs.append(message)
    logging.info(message)

def slugify(text):
    """Simple slugify function to create URL-friendly slugs."""
    # Convert to lowercase, remove non-alphanumeric characters, and replace spaces with hyphens
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text).strip('-')

def generate_unique_slug(title):
    """Generate a unique slug for the blog title."""
    base_slug = slugify(title)
    slug = base_slug
    count = 1
    # Ensure the slug is unique among already generated blogs
    while any(blog.get('slug') == slug for blog in blogs):
        slug = f"{base_slug}-{count}"
        count += 1
    return slug

def generate_pollinations_image(prompt: str, filename: str) -> None:
    """Generate and save an image using Pollinations.ai based on the given prompt."""
    image_model = pollinations.Image(width=1024, height=720)
    image = image_model(prompt=prompt)
    image.save(file=filename)
    log_event(f"Generated image saved as {filename} for prompt: {prompt}")

def generate_blog(topic: str, news_index: int):
    """
    Fetch a news article using GNews, generate a JSON-format blog article via OpenAI,
    generate images using Pollinations.ai, update image paths, and add a unique slug.
    """
    google_news = GNews()
    news = google_news.get_news_by_topic(topic)
    if news and len(news) > news_index:
        article = news[news_index]
        title = article.get('title')
        des = article.get('description', '')
        
        # Prompt template (do not modify the JSON format)
        prompt_template = r'''You are an experienced content writer and SEO specialist with a strong background in crafting engaging articles that rank well on search engines. Your task is to generate an article on the topic of: {title}. Change the title and make it attractive. A brief description about it is - "{des}". Also give me the description but in 1 line.
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
Stick to the formt of json file as you are part of a python program. ALSO GIVE ME VISUAL FOR EACH OF THE THOING IT IS NESSARY I WNAT 65 VISUALS!!!'''
        
        formatted_prompt = prompt_template.format(title=title, des=des)
        
        # Initialize the OpenAI client (replace 'yourapikeyhere' with your actual key)
        client = OpenAI(
          base_url="https://openrouter.ai/api/v1",
          api_key="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",
        )
        
        completion = client.chat.completions.create(
          model="google/gemini-2.0-pro-exp-02-05:free",
          messages=[{"role": "user", "content": formatted_prompt}]
        )
        
        output = completion.choices[0].message.content
        
        # Extract JSON from the response (looking for a JSON code block)
        if "```json" in output:
            match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
            if match:
                json_content = match.group(1)
                try:
                    blog_data = json.loads(json_content)
                except json.JSONDecodeError as e:
                    log_event(f"JSON decoding failed: {e}")
                    return None
                
                # Generate images and save to static folder
                generate_pollinations_image(blog_data["cover-image"], f"static/cover-{topic}-{news_index}.png")
                generate_pollinations_image(blog_data["part1"]["visual1"], f"static/visual1-{topic}-{news_index}.png")
                generate_pollinations_image(blog_data["part2"]["visual2"], f"static/visual2-{topic}-{news_index}.png")
                generate_pollinations_image(blog_data["part3"]["visual3"], f"static/visual3-{topic}-{news_index}.png")
                generate_pollinations_image(blog_data["part4"]["visual4"], f"static/visual4-{topic}-{news_index}.png")
                generate_pollinations_image(blog_data["part5"]["visual5"], f"static/visual5-{topic}-{news_index}.png")
                
                # Update image paths to point to the static folder
                blog_data["cover-image"] = f"/static/cover-{topic}-{news_index}.png"
                blog_data["part1"]["visual1"] = f"/static/visual1-{topic}-{news_index}.png"
                blog_data["part2"]["visual2"] = f"/static/visual2-{topic}-{news_index}.png"
                blog_data["part3"]["visual3"] = f"/static/visual3-{topic}-{news_index}.png"
                blog_data["part4"]["visual4"] = f"/static/visual4-{topic}-{news_index}.png"
                blog_data["part5"]["visual5"] = f"/static/visual5-{topic}-{news_index}.png"
                
                # Attach metadata and generate a unique slug
                blog_data['topic'] = topic
                blog_data['news_index'] = news_index
                blog_data['slug'] = generate_unique_slug(blog_data['title'])
                return blog_data
            else:
                log_event("Failed to extract JSON code block from AI response.")
                return None
        else:
            log_event("No JSON code block found in AI response.")
            return None
    else:
        log_event(f"No news available for topic {topic} at index {news_index}")
        return None

def generate_all_blogs():
    """
    Generate blogs sequentially—publishing each blog immediately as it is generated.
    First for TECHNOLOGY (5 blogs) then for SCIENCE (5 blogs).
    """
    # Optionally clear old blogs when a new batch is generated
    blogs.clear()
    # TECHNOLOGY blogs
    for i in range(5):
        blog = generate_blog("TECHNOLOGY", i)
        if blog:
            blogs.append(blog)
            log_event(f"Generated TECHNOLOGY blog at index {i} with slug '{blog['slug']}'")
        time.sleep(2)  # Short delay (adjust as needed)
    
    # SCIENCE blogs
    for i in range(5):
        blog = generate_blog("SCIENCE", i)
        if blog:
            blogs.append(blog)
            log_event(f"Generated SCIENCE blog at index {i} with slug '{blog['slug']}'")
        time.sleep(2)

# --------------------- Flask Routes ---------------------

@app.route('/')
def home():
    """Landing page that lists all published blogs with their cover images."""
    return render_template("home.html", blogs=blogs)

@app.route('/blog/<slug>')
def blog_page_slug(slug):
    """Individual blog page accessed via its unique slug."""
    blog = next((blog for blog in blogs if blog.get('slug') == slug), None)
    if blog:
        return render_template("blog.html", blog=blog)
    else:
        return "Blog not found", 404

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """
    Admin login route.
    Use username and password (akshit / akshit) to access the logs page.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "akshit" and password == "akshit":
            session['admin'] = True
            return redirect(url_for('logs_page'))
        else:
            flash("Invalid credentials")
    return render_template("admin_login.html")

@app.route('/logs')
def logs_page():
    """Logs page accessible only to authenticated admin users."""
    if not session.get('admin'):
        return redirect(url_for('admin'))
    return render_template("logs.html", logs=logs)

# --------------------- Background Blog Generator ---------------------

def start_blog_generator():
    """
    Start a background thread that sequentially generates blogs.
    Each blog is published immediately after generation.
    """
    generator_thread = threading.Thread(target=generate_all_blogs)
    generator_thread.daemon = True  # Ensures thread exits with app
    generator_thread.start()
    log_event("Immediate background blog generator started.")

# --------------------- APScheduler Setup ---------------------

scheduler = BackgroundScheduler()
# Schedule the daily blog generation job (clear and repopulate blogs at midnight)
scheduler.add_job(generate_all_blogs, trigger='cron', hour=0, minute=0)
scheduler.start()
log_event("Scheduler started: Blogs will be generated daily at midnight.")

# --------------------- Main Entry Point ---------------------

if __name__ == '__main__':
    # Start the immediate background blog generator so the UI is served first.
    start_blog_generator()
    app.run(host="0.0.0.0" , port="5000",debug=True)
