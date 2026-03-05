# Import required libraries
import streamlit as st
import kids_story_generator  # Custom module containing story and image generation logic

# 🧸 Set the title of the Streamlit app
st.title("🧸 Bedtime Story Creator")

# 📥 Input fields to collect story parameters from the user
person = st.text_input("Main Character")       # e.g. "Mazda car"
setting = st.text_input("Story Setting")       # e.g. "going for a race"

# 🚀 When the user clicks the 'Generate Story' button, run the generation pipeline
if st.button('Generate Story'):

    # 📚 Display the generated story
    st.subheader('Story')

    # 👩‍💻 Call the backend function to generate story and moral based on user input
    result = kids_story_generator.generate_story(person, setting)
    
    # 📝 Display the story text and the moral extracted from it
    st.write(result['story'])          # Main story output
    st.write(result['moral_story'])    # Moral of the story

    # 🎨 Generate an illustrated image that matches the story theme
    image_url = kids_story_generator.generate_story_image(
        f'Animated Illustrated scene of {person} in {setting} for a kids bedtime story'
    )

    # 🖼️ Display the generated image with a caption
    st.image(image_url, caption='Illustrated Story Scene')