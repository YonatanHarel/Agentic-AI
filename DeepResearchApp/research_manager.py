"""
Orchestrate all the flow and agents calls
"""
import asyncio
from agents import Runner, gen_trace_id, trace
from search_agent import search_agent
from email_agent import email_agent
from writer_agent import ReportData, writer_agent
from planner_agent import WebSearchItem, WebSearchPlan, planner_agent
from dotenv import load_dotenv

load_dotenv(override=True)


class ResearchManager:
    
    async def run(self, query: str):
        """ Run the deep research process, yeilding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/logs/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/logs/trace?trace_id={trace_id}"
            print("Starting research...")
            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan)
            yield "Searches completed, generating report..."
            report = await self.write_report(query, search_results)
            yield "Finished writing the report, going to send it by email..."
            await self.send_email(report)
            yield "Email sent, research completed"
            yield report.markdown_report            


    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query"""
        print("Searching...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)


    async def perform_searches(self, search_plan: WebSearchPlan):
        """ Call search() for each item in the plan.
        This actually perform the searches we have according to HOW_MANY_SEARCHES.
        We will run all the tasks in parallel and gether all results  
        """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results


    async def search(self, item: WebSearchItem):
        """ Perform a search for the query"""
        input = f"Search term: {item.query}\nReason for seasrching: {item.reason}"
        try:
            result = await Runner.run(search_agent, input)
            return result.final_output
        except Exception:
            return None


    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report of the query"""
        print("Generating report based on the search results...")
        input = f"Original query: {query}\nSummarized seasrch results: {search_results}"
        result = await Runner.run(writer_agent, input)
        print("Finished writing report")
        return result.final_output_as(ReportData)

    async def send_email(self, report: ReportData) -> None:
        print("Writing and sending the email...")
        result = await Runner.run(email_agent, report.markdown_report)
        print("Email sent")