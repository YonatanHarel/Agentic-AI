"""
The UI of this program
"""

from research_manager import ResearchManager
import gradio as gr


async def run(query: str):
    async for chunk in ResearchManager().run(query):
        yield chunk
    
with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    query_textbox = gr.Textbox(label="What topiv would you like to research?")
    run_btn = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")

    run_btn.click(fn=run, inputs=query_textbox, outputs=report)
    query_textbox.submit(fn=run, inputs=query_textbox, outputs=report)

ui.launch(inbrowser=True)