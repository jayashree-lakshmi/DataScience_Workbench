# 🔐 Set up environment with API key
import os 
from secret_key import openapi_key  # Import your OpenAI API key from a secure module
os.environ['OPENAI_API_KEY'] = openapi_key  # Set the API key as environment variable

# 📚 LangChain and OpenAI imports
from langchain_openai import OpenAI  # LangChain wrapper for OpenAI LLMs
from langchain.prompts import PromptTemplate  # Used to format prompts
from langchain.chains import LLMChain, SequentialChain  # Chains for connecting LLMs
import openai  # OpenAI's native SDK for image generation

# 🧠 Initialize the language model with desired creativity level
llm = OpenAI(temperature=0.7)  # 0 = more deterministic, 1 = more creative

def generate_story(person: str, setting: str) -> dict:
    """
    Generate a whimsical bedtime story and extract its moral using LangChain.
    Args:
        person (str): The story’s main character (e.g., "Bluey").
        setting (str): The environment where the story takes place (e.g., "Mexico vacation").
    Returns:
        dict: A dictionary with keys 'story' and 'moral_story'.
    """
    # 📝 Prompt for story generation
    main_character_name = PromptTemplate(
        input_variables=['person', 'setting'],
        template="""I want to generate a bedtime story for my kid. 
        He is interested in stories about {person}, and I'd like the story to take place in a {setting}. 
        Make it whimsical, light-hearted, and suitable for children."""
    )
    # 🔗 Chain to generate the main story
    story_chain = LLMChain(llm=llm, prompt=main_character_name, output_key='story')
    # 🧠 Prompt to extract the moral of the generated story
    story_prompt = PromptTemplate(
        input_variables=['story'],
        template="""Give me a moral of the story for this story. Story is as follows: {story}"""
    )
    # 🔗 Chain to generate the moral from the story
    moral_chain = LLMChain(llm=llm, prompt=story_prompt, output_key='moral_story')
    # 🔀 SequentialChain links both story and moral chains
    main_chain = SequentialChain(
        chains=[story_chain, moral_chain],
        input_variables=['person', 'setting'],
        output_variables=['story', 'moral_story']
    )
    # 🚀 Invoke the chain with user inputs
    results = main_chain.invoke({
        'person': person,
        'setting': setting
    })
    return results

def generate_story_image(prompt: str) -> str:
    """
    Generate an illustrated image for the story using OpenAI's image API.
    Args:
        prompt (str): A descriptive text prompt to guide image creation.
    Returns:
        str: URL of the generated image.
    """
    # 🎨 Generate a 1024x1024 image based on the prompt
    response = openai.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    # 🌐 Extract image URL from response
    image_url = response.data[0].url
    return image_url

# 🧪 Optional: Run locally for quick testing
if __name__ == '__main__':
    story_main_character = 'Bluey'
    story_setting = 'In a Mexico vacation'
    # ✅ Generate story and print results
    result = generate_story(story_main_character, story_setting)
    print('📖 Story text generated:')
    print(result['story'])
    print('\n💡 Moral of the story:')
    print(result['moral_story'])
    # 🎨 Generate image for the story prompt
    image_url = generate_story_image(
        f'Pixar-style animation of {story_main_character} in {story_setting} for a kids bedtime story'
    )
    print('🖼️ Story Image URL:')
    print(image_url)