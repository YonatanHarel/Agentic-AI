# Debate Project
In this project we have 2 kinds of agents and 3 kinds of tasks.
User responsible to giving the debate argument (aka <i>motion</i>)

## Agents
### debater
This agent responsible for creating a clear argument either in favor of or against the <i>motion</i>.

### judge
This agent responsible to take the debater agents arguments and decide which one is the winner based on the arguments.

## Tasks
Tasks arethe agents' operation.
Here for example, we have 2 tasks for debater agents - propose and oppose - which need to come up with argument in favor or against the <i>motion</i>.
The last task is the judgment task which is performed by the judge agent.


</br></br></br></br></br></br></br>


# CrewDebate Crew

Welcome to the CrewDebate Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/crew_debate/config/agents.yaml` to define your agents
- Modify `src/crew_debate/config/tasks.yaml` to define your tasks
- Modify `src/crew_debate/crew.py` to add your own logic, tools and specific args
- Modify `src/crew_debate/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the crew_debate Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The crew_debate Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the CrewDebate Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
