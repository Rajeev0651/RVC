"""Module which defines the code for the "Settings" tab."""

from __future__ import annotations

from functools import partial

import gradio as gr

from ultimate_rvc.core.manage.settings import delete_temp_files
from ultimate_rvc.web.common import confirm_box_js, confirmation_harness, render_msg


def render() -> None:
    """Render "Settings" tab."""
    dummy_checkbox = gr.Checkbox(visible=False)

    gr.Markdown("")
    with gr.Accordion("Temporary files", open=True):
        gr.Markdown("")
        with gr.Row(equal_height=True):
            temporary_files_btn = gr.Button("Delete all", variant="primary")
            temporary_files_msg = gr.Textbox(label="Output message", interactive=False)

    temporary_files_btn.click(
        confirmation_harness(delete_temp_files),
        inputs=dummy_checkbox,
        outputs=temporary_files_msg,
        js=confirm_box_js(
            "Are you sure you want to delete all temporary files? Any files uploaded"
            " directly via the UI will not be available for further processing until"
            " they are re-uploaded.",
        ),
    ).success(
        partial(
            render_msg,
            "[-] Successfully deleted all temporary files!",
        ),
        outputs=temporary_files_msg,
        show_progress="hidden",
    )
