import streamlit as st
import openai
import os
from dotenv import load_dotenv
import time
from jinja2 import Environment, FileSystemLoader

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Recipe Bot",
    page_icon="🍳",
    layout="centered"
)

class RecipeBot:
    def __init__(self):
        # Initialize OpenAI client (will use environment variable OPENAI_API_KEY)
        self.client = None
        if os.getenv("OPENAI_API_KEY"):
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Load system prompt from template
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self, additional_context=None):
        """Load and render the system prompt from Jinja2 template"""
        try:
            # Set up Jinja2 environment
            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('recipe_bot_prompt.j2')
            
            # Render template with optional context
            return template.render(additional_context=additional_context)
        except Exception as e:
            # Fallback to basic prompt if template loading fails
            st.warning(f"Could not load prompt template: {e}")
            return """You are a helpful recipe bot assistant. You specialize in:
            - Suggesting recipes based on ingredients or dietary preferences
            - Providing cooking instructions and tips
            - Helping with meal planning
            - Answering cooking and nutrition questions
            
            Keep your responses helpful, friendly, and focused on recipes and cooking."""

    def get_ai_response(self, user_message, conversation_history):
        """Get AI response - can be easily swapped for different models"""
        if not self.client:
            # Fallback response if no API key is provided
            return self._get_fallback_response(user_message)
        
        try:
            # Prepare messages for API
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            for msg in conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error getting AI response: {str(e)}")
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message):
        """Simple fallback responses when AI is not available"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['pasta', 'spaghetti', 'noodles']):
            return "🍝 Here's a simple pasta recipe: Cook pasta according to package directions. Meanwhile, heat olive oil in a pan, add garlic, then your favorite sauce. Toss with pasta and enjoy!"
        
        elif any(word in user_lower for word in ['chicken', 'meat']):
            return "🐔 For a quick chicken dish: Season chicken breast with salt, pepper, and herbs. Cook in a hot pan with oil for 6-7 minutes per side until golden and cooked through."
        
        elif any(word in user_lower for word in ['vegetarian', 'vegan', 'vegetables']):
            return "🥗 Try a veggie stir-fry: Heat oil in a wok, add your favorite vegetables, stir-fry for 3-5 minutes, season with soy sauce and garlic. Serve over rice!"
        
        elif any(word in user_lower for word in ['dessert', 'sweet', 'cake']):
            return "🍰 Quick dessert idea: Mix 1 mug of flour, sugar, cocoa powder, baking powder, milk, and oil. Microwave for 90 seconds for a mug cake!"
        
        else:
            return "👨‍🍳 I'm a recipe bot! I can help you with cooking ideas, recipes, and meal planning. What would you like to cook today? You can ask me about specific ingredients, dietary preferences, or types of cuisine!"


def main():
    # Initialize the bot
    if 'bot' not in st.session_state:
        st.session_state.bot = RecipeBot()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # App header
    st.title("🍳 Recipe Bot")
    st.write("Ask me for recipes, cooking tips, or meal ideas!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to cook today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking of a delicious response..."):
                response = st.session_state.bot.get_ai_response(
                    prompt, 
                    st.session_state.messages[:-1]  # Exclude the current message
                )
            st.write(response)
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with instructions
    with st.sidebar:        
        st.header("💡 Try asking about:")
        st.write("- Recipes with specific ingredients")
        st.write("- Dietary preferences (vegetarian, vegan, etc.)")
        st.write("- Cooking techniques")
        st.write("- Meal planning ideas")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main() 