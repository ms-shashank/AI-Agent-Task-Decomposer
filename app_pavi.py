import streamlit as st
import openai
import json
import re
from typing import List, Dict
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Project Task Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .task-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .backend-badge {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .frontend-badge {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'code_outputs' not in st.session_state:
    st.session_state.code_outputs = {}
if 'openai_key' not in st.session_state:
    st.session_state.openai_key = ''
if 'project_description' not in st.session_state:
    st.session_state.project_description = ''

class ProjectCoordinator:
    """Coordinator that analyzes and breaks down projects"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def analyze_and_breakdown(self, description: str) -> List[Dict]:
        """Analyze project and create task breakdown"""
        
        system_prompt = """You are an expert software architect. Analyze project descriptions and break them into specific technical tasks.
        
For each task, determine if it requires backend development (APIs, database, logic) or frontend development (UI, components, user interaction).

Return a JSON array with tasks in this exact format:
[
    {
        "id": 1,
        "name": "Clear task name",
        "category": "BACKEND" or "FRONTEND",
        "description": "Detailed technical requirements",
        "priority": "High" or "Medium" or "Low"
    }
]

Focus on creating comprehensive, well-defined tasks."""

        user_prompt = f"""Project Description: {description}

Break this down into specific technical tasks. Include:
- Database design and models
- API endpoints and business logic
- Authentication and security
- UI components and user flows
- State management and API integration

Return ONLY valid JSON array."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6
            )
            
            content = response.choices[0].message.content.strip()
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
                
        except Exception as e:
            st.error(f"Coordinator error: {str(e)}")
            return []

class BackendDeveloper:
    """Generates backend code and architecture"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def create_implementation(self, task: Dict, context: str) -> Dict:
        """Create complete backend implementation"""
        
        system_prompt = """You are a senior backend engineer specializing in Python, FastAPI, and SQLite.
        
Generate complete, working Python code - NOT descriptions or placeholders.

Write actual production-ready code with:
- Full SQLAlchemy models with all fields and relationships
- Complete FastAPI routes with all CRUD operations
- Working business logic functions
- Proper error handling and validation"""

        user_prompt = f"""Context: {context}

Task: {task['name']}
Details: {task['description']}

Generate COMPLETE, WORKING CODE for:

1. DATABASE MODELS (SQLAlchemy):
Write full Python code with all model classes, fields, relationships, and table definitions.

2. API ROUTES (FastAPI):
Write complete FastAPI router code with all endpoints, request/response models, and handlers.

3. BUSINESS LOGIC:
Write helper functions, validation logic, and any utility functions needed.

4. DEPENDENCIES:
List exact package names and versions.

IMPORTANT: Write ACTUAL CODE, not JSON. Write complete working Python code that can be run directly.
Format your response with clear sections using comments like:
# === DATABASE MODELS ===
# === API ROUTES ===
# === BUSINESS LOGIC ===
# === DEPENDENCIES ==="""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response into sections
            result = {
                'models': '',
                'routes': '',
                'logic': '',
                'dependencies': ''
            }
            
            # Try to find sections with markers
            models_match = re.search(r'#\s*===\s*DATABASE MODELS\s*===\s*(.*?)(?=#\s*===|$)', content, re.DOTALL | re.IGNORECASE)
            routes_match = re.search(r'#\s*===\s*API ROUTES\s*===\s*(.*?)(?=#\s*===|$)', content, re.DOTALL | re.IGNORECASE)
            logic_match = re.search(r'#\s*===\s*BUSINESS LOGIC\s*===\s*(.*?)(?=#\s*===|$)', content, re.DOTALL | re.IGNORECASE)
            deps_match = re.search(r'#\s*===\s*DEPENDENCIES\s*===\s*(.*?)(?=#\s*===|$)', content, re.DOTALL | re.IGNORECASE)
            
            if models_match:
                result['models'] = models_match.group(1).strip()
            if routes_match:
                result['routes'] = routes_match.group(1).strip()
            if logic_match:
                result['logic'] = logic_match.group(1).strip()
            if deps_match:
                result['dependencies'] = deps_match.group(1).strip()
            
            # If no sections found, put everything in models as fallback
            if not any(result.values()):
                result['models'] = content
                result['routes'] = "# Code generated above"
                result['logic'] = "# Code generated above"
                result['dependencies'] = "# Check requirements above"
            
            return result
                
        except Exception as e:
            st.error(f"Backend developer error: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return {
                'models': '# Error generating code',
                'routes': '# Error generating code',
                'logic': '# Error generating code',
                'dependencies': '# Error generating code'
            }

class FrontendDeveloper:
    """Generates frontend code and components"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def create_implementation(self, task: Dict, context: str) -> Dict:
        """Create complete frontend implementation"""
        
        system_prompt = """You are a senior frontend engineer specializing in modern React development.

Generate complete, working React code - NOT descriptions or placeholders.

Write actual production-ready code with:
- Full React components with complete JSX
- All useState and useEffect hooks properly implemented
- Complete styling code (CSS or Tailwind)
- Working API integration functions"""

        user_prompt = f"""Context: {context}

Task: {task['name']}
Details: {task['description']}

Generate COMPLETE, WORKING CODE for:

1. REACT COMPONENT:
Write full React functional component with complete JSX, all hooks, event handlers, and logic.

2. STYLES:
Write complete CSS or Tailwind styling code.

3. HOOKS & API:
Write custom hooks, API call functions with fetch/axios, error handling.

4. DEPENDENCIES:
List exact NPM package names and versions.

IMPORTANT: Write ACTUAL CODE, not JSON. Write complete working React code that can be used directly.
Format your response with clear sections using comments like:
// === REACT COMPONENT ===
// === STYLES ===
// === HOOKS & API ===
// === DEPENDENCIES ==="""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response into sections
            result = {
                'component': '',
                'styles': '',
                'hooks': '',
                'dependencies': ''
            }
            
            # Split by section markers
            sections = {
                'component': r'//\s*===\s*REACT COMPONENT\s*===\s*(.*?)(?=//\s*===|$)',
                'styles': r'//\s*===\s*STYLES\s*===\s*(.*?)(?=//\s*===|$)',
                'hooks': r'//\s*===\s*HOOKS & API\s*===\s*(.*?)(?=//\s*===|$)',
                'dependencies': r'//\s*===\s*DEPENDENCIES\s*===\s*(.*?)(?=//\s*===|$)'
            }
            
            for key, pattern in sections.items():
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    result[key] = match.group(1).strip()
            
            # If no sections found, try to return the whole content
            if not any(result.values()):
                result['component'] = content
            
            return result
                
        except Exception as e:
            st.error(f"Frontend developer error: {str(e)}")
            return {}

def main():
    # Header
    st.markdown('<h1 class="main-header">⚡ Project Task Generator</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>AI-Powered Development Assistant</p>", unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
        st.title("Settings")
        
        api_key = st.text_input(
            "🔑 OpenAI API Key",
            type="password",
            value=st.session_state.openai_key,
            placeholder="sk-..."
        )
        
        if api_key:
            st.session_state.openai_key = api_key
            st.success("✓ API Key configured")
        
        st.divider()
        
        st.subheader("📊 Project Stats")
        if st.session_state.task_list:
            total = len(st.session_state.task_list)
            backend = sum(1 for t in st.session_state.task_list if t.get('category') == 'BACKEND')
            frontend = total - backend
            
            col1, col2 = st.columns(2)
            col1.metric("Backend", backend, delta=None)
            col2.metric("Frontend", frontend, delta=None)
        else:
            st.info("No tasks yet")
        
        st.divider()
        
        if st.button("🗑️ Reset Everything", use_container_width=True):
            st.session_state.task_list = []
            st.session_state.code_outputs = {}
            st.session_state.project_description = ''
            st.rerun()
        
        st.divider()
        st.caption("Powered by OpenAI GPT-3.5")
    
    # Main content
    if not st.session_state.openai_key:
        st.warning("👈 Please configure your OpenAI API key in the sidebar to get started")
        st.info("""
        **Get your API key:**
        1. Visit [OpenAI Platform](https://platform.openai.com/)
        2. Sign in or create an account
        3. Navigate to API Keys section
        4. Create a new secret key
        """)
        return
    
    # Project input section
    st.header("1️⃣ Describe Your Project")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        project_input = st.text_area(
            "What do you want to build?",
            placeholder="Example: A social media platform where users can create profiles, post updates, like and comment on posts, and follow other users",
            height=120,
            help="Be specific about features and functionality you need"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_clicked = st.button("🔍 Analyze Project", type="primary", use_container_width=True)
        
        if st.session_state.task_list:
            if st.button("✏️ Edit Tasks", use_container_width=True):
                st.session_state.task_list = []
                st.session_state.code_outputs = {}
    
    # Process project
    if analyze_clicked and project_input:
        with st.spinner("🤖 AI is analyzing your project..."):
            coordinator = ProjectCoordinator(st.session_state.openai_key)
            tasks = coordinator.analyze_and_breakdown(project_input)
            
            if tasks:
                st.session_state.task_list = tasks
                st.session_state.project_description = project_input
                st.success(f"✅ Generated {len(tasks)} technical tasks!")
                st.balloons()
            else:
                st.error("❌ Could not analyze project. Please try again with more details.")
    
    # Display tasks
    if st.session_state.task_list:
        st.header("2️⃣ Task Breakdown")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_option = st.selectbox(
                "Filter by type:",
                ["All Tasks", "Backend Only", "Frontend Only"]
            )
        
        filtered_tasks = st.session_state.task_list
        if filter_option == "Backend Only":
            filtered_tasks = [t for t in st.session_state.task_list if t.get('category') == 'BACKEND']
        elif filter_option == "Frontend Only":
            filtered_tasks = [t for t in st.session_state.task_list if t.get('category') == 'FRONTEND']
        
        # Display tasks in a grid
        for idx, task in enumerate(filtered_tasks):
            task_key = f"task_{task.get('id', idx)}"
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    category = task.get('category', 'UNKNOWN')
                    badge_class = 'backend-badge' if category == 'BACKEND' else 'frontend-badge'
                    
                    st.markdown(f"""
                    <div class="task-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0;">#{task.get('id', idx)} {task.get('name', 'Task')}</h3>
                            <span class="agent-badge {badge_class}">{category}</span>
                        </div>
                        <p style="color: #666; margin-top: 0.5rem;">{task.get('description', 'No description')}</p>
                        <small style="color: #999;">Priority: {task.get('priority', 'Medium')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if task_key not in st.session_state.code_outputs:
                        if st.button("⚙️ Generate", key=f"gen_{task_key}", use_container_width=True):
                            with st.spinner("Generating code..."):
                                if category == 'BACKEND':
                                    developer = BackendDeveloper(st.session_state.openai_key)
                                else:
                                    developer = FrontendDeveloper(st.session_state.openai_key)
                                
                                code = developer.create_implementation(
                                    task, 
                                    st.session_state.project_description
                                )
                                
                                if code:
                                    st.session_state.code_outputs[task_key] = {
                                        'task': task,
                                        'code': code,
                                        'generated_at': datetime.now().strftime("%H:%M:%S")
                                    }
                                    st.rerun()
                    else:
                        st.success("✓ Done")
                        if st.button("🔄", key=f"regen_{task_key}", use_container_width=True):
                            del st.session_state.code_outputs[task_key]
                            st.rerun()
    
    # Display generated code
    if st.session_state.code_outputs:
        st.header("3️⃣ Generated Code")
        
        for task_key, output in st.session_state.code_outputs.items():
            task = output['task']
            code = output['code']
            
            with st.expander(f"📝 {task.get('name', 'Code Output')} - Generated at {output['generated_at']}", expanded=True):
                if task.get('category') == 'BACKEND':
                    tab1, tab2, tab3, tab4 = st.tabs(["📦 Models", "🛣️ Routes", "⚙️ Logic", "📋 Dependencies"])
                    
                    with tab1:
                        st.code(code.get('models', '# No models generated'), language='python', line_numbers=True)
                    with tab2:
                        st.code(code.get('routes', '# No routes generated'), language='python', line_numbers=True)
                    with tab3:
                        st.code(code.get('logic', '# No logic generated'), language='python', line_numbers=True)
                    with tab4:
                        deps = code.get('dependencies', [])
                        if isinstance(deps, list):
                            st.markdown("```\n" + "\n".join(deps) + "\n```")
                        else:
                            st.code(deps, language='text')
                else:
                    tab1, tab2, tab3, tab4 = st.tabs(["⚛️ Component", "🎨 Styles", "🔗 Hooks", "📋 Dependencies"])
                    
                    with tab1:
                        st.code(code.get('component', '// No component generated'), language='javascript', line_numbers=True)
                    with tab2:
                        st.code(code.get('styles', '/* No styles generated */'), language='css', line_numbers=True)
                    with tab3:
                        st.code(code.get('hooks', '// No hooks generated'), language='javascript', line_numbers=True)
                    with tab4:
                        deps = code.get('dependencies', [])
                        if isinstance(deps, list):
                            st.markdown("```\n" + "\n".join(deps) + "\n```")
                        else:
                            st.code(deps, language='text')
        
        # Download all code button
        st.divider()
        if st.button("📥 Export All Code as JSON", type="secondary"):
            export_data = {
                'project': st.session_state.project_description,
                'tasks': st.session_state.task_list,
                'generated_code': st.session_state.code_outputs,
                'timestamp': datetime.now().isoformat()
            }
            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"project_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()