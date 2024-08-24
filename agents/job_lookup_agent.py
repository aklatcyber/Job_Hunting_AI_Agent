import os
import sys


# Add the parent directory to the system path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

    # Define the prompt template with instructions for the language model
    template = """'Persona':'You are an expert job hunter/recruiter based in Canada'
    'Context':'Given the list {name_of_job} I want you to get me the top 10 jobs in Senior Software Engineer jobs in Canada. It must be:
    - Full Time Permanent
    - Must be posted last 30 days
    - Less than or equal to 5 years experience needed
    - Remote Job
    - Must be in Canada
    'Format': 'The output must be in table form with job name in first column, 
    location in second column, link to apply in third column, salary in fourth column, on fifth column is the company name, 6th column add yes or no if its remote job,7th when it was posted'
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
