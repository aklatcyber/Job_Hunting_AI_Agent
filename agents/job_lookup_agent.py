from langchain import hub
from langchain.agents import (
    create_react_agent,
    AgentExecutor,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from dotenv import load_dotenv
from agent_api.serpjob import scrape_job_profile
import os
import sys


# Add the parent directory to the system path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from a .env file
dotenv_path = '~/.env'
load_dotenv(dotenv_path=dotenv_path)

# Define the lookup function to find job profiles
def lookup(name: str) -> str:
     # Initialize the OpenAI language model with specified parameters
    llm = ChatOpenAI(
        temperature=0, # Set temperature to 0 for deterministic output
        model_name="gpt-4", # Use the GPT-4 model
        openai_api_key=os.environ["OPENAI_API_KEY"], # API key for authentication
    )

    # Example Format: AI provides an example to guide the user
    example_format = """
    Example Output:
    
    | Job Name                     | Location          | Link to Apply                     | Salary      | Company Name    | Remote Job | Posted Date |
    |------------------------------|-------------------|-----------------------------------|-------------|-----------------|------------|-------------|
    | Senior Software Engineer        | Vancouver, BC     | [Apply Here](https://example.com)  | $120k-$150k | ABC Tech         | Yes        | 2024-08-20  |
    | Software Specialist                | Remote, BC        | [Apply Here](https://example.com)  | $130k-$160k | XYZ Innovations  | Yes        | 2024-08-18  |
    | Lead Software Engineer| Victoria, BC      | [Apply Here](https://example.com)  | $110k-$140k | InnovateAI       | Yes        | 2024-08-15  |
    """

    # Define the prompt template with instructions for the language model
    template = f"""'Persona':'You are an expert job hunter/recruiter based in Canada'
    'Context':'Given the list {{name_of_job}} I want you to get me the top 10 jobs in Senior Software Engineer jobs in Canada. It must be:
    - Full Time Permanent
    - Must be posted last 30 days
    - Less than or equal to 5 years experience needed
    - Remote Job
    - Must be in Canada
    'Format': 'The output must be in table form with the following columns:
    1. Job Name
    2. Location
    3. Link to Apply
    4. Salary
    5. Company Name
    6. Remote Job (Yes/No)
    7. Posted Date

    Please follow the example format below for the table structure:

    {example_format}'
    """

    # Create a PromptTemplate object with the defined template
    prompt_template = PromptTemplate(
        template=template, input_variables=["name_of_job"]
    )

    # Define tools available for the agent, including the job scraping function
    tools_for_agent = [
        Tool(
            name="Crawl Google 4 list of jobs",
            func=scrape_job_profile,
            description="useful for when you need get the list of jobs",
        )
    ]

    # Pull the React prompt from the hub
    react_prompt = hub.pull("hwchase17/react")

    # Create a React agent with the language model and tools
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)

    # Create an AgentExecutor to run the agent with verbose output
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)

    # Invoke the agent with the formatted prompt and capture the result
    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(name_of_job=name)}
    )

    # Extract and return the job profile URLs from the result
    job_url_profile = result["output"]
    return job_url_profile

# Run the lookup function if the script is executed directly
if __name__ == "__main__":
    job_urls = lookup(name="Remote Senior Software Engineer jobs in Canada")
    print(job_urls)
