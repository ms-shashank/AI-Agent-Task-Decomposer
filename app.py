import streamlit as st
import openai
import json
import re
from typing import List, Dict
from datetime import datetime


st.set_page_config(
    page_title="AI Agent Task Decomposer",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = {}
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

class CoordinatorAgent:
    """Main coordinator that breaks down project briefs into tasks"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def decompose_project(self, project_brief: str) -> List[Dict]:
        """Break down project brief into technical tasks"""
        
        prompt = f"""You are a technical project coordinator. Given a project brief, break it down into specific, actionable technical tasks.

Project Brief: {project_brief}

Analyze this project and create a list of tasks. For each task:
1. Provide a clear task title
2. Specify if it's a FRONTEND or BACKEND task
3. Give detailed requirements
4. List dependencies (if any)

Return your response as a JSON array with this structure:
[
    {{
        "task_id": 1,
        "title": "Task title",
        "agent_type": "FRONTEND" or "BACKEND",
        "requirements": "Detailed description of what needs to be built",
        "dependencies": []
    }}
]

Focus on:
- User authentication and authorization
- Database schema design
- API endpoints
- Frontend components
- Business logic workflows
- Data validation

Return ONLY the JSON array, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical project coordinator that decomposes projects into tasks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                tasks = json.loads(json_match.group())
                return tasks
            else:
                return json.loads(content)
                
        except Exception as e:
            st.error(f"Error in coordinator agent: {str(e)}")
            return []

class BackendAgent:
    """Backend agent that generates APIs, business logic, and database schemas"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_code(self, task: Dict, project_context: str) -> Dict:
        """Generate backend code including API, business logic, and database schema"""
        
        prompt = f"""You are a backend development expert specializing in Python FastAPI and SQLite3.

Project Context: {project_context}

Task: {task['title']}
Requirements: {task['requirements']}

Generate complete, production-ready code including:

1. DATABASE SCHEMA (SQLite3 with SQLAlchemy)
2. API ENDPOINTS (FastAPI with proper routing)
3. BUSINESS LOGIC (validation, workflows, error handling)
4. AUTHENTICATION (if required - JWT based)

Return your response as a JSON object with this structure:
{{
    "database_schema": "Complete SQLAlchemy models code",
    "api_endpoints": "Complete FastAPI router code",
    "business_logic": "Helper functions and business logic",
    "requirements": "List of Python packages needed"
}}

Make the code:
- Production-ready with error handling
- Well-documented with comments
- Following best practices
- Scalable and maintainable
- Include proper validation

Return ONLY the JSON object."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert backend developer specializing in Python, FastAPI, and SQLite3."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                code = json.loads(json_match.group())
                return code
            else:
                return json.loads(content)
                
        except Exception as e:
            st.error(f"Error in backend agent: {str(e)}")
            return {}

class FrontendAgent:
    """Frontend agent that generates React components"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_code(self, task: Dict, project_context: str) -> Dict:
        """Generate React UI components"""
        
        prompt = f"""You are a frontend development expert specializing in React and responsive UI design.

Project Context: {project_context}

Task: {task['title']}
Requirements: {task['requirements']}

Generate complete, production-ready React components including:

1. MAIN COMPONENT (React functional component with hooks)
2. STYLING (Tailwind CSS or inline styles for responsiveness)
3. STATE MANAGEMENT (useState, useEffect as needed)
4. API INTEGRATION (fetch calls to backend)
5. FORM VALIDATION (if applicable)

Return your response as a JSON object with this structure:
{{
    "component_code": "Complete React component code",
    "styling": "CSS or Tailwind classes",
    "api_integration": "API call functions",
    "dependencies": "List of npm packages needed"
}}

Make the code:
- Responsive and mobile-friendly
- Accessible (ARIA labels, semantic HTML)
- Well-documented with comments
- Following React best practices
- Include proper error handling

Return ONLY the JSON object."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert frontend developer specializing in React and responsive UI design."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                code = json.loads(json_match.group())
                return code
            else:
                return json.loads(content)
                
        except Exception as e:
            st.error(f"Error in frontend agent: {str(e)}")
            return {}

def main():
    st.title("🤖 AI Agent Task Decomposer")
    st.markdown("### Transform project briefs into concrete technical tasks and code")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            help="Enter your OpenAI API key"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("API Key set!")
        
        # st.markdown("---")
        # st.markdown("### About")
        # st.markdown("""
        # This AI agent system:
        # - 🎯 Decomposes project briefs
        # - 🔨 Generates backend code (FastAPI + SQLite)
        # - 🎨 Creates frontend components (React)
        # - 📋 Manages task dependencies
        # """)
        
        if st.button("Clear All Tasks", type="secondary"):
            st.session_state.tasks = []
            st.session_state.generated_code = {}
            st.rerun()
    
    # Main content
    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
        return
    
    # Project brief input
    st.header("📝 Step 1: Enter Project Brief")
    project_brief = st.text_area(
        "Describe your project",
        placeholder="Example: Build a task management app with user authentication and task sharing",
        height=100
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        decompose_btn = st.button("🚀 Decompose Project", type="primary", disabled=not project_brief)
    
    # Decompose project
    if decompose_btn and project_brief:
        with st.spinner("🤔 Analyzing project and breaking down tasks..."):
            coordinator = CoordinatorAgent(st.session_state.api_key)
            tasks = coordinator.decompose_project(project_brief)
            
            if tasks:
                st.session_state.tasks = tasks
                st.session_state.project_brief = project_brief
                st.success(f"✅ Decomposed into {len(tasks)} tasks!")
            else:
                st.error("Failed to decompose project. Please try again.")
    
    # Display tasks
    if st.session_state.tasks:
        st.header("📋 Step 2: Review Tasks")
        
        # Task summary
        backend_tasks = sum(1 for t in st.session_state.tasks if t.get('agent_type') == 'BACKEND')
        frontend_tasks = sum(1 for t in st.session_state.tasks if t.get('agent_type') == 'FRONTEND')
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", len(st.session_state.tasks))
        col2.metric("Backend Tasks", backend_tasks)
        col3.metric("Frontend Tasks", frontend_tasks)
        
        # Display each task
        for i, task in enumerate(st.session_state.tasks):
            with st.expander(f"Task {task.get('task_id', i+1)}: {task.get('title', 'Untitled')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Type:** `{task.get('agent_type', 'UNKNOWN')}`")
                    st.markdown(f"**Requirements:** {task.get('requirements', 'No requirements specified')}")
                    
                    if task.get('dependencies'):
                        st.markdown(f"**Dependencies:** {', '.join(map(str, task['dependencies']))}")
                
                with col2:
                    task_key = f"task_{task.get('task_id', i+1)}"
                    
                    if task_key not in st.session_state.generated_code:
                        if st.button(f"Generate Code", key=f"gen_{task_key}"):
                            with st.spinner(f"Generating code for {task.get('title')}..."):
                                if task.get('agent_type') == 'BACKEND':
                                    agent = BackendAgent(st.session_state.api_key)
                                else:
                                    agent = FrontendAgent(st.session_state.api_key)
                                
                                code = agent.generate_code(task, st.session_state.project_brief)
                                
                                if code:
                                    st.session_state.generated_code[task_key] = {
                                        'task': task,
                                        'code': code,
                                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                    st.rerun()
                    else:
                        st.success("✅ Code Generated")
                        if st.button(f"Regenerate", key=f"regen_{task_key}"):
                            del st.session_state.generated_code[task_key]
                            st.rerun()
    
    # Display generated code
    if st.session_state.generated_code:
        st.header("💻 Step 3: Generated Code")
        
        for task_key, data in st.session_state.generated_code.items():
            task = data['task']
            code = data['code']
            
            st.subheader(f"📦 {task.get('title', 'Untitled')}")
            st.caption(f"Generated at: {data['timestamp']}")
            
            if task.get('agent_type') == 'BACKEND':
                # Backend code display
                tabs = st.tabs(["Database Schema", "API Endpoints", "Business Logic", "Requirements"])
                
                with tabs[0]:
                    st.code(code.get('database_schema', 'No schema generated'), language='python')
                
                with tabs[1]:
                    st.code(code.get('api_endpoints', 'No endpoints generated'), language='python')
                
                with tabs[2]:
                    st.code(code.get('business_logic', 'No business logic generated'), language='python')
                
                with tabs[3]:
                    requirements = code.get('requirements', 'No requirements specified')
                    if isinstance(requirements, list):
                        st.markdown('\n'.join([f"- {req}" for req in requirements]))
                    else:
                        st.text(requirements)
            
            else:
                # Frontend code display
                tabs = st.tabs(["Component", "Styling", "API Integration", "Dependencies"])
                
                with tabs[0]:
                    st.code(code.get('component_code', 'No component generated'), language='javascript')
                
                with tabs[1]:
                    styling = code.get('styling', 'No styling provided')
                    st.code(styling, language='css')
                
                with tabs[2]:
                    st.code(code.get('api_integration', 'No API integration provided'), language='javascript')
                
                with tabs[3]:
                    dependencies = code.get('dependencies', 'No dependencies specified')
                    if isinstance(dependencies, list):
                        st.markdown('\n'.join([f"- {dep}" for dep in dependencies]))
                    else:
                        st.text(dependencies)
            
            st.markdown("---")

if __name__ == "__main__":
    main()